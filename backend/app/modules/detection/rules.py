"""
Hard-limit rule-based detector implementation.

Owner: Member 2.
"""

from __future__ import annotations

from app.modules.detection.interfaces import Detector
from app.schemas.detection import SignalEvidence
from app.schemas.traffic import BaselineProfile, WindowFeatures


class RuleDetector(Detector):
    """
    Checks ``WindowFeatures`` against hard-coded safety thresholds.

    Signals evaluated:
      - ``top_ip_share``       > 0.50  -> single-source flood (weight 0.30)
      - ``requests_per_sec``   > 100.0 -> volume flood (weight 0.30)
      - ``top_endpoint_share`` > 0.75  -> targeted endpoint flood (weight 0.25)
      - ``status_5xx_rate``    > 0.15  -> server stress indicator (weight 0.15)
    """

    def __init__(
        self,
        max_top_ip_share: float = 0.50,
        max_rps: float = 100.0,
        max_top_endpoint_share: float = 0.75,
        max_5xx_rate: float = 0.15,
    ) -> None:
        self._max_top_ip_share = max_top_ip_share
        self._max_rps = max_rps
        self._max_top_endpoint_share = max_top_endpoint_share
        self._max_5xx_rate = max_5xx_rate

    @property
    def name(self) -> str:
        return "RuleDetector"

    def evaluate(
        self,
        features: WindowFeatures,
        baseline: BaselineProfile | None,
    ) -> list[SignalEvidence]:
        """Evaluate hard threshold rules against the current window."""
        rules = [
            (
                "top_ip_share",
                features.top_ip_share,
                self._max_top_ip_share,
                0.30,
                f"Top IP holds {features.top_ip_share:.0%} of requests (threshold {self._max_top_ip_share:.0%}).",
            ),
            (
                "requests_per_sec",
                features.requests_per_sec,
                self._max_rps,
                0.30,
                f"Request rate is {features.requests_per_sec:.1f} req/s (threshold {self._max_rps:.1f} req/s).",
            ),
            (
                "top_endpoint_share",
                features.top_endpoint_share,
                self._max_top_endpoint_share,
                0.25,
                f"Top endpoint holds {features.top_endpoint_share:.0%} of traffic (threshold {self._max_top_endpoint_share:.0%}).",
            ),
            (
                "status_5xx_rate",
                features.status_5xx_rate,
                self._max_5xx_rate,
                0.15,
                f"5xx error rate is {features.status_5xx_rate:.0%} (threshold {self._max_5xx_rate:.0%}).",
            ),
        ]

        signals: list[SignalEvidence] = []
        for sig_name, observed, threshold, weight, desc in rules:
            triggered = observed > threshold
            signals.append(
                SignalEvidence(
                    name=sig_name,
                    observed_value=round(observed, 4),
                    baseline_value=None,
                    threshold=threshold,
                    deviation=None,
                    weight=weight,
                    triggered=triggered,
                    description=desc,
                )
            )
        return signals