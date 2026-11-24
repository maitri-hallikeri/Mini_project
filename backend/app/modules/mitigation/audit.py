"""
Database-backed audit logger implementation.

Owner: Member 2.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.modules.mitigation.interfaces import AuditLogger
from app.schemas.mitigation import AuditRecord


class DbAuditLogger(AuditLogger):
    """
    Writes immutable audit records to ``audit_logs`` via ``AuditRepository``
    and retains an in-memory buffer for inspection and testing.
    """

    def __init__(self, audit_repo: Any = None) -> None:
        self._repo = audit_repo
        self.records: list[AuditRecord] = []

    def record(
        self,
        event_type: str,
        details: dict,
        action_id: str | None = None,
        actor: str = "controller",
    ) -> None:
        """Persist one immutable audit entry."""
        entry = AuditRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC),
            actor=actor,
            event_type=event_type,
            details=details,
            action_id=action_id,
        )
        self.records.append(entry)

        if self._repo is not None:
            try:
                self._repo.add(entry)
            except NotImplementedError:
                # Member 3's repository stub is not yet implemented
                pass