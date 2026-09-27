"""Configuration management for Fuse."""

import os
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseModel):
    """Fuse system settings loaded from environment variables."""

    # Jev (TypeSafe AI)
    typesafe_api_key: str = Field(default_factory=lambda: os.getenv("TYPESAFE_API_KEY", ""))

    # LLM Settings (Tier 3 / Layer 3)
    llm_provider: Literal["gemini", "groq"] = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini")  # type: ignore
    )
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-3.8-flash"))
    groq_api_key: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    groq_model: str = Field(default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"))

    # Proxy Networking
    proxy_host: str = Field(default_factory=lambda: os.getenv("PROXY_HOST", "0.0.0.0"))
    proxy_port: int = Field(default_factory=lambda: int(os.getenv("PROXY_PORT", "8000")))
    target_base_url: str = Field(default_factory=lambda: os.getenv("TARGET_BASE_URL", "http://localhost:9000"))

    # Layer 1: Deterministic Hard Ceiling
    hard_ceiling_calls: int = Field(default_factory=lambda: int(os.getenv("HARD_CEILING_CALLS", "20")))
    hard_ceiling_window_seconds: float = Field(
        default_factory=lambda: float(os.getenv("HARD_CEILING_WINDOW_SECONDS", "10"))
    )

    # Anomaly Threshold (Trips Layer 2 Jev evaluation)
    anomaly_threshold_calls: int = Field(default_factory=lambda: int(os.getenv("ANOMALY_THRESHOLD_CALLS", "8")))
    anomaly_threshold_window_seconds: float = Field(
        default_factory=lambda: float(os.getenv("ANOMALY_THRESHOLD_WINDOW_SECONDS", "5"))
    )

    # Layer 2: Confidence & Scoring Thresholds
    confidence_high: float = Field(default_factory=lambda: float(os.getenv("CONFIDENCE_HIGH", "0.7")))
    confidence_low: float = Field(default_factory=lambda: float(os.getenv("CONFIDENCE_LOW", "0.4")))
    anomaly_noul_threshold: float = Field(
        default_factory=lambda: float(os.getenv("ANOMALY_NOUL_THRESHOLD", "0.5"))
    )
    severity_dangerous: float = Field(
        default_factory=lambda: float(os.getenv("SEVERITY_DANGEROUS", "1.5"))
    )
    classifier_timeout_ms: int = Field(
        default_factory=lambda: int(os.getenv("CLASSIFIER_TIMEOUT_MS", "1000"))
    )

    # Audit file
    audit_log_path: str = Field(default_factory=lambda: os.getenv("AUDIT_LOG_PATH", "audit.jsonl"))


# Singleton settings instance
settings = Settings()
