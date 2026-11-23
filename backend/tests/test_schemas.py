"""
Schema contract tests.

Owner: Member 3 (backend core).

Every schema must:
  - Accept a valid sample instance without error.
  - Reject values that violate declared range constraints.
  - Expose the enum members specified in the prompt.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.detection import RiskAssessment, RiskLevel, Scenario, SignalEvidence
from app.schemas.incident import Incident, IncidentStatus, MetricsSummary
from app.schemas.mitigation import ActionStatus, ActionType, AuditRecord, MitigationAction
from app.schemas.recovery import RecoveryAction, RecoveryEvent, ReplicaHealth
from app.schemas.traffic import RequestLogRecord, WindowFeatures

NOW = datetime.now(UTC)


# ------------------------------------------------------------------ #
# Enum membership
# ------------------------------------------------------------------ #


def test_risk_level_members():
    assert set(RiskLevel) == {RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL}


def test_scenario_members():
    assert Scenario.NONE in Scenario
    assert Scenario.REQUEST_FLOOD in Scenario
    assert Scenario.ENDPOINT_FLOOD in Scenario
    assert Scenario.BURST_ANOMALY in Scenario
    assert Scenario.UNKNOWN in Scenario


def test_action_type_members():
    expected = {
        ActionType.LOG_ONLY, ActionType.INCREASE_MONITORING, ActionType.RATE_LIMIT,
        ActionType.PROTECT_ENDPOINT, ActionType.TEMP_BLOCK_IP, ActionType.ROLLBACK,
    }
    assert set(ActionType) == expected


def test_action_status_members():
    assert set(ActionStatus) == {
        ActionStatus.ACTIVE, ActionStatus.EXPIRED,
        ActionStatus.ROLLED_BACK, ActionStatus.FAILED,
    }


def test_recovery_action_members():
    assert set(RecoveryAction) == {
        RecoveryAction.RESTART,
        RecoveryAction.REMOVE_FROM_ROUTING,
        RecoveryAction.RESTORE_ROUTING,
    }


def test_incident_status_members():
    assert set(IncidentStatus) == {
        IncidentStatus.OPEN, IncidentStatus.MITIGATING,
        IncidentStatus.RECOVERING, IncidentStatus.RESOLVED,
    }


# ------------------------------------------------------------------ #
# Valid sample instances
# ------------------------------------------------------------------ #


def test_request_log_record_valid():
    r = RequestLogRecord(
        timestamp=NOW, remote_addr="1.2.3.4", method="GET",
        path="/index", status=200, bytes_sent=512,
        request_time_ms=5.0, upstream=None, user_agent=None,
    )
    assert r.status == 200


def test_window_features_valid():
    wf = WindowFeatures(
        window_start=NOW, window_end=NOW, duration_s=10.0,
        total_requests=100, requests_per_sec=10.0,
        unique_ips=5, top_ip="1.2.3.4", top_ip_share=0.4,
        max_requests_per_ip=40, mean_requests_per_ip=20.0,
        top_endpoint="/api", top_endpoint_share=0.6,
        status_4xx_rate=0.01, status_5xx_rate=0.0,
        avg_latency_ms=12.0, p95_latency_ms=30.0,
        burstiness=0.5,
    )
    assert wf.total_requests == 100


def test_signal_evidence_valid():
    s = SignalEvidence(
        name="top_ip_share", observed_value=0.72,
        baseline_value=0.15, threshold=0.5,
        deviation=11.4, weight=0.3, triggered=True,
        description="High share",
    )
    assert s.triggered is True


def test_risk_assessment_valid():
    ra = RiskAssessment(
        window_start=NOW, window_end=NOW,
        score=75.0, level=RiskLevel.HIGH,
        scenario=Scenario.ENDPOINT_FLOOD,
    )
    assert ra.level == RiskLevel.HIGH


def test_mitigation_action_valid():
    ma = MitigationAction(
        id="uuid-1", action_type=ActionType.TEMP_BLOCK_IP,
        status=ActionStatus.ACTIVE, target="1.2.3.4",
        parameters={}, risk_level="HIGH", reason="test",
        created_at=NOW, expires_at=NOW,
    )
    assert ma.action_type == ActionType.TEMP_BLOCK_IP


def test_audit_record_valid():
    ar = AuditRecord(
        id="uuid-2", timestamp=NOW,
        actor="controller", event_type="ACTION_APPLIED",
        details={},
    )
    assert ar.actor == "controller"


def test_replica_health_valid():
    rh = ReplicaHealth(
        replica_id="app1", url="http://app1:8080",
        healthy=True, latency_ms=5.0,
        consecutive_failures=0, last_checked=NOW,
    )
    assert rh.healthy is True


def test_recovery_event_valid():
    re_ = RecoveryEvent(
        replica_id="app1", action=RecoveryAction.RESTART,
        success=True, timestamp=NOW, details={},
    )
    assert re_.success is True


def test_incident_valid():
    inc = Incident(
        id="uuid-3", status=IncidentStatus.OPEN,
        scenario="ENDPOINT_FLOOD", peak_risk_level="HIGH",
        started_at=NOW,
    )
    assert inc.status == IncidentStatus.OPEN


def test_metrics_summary_valid():
    ms = MetricsSummary(incident_count=0)
    assert ms.incident_count == 0
    assert ms.detection_latency_s is None


# ------------------------------------------------------------------ #
# Constraint rejection
# ------------------------------------------------------------------ #


def test_window_features_top_ip_share_out_of_range():
    with pytest.raises(ValidationError):
        WindowFeatures(
            window_start=NOW, window_end=NOW, duration_s=10.0,
            total_requests=100, requests_per_sec=10.0,
            unique_ips=5, top_ip=None, top_ip_share=1.5,  # > 1.0 — invalid
            max_requests_per_ip=40, mean_requests_per_ip=20.0,
            top_endpoint=None, top_endpoint_share=0.0,
            status_4xx_rate=0.0, status_5xx_rate=0.0,
            avg_latency_ms=0.0, p95_latency_ms=0.0, burstiness=0.0,
        )


def test_risk_assessment_score_out_of_range():
    with pytest.raises(ValidationError):
        RiskAssessment(
            window_start=NOW, window_end=NOW,
            score=150.0,  # > 100 — invalid
            level=RiskLevel.HIGH,
        )


def test_metrics_summary_availability_out_of_range():
    with pytest.raises(ValidationError):
        MetricsSummary(incident_count=0, availability_pct=110.0)  # > 100 — invalid


def test_signal_evidence_weight_out_of_range():
    with pytest.raises(ValidationError):
        SignalEvidence(
            name="x", observed_value=1.0,
            weight=1.5,  # > 1.0 — invalid
            triggered=False, description="test",
        )
