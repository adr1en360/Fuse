"""FastAPI reverse proxy implementation of Fuse."""

import asyncio
from contextlib import asynccontextmanager
import hashlib
import time
from typing import Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx

from src.config import settings
from src.dashboard import dashboard
from src.jev_client import jev_client
from src.llm_client import gemini_client
from src.models import (
    CallRecord,
    DecisionResult,
    RoutingAction,
    ServiceProfile,
)
from src.router import router
from src.sliding_window import window_tracker

http_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(connect=0.2, read=10.0, write=5.0, pool=5.0)
    )
    yield
    if http_client:
        await http_client.aclose()


# In-memory burst cache to prevent redundant AI model API calls during rapid concurrent bursts
_decision_cache = {}


def get_cached_decision(session_id: str, max_age: float = 3.0) -> Optional[DecisionResult]:
    if session_id in _decision_cache:
        ts, dec = _decision_cache[session_id]
        if time.time() - ts < max_age:
            return dec
    return None


def set_cached_decision(session_id: str, decision: DecisionResult) -> None:
    _decision_cache[session_id] = (time.time(), decision)


app = FastAPI(
    title="Fuse Intelligent Circuit Breaker",
    description="Confidence-gated agent proxy powered by Jev (TypeSafe System One) and Gemini 3.8 Flash",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {
        "status": "active",
        "proxy": "Fuse",
        "model": settings.gemini_model,
        "target": settings.target_base_url,
    }


@app.get("/metrics")
async def get_metrics():
    return dashboard.stats


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_handler(request: Request, full_path: str):
    start_time = time.time()
    body_bytes = await request.body()

    # 1. Identify Session & Service Context
    session_id = (
        request.headers.get("X-Session-ID")
        or request.query_params.get("session_id")
        or "agent-default"
    )
    service_hint = request.headers.get("X-Fuse-Service")
    service_profile = ServiceProfile.from_request(
        method=request.method,
        path=f"/{full_path}",
        header_hint=service_hint,
    )

    # 2. Compute canonical argument hash
    hash_payload = f"{request.method}:{full_path}:{request.url.query}:{body_bytes.decode('utf-8', errors='ignore')}"
    arg_hash = hashlib.sha256(hash_payload.encode()).hexdigest()[:12]
    call_id = f"call-{int(start_time * 1000)}-{arg_hash[:6]}"

    call_record = CallRecord(
        call_id=call_id,
        session_id=session_id,
        timestamp=start_time,
        iso_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start_time)),
        method=request.method,
        endpoint=f"/{full_path}",
        arg_hash=arg_hash,
    )

    # 3. Layer 1 Deterministic Evaluation
    is_ceil, ceil_count, ceil_limit = window_tracker.check_hard_ceiling(session_id, now=start_time)
    is_anom, anom_count, anom_limit = window_tracker.check_anomaly_threshold(session_id, now=start_time)

    layer1_decision = router.route_layer1(
        is_ceiling_breached=is_ceil,
        ceiling_count=ceil_count,
        ceiling_limit=ceil_limit,
        is_anomaly_breached=is_anom,
        anomaly_count=anom_count,
        anomaly_limit=anom_limit,
    )

    # Case A: Hard Ceiling Breached -> BLOCK immediately (Zero AI bypass)
    if layer1_decision and layer1_decision.action == RoutingAction.BLOCK:
        window_tracker.record_call(call_record)
        duration_ms = (time.time() - start_time) * 1000
        dashboard.record_decision(
            session_id=session_id,
            endpoint=f"/{full_path}",
            method=request.method,
            arg_hash=arg_hash,
            decision=layer1_decision,
            status_code=429,
            duration_ms=duration_ms,
        )
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(int(settings.hard_ceiling_window_seconds))},
            content={
                "error": "Hard ceiling tripped",
                "message": layer1_decision.reason,
                "layer": layer1_decision.layer,
                "action": layer1_decision.action.value,
            },
        )

    # Case B: Normal call rate under anomaly threshold -> Forward directly
    if layer1_decision and layer1_decision.action == RoutingAction.FORWARD:
        window_tracker.record_call(call_record)
        return await forward_to_downstream(
            request=request,
            full_path=full_path,
            body_bytes=body_bytes,
            session_id=session_id,
            arg_hash=arg_hash,
            start_time=start_time,
            decision=layer1_decision,
            call_record=call_record,
        )

    # Case C: Anomaly Threshold Tripped -> Escalate to Layer 2 (Jev System One)
    window_tracker.record_call(call_record)
    recent_calls = window_tracker.get_recent_window(session_id, limit=10)
    ceiling_usage = window_tracker.get_ceiling_usage(session_id, now=start_time)

    # Check session decision cache to prevent duplicate AI calls during high-concurrency bursts
    cached_decision = get_cached_decision(session_id, max_age=3.0)
    if cached_decision:
        final_decision = cached_decision
    else:
        jev_decision = await jev_client.evaluate(
            session_id=session_id,
            recent_calls=recent_calls,
            ceiling_usage=ceiling_usage,
            service_profile=service_profile,
        )

        layer2_decision = router.route_layer2(
            jev=jev_decision,
            service_profile=service_profile,
            ceiling_usage=ceiling_usage,
        )

        final_decision = layer2_decision

        # Case D: Jev Escaped ('unrecognized') or Low Confidence -> Escalate to Layer 3 (Gemini 3.8 Flash)
        if layer2_decision.action == RoutingAction.ESCALATE_LLM:
            llm_verdict = await gemini_client.analyze_root_cause(
                session_id=session_id,
                recent_calls=recent_calls,
                service_profile=service_profile,
                jev_decision=jev_decision,
                ceiling_usage=ceiling_usage,
            )
            final_decision = router.apply_llm_verdict(
                verdict=llm_verdict,
                jev_decision=jev_decision,
                service_profile=service_profile,
            )

        set_cached_decision(session_id, final_decision)

    # 4. Enforce Final Decision Action
    if final_decision.action == RoutingAction.FORWARD:
        return await forward_to_downstream(
            request=request,
            full_path=full_path,
            body_bytes=body_bytes,
            session_id=session_id,
            arg_hash=arg_hash,
            start_time=start_time,
            decision=final_decision,
            call_record=call_record,
        )

    elif final_decision.action == RoutingAction.BACKOFF:
        backoff_sec = final_decision.backoff_seconds or 2.0
        await asyncio.sleep(backoff_sec)
        return await forward_to_downstream(
            request=request,
            full_path=full_path,
            body_bytes=body_bytes,
            session_id=session_id,
            arg_hash=arg_hash,
            start_time=start_time,
            decision=final_decision,
            call_record=call_record,
            extra_headers={"X-Fuse-Backoff-Applied": f"{backoff_sec}s"},
        )

    elif final_decision.action == RoutingAction.BLOCK:
        duration_ms = (time.time() - start_time) * 1000
        dashboard.record_decision(
            session_id=session_id,
            endpoint=f"/{full_path}",
            method=request.method,
            arg_hash=arg_hash,
            decision=final_decision,
            status_code=429,
            duration_ms=duration_ms,
        )
        return JSONResponse(
            status_code=429,
            content={
                "error": "Circuit breaker tripped",
                "reason": final_decision.reason,
                "layer": final_decision.layer,
                "action": final_decision.action.value,
                "remediation": getattr(final_decision.llm_verdict, "remediation_advice", None),
            },
        )

    elif final_decision.action == RoutingAction.ESCALATE_HUMAN:
        duration_ms = (time.time() - start_time) * 1000
        dashboard.record_decision(
            session_id=session_id,
            endpoint=f"/{full_path}",
            method=request.method,
            arg_hash=arg_hash,
            decision=final_decision,
            status_code=429,
            duration_ms=duration_ms,
        )
        return JSONResponse(
            status_code=429,
            content={
                "error": "Escalated to human operator",
                "reason": final_decision.reason,
                "layer": final_decision.layer,
                "action": final_decision.action.value,
            },
        )

    # Fallback default forward
    return await forward_to_downstream(
        request=request,
        full_path=full_path,
        body_bytes=body_bytes,
        session_id=session_id,
        arg_hash=arg_hash,
        start_time=start_time,
        decision=final_decision,
        call_record=call_record,
    )


