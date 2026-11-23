"""
ORM model for the immutable audit log.

Owner: Member 3 (backend core).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    """
    Immutable audit entry for any event that changes mitigation state.

    Corresponds to ``schemas.mitigation.AuditRecord``.
    ``details`` is stored as JSON text.
    No ``updated_at`` column — audit records are write-once.
    """

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID v4
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    action_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("mitigation_actions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} event={self.event_type} actor={self.actor}>"
