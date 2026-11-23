"""
Abstract base classes for the traffic analysis module.

Owner: Member 1.
Contract owner: Member 3 (do not change without a PR approved by both members).

These interfaces define the boundary between Member 1's implementation and
the orchestrator.  Concrete classes in the other files in this module must
inherit from these ABCs and implement every abstract method.
"""

from __future__ import annotations

import abc
from datetime import datetime

from app.schemas.traffic import BaselineProfile, RequestLogRecord, WindowFeatures


class LogSource(abc.ABC):
    """
    Reads new raw request log records from an external source.

    Implementations:
      - ``NginxLogSource`` (log_source.py): tails the Nginx access log file.
    """

    @abc.abstractmethod
    def read_new_records(self) -> list[RequestLogRecord]:
        """
        Return all log records that have arrived since the last call.

        Returns:
            A (possibly empty) list of parsed ``RequestLogRecord`` objects
            ordered by timestamp ascending.

        Raises:
            NotImplementedError: Concrete implementation required by Member 1.
        """


class LogParser(abc.ABC):
    """
    Parses a single raw Nginx access log line into a structured record.

    Implementations:
      - ``NginxLogParser`` (parser.py): parses the default combined log format.
    """

    @abc.abstractmethod
    def parse_line(self, line: str) -> RequestLogRecord | None:
        """
        Parse one raw log line.

        Args:
            line: A single line from the Nginx access log.

        Returns:
            A ``RequestLogRecord`` if the line is valid, or ``None`` if it
            should be skipped (empty line, comment, parse error).

        Raises:
            NotImplementedError: Concrete implementation required by Member 1.
        """


class WindowAggregator(abc.ABC):
    """
    Accumulates log records into fixed-width time windows.

    Implementations:
      - ``FixedWindowAggregator`` (windowing.py).
    """

    @abc.abstractmethod
    def add(self, records: list[RequestLogRecord]) -> None:
        """
        Add a batch of records to the internal buffer.

        Args:
            records: Records returned by ``LogSource.read_new_records()``.
        """

    @abc.abstractmethod
    def pop_ready_windows(
        self, now: datetime
    ) -> list[tuple[datetime, datetime, list[RequestLogRecord]]]:
        """
        Return all windows whose end time is <= ``now`` and clear them from
        the buffer.

        Args:
            now: Current UTC datetime used to decide which windows are complete.

        Returns:
            List of ``(window_start, window_end, records)`` tuples.
            Returns an empty list if no windows are complete yet.
        """


class FeatureExtractor(abc.ABC):
    """
    Computes aggregate traffic features from the records in one window.

    Implementations:
      - ``WindowFeatureExtractor`` (features.py).
    """

    @abc.abstractmethod
    def extract(
        self,
        records: list[RequestLogRecord],
        window_start: datetime,
        window_end: datetime,
    ) -> WindowFeatures:
        """
        Compute ``WindowFeatures`` from a list of records.

        Args:
            records:      All records that fall within the window.
            window_start: Inclusive start of the window.
            window_end:   Exclusive end of the window.

        Returns:
            A fully-populated ``WindowFeatures`` instance.
        """


class BaselineStore(abc.ABC):
    """
    Stores and retrieves the learned normal-traffic baseline.

    Implementations:
      - ``InMemoryBaselineStore`` (baseline.py): keeps the profile in RAM;
        Member 1 may add persistence later.

    The baseline is updated only from windows that the detection engine judges
    to be non-attack traffic (i.e. ``RiskLevel.LOW``).
    """

    @abc.abstractmethod
    def get(self, at: datetime) -> BaselineProfile | None:
        """
        Return the current baseline profile valid at the given datetime.

        Args:
            at: The datetime for which the baseline is requested (used to
                select the matching hour-of-day bucket).

        Returns:
            The ``BaselineProfile``, or ``None`` if not enough data has been
            collected yet.
        """

    @abc.abstractmethod
    def update(self, features: WindowFeatures) -> None:
        """
        Update the baseline with features from a window judged to be normal.

        Args:
            features: A ``WindowFeatures`` instance from a non-attack window.
        """
