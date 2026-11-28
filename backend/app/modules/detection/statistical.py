"""
Statistical anomaly detector (z-score vs hourly baseline).

Owner: Member 2.
"""

from __future__ import annotations

from app.modules.detection.interfaces import Detector
from app.schemas.detection import SignalEvidence
from app.schemas.traffic import BaselineProfile, WindowFeatures

# Feature names tracked in BaselineProfile and their scorer weights
MONITORED_FEATURES: list[tuple[str, float]] = [
    ("requests_per_sec", 0.25),
    ("top_ip_share", 0.25),
    ("top_endpoint_share", 0.20),
    ("status_5xx_rate", 0.15),
    ("avg_latency_ms", 0.15),
]


class StatisticalDetector(Detector):
    """
    Detects anomalies by comparing the current window's features against
    the learned hourly ``BaselineProfile`` using z-scores:
      z = (observed - mean) / std
    """

    def __init__(self, z_threshold: float = 3.0) -> None:
        self._z_threshold = z_threshold

    @property
    def name(self) -> str:
        return "StatisticalDetector"

    def evaluate(
        self,
        features: WindowFeatures,
        baseline: BaselineProfile | None,
    ) -> list[SignalEvidence]:
        """Compute z-scores against the matching hour-of-day baseline bucket."""
        hour_key = str(features.window_start.hour)
        signals: list[SignalEvidence] = []

        for feat_name, weight in MONITORED_FEATURES:
            observed = float(getattr(features, feat_name, 0.0))
            hour_map = getattr(baseline, feat_name, {}) if baseline is not None else {}
            stats = hour_map.get(hour_key) if isinstance(hour_map, dict) else None

            if stats is None:
                signals.append(
                    SignalEvidence(
                        name=f"z_{feat_name}",
                        observed_value=round(observed, 4),
                        baseline_value=None,
                        threshold=self._z_threshold,
                        deviation=None,
                        weight=weight,
                        triggered=False,
                        description=f"No baseline available yet for {feat_name} at hour {hour_key}.",
                    )
                )
                continue

            # Guard against zero standard deviation in flat baselines
            effective_std = stats.std if stats.std > 1e-6 else 1e-6
            z_score = (observed - stats.mean) / effective_std
            triggered = z_score > self._z_threshold

            signals.append(
                SignalEvidence(
                    name=f"z_{feat_name}",
                    observed_value=round(observed, 4),
                    baseline_value=round(stats.mean, 4),
                    threshold=self._z_threshold,
                    deviation=round(z_score, 2),
                    weight=weight,
                    triggered=triggered,
                    description=(
                        f"{feat_name}={observed:.2f} vs baseline {stats.mean:.2f} "
                        f"(z={z_score:.2f}, threshold={self._z_threshold})."
                    ),
                )
            )

        return signals
