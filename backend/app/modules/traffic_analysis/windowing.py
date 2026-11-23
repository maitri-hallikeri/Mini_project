"""
Fixed time-window aggregator — stub implementation.

Owner: Member 1.
# TODO(member1): implement FixedWindowAggregator
"""

from __future__ import annotations

from datetime import datetime

from app.modules.traffic_analysis.interfaces import WindowAggregator
from app.schemas.traffic import RequestLogRecord


class FixedWindowAggregator(WindowAggregator):
    """
    Accumulates records into non-overlapping fixed-width windows.

    Args:
        window_seconds: Width of each window in seconds
                        (from ``Settings.WINDOW_SECONDS``).

    TODO(member1):
      - Keep an internal buffer keyed by window start time.
      - In ``add()``, assign each record to its window bucket based on its
        ``timestamp``.
      - In ``pop_ready_windows(now)``, return and clear all buckets whose
        end time (start + window_seconds) is <= ``now``.
    """

    def __init__(self, window_seconds: int = 10) -> None:
        self._window_seconds = window_seconds

    def add(self, records: list[RequestLogRecord]) -> None:
        """
        Raises:
            NotImplementedError: TODO(member1): buffer records into window buckets.
        """
        raise NotImplementedError(
            "TODO(member1): buffer records into fixed-width window buckets"
        )

    def pop_ready_windows(
        self, now: datetime
    ) -> list[tuple[datetime, datetime, list[RequestLogRecord]]]:
        """
        Raises:
            NotImplementedError: TODO(member1): return completed windows.
        """
        raise NotImplementedError(
            "TODO(member1): pop and return all window buckets whose end <= now"
        )
