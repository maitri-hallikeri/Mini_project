"""
API contract tests — verifies every route returns the status code and
response shape specified in section 8 of the prompt.

Owner: Member 3 (backend core).
"""

from __future__ import annotations

# ------------------------------------------------------------------ #
# GET /api/v1/health
# ------------------------------------------------------------------ #


def test_health_200(client):
    assert client.get("/api/v1/health").status_code == 200


# ------------------------------------------------------------------ #
# GET /api/v1/traffic/windows
# ------------------------------------------------------------------ #


def test_traffic_windows_200_empty_list(client):
    r = client.get("/api/v1/traffic/windows")
    assert r.status_code == 200
    assert r.json() == []


def test_traffic_windows_accepts_limit_param(client):
    r = client.get("/api/v1/traffic/windows?limit=10")
    assert r.status_code == 200


def test_traffic_windows_accepts_since_param(client):
    r = client.get("/api/v1/traffic/windows?since=2026-01-01T00:00:00Z")
    assert r.status_code == 200


# ------------------------------------------------------------------ #
# GET /api/v1/risk/current
# ------------------------------------------------------------------ #


def test_risk_current_200_null(client):
    r = client.get("/api/v1/risk/current")
    assert r.status_code == 200
    assert r.json() is None


# ------------------------------------------------------------------ #
# GET /api/v1/risk/history
# ------------------------------------------------------------------ #


def test_risk_history_200_empty_list(client):
    r = client.get("/api/v1/risk/history")
    assert r.status_code == 200
    assert r.json() == []


# ------------------------------------------------------------------ #
# GET /api/v1/mitigations
# ------------------------------------------------------------------ #


def test_mitigations_200_empty_list(client):
    r = client.get("/api/v1/mitigations")
    assert r.status_code == 200
    assert r.json() == []


def test_mitigations_accepts_status_param(client):
    r = client.get("/api/v1/mitigations?status=ACTIVE")
    assert r.status_code == 200


# ------------------------------------------------------------------ #
# POST /api/v1/mitigations/{id}/rollback  → 501
# ------------------------------------------------------------------ #


def test_mitigations_rollback_501(client):
    r = client.post("/api/v1/mitigations/nonexistent-id/rollback")
    assert r.status_code == 501
    body = r.json()
    assert "detail" in body
    assert "TODO" in body["detail"]


# ------------------------------------------------------------------ #
# GET /api/v1/incidents
# ------------------------------------------------------------------ #


def test_incidents_200_empty_list(client):
    r = client.get("/api/v1/incidents")
    assert r.status_code == 200
    assert r.json() == []


# ------------------------------------------------------------------ #
# GET /api/v1/incidents/{id}  → 404 with JSON error body
# ------------------------------------------------------------------ #


def test_incidents_by_id_404(client):
    r = client.get("/api/v1/incidents/does-not-exist")
    assert r.status_code == 404


def test_incidents_by_id_404_json_envelope(client):
    r = client.get("/api/v1/incidents/does-not-exist")
    body = r.json()
    assert "detail" in body
    assert "code" in body
    assert body["code"] == "NOT_FOUND"


# ------------------------------------------------------------------ #
# GET /api/v1/replicas
# ------------------------------------------------------------------ #


def test_replicas_200_empty_list(client):
    r = client.get("/api/v1/replicas")
    assert r.status_code == 200
    assert r.json() == []


# ------------------------------------------------------------------ #
# GET /api/v1/metrics/summary
# ------------------------------------------------------------------ #


def test_metrics_summary_200(client):
    r = client.get("/api/v1/metrics/summary")
    assert r.status_code == 200


def test_metrics_summary_zero_incident_count(client):
    body = client.get("/api/v1/metrics/summary").json()
    assert body["incident_count"] == 0


def test_metrics_summary_null_floats(client):
    body = client.get("/api/v1/metrics/summary").json()
    for field in ("detection_latency_s", "mitigation_latency_s",
                  "recovery_time_s", "availability_pct", "legit_success_rate_pct"):
        assert body[field] is None, f"{field} should be null"


# ------------------------------------------------------------------ #
# OpenAPI docs are reachable
# ------------------------------------------------------------------ #


def test_openapi_docs_reachable(client):
    assert client.get("/docs").status_code == 200


def test_openapi_json_reachable(client):
    assert client.get("/openapi.json").status_code == 200


def test_openapi_lists_all_routes(client):
    """Verify all 7 route groups appear in the OpenAPI spec."""
    paths = client.get("/openapi.json").json().get("paths", {})
    path_str = str(paths)
    expected_routes = (
        "/health", "/traffic", "/risk", "/mitigations",
        "/incidents", "/replicas", "/metrics",
    )
    for expected in expected_routes:
        assert expected in path_str, f"Route group '{expected}' missing from OpenAPI spec"
