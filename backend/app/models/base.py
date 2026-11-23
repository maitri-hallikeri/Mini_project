"""
Declarative base for all SQLAlchemy ORM models.

Owner: Member 3 (backend core).

All ORM models must inherit from ``Base``.  The ``created_at`` and
``updated_at`` mixin columns are defined here as a ``TimestampMixin`` so
every table gets them consistently.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base; holds the shared ``MetaData`` registry."""


class TimestampMixin:
    """
    Adds ``created_at`` and ``updated_at`` columns to any model that inherits it.

    Both values are stored as UTC datetimes.
    ``updated_at`` is refreshed automatically on every UPDATE by the
    ``onupdate`` hook.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
