"""
Unit tests for the Mitigation module (Owner: Member 2).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.modules.mitigation.audit import DbAuditLogger
from app.modules.mitigation.controller import DefaultMitigationController
from app.modules.mitigation.nginx_writer import NginxRuleWriter
from app.schemas.detection import RiskAssessment, RiskLevel, Scenario
from app.schemas.mitigation import ActionStatus, ActionType


def _make_assessment(
    level: RiskLevel,
    score: float = 50.0,
    ips: list[str] | None = None,
    endpoints: list[str] | None = None,
) -> RiskAssessment:
    now = datetime.now(UTC)
    return RiskAssessment(
        window_start=now - timedelta(seconds=10),
        window_end=now,
        score=score,
        level=level,
        scenario=Scenario.REQUEST_FLOOD if level != RiskLevel.LOW else Scenario.NONE,
        offending_ips=ips or [],
        offending_endpoints=endpoints or [],
        detectors_used=["RuleDetector"],
    )


def test_low_risk_produces_log_only(tmp_path):
    writer = NginxRuleWriter(str(tmp_path / "blocklist.conf"))
    audit = DbAuditLogger()
    ctrl = DefaultMitigationController(rule_writer=writer, audit_logger=audit)

    actions = ctrl.decide(_make_assessment(RiskLevel.LOW, score=10.0))
    assert len(actions) == 1
    assert actions[0].action_type == ActionType.LOG_ONLY
    assert actions[0].expires_at is None


def test_medium_risk_rate_limits_without_blocking(tmp_path):
    writer = NginxRuleWriter(str(tmp_path / "blocklist.conf"))
    audit = DbAuditLogger()
    ctrl = DefaultMitigationController(rule_writer=writer, audit_logger=audit)

    actions = ctrl.decide(_make_assessment(RiskLevel.MEDIUM, score=45.0, ips=["198.51.100.20"]))
    types = {a.action_type for a in actions}
    assert ActionType.INCREASE_MONITORING in types
    assert ActionType.RATE_LIMIT in types
    assert ActionType.TEMP_BLOCK_IP not in types
    assert all(a.expires_at is not None for a in actions)


def test_high_risk_protects_endpoint_and_rate_limits_ip(tmp_path):
    writer = NginxRuleWriter(str(tmp_path / "blocklist.conf"))
    audit = DbAuditLogger()
    ctrl = DefaultMitigationController(rule_writer=writer, audit_logger=audit)

    actions = ctrl.decide(
        _make_assessment(RiskLevel.HIGH, score=75.0, ips=["198.51.100.43"], endpoints=["/login"])
    )
    types = {a.action_type for a in actions}
    assert ActionType.RATE_LIMIT in types
    assert ActionType.PROTECT_ENDPOINT in types


def test_critical_risk_blocks_ip_and_respects_whitelist(tmp_path):
    blocklist = tmp_path / "blocklist.conf"
    writer = NginxRuleWriter(str(blocklist))
    audit = DbAuditLogger()
    ctrl = DefaultMitigationController(rule_writer=writer, audit_logger=audit)

    # 127.0.0.1 is whitelisted; 198.51.100.43 should be blocked
    actions = ctrl.decide(
        _make_assessment(RiskLevel.CRITICAL, score=95.0, ips=["127.0.0.1", "198.51.100.43"])
    )
    applied = ctrl.apply(actions)

    assert len(applied) == 1
    assert applied[0].action_type == ActionType.TEMP_BLOCK_IP
    assert applied[0].target == "198.51.100.43"
    assert "deny 198.51.100.43;" in blocklist.read_text(encoding="utf-8")
    assert "127.0.0.1" not in blocklist.read_text(encoding="utf-8")


def test_expire_due_and_rollback(tmp_path):
    blocklist = tmp_path / "blocklist.conf"
    writer = NginxRuleWriter(str(blocklist))
    audit = DbAuditLogger()
    ctrl = DefaultMitigationController(rule_writer=writer, audit_logger=audit, default_ttl_s=60)

    applied = ctrl.apply(
        ctrl.decide(_make_assessment(RiskLevel.CRITICAL, score=92.0, ips=["198.51.100.99"]))
    )
    action_id = applied[0].id

    # Rollback removes IP from Nginx immediately
    rolled = ctrl.rollback(action_id, actor="operator")
    assert rolled.status == ActionStatus.ROLLED_BACK
    assert "deny 198.51.100.99;" not in blocklist.read_text(encoding="utf-8")