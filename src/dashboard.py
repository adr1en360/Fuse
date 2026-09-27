"""Dashboard and tamper-evident audit logger for Fuse."""

import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Configure UTF-8 for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import settings
from src.models import AuditRecord, DecisionResult, RoutingAction

logger = logging.getLogger("fuse.dashboard")
console = Console(force_terminal=True, safe_box=True)


class FuseDashboard:
    """Manages real-time statistics and cryptographic audit logging."""

    def __init__(self, log_path: str = settings.audit_log_path):
        self.log_path = log_path
        self.stats = {
            "total_calls": 0,
            "forwarded": 0,
            "backoff_applied": 0,
            "blocked": 0,
            "escaped_to_llm": 0,
            "escalated_human": 0,
            "layer1_trips": 0,
            "layer2_jev_trips": 0,
            "layer3_gemini_trips": 0,
        }
        self._last_log_hash = "0" * 64

    def record_decision(
        self,
        session_id: str,
        endpoint: str,
        method: str,
        arg_hash: str,
        decision: DecisionResult,
        status_code: int,
        duration_ms: float,
    ) -> AuditRecord:
        """Updates runtime statistics and appends an audit record to disk."""
        # Update metrics
        self.stats["total_calls"] += 1
        if decision.action == RoutingAction.FORWARD:
            self.stats["forwarded"] += 1
        elif decision.action == RoutingAction.BACKOFF:
            self.stats["backoff_applied"] += 1
        elif decision.action == RoutingAction.BLOCK:
            self.stats["blocked"] += 1
        elif decision.action == RoutingAction.ESCALATE_LLM:
            self.stats["escaped_to_llm"] += 1
        elif decision.action == RoutingAction.ESCALATE_HUMAN:
            self.stats["escalated_human"] += 1

        if "LAYER_1" in decision.layer:
            self.stats["layer1_trips"] += 1
        elif "LAYER_2" in decision.layer:
            self.stats["layer2_jev_trips"] += 1
        elif "LAYER_3" in decision.layer:
            self.stats["layer3_gemini_trips"] += 1

        iso_ts = datetime.now(timezone.utc).isoformat()
        record_id = hashlib.sha256(f"{session_id}:{iso_ts}:{arg_hash}".encode()).hexdigest()[:16]

        record = AuditRecord(
            record_id=record_id,
            timestamp=iso_ts,
            session_id=session_id,
            endpoint=endpoint,
            method=method,
            arg_hash=arg_hash,
            decision=decision,
            status_code=status_code,
            duration_ms=duration_ms,
        )

        self._append_to_audit_log(record)
        try:
            self._print_terminal_event(record)
        except Exception:
            try:
                print(f"[Fuse] {record.decision.action.value} ({record.decision.layer}) {record.method} {record.endpoint} [{record.status_code}]")
            except Exception:
                pass
        return record

    def _append_to_audit_log(self, record: AuditRecord) -> None:
        """Appends record with SHA-256 chain hash for tamper-evident logging."""
        record_json = record.model_dump_json()
        combined = f"{self._last_log_hash}|{record_json}".encode()
        current_hash = hashlib.sha256(combined).hexdigest()
        self._last_log_hash = current_hash

        entry = {
            "record": json.loads(record_json),
            "prev_hash": self._last_log_hash,
            "chain_hash": current_hash,
        }

        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error("Failed to write audit entry: %s", e)

    def _print_terminal_event(self, record: AuditRecord) -> None:
        """Renders live event card in console."""
        from rich import box
        d = record.decision
        action_style = {
            RoutingAction.FORWARD: "bold green",
            RoutingAction.BACKOFF: "bold yellow",
            RoutingAction.BLOCK: "bold red",
            RoutingAction.ESCALATE_LLM: "bold magenta",
            RoutingAction.ESCALATE_HUMAN: "bold cyan on red",
        }.get(d.action, "bold white")

        layer_color = "red" if "1" in d.layer else ("magenta" if "2" in d.layer else "cyan")

        title = f"Fuse Event | {d.action.value} via {d.layer}"

        details = Text()
        details.append(f"Session: {record.session_id}  Endpoint: {record.method} {record.endpoint}\n")
        details.append(f"Reason: {d.reason}\n")

        if d.jev_decision:
            jev = d.jev_decision
            details.append(
                f"Jev Pattern: {jev.pattern_type.value} (conf: {jev.pattern_confidence:.2f})  "
                f"Anomaly: {jev.is_anomaly:.2f}  Severity: {jev.severity_score:.1f}\n"
            )

        if d.llm_verdict:
            llm = d.llm_verdict
            details.append(f"Gemini Root Cause: {llm.root_cause} (Remediation: {llm.remediation_advice})\n")

        details.append(f"Status: {record.status_code} | Latency: {record.duration_ms:.1f}ms | Audit ID: {record.record_id}")

        console.print(Panel(details, title=title, box=box.ASCII, expand=False))

    def render_summary_table(self) -> None:
        """Prints high-level operational statistics table."""
        table = Table(title="🛡️ Fuse Intelligent Circuit Breaker — Real-Time Metrics", border_style="cyan")
        table.add_column("Metric", style="bold white")
        table.add_column("Value", style="bold green", justify="right")

        table.add_row("Total Intercepted Calls", str(self.stats["total_calls"]))
        table.add_row("Forwarded (Safe / Burst)", str(self.stats["forwarded"]))
        table.add_row("Backoff Applied (Retry Storm)", str(self.stats["backoff_applied"]))
        table.add_row("Blocked (Hard Ceiling / Loop)", str(self.stats["blocked"]))
        table.add_row("Escaped to Gemini 3.8 Flash", str(self.stats["escaped_to_llm"]))
        table.add_row("Human Escalations", str(self.stats["escalated_human"]))
        table.add_row("Layer 1 Deterministic Trips", str(self.stats["layer1_trips"]))
        table.add_row("Layer 2 Jev System One Trips", str(self.stats["layer2_jev_trips"]))
        table.add_row("Layer 3 Gemini Flash Trips", str(self.stats["layer3_gemini_trips"]))

        console.print(table)


dashboard = FuseDashboard()
