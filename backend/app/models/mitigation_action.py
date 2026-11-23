"""
ORM model for a persisted mitigation action.

Owner: Member 3 (backend core).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class MitigationActionModel(Base, TimestampMixin):
    """
    Persisted record of one mitigation action.

    Corresponds to ``schemas.mitigation.MitigationAction``.
    ``parameters`` is stored as JSON text.
    """

    __tablename__ = "mitigation_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID v4

    action_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE")
    target: Mapped[str | None] = mapped_column(String(512), nullable=True)
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    incident_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<MitigationAction id={self.id} type={self.action_type} status={self.status}>"
