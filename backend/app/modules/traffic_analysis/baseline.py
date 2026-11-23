"""
In-memory baseline store — stub implementation.

Owner: Member 1.
# TODO(member1): implement InMemoryBaselineStore
"""

from __future__ import annotations

from datetime import datetime

from app.modules.traffic_analysis.interfaces import BaselineStore
from app.schemas.traffic import BaselineProfile, WindowFeatures


class InMemoryBaselineStore(BaselineStore):
    """
    Maintains a rolling baseline of normal traffic statistics, bucketed by
    hour of day, in process memory.

    TODO(member1):
      - On ``update()``, compute running mean and std for each feature in
        ``WindowFeatures`` for the matching hour-of-day bucket using an
        incremental (Welford) algorithm so the full history need not be stored.
      - Only call ``update()`` from windows that the detection engine judged
        as ``RiskLevel.LOW`` (the pipeline enforces this — do not check here).
      - On ``get()``, return the ``BaselineProfile`` if ``sample_count >= 30``
        (configurable threshold), otherwise return ``None`` so the detection
        engine falls back to threshold-only detection.
    """

    def __init__(self) -> None:
        self._profile: BaselineProfile | None = None

    def get(self, at: datetime) -> BaselineProfile | None:
        """
        Raises:
            NotImplementedError: TODO(member1): return baseline profile for hour bucket.
        """
        raise NotImplementedError(
            "TODO(member1): return BaselineProfile for the hour-of-day bucket matching `at`"
        )

    def update(self, features: WindowFeatures) -> None:
        """
        Raises:
            NotImplementedError: TODO(member1): update rolling statistics with new features.
        """
        raise NotImplementedError(
            "TODO(member1): update per-hour rolling mean/std with WindowFeatures values"
        )
