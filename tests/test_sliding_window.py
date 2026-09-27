"""Unit tests for Layer 1 sliding window tracker."""

import time
import pytest
from src.sliding_window import SlidingWindowTracker
from src.models import CallRecord


def test_sliding_window_normal_traffic():
    tracker = SlidingWindowTracker(
        hard_ceiling_calls=10,
        hard_ceiling_window_sec=5.0,
        anomaly_calls=5,
        anomaly_window_sec=3.0,
    )

    now = time.time()
    for i in range(3):
        rec = CallRecord(
            call_id=f"c-{i}",
            session_id="session-1",
            timestamp=now + (i * 0.1),
            iso_timestamp="2026-09-27T12:00:00Z",
            method="GET",
            endpoint="/search",
            arg_hash=f"hash-{i}",
        )
        tracker.record_call(rec)

    is_ceil, count_c, max_c = tracker.check_hard_ceiling("session-1", now=now + 0.3)
    is_anom, count_a, max_a = tracker.check_anomaly_threshold("session-1", now=now + 0.3)

    assert not is_ceil
    assert count_c == 3
    assert not is_anom
    assert count_a == 3
    assert tracker.get_ceiling_usage("session-1", now=now + 0.3) == "3/10"


def test_sliding_window_anomaly_trip():
    tracker = SlidingWindowTracker(
        hard_ceiling_calls=10,
        hard_ceiling_window_sec=5.0,
        anomaly_calls=5,
        anomaly_window_sec=2.0,
    )

    now = time.time()
    for i in range(6):
        rec = CallRecord(
            call_id=f"c-{i}",
            session_id="session-2",
            timestamp=now + (i * 0.05),
            iso_timestamp="2026-09-27T12:00:00Z",
            method="POST",
            endpoint="/pay",
            arg_hash="same-hash",
        )
        tracker.record_call(rec)

    is_ceil, count_c, _ = tracker.check_hard_ceiling("session-2", now=now + 0.3)
    is_anom, count_a, _ = tracker.check_anomaly_threshold("session-2", now=now + 0.3)

    assert not is_ceil  # under 10
    assert count_c == 6
    assert is_anom      # 6 >= 5 in 2.0s
    assert count_a == 6


def test_sliding_window_hard_ceiling_block():
    tracker = SlidingWindowTracker(
        hard_ceiling_calls=5,
        hard_ceiling_window_sec=2.0,
        anomaly_calls=3,
        anomaly_window_sec=1.0,
    )

    now = time.time()
    for i in range(5):
        rec = CallRecord(
            call_id=f"c-{i}",
            session_id="session-3",
            timestamp=now + (i * 0.01),
            iso_timestamp="2026-09-27T12:00:00Z",
            method="POST",
            endpoint="/loop",
            arg_hash="loop-hash",
        )
        tracker.record_call(rec)

    is_ceil, count_c, limit_c = tracker.check_hard_ceiling("session-3", now=now + 0.1)
    assert is_ceil
    assert count_c == 5
    assert limit_c == 5
