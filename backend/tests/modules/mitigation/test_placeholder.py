"""
Placeholder tests for the mitigation module.

Owner: Member 2.
"""

from __future__ import annotations

from datetime import UTC

import pytest


@pytest.mark.skip(reason="TODO(member2): add module tests")
def test_mitigation_placeholder():
    """Placeholder — Member 2 must replace this with real tests."""


def test_controller_decide_raises_not_implemented():
    """DefaultMitigationController.decide() must raise NotImplementedError."""
    from app.modules.mitigation.controller import DefaultMitigationController

    ctrl = DefaultMitigationController()
    with pytest.raises(NotImplementedError):
        ctrl.decide(None)  # type: ignore[arg-type]


def test_controller_apply_raises_not_implemented():
    """DefaultMitigationController.apply() must raise NotImplementedError."""
    from app.modules.mitigation.controller import DefaultMitigationController

    ctrl = DefaultMitigationController()
    with pytest.raises(NotImplementedError):
        ctrl.apply([])


def test_controller_expire_due_raises_not_implemented():
    """DefaultMitigationController.expire_due() must raise NotImplementedError."""
    from datetime import datetime

    from app.modules.mitigation.controller import DefaultMitigationController

    ctrl = DefaultMitigationController()
    with pytest.raises(NotImplementedError):
        ctrl.expire_due(datetime.now(UTC))


def test_nginx_rule_writer_raises_not_implemented():
    """NginxRuleWriter stubs must raise NotImplementedError."""
    from app.modules.mitigation.nginx_writer import NginxRuleWriter

    writer = NginxRuleWriter("/tmp/blocklist.conf")
    with pytest.raises(NotImplementedError):
        writer.write_blocklist([])
    with pytest.raises(NotImplementedError):
        writer.write_rate_limits([])
    with pytest.raises(NotImplementedError):
        writer.reload()


def test_audit_logger_raises_not_implemented():
    """DbAuditLogger.record() must raise NotImplementedError."""
    from app.modules.mitigation.audit import DbAuditLogger

    logger = DbAuditLogger(audit_repo=None)
    with pytest.raises(NotImplementedError):
        logger.record("TEST_EVENT", {})
