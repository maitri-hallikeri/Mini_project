"""
Mitigation controller — stub implementation.

Owner: Member 2.
# TODO(member2): implement DefaultMitigationController
# TODO(member2): adapt from protection_engine/app/mitigation.py
"""

from __future__ import annotations

from datetime import datetime

from app.modules.mitigation.interfaces import MitigationController
from app.schemas.mitigation import MitigationAction


class DefaultMitigationController(MitigationController):
    """
    Decides and applies mitigation actions based on a ``RiskAssessment``.

    Policy (see mitigation README for full table):
      LOW      → LOG_ONLY
      MEDIUM   → RATE_LIMIT + INCREASE_MONITORING
      HIGH     → RATE_LIMIT + PROTECT_ENDPOINT
      CRITICAL → TEMP_BLOCK_IP + operator alert

    TODO(member2): adapt from protection_engine/app/mitigation.py —
    the existing ``MitigationManager.evaluate_and_mitigate()`` contains
    a risk-based decision matrix that maps directly to ``decide()``.
    """

    def decide(self, assessment) -> list[MitigationAction]:  # noqa: ANN001
        """
        Raises:
            NotImplementedError: TODO(member2): implement risk-to-action decision logic.
        """
        raise NotImplementedError(
            "TODO(member2): implement risk-to-action decision logic in decide()"
        )

    def apply(self, actions: list[MitigationAction]) -> list[MitigationAction]:
        """
        Raises:
            NotImplementedError: TODO(member2): call RuleWriter and persist actions.
        """
        raise NotImplementedError(
            "TODO(member2): call NginxRuleWriter and update action status to ACTIVE"
        )

    def expire_due(self, now: datetime) -> list[MitigationAction]:
        """
        Raises:
            NotImplementedError: TODO(member2): expire actions past their TTL.
        """
        raise NotImplementedError(
            "TODO(member2): find ACTIVE actions with expires_at <= now and set EXPIRED"
        )

    def rollback(self, action_id: str, actor: str) -> MitigationAction:
        """
        Raises:
            NotImplementedError: TODO(member2/member3): implement rollback logic.
        """
        raise NotImplementedError(
            "TODO(member2/member3): look up action_id, set ROLLED_BACK, reload Nginx, write audit"
        )
