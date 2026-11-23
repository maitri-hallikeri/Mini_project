"""
ORM model for a replica health / recovery event.

Owner: Member 3 (backend core).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ReplicaEvent(Base):
    """
    Persisted record of one recovery action taken for an application replica.

    Corresponds to ``schemas.recovery.RecoveryEvent``.
    ``details`` is stored as JSON text.
    Write-once — no ``updated_at``.
    """

    __tablename__ = "replica_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    replica_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    def __repr__(self) -> str:
        return f"<ReplicaEvent id={self.id} replica={self.replica_id} action={self.action}>"
