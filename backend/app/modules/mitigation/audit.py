"""
Database-backed audit logger — stub implementation.

Owner: Member 2.
# TODO(member2): implement DbAuditLogger
"""

from __future__ import annotations

from app.modules.mitigation.interfaces import AuditLogger


class DbAuditLogger(AuditLogger):
    """
    Writes immutable audit records to the ``audit_logs`` table via
    ``AuditRepository``.

    Args:
        audit_repo: An ``AuditRepository`` instance (injected by the orchestrator).

    TODO(member2):
      - Generate a UUID v4 for each record.
      - Set ``timestamp`` to utcnow().
      - Set ``actor`` to "controller" for automated events.
      - Call ``audit_repo.add(AuditRecord(...))`` to persist.
    """

    def __init__(self, audit_repo) -> None:  # noqa: ANN001
        self._repo = audit_repo

    def record(
        self,
        event_type: str,
        details: dict,
        action_id: str | None = None,
    ) -> None:
        """
        Raises:
            NotImplementedError: TODO(member2): persist AuditRecord via audit_repo.
        """
        raise NotImplementedError(
            "TODO(member2): create an AuditRecord and call audit_repo.add()"
        )
