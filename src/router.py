"""Confidence-gated decision router for Fuse.

Implements the 3-layer safety hierarchy:
Layer 1: Deterministic Hard Ceiling (Strict block, no AI bypass).
Layer 2: Jev System One (Fast typed decisions with calibrated confidence + escape hatch).
Layer 3: Gemini 3.8 Flash (Deep root cause when Jev escapes or is uncertain).
"""

import logging
from typing import Optional

from src.config import settings
from src.models import (
    DecisionResult,
    JevDecision,
    LLMVerdict,
    PatternType,
    RoutingAction,
    ServiceProfile,
)

logger = logging.getLogger("fuse.router")


class DecisionRouter:
    """Decides enforcement action based on multi-tier signals and confidence bounds."""

    def __init__(
        self,
        confidence_high: float = settings.confidence_high,
        confidence_low: float = settings.confidence_low,
        anomaly_threshold: float = settings.anomaly_noul_threshold,
        severity_dangerous: float = settings.severity_dangerous,
    ):
        self.confidence_high = confidence_high
        self.confidence_low = confidence_low
        self.anomaly_threshold = anomaly_threshold
        self.severity_dangerous = severity_dangerous

    def route_layer1(
        self,
        is_ceiling_breached: bool,
        ceiling_count: int,
        ceiling_limit: int,
        is_anomaly_breached: bool,
        anomaly_count: int,
        anomaly_limit: int,
    ) -> Optional[DecisionResult]:
        """Evaluates Layer 1 deterministic counting rules.
        
        Returns a DecisionResult if Layer 1 immediately resolves the call, or None to escalate to Layer 2.
        """
        # Hard ceiling is inviolable: pure counting, zero AI override
        if is_ceiling_breached:
            return DecisionResult(
                action=RoutingAction.BLOCK,
                layer="LAYER_1_HARD_CEILING",
                reason=(
                    f"Deterministic hard ceiling breached: {ceiling_count}/{ceiling_limit} calls in window. "
                    "Inviolable ceiling enforced without AI bypass."
                ),
            )

        # Normal traffic under anomaly threshold: forward immediately
        if not is_anomaly_breached:
            return DecisionResult(
                action=RoutingAction.FORWARD,
                layer="LAYER_1_NORMAL",
                reason=f"Call rate normal ({anomaly_count}/{anomaly_limit}). Forwarded without AI overhead.",
            )

        # Anomaly threshold tripped -> escalate to Layer 2 (Jev)
        return None

    def route_layer2(
        self,
        jev: JevDecision,
        service_profile: ServiceProfile,
        ceiling_usage: str,
    ) -> DecisionResult:
        """Evaluates Layer 2 Jev System One output with confidence gating and escape hatch."""

        # 1. ESCAPE HATCH: Pattern explicitly unrecognized by Jev
        if jev.pattern_type == PatternType.UNRECOGNIZED:
            return DecisionResult(
                action=RoutingAction.ESCALATE_LLM,
                layer="LAYER_2_ESCAPE_UNRECOGNIZED",
                reason=(
                    "Jev System One signaled 'unrecognized' pattern. "
                    "Escaping to Layer 3 (Gemini 3.8 Flash) for root-cause session inspection."
                ),
                jev_decision=jev,
                service_profile=service_profile,
            )

        # 2. SEVERE CRISIS: High severity and high anomaly probability -> Escalate to Human
        if jev.severity_score >= self.severity_dangerous and jev.is_anomaly >= 0.85:
            return DecisionResult(
                action=RoutingAction.ESCALATE_HUMAN,
                layer="LAYER_2_HUMAN_ESCALATION",
                reason=(
                    f"Critical danger detected on {service_profile.name} (Severity: {jev.severity_score:.1f}, "
                    f"Anomaly Prob: {jev.is_anomaly:.2f}). Escalate immediately to human operator."
                ),
                jev_decision=jev,
                service_profile=service_profile,
            )

        # 3. HIGH CONFIDENCE PATH: Act directly on Jev's typed classification
        if jev.pattern_confidence >= self.confidence_high:
            # Parallel work: legitimate concurrent activity
            if jev.pattern_type == PatternType.PARALLEL_WORK:
                return DecisionResult(
                    action=RoutingAction.FORWARD,
                    layer="LAYER_2_JEV_DIRECT",
                    reason=(
                        f"Jev identified legitimate parallel work (confidence: {jev.pattern_confidence:.2f}, "
                        f"anomaly prob: {jev.is_anomaly:.2f}). Forwarding burst."
                    ),
                    jev_decision=jev,
                    service_profile=service_profile,
                )

            # Retry storm: identical calls repeating without backoff
            elif jev.pattern_type == PatternType.RETRY_STORM:
                backoff_time = 4.0 if service_profile.is_mutating else 2.0
                return DecisionResult(
                    action=RoutingAction.BACKOFF,
                    layer="LAYER_2_JEV_DIRECT",
                    reason=(
                        f"Jev identified retry storm (confidence: {jev.pattern_confidence:.2f}). "
                        f"Applying {backoff_time}s exponential backoff to safeguard {service_profile.name}."
                    ),
                    backoff_seconds=backoff_time,
                    jev_decision=jev,
                    service_profile=service_profile,
                )

            # Loop bug: circular execution
            elif jev.pattern_type == PatternType.LOOP_BUG:
                return DecisionResult(
                    action=RoutingAction.BLOCK,
                    layer="LAYER_2_JEV_DIRECT",
                    reason=(
                        f"Jev confirmed loop bug with high confidence ({jev.pattern_confidence:.2f}). "
                        "Circuit breaker tripped to stop runaway token drain."
                    ),
                    jev_decision=jev,
                    service_profile=service_profile,
                )

        # 4. LOW CONFIDENCE / AMBIGUOUS: Escalate to Layer 3 LLM
        return DecisionResult(
            action=RoutingAction.ESCALATE_LLM,
            layer="LAYER_2_LOW_CONFIDENCE",
            reason=(
                f"Jev confidence ({jev.pattern_confidence:.2f}) is below threshold ({self.confidence_high:.2f}). "
                "Routing to Layer 3 (Gemini 3.8 Flash) for second opinion."
            ),
            jev_decision=jev,
            service_profile=service_profile,
        )

    def apply_llm_verdict(
        self,
        verdict: LLMVerdict,
        jev_decision: Optional[JevDecision],
        service_profile: ServiceProfile,
    ) -> DecisionResult:
        """Applies the final decision synthesized from Layer 3 Gemini 3.8 Flash diagnosis."""
        return DecisionResult(
            action=verdict.recommended_action,
            layer="LAYER_3_GEMINI",
            reason=f"Gemini 3.8 Flash Diagnosis: {verdict.diagnosis}. Root cause: {verdict.root_cause}",
            backoff_seconds=verdict.suggested_backoff_seconds or 0.0,
            jev_decision=jev_decision,
            llm_verdict=verdict,
            service_profile=service_profile,
        )


router = DecisionRouter()
