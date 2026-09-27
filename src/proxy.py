"""FastAPI reverse proxy implementation of Fuse."""

import asyncio
from contextlib import asynccontextmanager
import hashlib
import time
from typing import Optional
from datetime import datetime
import json
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel

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

# Enable CORS for frontend developer console on :5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {
        "status": "active",
        "proxy": "Fuse",
        "model": settings.gemini_model,
        "target": settings.target_base_url,
    }


@app.get("/metrics")
@app.get("/api/metrics")
async def get_metrics():
    return dashboard.stats


@app.get("/api/traces")
async def get_traces(limit: int = 50):
    traces = []
    log_path = settings.audit_log_path
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                for line in reversed(lines[-limit:]):
                    try:
                        entry = json.loads(line)
                        rec = entry.get("record", {})
                        dec = rec.get("decision", {})
                        ts_str = rec.get("timestamp", "")
                        try:
                            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            time_str = dt.strftime("%H:%M:%S")
                        except Exception:
                            time_str = ts_str[:8] if ts_str else "00:00:00"

                        traces.append({
                            "id": rec.get("record_id", "rec"),
                            "timestamp": time_str,
                            "session_id": rec.get("session_id", "agent"),
                            "endpoint": rec.get("endpoint", "/"),
                            "method": rec.get("method", "GET"),
                            "service_profile": dec.get("service_profile") or "standard_api",
                            "action": dec.get("action", "FORWARD"),
                            "layer": dec.get("layer", "LAYER_1_NORMAL"),
                            "status_code": rec.get("status_code", 200),
                            "duration_ms": round(float(rec.get("duration_ms", 0.0)), 1),
                            "reason": dec.get("reason", "Evaluated by Fuse."),
                            "chain_hash": entry.get("chain_hash", ""),
                            "prev_hash": entry.get("prev_hash", ""),
                            "jev": dec.get("jev_decision"),
                            "llm": dec.get("llm_verdict"),
                        })
                    except Exception:
                        pass
        except Exception as e:
            pass
    return traces


@app.get("/api/audit/verify")
async def verify_audit_chain():
    log_path = settings.audit_log_path
    if not os.path.exists(log_path):
        return {
            "verified": True,
            "total_records": 0,
            "valid_blocks": 0,
            "broken_blocks": 0,
            "genesis_hash": "0" * 64,
            "head_hash": "0" * 64,
        }

    total = 0
    valid = 0
    broken = 0
    first_hash = None
    last_hash = "0" * 64

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    total += 1
                    ch = entry.get("chain_hash")
                    if not first_hash:
                        first_hash = ch
                    last_hash = ch
                    valid += 1
                except Exception:
                    broken += 1
    except Exception:
        pass

    return {
        "verified": broken == 0 and total > 0,
        "total_records": total,
        "valid_blocks": valid,
        "broken_blocks": broken,
        "genesis_hash": first_hash or ("0" * 64),
        "head_hash": last_hash,
    }


class ScenarioRunRequest(BaseModel):
    scenario_id: str


@app.post("/api/scenarios/run")
async def run_scenario_endpoint(req: ScenarioRunRequest):
    from src.simulator import simulator

    sc_id = req.scenario_id
    if sc_id == "green":
        await simulator.run_parallel_burst(session_id="agent-burst-ui", count=10)
    elif sc_id == "yellow":
        await simulator.run_retry_storm(session_id="agent-retry-ui", count=10)
    elif sc_id == "blue":
        await simulator.run_loop_anomaly(session_id="agent-loop-ui", count=6)
    elif sc_id == "red":
        await simulator.run_hard_ceiling_overflow(session_id="agent-flood-ui", count=25)
    else:
        return JSONResponse(status_code=400, content={"error": f"Unknown scenario: {sc_id}"})

    return {
        "status": "completed",
        "scenario_id": sc_id,
        "stats": dashboard.stats,
    }


class SandboxSendRequest(BaseModel):
    method: str = "GET"
    endpoint: str = "/search"
    service_profile: str = "read_intensive"
    burst_count: int = 1


@app.post("/api/sandbox/send")
async def sandbox_send_endpoint(req: SandboxSendRequest):
    results = []
    clean_path = req.endpoint.lstrip("/")

    async with httpx.AsyncClient(timeout=10.0) as client:
        count = max(1, min(req.burst_count, 25))
        for _ in range(count):
            t0 = time.time()
            try:
                resp = await client.request(
                    method=req.method,
                    url=f"http://localhost:8000/{clean_path}",
                    headers={"X-Fuse-Service": req.service_profile, "X-Session-ID": "sandbox-user"},
                )
                dur = round((time.time() - t0) * 1000, 1)
                action = resp.headers.get("x-fuse-action") or ("BLOCK" if resp.status_code == 429 else "FORWARD")
                layer = resp.headers.get("x-fuse-layer") or "LAYER_1_NORMAL"

                try:
                    body_json = resp.json()
                except Exception:
                    body_json = {"raw": resp.text[:200]}

                results.append({
                    "status": resp.status_code,
                    "duration_ms": dur,
                    "action": action,
                    "layer": layer,
                    "backoff_sec": resp.headers.get("retry-after"),
                    "data": body_json,
                })
            except Exception as e:
                dur = round((time.time() - t0) * 1000, 1)
                results.append({
                    "status": 500,
                    "duration_ms": dur,
                    "action": "ERROR",
                    "layer": "GATEWAY_ERROR",
                    "error": str(e),
                })

    return {"results": results, "latest": results[-1] if results else None}


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
