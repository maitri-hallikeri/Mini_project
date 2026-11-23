"""
Repository for the immutable audit log.

Owner: Member 3 (backend core).
TODO(member3): implement add, list with real query logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from app.models.audit_log import AuditLog
from app.schemas.mitigation import AuditRecord

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AuditRepository:
    """
    Write-once CRUD access to the ``audit_logs`` table.

    Audit records are never updated or deleted.

    Args:
        db: An open SQLAlchemy ``Session``.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, record: AuditRecord) -> AuditLog:
        """
        Persist a new ``AuditRecord``.

        Args:
            record: The audit record produced by the mitigation audit logger.

        Returns:
            The newly inserted ``AuditLog`` ORM row.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): insert AuditRecord into audit_logs")

    def list(
        self,
        action_id: str | None = None,
        since: datetime | None = None,
        limit: int = 200,
    ) -> list[AuditLog]:
        """
        Return audit log entries, optionally filtered.

        Args:
            action_id: If given, return only entries for this mitigation action.
            since: If given, return only entries with ``timestamp >= since``.
            limit: Maximum number of rows to return.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): list audit_logs with optional filters")
