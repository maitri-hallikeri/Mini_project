"""
Abstract base classes for the detection module.

Owner: Member 2.
Contract owner: Member 3 (do not change without a PR approved by both members).
"""

from __future__ import annotations

import abc

from app.schemas.detection import RiskAssessment, SignalEvidence
from app.schemas.traffic import BaselineProfile, WindowFeatures


class Detector(abc.ABC):
    """
    A single detection strategy that evaluates one or more signals.

    Every ``Detector`` examines ``WindowFeatures`` (and optionally a
    ``BaselineProfile``) and returns a list of ``SignalEvidence`` objects —
    one per signal it checked, whether it triggered or not.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Human-readable name used in ``RiskAssessment.detectors_used``."""

    @abc.abstractmethod
    def evaluate(
        self,
        features: WindowFeatures,
        baseline: BaselineProfile | None,
    ) -> list[SignalEvidence]:
        """
        Evaluate this detector against the current window.

        Args:
            features: Extracted features for the current window.
            baseline: Learned baseline, or ``None`` if not enough data yet.

        Returns:
            A list of ``SignalEvidence`` objects.  Include both triggered and
            non-triggered signals so the scorer has a complete picture.
        """


class RiskScorer(abc.ABC):
    """
    Combines signal evidence into a final risk score and level.

    Implementations:
      - ``WeightedRiskScorer`` (risk_scoring.py).
    """

    @abc.abstractmethod
    def score(
        self,
        features: WindowFeatures,
        signals: list[SignalEvidence],
    ) -> RiskAssessment:
        """
        Compute a ``RiskAssessment`` from the aggregated signal evidence.

        Args:
            features: The window features (used to populate window timestamps
                      and extract offending IPs/endpoints).
            signals:  All signals collected from all enabled detectors.

        Returns:
            A fully-populated ``RiskAssessment`` with score (0-100) and level.

        Rules (enforced by the implementation):
          - Multiple triggered signals are required before level reaches HIGH.
          - Score thresholds come from ``Settings.RISK_*_MIN``.
        """


class DetectionEngineBase(abc.ABC):
    """
    Orchestrates all enabled detectors and the risk scorer.

    Implementations:
      - ``DetectionEngine`` (engine.py) — this is the class the orchestrator
        pipeline calls; it is wired together here, not in the orchestrator.
    """

    @abc.abstractmethod
    def assess(
        self,
        features: WindowFeatures,
        baseline: BaselineProfile | None,
    ) -> RiskAssessment:
        """
        Run all enabled detectors, aggregate signals, score, and return a
        ``RiskAssessment``.

        Args:
            features: Extracted features for the current window.
            baseline: Learned baseline, or ``None`` if not yet available.

        Returns:
            A ``RiskAssessment`` ready to be persisted and acted upon.
        """
