"""
Abstract base classes for the mitigation module.

Owner: Member 2.
Contract owner: Member 3 (do not change without a PR approved by both members).
"""

from __future__ import annotations

import abc
from datetime import datetime

from app.schemas.mitigation import MitigationAction


class MitigationController(abc.ABC):
    """
    Decides which mitigation actions to take and applies them.

    Default risk-to-action policy:
      LOW      → LOG_ONLY (record event, no traffic action).
      MEDIUM   → RATE_LIMIT + INCREASE_MONITORING (conservative; avoid false blocks).
      HIGH     → RATE_LIMIT + PROTECT_ENDPOINT for targeted endpoints.
      CRITICAL → TEMP_BLOCK_IP for high-confidence sources + operator alert.

    Every action except LOG_ONLY must have an ``expires_at`` set so that all
    restrictions are automatically reversed even if rollback is never called.
    """

    @abc.abstractmethod
    def decide(self, assessment) -> list[MitigationAction]:  # noqa: ANN001
        """
        Choose which mitigation actions to apply for a given ``RiskAssessment``.

        Args:
            assessment: ``RiskAssessment`` from the detection engine.

        Returns:
            List of ``MitigationAction`` objects to apply (not yet applied).
        """

    @abc.abstractmethod
    def apply(self, actions: list[MitigationAction]) -> list[MitigationAction]:
        """
        Apply a list of mitigation actions (write Nginx rules, etc.).

        Args:
            actions: Actions returned by ``decide()``.

        Returns:
            The same list with ``status`` updated to ACTIVE or FAILED.
        """

    @abc.abstractmethod
    def expire_due(self, now: datetime) -> list[MitigationAction]:
        """
        Expire all actions whose ``expires_at <= now``.

        Args:
            now: Current UTC datetime.

        Returns:
            List of actions that were expired in this call.
        """

    @abc.abstractmethod
    def rollback(self, action_id: str, actor: str) -> MitigationAction:
        """
        Manually roll back an ACTIVE action before it expires.

        Args:
            action_id: UUID of the action to roll back.
            actor:     Who requested the rollback ("operator" or "controller").

        Returns:
            The updated ``MitigationAction`` with status ROLLED_BACK.

        Raises:
            KeyError: If no action with ``action_id`` is found.
        """


class RuleWriter(abc.ABC):
    """
    Writes Nginx configuration rules for IP blocks and rate limits.

    Implementations:
      - ``NginxRuleWriter`` (nginx_writer.py).
    """

    @abc.abstractmethod
    def write_blocklist(self, ips: list[str]) -> None:
        """
        Overwrite the Nginx blocklist file with the given IP addresses.

        Args:
            ips: List of IP addresses to block.
        """

    @abc.abstractmethod
    def write_rate_limits(self, rules: list[dict]) -> None:
        """
        Write Nginx rate-limit configuration for given IPs/endpoints.

        Args:
            rules: List of dicts with keys ``target``, ``rate``, ``burst``.
        """

    @abc.abstractmethod
    def reload(self) -> None:
        """Signal Nginx to reload its configuration without dropping connections."""


class AuditLogger(abc.ABC):
    """
    Records immutable audit entries for all state-changing mitigation events.

    Implementations:
      - ``DbAuditLogger`` (audit.py): writes to ``audit_logs`` via the repository.
    """

    @abc.abstractmethod
    def record(
        self,
        event_type: str,
        details: dict,
        action_id: str | None = None,
    ) -> None:
        """
        Persist one audit entry.

        Args:
            event_type: Short label (e.g. ACTION_APPLIED, ACTION_EXPIRED).
            details:    Key-value data for the event.
            action_id:  UUID of the related ``MitigationAction``, if any.
        """
