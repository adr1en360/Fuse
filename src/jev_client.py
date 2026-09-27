"""Layer 2: Jev (TypeSafe AI System One) decision engine.

Queries Jev using typed primitives (Choice, Score, Noul) with calibrated confidence.
Embeds the downstream service profile into state for context-aware risk analysis.
"""

import logging
from typing import Any, Dict, List, Optional
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score

from src.config import settings
from src.models import (
    CallRecord,
    JevDecision,
    JevState,
    PatternType,
    ServiceProfile,
)

logger = logging.getLogger("fuse.jev")


class JevClient:
    """Interface to TypeSafe AI's Jev System One model."""

    def __init__(self, api_key: str = settings.typesafe_api_key):
        self.api_key = api_key
        self._client: Optional[AsyncTypeSafeClient] = None

    def _get_client(self) -> AsyncTypeSafeClient:
        if self._client is None:
            self._client = AsyncTypeSafeClient(api_key=self.api_key)
        return self._client

    def build_state(
        self,
        session_id: str,
        recent_calls: List[CallRecord],
        ceiling_usage: str,
        service_profile: ServiceProfile,
        prior_decisions: Optional[List[str]] = None,
    ) -> JevState:
        """Constructs state context including service profile, call window, and ceiling metrics."""
        call_window = [
            {
                "call_id": c.call_id,
                "method": c.method,
                "endpoint": c.endpoint,
                "arg_hash": c.arg_hash,
                "status_code": c.status_code,
                "latency_ms": c.latency_ms,
                "iso_timestamp": c.iso_timestamp,
            }
            for c in recent_calls
        ]

        return JevState(
            service_profile=service_profile.model_dump(),
            call_window=call_window,
            ceiling_usage=ceiling_usage,
            session_id=session_id,
            prior_decisions=prior_decisions or [],
        )

    def get_questions(self) -> Dict[str, Any]:
        """Returns the 3 canonical System One questions for Fuse traffic analysis."""
        return {
            "pattern_type": Choice(
                instructions=(
                    "Given `call_window` and `service_profile`, what traffic pattern "
                    "do these calls represent?"
                ),
                criteria={
                    "parallel_work": "Different endpoints or distinct arg_hashes executing legitimate concurrent work",
                    "retry_storm": "Same endpoint and identical arg_hash repeating without backoff after errors",
                    "loop_bug": "Repeating cyclical sequence of alternating tool calls making no forward progress",
                    "unrecognized": "Traffic pattern does not clearly fit parallel work, retry storm, or loop bug — unknown or ambiguous behavior",
                },
            ),
            "is_genuine_anomaly": Noul(
                instructions=(
                    "Given `service_profile`, `call_window`, and `ceiling_usage`, is this traffic "
                    "actually harmful, dangerous, or abusive to this downstream service?"
                ),
            ),
            "severity": Score(
                instructions=(
                    "Given `service_profile` and `call_window`, how severe is the risk to service stability or cost?",
                ),
                criteria=[
                    "Harmless — elevated call rate but legitimate, safe, and normal for this service profile",
                    "Concerning — could degrade service performance or risk rate limits if sustained",
                    "Dangerous — high risk of duplicate side-effects, severe financial cost, or immediate service ban",
                ],
            ),
        }

    async def evaluate(
        self,
        session_id: str,
        recent_calls: List[CallRecord],
        ceiling_usage: str,
        service_profile: ServiceProfile,
        prior_decisions: Optional[List[str]] = None,
    ) -> JevDecision:
        """Sends state and typed questions to Jev, returning structured decision with confidence."""
        state = self.build_state(
            session_id=session_id,
            recent_calls=recent_calls,
            ceiling_usage=ceiling_usage,
            service_profile=service_profile,
            prior_decisions=prior_decisions,
        )

        client = self._get_client()
        questions = self.get_questions()

        try:
            response = await client.system_one(
                state=state.model_dump(),
                questions=questions,
            )

            # Extract Choice: pattern_type
            choice_ans = response.choices["pattern_type"]
            pattern_str = choice_ans.choice
            try:
                pattern = PatternType(pattern_str)
            except ValueError:
                pattern = PatternType.UNRECOGNIZED

            # Extract Noul: is_genuine_anomaly
            noul_ans = response.nouls["is_genuine_anomaly"]
            is_anomaly = float(noul_ans.noul)

            # Extract Score: severity
            score_ans = response.scores["severity"]
            severity_score = float(score_ans.score)

            return JevDecision(
                pattern_type=pattern,
                pattern_confidence=float(getattr(choice_ans, "confidence", 0.8)),
                is_anomaly=is_anomaly,
                anomaly_confidence=float(getattr(noul_ans, "confidence", 0.8)),
                severity_score=severity_score,
                severity_confidence=float(getattr(score_ans, "confidence", 0.8)),
                raw_probabilities={
                    "pattern": getattr(choice_ans, "probabilities", {}),
                    "severity": getattr(score_ans, "probabilities", {}),
                },
            )

        except Exception as e:
            logger.warning("TypeSafe Jev call failed or unconfigured (%s). Using fallback evaluator.", e)
            return self._heuristic_fallback(recent_calls, service_profile)

    def _heuristic_fallback(
        self, recent_calls: List[CallRecord], service_profile: ServiceProfile
    ) -> JevDecision:
        """Deterministic fallback if external API is unreachable or during offline testing."""
        if not recent_calls:
            return JevDecision(
                pattern_type=PatternType.PARALLEL_WORK,
                pattern_confidence=0.9,
                is_anomaly=0.1,
                anomaly_confidence=0.9,
                severity_score=0.0,
                severity_confidence=0.9,
            )

        arg_hashes = [c.arg_hash for c in recent_calls]
        unique_hashes = len(set(arg_hashes))
        total_calls = len(arg_hashes)

        # Retry storm: identical hashes repeatedly
        if total_calls >= 4 and unique_hashes == 1:
            return JevDecision(
                pattern_type=PatternType.RETRY_STORM,
                pattern_confidence=0.88,
                is_anomaly=0.85,
                anomaly_confidence=0.85,
                severity_score=1.5 if service_profile.is_mutating else 1.0,
                severity_confidence=0.85,
            )

        # Parallel work: diverse hashes or endpoints
        if unique_hashes >= 3:
            return JevDecision(
                pattern_type=PatternType.PARALLEL_WORK,
                pattern_confidence=0.85,
                is_anomaly=0.15,
                anomaly_confidence=0.85,
                severity_score=0.2,
                severity_confidence=0.85,
            )

        # Default fallback
        return JevDecision(
            pattern_type=PatternType.UNRECOGNIZED,
            pattern_confidence=0.5,
            is_anomaly=0.5,
            anomaly_confidence=0.5,
            severity_score=1.0,
            severity_confidence=0.5,
        )


jev_client = JevClient()