async def forward_to_downstream(
    request: Request,
    full_path: str,
    body_bytes: bytes,
    session_id: str,
    arg_hash: str,
    start_time: float,
    decision: DecisionResult,
    call_record: CallRecord,
    extra_headers: Optional[dict] = None,
) -> Response:
    """Forwards call to target downstream service and logs metrics."""
    global http_client
    target_url = f"{settings.target_base_url.rstrip('/')}/{full_path}"
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    headers = dict(request.headers)
    headers.pop("host", None)
    if extra_headers:
        headers.update(extra_headers)

    headers["X-Fuse-Proxy"] = "active"
    headers["X-Fuse-Layer"] = decision.layer

    status_code = 200
    response_content = b"{}"
    response_headers = {}

    try:
        if http_client is None:
            http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(connect=0.2, read=10.0, write=5.0, pool=5.0)
            )

        resp = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body_bytes,
        )
        status_code = resp.status_code
        response_content = resp.content
        response_headers = dict(resp.headers)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        # Fallback simulation if downstream mock server not running
        status_code = 200
        response_content = (
            b'{"status": "simulated_ok", "message": "Downstream target simulated response"}'
        )
    except Exception as e:
        status_code = 502
        response_content = json.dumps({"error": "Bad Gateway", "details": str(e)}).encode()

    duration_ms = (time.time() - start_time) * 1000
    call_record.status_code = status_code
    call_record.latency_ms = duration_ms

    dashboard.record_decision(
        session_id=session_id,
        endpoint=f"/{full_path}",
        method=request.method,
        arg_hash=arg_hash,
        decision=decision,
        status_code=status_code,
        duration_ms=duration_ms,
    )

    response_headers["X-Fuse-Proxy"] = "active"
    response_headers["X-Fuse-Layer"] = decision.layer

    return Response(
        content=response_content,
        status_code=status_code,
        headers=response_headers,
    )
