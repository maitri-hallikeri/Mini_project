
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.modules.traffic_analysis.interfaces import WindowAggregator
from app.schemas.traffic import RequestLogRecord


class FixedWindowAggregator(WindowAggregator):
    """
    Groups incoming request records into fixed-width time windows.
    """

    def __init__(self, window_seconds: int = 10) -> None:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self._window_seconds = window_seconds
        self._windows: dict[datetime, list[RequestLogRecord]] = {}

    def add(self, records: list[RequestLogRecord]) -> None:
        for record in records:
            timestamp = record.timestamp

            if timestamp.tzinfo is None:
                raise ValueError("Record timestamp must be timezone-aware")

            timestamp = timestamp.astimezone(UTC)

            timestamp_seconds = timestamp.timestamp()

            window_start_seconds = (
                int(timestamp_seconds // self._window_seconds)
                * self._window_seconds
            )

            window_start = datetime.fromtimestamp(
                window_start_seconds,
                tz=UTC
            )

            if window_start not in self._windows:
                self._windows[window_start] = []

            self._windows[window_start].append(record)

    def pop_ready_windows(
        self,
        now: datetime
    ) -> list[tuple[datetime, datetime, list[RequestLogRecord]]]:

        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        now = now.astimezone(UTC)

        ready_windows = []

        for window_start in sorted(self._windows):
            window_end = window_start + timedelta(
                seconds=self._window_seconds
            )

            if window_end <= now:
                records = self._windows.pop(window_start)

                ready_windows.append(
                    (window_start, window_end, records)
                )

        return ready_windows
