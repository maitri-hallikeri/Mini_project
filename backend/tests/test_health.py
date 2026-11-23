"""
Tests for GET /api/v1/health.

Owner: Member 3 (backend core).
"""

from __future__ import annotations

from datetime import datetime


def test_health_returns_200(client):
    """Health endpoint must return HTTP 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_response_shape(client):
    """Response body must contain all required keys."""
    response = client.get("/api/v1/health")
    body = response.json()
    assert "status" in body
    assert "app_version" in body
    assert "env" in body
    assert "pipeline_enabled" in body
    assert "server_time" in body


def test_health_status_ok(client):
    """status field must be 'ok'."""
    body = client.get("/api/v1/health").json()
    assert body["status"] == "ok"


def test_health_pipeline_disabled_by_default(client):
    """pipeline_enabled must be false in the test environment."""
    body = client.get("/api/v1/health").json()
    assert body["pipeline_enabled"] is False


def test_health_server_time_is_valid_iso(client):
    """server_time must be a parseable ISO-8601 datetime string."""
    body = client.get("/api/v1/health").json()
    dt = datetime.fromisoformat(body["server_time"])
    assert dt.tzinfo is not None, "server_time must be timezone-aware"
