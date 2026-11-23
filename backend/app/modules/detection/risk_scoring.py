"""
Weighted risk scorer — stub implementation.

Owner: Member 2.
# TODO(member2): implement WeightedRiskScorer
"""

from __future__ import annotations

from app.modules.detection.interfaces import RiskScorer
from app.schemas.detection import RiskAssessment, SignalEvidence
from app.schemas.traffic import WindowFeatures


class WeightedRiskScorer(RiskScorer):
    """
    Produces a composite risk score by summing ``signal.weight`` for each
    triggered signal, then normalising to [0, 100].

    Rules to enforce (checked before returning HIGH or CRITICAL):
      - HIGH requires at least 2 triggered signals.
      - CRITICAL requires at least 3 triggered signals.
    These guard against a single noisy signal escalating to a high level.

    Score-to-level mapping (thresholds from ``Settings``):
      - score <  RISK_MEDIUM_MIN  → LOW
      - score <  RISK_HIGH_MIN    → MEDIUM
      - score <  RISK_CRITICAL_MIN → HIGH
      - score >= RISK_CRITICAL_MIN → CRITICAL

    TODO(member2):
      - Compute the weighted sum of triggered signals.
      - Apply the multi-signal guard before assigning HIGH/CRITICAL.
      - Classify ``scenario`` based on which signals fired.
      - Collect ``offending_ips`` and ``offending_endpoints`` from features.
    """

    def score(
        self,
        features: WindowFeatures,
        signals: list[SignalEvidence],
    ) -> RiskAssessment:
        """
        Raises:
            NotImplementedError: TODO(member2): compute weighted risk score.
        """
        raise NotImplementedError(
            "TODO(member2): compute weighted risk score from SignalEvidence list "
            "and return a RiskAssessment"
        )
