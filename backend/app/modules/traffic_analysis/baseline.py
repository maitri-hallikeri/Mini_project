
from __future__ import annotations

from datetime import datetime, timezone
from math import sqrt

from app.modules.traffic_analysis.interfaces import BaselineStore
from app.schemas.traffic import (
    BaselineProfile,
    PerHourStats,
    WindowFeatures,
)


class InMemoryBaselineStore(BaselineStore):
    """
    Maintains online normal-traffic statistics for each UTC hour.

    Uses Welford's algorithm to calculate mean and standard deviation
    without storing the complete history of traffic windows.
    """

    MIN_SAMPLES = 30

    FEATURE_NAMES = (
        "requests_per_sec",
        "unique_ips",
        "top_ip_share",
        "top_endpoint_share",
        "status_5xx_rate",
        "avg_latency_ms",
    )

    def __init__(self) -> None:
        self._sample_count = 0
        self._last_updated: datetime | None = None

        # Statistics are maintained separately for each feature and hour.
        self._counts: dict[str, int] = {}
        self._means: dict[str, float] = {}
        self._m2: dict[str, float] = {}

        for feature in self.FEATURE_NAMES:
            for hour in range(24):
                key = f"{feature}:{hour}"
                self._counts[key] = 0
                self._means[key] = 0.0
                self._m2[key] = 0.0

    def update(self, features: WindowFeatures) -> None:
        """
        Update the baseline using one normal traffic window.

        The pipeline is responsible for calling this method only
        when the detection engine considers a window LOW risk.
        """

        hour = features.window_start.astimezone(
            timezone.utc
        ).hour

        for feature in self.FEATURE_NAMES:
            key = f"{feature}:{hour}"
            value = float(getattr(features, feature))

            self._counts[key] += 1

            count = self._counts[key]

            delta = value - self._means[key]
            self._means[key] += delta / count
            delta2 = value - self._means[key]

            self._m2[key] += delta * delta2

        self._sample_count += 1
        self._last_updated = features.window_end.astimezone(
            timezone.utc
        )

    def get(self, at: datetime) -> BaselineProfile | None:
        """
        Return the learned baseline after at least 30 samples.
        """

        if at.tzinfo is None:
            raise ValueError("at must be timezone-aware")

        if self._sample_count < self.MIN_SAMPLES:
            return None

        profile_data = {}

        for feature in self.FEATURE_NAMES:
            hourly_stats = {}

            for hour in range(24):
                key = f"{feature}:{hour}"
                count = self._counts[key]

                if count == 0:
                    continue

                mean_value = self._means[key]

                # Population standard deviation.
                variance = self._m2[key] / count
                std_value = sqrt(max(0.0, variance))

                hourly_stats[str(hour)] = PerHourStats(
                    mean=mean_value,
                    std=std_value,
                )

            profile_data[feature] = hourly_stats

        return BaselineProfile(
            sample_count=self._sample_count,
            last_updated=self._last_updated,
            **profile_data,
        )
