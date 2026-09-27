"""Unit tests for the confidence-gated decision router."""

import pytest
from src.router import DecisionRouter
from src.models import (
    JevDecision,
    LLMVerdict,
    PatternType,
    RoutingAction,
    ServiceCategory,
    ServiceProfile,
)


@pytest.fixture
def test_router():
    return DecisionRouter(
        confidence_high=0.7,
        confidence_low=0.4,
        anomaly_threshold=0.5,
        severity_dangerous=1.5,
    )


@pytest.fixture
def payments_profile():
    return ServiceProfile(
        name="stripe",
        category=ServiceCategory.HIGH_CONSEQUENCE,
        is_mutating=True,
        cost_tier="high",
    )


@pytest.fixture
def search_profile():
    return ServiceProfile(
        name="vector_search",
        category=ServiceCategory.READ_INTENSIVE,
        is_mutating=False,
        cost_tier="low",
    )


def test_layer1_hard_ceiling_breach(test_router):
    # If ceiling breached, must BLOCK immediately
    res = test_router.route_layer1(
        is_ceiling_breached=True,
        ceiling_count=20,
        ceiling_limit=20,
        is_anomaly_breached=True,
        anomaly_count=10,
        anomaly_limit=8,
    )
    assert res is not None
    assert res.action == RoutingAction.BLOCK
    assert res.layer == "LAYER_1_HARD_CEILING"


def test_layer1_normal_traffic(test_router):
    # Under anomaly threshold, must FORWARD immediately without AI
    res = test_router.route_layer1(
        is_ceiling_breached=False,
        ceiling_count=3,
        ceiling_limit=20,
        is_anomaly_breached=False,
        anomaly_count=3,
        anomaly_limit=8,
    )
    assert res is not None
    assert res.action == RoutingAction.FORWARD
    assert res.layer == "LAYER_1_NORMAL"


def test_layer2_parallel_work_burst(test_router, search_profile):
    jev = JevDecision(
        pattern_type=PatternType.PARALLEL_WORK,
        pattern_confidence=0.85,
        is_anomaly=0.1,
        anomaly_confidence=0.9,
        severity_score=0.1,
        severity_confidence=0.9,
    )
    res = test_router.route_layer2(jev, search_profile, "8/20")
    assert res.action == RoutingAction.FORWARD
    assert res.layer == "LAYER_2_JEV_DIRECT"


def test_layer2_retry_storm_backoff(test_router, payments_profile):
    jev = JevDecision(
        pattern_type=PatternType.RETRY_STORM,
        pattern_confidence=0.92,
        is_anomaly=0.88,
        anomaly_confidence=0.9,
        severity_score=1.2,
        severity_confidence=0.85,
    )
    res = test_router.route_layer2(jev, payments_profile, "9/20")
    assert res.action == RoutingAction.BACKOFF
    assert res.layer == "LAYER_2_JEV_DIRECT"
    assert res.backoff_seconds > 0.0


def test_layer2_unrecognized_escape_hatch(test_router, search_profile):
    # Escape hatch: Jev outputs 'unrecognized' -> Escalate to LLM
    jev = JevDecision(
        pattern_type=PatternType.UNRECOGNIZED,
        pattern_confidence=0.88,
        is_anomaly=0.6,
        anomaly_confidence=0.7,
        severity_score=0.8,
        severity_confidence=0.7,
    )
    res = test_router.route_layer2(jev, search_profile, "8/20")
    assert res.action == RoutingAction.ESCALATE_LLM
    assert res.layer == "LAYER_2_ESCAPE_UNRECOGNIZED"


def test_layer2_human_escalation_crisis(test_router, payments_profile):
    jev = JevDecision(
        pattern_type=PatternType.RETRY_STORM,
        pattern_confidence=0.95,
        is_anomaly=0.95,
        anomaly_confidence=0.95,
        severity_score=1.8,  # >= 1.5
        severity_confidence=0.95,
    )
    res = test_router.route_layer2(jev, payments_profile, "15/20")
    assert res.action == RoutingAction.ESCALATE_HUMAN
    assert res.layer == "LAYER_2_HUMAN_ESCALATION"


def test_layer2_low_confidence_escalate_llm(test_router, search_profile):
    jev = JevDecision(
        pattern_type=PatternType.LOOP_BUG,
        pattern_confidence=0.52,  # < 0.7
        is_anomaly=0.5,
        anomaly_confidence=0.5,
        severity_score=0.9,
        severity_confidence=0.5,
    )
    res = test_router.route_layer2(jev, search_profile, "8/20")
    assert res.action == RoutingAction.ESCALATE_LLM
    assert res.layer == "LAYER_2_LOW_CONFIDENCE"


def test_layer3_verdict_application(test_router, search_profile):
    verdict = LLMVerdict(
        diagnosis="Agent is looping between two search queries.",
        root_cause="Hallucinated tool dependency.",
        recommended_action=RoutingAction.BLOCK,
        suggested_backoff_seconds=0.0,
        can_auto_remediate=False,
    )
    res = test_router.apply_llm_verdict(verdict, None, search_profile)
    assert res.action == RoutingAction.BLOCK
    assert res.layer == "LAYER_3_GEMINI"
