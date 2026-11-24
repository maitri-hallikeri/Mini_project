"""
Unit tests for the Recovery module (Owner: Member 2).
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx

from app.modules.recovery.health_checker import HttpHealthChecker
from app.modules.recovery.recovery_manager import DefaultRecoveryManager
from app.schemas.recovery import RecoveryAction, ReplicaHealth


def test_http_health_checker_tracks_healthy_and_failing_replicas():
    def handler(request: httpx.Request) -> httpx.Response:
        if "app1" in str(request.url):
            return httpx.Response(200, json={"status": "ok"})
        return httpx.Response(503)

    mock_client = httpx.Client(transport=httpx.MockTransport(handler))
    checker = HttpHealthChecker(
        replica_urls=["http://app1:8080", "http://app2:8080"],
        client=mock_client,
    )

    first = checker.check_all()
    assert first[0].replica_id == "app1"
    assert first[0].healthy is True
    assert first[0].consecutive_failures == 0

    assert first[1].replica_id == "app2"
    assert first[1].healthy is False
    assert first[1].consecutive_failures == 1

    second = checker.check_all()
    assert second[1].consecutive_failures == 2


def test_recovery_manager_restarts_after_threshold():
    mgr = DefaultRecoveryManager(failure_threshold=3, restart_fn=lambda _id: True)

    # Below threshold (2 failures) -> no action yet
    below = [
        ReplicaHealth(
            replica_id="app2",
            url="http://app2:8080",
            healthy=False,
            consecutive_failures=2,
            last_checked=datetime.now(UTC),
        )
    ]
    assert mgr.recover(below) == []

    # At threshold (3 failures) -> RESTART triggered
    at_threshold = [below[0].model_copy(update={"consecutive_failures": 3})]
    events = mgr.recover(at_threshold)
    assert len(events) == 1
    assert events[0].action == RecoveryAction.RESTART
    assert events[0].success is True
    assert "recovery_time_s" in events[0].details


def test_recovery_manager_reroutes_and_restores_when_restart_fails(tmp_path):
    upstream = tmp_path / "upstream_state.conf"
    mgr = DefaultRecoveryManager(
        failure_threshold=3,
        restart_fn=lambda _id: False,
        upstream_path=str(upstream),
    )

    unhealthy = [
        ReplicaHealth(
            replica_id="app2",
            url="http://app2:8080",
            healthy=False,
            consecutive_failures=3,
            last_checked=datetime.now(UTC),
        )
    ]
    events = mgr.recover(unhealthy)
    assert events[0].action == RecoveryAction.REMOVE_FROM_ROUTING
    assert "server app2:8080 down;" in upstream.read_text(encoding="utf-8")

    restored = mgr.restore_routing("app2")
    assert restored.action == RecoveryAction.RESTORE_ROUTING
    assert "app2" not in upstream.read_text(encoding="utf-8")