"""Layer 1: Deterministic sliding window & rate tracker.

Guarantees:
1. Strict hard ceiling: Count-based, cannot be bypassed by any agent or AI model.
2. Anomaly detection: Fast sliding window trip that invokes Layer 2 (Jev) when call velocity spikes.
3. Clean memory bounds: Automatically purges calls older than the sliding window.
"""

import time
from collections import defaultdict, deque
from typing import Dict, List, Tuple
from threading import Lock

from src.config import settings
from src.models import CallRecord


class SlidingWindowTracker:
    """Thread-safe sliding window rate and anomaly tracker."""

    def __init__(
        self,
        hard_ceiling_calls: int = settings.hard_ceiling_calls,
        hard_ceiling_window_sec: float = settings.hard_ceiling_window_seconds,
        anomaly_calls: int = settings.anomaly_threshold_calls,
        anomaly_window_sec: float = settings.anomaly_threshold_window_seconds,
    ):
        self.hard_ceiling_calls = hard_ceiling_calls
        self.hard_ceiling_window_sec = hard_ceiling_window_sec
        self.anomaly_calls = anomaly_calls
        self.anomaly_window_sec = anomaly_window_sec

        # Maps session_id -> deque of CallRecord
        self._history: Dict[str, deque[CallRecord]] = defaultdict(deque)
        self._lock = Lock()

    def record_call(self, record: CallRecord) -> None:
        """Appends a new call to the session's sliding history."""
        with self._lock:
            q = self._history[record.session_id]
            q.append(record)
            self._prune_session(record.session_id, record.timestamp)

    def _prune_session(self, session_id: str, current_time: float) -> None:
        """Removes calls older than the maximum window (runs under lock)."""
        max_window = max(self.hard_ceiling_window_sec, self.anomaly_window_sec, 60.0)
        cutoff = current_time - max_window
        q = self._history[session_id]
        while q and q[0].timestamp < cutoff:
            q.popleft()

    def check_hard_ceiling(self, session_id: str, now: float | None = None) -> Tuple[bool, int, int]:
        """Checks if the deterministic hard ceiling is breached.
        
        Returns:
            (is_breached, current_call_count, ceiling_limit)
        """
        now = now or time.time()
        cutoff = now - self.hard_ceiling_window_sec

        with self._lock:
            q = self._history[session_id]
            count = sum(1 for call in q if call.timestamp >= cutoff)
            is_breached = count >= self.hard_ceiling_calls
            return is_breached, count, self.hard_ceiling_calls

    def check_anomaly_threshold(self, session_id: str, now: float | None = None) -> Tuple[bool, int, int]:
        """Checks if the anomaly threshold is breached, triggering Jev classification.
        
        Returns:
            (is_breached, current_call_count, anomaly_limit)
        """
        now = now or time.time()
        cutoff = now - self.anomaly_window_sec

        with self._lock:
            q = self._history[session_id]
            count = sum(1 for call in q if call.timestamp >= cutoff)
            is_breached = count >= self.anomaly_calls
            return is_breached, count, self.anomaly_calls

    def get_recent_window(self, session_id: str, limit: int = 10) -> List[CallRecord]:
        """Returns the most recent N calls for a session to feed into Jev state."""
        with self._lock:
            q = self._history[session_id]
            # Return last `limit` items
            items = list(q)
            return items[-limit:] if len(items) > limit else items

    def get_ceiling_usage(self, session_id: str, now: float | None = None) -> str:
        """Returns formatted ceiling usage string, e.g., '12/20'."""
        now = now or time.time()
        cutoff = now - self.hard_ceiling_window_sec
        with self._lock:
            q = self._history[session_id]
            count = sum(1 for call in q if call.timestamp >= cutoff)
            return f"{count}/{self.hard_ceiling_calls}"

    def reset_session(self, session_id: str) -> None:
        """Resets the history for a specific session."""
        with self._lock:
            if session_id in self._history:
                self._history[session_id].clear()


# Global tracker instance
window_tracker = SlidingWindowTracker()
