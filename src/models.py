"""Data models and schemas for Fuse."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ServiceCategory(str, Enum):
    """Category of downstream service for context-aware risk analysis."""
    READ_INTENSIVE = "read_intensive"       # Search, vector DB, read-only GET endpoints
    STANDARD_API = "standard_api"           # Normal REST APIs, mixed read/write
    HIGH_CONSEQUENCE = "high_consequence"   # Payments, SMS, financial, mutating external LLMs


class ServiceProfile(BaseModel):
    """Contextual profile describing downstream service characteristics."""
    name: str = "default_downstream"
    category: ServiceCategory = ServiceCategory.STANDARD_API
    is_mutating: bool = False
    cost_tier: str = "medium"  # low, medium, high
    typical_concurrency: str = "medium"  # low, medium, high

    @classmethod
    def from_request(cls, method: str, path: str, header_hint: Optional[str] = None) -> "ServiceProfile":
        """Infers service profile from HTTP method, path, and optional header."""
        is_mut = method.upper() in {"POST", "PUT", "PATCH", "DELETE"}
        hint = (header_hint or "").lower()

        if "payment" in hint or "stripe" in hint or "pay" in path.lower() or "billing" in path.lower():
            return cls(
                name="payments_api",
                category=ServiceCategory.HIGH_CONSEQUENCE,
                is_mutating=True,
                cost_tier="high",
                typical_concurrency="low",
            )
        elif "search" in hint or "query" in path.lower() or method.upper() == "GET":
            return cls(
                name="read_api",
                category=ServiceCategory.READ_INTENSIVE,
                is_mutating=is_mut,
                cost_tier="low",
                typical_concurrency="high",
            )
        return cls(
            name="standard_api",
            category=ServiceCategory.STANDARD_API,
            is_mutating=is_mut,
            cost_tier="medium",
            typical_concurrency="medium",
        )


class CallRecord(BaseModel):
    """Metadata recorded for an individual API call through the proxy."""
    call_id: str
    session_id: str
    timestamp: float
    iso_timestamp: str
    method: str
    endpoint: str
    arg_hash: str
    status_code: Optional[int] = None
    latency_ms: Optional[float] = None


class JevState(BaseModel):
    """State sent to Jev (TypeSafe System One) for classification."""
    service_profile: Dict[str, Any]
    call_window: List[Dict[str, Any]]
    ceiling_usage: str
    session_id: str
    prior_decisions: List[str] = Field(default_factory=list)


class PatternType(str, Enum):
    """Pattern classifications evaluated by Jev."""
    PARALLEL_WORK = "parallel_work"
    RETRY_STORM = "retry_storm"
    LOOP_BUG = "loop_bug"
    UNRECOGNIZED = "unrecognized"


class RoutingAction(str, Enum):
    """Enforcement action selected by the Fuse router."""
    FORWARD = "FORWARD"
    BACKOFF = "BACKOFF"
    BLOCK = "BLOCK"
    ESCALATE_LLM = "ESCALATE_LLM"
    ESCALATE_HUMAN = "ESCALATE_HUMAN"


class JevDecision(BaseModel):
    """Structured response from Jev System One evaluation."""
    pattern_type: PatternType
    pattern_confidence: float
    is_anomaly: float  # Noul probability (0.0 to 1.0)
    anomaly_confidence: float
    severity_score: float  # 0 to 2
    severity_confidence: float
    raw_probabilities: Dict[str, Any] = Field(default_factory=dict)


class LLMVerdict(BaseModel):
    """Structured verdict from Layer 3 Gemini 3.8 Flash root-cause analysis."""
    diagnosis: str
    root_cause: str
    recommended_action: RoutingAction
    suggested_backoff_seconds: Optional[float] = None
    can_auto_remediate: bool = False
    remediation_advice: str = ""


class DecisionResult(BaseModel):
    """Complete decision outcome produced by Fuse."""
    action: RoutingAction
    layer: str  # "LAYER_1_HARD_CEILING", "LAYER_2_JEV_DIRECT", "LAYER_3_GEMINI", "LAYER_3_HUMAN"
    reason: str
    backoff_seconds: float = 0.0
    jev_decision: Optional[JevDecision] = None
    llm_verdict: Optional[LLMVerdict] = None
    service_profile: Optional[ServiceProfile] = None
    timestamp: float = Field(default_factory=lambda: datetime.now(timezone.utc).timestamp())


class AuditRecord(BaseModel):
    """Tamper-evident record written to audit.jsonl."""
    record_id: str
    timestamp: str
    session_id: str
    endpoint: str
    method: str
    arg_hash: str
    decision: DecisionResult
    status_code: int
    duration_ms: float
