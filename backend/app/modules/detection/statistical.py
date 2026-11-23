"""
Statistical anomaly detector (EWMA / z-score) — stub implementation.

Owner: Member 2.
# TODO(member2): implement StatisticalDetector
"""

from __future__ import annotations

from app.modules.detection.interfaces import Detector
from app.schemas.detection import SignalEvidence
from app.schemas.traffic import BaselineProfile, WindowFeatures


class StatisticalDetector(Detector):
    """
    Detects anomalies by comparing the current window's features against the
    learned ``BaselineProfile`` using z-scores.

    For each feature with a baseline (mean, std):
      z = (observed - mean) / std

    A high absolute z-score indicates deviation from normal traffic.
    Returns ``None`` deviation and sets ``triggered=False`` when no baseline
    is available for a feature yet.

    TODO(member2):
      - Iterate over the per-feature baseline buckets in ``BaselineProfile``.
      - Select the bucket matching the window's hour of day.
      - Compute z-scores and decide trigger thresholds.
    """

    @property
    def name(self) -> str:
        return "StatisticalDetector"

    def evaluate(
        self,
        features: WindowFeatures,
        baseline: BaselineProfile | None,
    ) -> list[SignalEvidence]:
        """
        Raises:
            NotImplementedError: TODO(member2): compute z-scores against baseline.
        """
        raise NotImplementedError(
            "TODO(member2): compute z-scores for each feature against BaselineProfile "
            "and return SignalEvidence per feature"
        )
