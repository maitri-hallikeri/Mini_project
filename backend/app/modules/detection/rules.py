"""
Hard-limit rule-based detector — stub implementation.

Owner: Member 2.
# TODO(member2): implement RuleDetector
# TODO(member2): adapt from protection_engine/app/decision_engine.py
"""

from __future__ import annotations

from app.modules.detection.interfaces import Detector
from app.schemas.detection import SignalEvidence
from app.schemas.traffic import BaselineProfile, WindowFeatures


class RuleDetector(Detector):
    """
    Checks ``WindowFeatures`` against hard-coded threshold rules.

    Signals this detector evaluates:
      - ``top_ip_share``        > configurable limit → single-source flood.
      - ``requests_per_sec``    > configurable limit → volume flood.
      - ``status_5xx_rate``     > configurable limit → server stress indicator.
      - ``top_endpoint_share``  > configurable limit → endpoint flood.

    All thresholds should come from ``Settings`` (not hard-coded here) so
    Member 3 can tune them without editing this file.

    TODO(member2): adapt threshold values from protection_engine/app/decision_engine.py
    """

    @property
    def name(self) -> str:
        return "RuleDetector"

    def evaluate(
        self,
        features: WindowFeatures,
        baseline: BaselineProfile | None,
    ) -> list[SignalEvidence]:
        """
        Raises:
            NotImplementedError: TODO(member2): check features against hard thresholds.
        """
        raise NotImplementedError(
            "TODO(member2): check WindowFeatures against hard rule thresholds "
            "and return one SignalEvidence per rule checked"
        )
