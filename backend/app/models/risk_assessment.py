"""
ORM model for a persisted risk assessment result.

Owner: Member 3 (backend core).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class RiskAssessmentModel(Base, TimestampMixin):
    """
    Persisted record of one risk assessment.

    Corresponds to ``schemas.detection.RiskAssessment``.
    Lists (signals, offending_ips, offending_endpoints, detectors_used) are
    stored as JSON text; SQLAlchemy's ``JSON`` type is dialect-specific so we
    keep them as ``Text`` and serialise/deserialise in the repository layer.
    """

    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    score: Mapped[float] = mapped_column(Float, nullable=False)
    level: Mapped[str] = mapped_column(String(16), nullable=False)
    scenario: Mapped[str] = mapped_column(String(32), nullable=False, default="NONE")

    # JSON-serialised lists
    signals_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    offending_ips_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    offending_endpoints_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    detectors_used_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    def __repr__(self) -> str:
        return f"<RiskAssessment id={self.id} score={self.score} level={self.level}>"
