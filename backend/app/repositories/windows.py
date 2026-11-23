"""
Repository for traffic window records.

Owner: Member 3 (backend core).
TODO(member3): implement add, get, list with real query logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from app.models.traffic_window import TrafficWindow
from app.schemas.traffic import WindowFeatures

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class WindowRepository:
    """
    CRUD access to the ``traffic_windows`` table.

    Args:
        db: An open SQLAlchemy ``Session`` (injected by ``Depends(get_db)``).
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, features: WindowFeatures) -> TrafficWindow:
        """
        Persist a new ``WindowFeatures`` snapshot.

        Args:
            features: Extracted features for the window to persist.

        Returns:
            The newly inserted ``TrafficWindow`` ORM row.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): persist WindowFeatures to traffic_windows table")

    def get(self, window_id: int) -> TrafficWindow | None:
        """
        Retrieve a single window by primary key.

        Args:
            window_id: Integer primary key.

        Returns:
            The ``TrafficWindow`` row or ``None`` if not found.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): query traffic_windows by id")

    def list(
        self,
        limit: int = 100,
        since: datetime | None = None,
    ) -> list[TrafficWindow]:
        """
        Return recent windows, optionally filtered by start time.

        Args:
            limit: Maximum number of rows to return.
            since: If given, return only windows whose ``window_start >= since``.

        Returns:
            List of ``TrafficWindow`` rows ordered by ``window_start`` descending.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): list traffic_windows with optional since filter")
