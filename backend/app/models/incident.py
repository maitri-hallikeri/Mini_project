"""
ORM model for a DDoS incident record.

Owner: Member 3 (backend core).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Incident(Base, TimestampMixin):
    """
    Persisted incident record.

    Corresponds to ``schemas.incident.Incident``.
    The ``actions`` list is NOT stored here as a FK relationship because
    the repository layer assembles the full Pydantic model from both tables.
    ``legit_success_rate`` is null until the incident is RESOLVED.
    """

    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID v4
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="OPEN", index=True)
    scenario: Mapped[str] = mapped_column(String(32), nullable=False)
    peak_risk_level: Mapped[str] = mapped_column(String(16), nullable=False)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    t_detect: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    t_mitigate: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    t_recover: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    legit_success_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<Incident id={self.id} status={self.status} scenario={self.scenario}>"
