"""
Placeholder tests for the recovery module.

Owner: Member 2.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="TODO(member2): add module tests")
def test_recovery_placeholder():
    """Placeholder — Member 2 must replace this with real tests."""


def test_health_checker_raises_not_implemented():
    """HttpHealthChecker.check_all() must raise NotImplementedError."""
    from app.modules.recovery.health_checker import HttpHealthChecker

    checker = HttpHealthChecker(replica_urls=["http://app1:8080"])
    with pytest.raises(NotImplementedError):
        checker.check_all()


def test_recovery_manager_recover_raises_not_implemented():
    """DefaultRecoveryManager.recover() must raise NotImplementedError."""
    from app.modules.recovery.recovery_manager import DefaultRecoveryManager

    mgr = DefaultRecoveryManager()
    with pytest.raises(NotImplementedError):
        mgr.recover([])


def test_recovery_manager_restore_routing_raises_not_implemented():
    """DefaultRecoveryManager.restore_routing() must raise NotImplementedError."""
    from app.modules.recovery.recovery_manager import DefaultRecoveryManager

    mgr = DefaultRecoveryManager()
    with pytest.raises(NotImplementedError):
        mgr.restore_routing("app1")
