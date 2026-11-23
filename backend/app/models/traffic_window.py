"""
ORM model for a persisted traffic window and its extracted features.

Owner: Member 3 (backend core).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class TrafficWindow(Base, TimestampMixin):
    """
    Persisted record of one aggregated traffic window.

    Corresponds to ``schemas.traffic.WindowFeatures``.
    Written by the orchestrator after each successful feature extraction.
    """

    __tablename__ = "traffic_windows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_s: Mapped[float] = mapped_column(Float, nullable=False)

    # Volume
    total_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    requests_per_sec: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # IP distribution
    unique_ips: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    top_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    top_ip_share: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_requests_per_ip: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mean_requests_per_ip: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Endpoint distribution
    top_endpoint: Mapped[str | None] = mapped_column(String(512), nullable=True)
    top_endpoint_share: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Error rates
    status_4xx_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status_5xx_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Latency
    avg_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    p95_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Burst pattern
    burstiness: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    def __repr__(self) -> str:
        return f"<TrafficWindow id={self.id} start={self.window_start} rps={self.requests_per_sec}>"
