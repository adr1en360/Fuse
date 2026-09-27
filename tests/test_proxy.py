"""Integration tests for the Fuse reverse proxy."""

from unittest.mock import AsyncMock, patch
import pytest
from fastapi import Response
from fastapi.testclient import TestClient
from src.proxy import app
from src.sliding_window import window_tracker


@pytest.fixture(autouse=True)
def reset_tracker():
    window_tracker.reset_session("test-session")
    window_tracker.reset_session("test-burst")
    window_tracker.reset_session("test-retry")
    window_tracker.reset_session("test-ceiling")


def test_proxy_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["proxy"] == "Fuse"
    assert data["status"] == "active"


@patch("src.proxy.forward_to_downstream", new_callable=AsyncMock)
def test_proxy_normal_forwarding(mock_fwd):
    mock_fwd.return_value = Response(
        content=b'{"ok": true}',
        status_code=200,
        headers={"X-Fuse-Proxy": "active"},
    )

    client = TestClient(app)
    resp = client.get(
        "/search?query=fuse",
        headers={"X-Session-ID": "test-session", "X-Fuse-Service": "search"},
    )
    assert resp.status_code == 200
    assert resp.headers.get("X-Fuse-Proxy") == "active"


@patch("src.proxy.forward_to_downstream", new_callable=AsyncMock)
def test_proxy_hard_ceiling_trip(mock_fwd):
    mock_fwd.return_value = Response(
        content=b'{"ok": true}',
        status_code=200,
        headers={"X-Fuse-Proxy": "active"},
    )

    client = TestClient(app)
    session_id = "test-ceiling"

    # Blast 25 requests instantly
    responses = []
    for i in range(25):
        resp = client.get(
            f"/search?query={i}",
            headers={"X-Session-ID": session_id},
        )
        responses.append(resp)

    # Hard ceiling is 20, so calls 21..25 must return 429
    blocked_count = sum(1 for r in responses if r.status_code == 429)
    assert blocked_count >= 5

    # Check headers and payload on blocked response
    blocked_resp = [r for r in responses if r.status_code == 429][0]
    assert blocked_resp.headers.get("Retry-After") is not None
    data = blocked_resp.json()
    assert "Hard ceiling" in data["error"] or "Hard ceiling" in data.get("message", "")


def test_proxy_metrics():
    client = TestClient(app)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    metrics = resp.json()
    assert "total_calls" in metrics
    assert metrics["total_calls"] >= 0
