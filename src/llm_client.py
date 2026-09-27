"""Layer 3: Gemini 3.8 Flash root-cause analysis client.

Invoked when Jev System One triggers the escape hatch ('unrecognized')
or reports low confidence on an ambiguous traffic pattern.
"""

import json
import logging
from typing import List, Optional
from google import genai
from google.genai import types

from src.config import settings
from src.models import (
    CallRecord,
    JevDecision,
    LLMVerdict,
    RoutingAction,
    ServiceProfile,
)

logger = logging.getLogger("fuse.llm")


class GeminiRootCauseClient:
    """Performs deep session inspection and root-cause analysis using Gemini."""

    def __init__(
        self,
        api_key: str = settings.gemini_api_key,
        model: str = settings.gemini_model,
    ):
        self.api_key = api_key
        self.model = model
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    async def analyze_root_cause(
        self,
        session_id: str,
        recent_calls: List[CallRecord],
        service_profile: ServiceProfile,
        jev_decision: Optional[JevDecision],
        ceiling_usage: str,
    ) -> LLMVerdict:
        """Sends session history to Gemini 3.8 Flash for deep root-cause synthesis."""
        client = self._get_client()

        calls_summary = [
            {
                "call_id": c.call_id,
                "endpoint": c.endpoint,
                "method": c.method,
                "arg_hash": c.arg_hash,
                "status_code": c.status_code,
                "latency_ms": c.latency_ms,
                "iso_timestamp": c.iso_timestamp,
            }
            for c in recent_calls
        ]

        jev_summary = (
            {
                "pattern_type": jev_decision.pattern_type.value,
                "pattern_confidence": jev_decision.pattern_confidence,
                "is_anomaly": jev_decision.is_anomaly,
                "severity_score": jev_decision.severity_score,
            }
            if jev_decision
            else "None (Evaluated directly by Layer 3)"
        )

        prompt = f"""
You are the Root Cause Analysis engine inside Fuse, an intelligent circuit breaker proxy for AI agents.
An autonomous agent's outbound calls have tripped the anomaly detector. Jev (System One) was either unsure or flagged an unrecognized pattern.

Context:
- Session ID: {session_id}
- Downstream Service Profile: {service_profile.model_dump_json()}
- Current Ceiling Usage: {ceiling_usage}
- Jev Initial Assessment: {json.dumps(jev_summary)}

Recent Call History:
{json.dumps(calls_summary, indent=2)}

Perform a thorough root-cause diagnosis. Return a valid JSON object with EXACTLY these fields:
{{
  "diagnosis": "Brief summary of what the agent is doing wrong or whether this is safe",
  "root_cause": "The underlying cause (e.g. repeated 503 without exponential backoff, alternating loop without state change, or safe parallel retrieval)",
  "recommended_action": "FORWARD" | "BACKOFF" | "BLOCK" | "ESCALATE_HUMAN",
  "suggested_backoff_seconds": float (e.g. 3.0 or 0.0),
  "can_auto_remediate": boolean,
  "remediation_advice": "Actionable feedback for agent prompt or error message"
}}
Return only the raw JSON string without markdown fencing.
"""

        try:
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )

            text = response.text or "{}"
            data = json.loads(text)

            rec_action_str = data.get("recommended_action", "BACKOFF").upper()
            try:
                rec_action = RoutingAction(rec_action_str)
            except ValueError:
                rec_action = RoutingAction.BACKOFF

            return LLMVerdict(
                diagnosis=data.get("diagnosis", "Automated root cause analysis completed."),
                root_cause=data.get("root_cause", "Unspecified agent pattern anomaly."),
                recommended_action=rec_action,
                suggested_backoff_seconds=float(data.get("suggested_backoff_seconds", 3.0)),
                can_auto_remediate=bool(data.get("can_auto_remediate", False)),
                remediation_advice=data.get("remediation_advice", ""),
            )

        except Exception as e:
            logger.warning("Gemini analysis call failed (%s). Using fallback heuristic verdict.", e)
            return self._heuristic_fallback(recent_calls, service_profile, jev_decision)

    def _heuristic_fallback(
        self,
        recent_calls: List[CallRecord],
        service_profile: ServiceProfile,
        jev_decision: Optional[JevDecision],
    ) -> LLMVerdict:
        """Deterministic root-cause synthesis when offline or during test mocking."""
        arg_hashes = [c.arg_hash for c in recent_calls]
        unique_hashes = len(set(arg_hashes))

        if unique_hashes == 1 and len(recent_calls) >= 3:
            return LLMVerdict(
                diagnosis="Agent is stuck in an unchecked retry loop hitting identical endpoint.",
                root_cause="Downstream service temporary failure without agent exponential backoff logic.",
                recommended_action=RoutingAction.BACKOFF,
                suggested_backoff_seconds=4.0 if service_profile.is_mutating else 2.0,
                can_auto_remediate=True,
                remediation_advice="Inject Retry-After header and pause agent turn execution.",
            )

        return LLMVerdict(
            diagnosis="Complex repeating pattern with non-advancing state.",
            root_cause="Cyclical tool dependency or prompt hallucination.",
            recommended_action=RoutingAction.BLOCK,
            suggested_backoff_seconds=0.0,
            can_auto_remediate=False,
            remediation_advice="Interrupt agent execution and prompt user for manual disambiguation.",
        )


gemini_client = GeminiRootCauseClient()
