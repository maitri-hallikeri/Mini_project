"""
Detection engine — wires detectors and scorer, implements DetectionEngineBase.

Owner: Member 2.
# TODO(member2): implement the detector calls and scorer once stubs are filled in.

This file is intentionally wired: ``assess()`` calls all enabled detectors
and passes their combined signals to the scorer.  Only the detectors and
scorer themselves are stubs (they raise NotImplementedError).
"""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.modules.detection.interfaces import DetectionEngineBase, Detector, RiskScorer
from app.schemas.detection import RiskAssessment, SignalEvidence
from app.schemas.traffic import BaselineProfile, WindowFeatures

logger = logging.getLogger(__name__)


class DetectionEngine(DetectionEngineBase):
    """
    Runs all enabled ``Detector`` instances then passes the aggregated signals
    to a ``RiskScorer`` to produce the final ``RiskAssessment``.

    Args:
        detectors: Ordered list of detectors to run.  At minimum:
                   ``[RuleDetector(), StatisticalDetector()]``.
                   Add ``MLDetector()`` only when
                   ``Settings.ML_DETECTOR_ENABLED=true``.
        scorer:    The scorer that turns signals into a risk assessment.
                   Pass a ``WeightedRiskScorer`` instance.

    The wiring (which detectors are enabled) is done in
    ``orchestrator/scheduler.py``, not here.
    """

    def __init__(self, detectors: list[Detector], scorer: RiskScorer) -> None:
        self._detectors = detectors
        self._scorer = scorer
        self._settings = get_settings()

    def assess(
        self,
        features: WindowFeatures,
        baseline: BaselineProfile | None,
    ) -> RiskAssessment:
        """
        Run all enabled detectors, collect signals, and score.

        This method is wired — it calls each detector in turn and passes the
        combined signal list to the scorer.  The detectors and scorer
        themselves still raise ``NotImplementedError`` until Member 2
        implements them.

        Args:
            features: Extracted features for the current window.
            baseline: Learned baseline profile, or ``None``.

        Returns:
            A ``RiskAssessment`` for the current window.
        """
        all_signals: list[SignalEvidence] = []
        detectors_used: list[str] = []

        for detector in self._detectors:
            # Each detector call will raise NotImplementedError until Member 2
            # implements the stub.
            signals = detector.evaluate(features, baseline)
            all_signals.extend(signals)
            detectors_used.append(detector.name)
            logger.debug("Detector %s returned %d signals.", detector.name, len(signals))

        assessment = self._scorer.score(features, all_signals)

        # Stamp which detectors ran (the scorer may not know).
        return assessment.model_copy(update={"detectors_used": detectors_used})
