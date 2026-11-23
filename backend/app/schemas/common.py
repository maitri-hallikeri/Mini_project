"""
Common types shared across all schema modules.

Owner: Member 3 (backend core).

Convention: every datetime field in every schema MUST be timezone-aware UTC.
Use ``UTCDatetime`` as the annotated type to enforce this automatically.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from pydantic import BeforeValidator


def _ensure_utc(value: object) -> datetime:
    """
    Coerce a value to a timezone-aware UTC datetime.

    Accepts:
      - A ``datetime`` that is already UTC-aware  → returned as-is.
      - A naive ``datetime``                       → assumed UTC, made aware.
      - Any other type                             → let Pydantic's normal
        datetime parsing handle it first.
    """
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
    return value  # type: ignore[return-value]


# Use this type for every datetime field in every schema.
UTCDatetime = Annotated[datetime, BeforeValidator(_ensure_utc)]
