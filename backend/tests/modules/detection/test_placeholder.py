"""
Placeholder tests for the detection module.

Owner: Member 2.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="TODO(member2): add module tests")
def test_detection_placeholder():
    """Placeholder — Member 2 must replace this with real tests."""


def test_rule_detector_raises_not_implemented():
    """RuleDetector.evaluate() must raise NotImplementedError."""
    from app.modules.detection.rules import RuleDetector

    detector = RuleDetector()
    with pytest.raises(NotImplementedError):
        detector.evaluate(None, None)  # type: ignore[arg-type]


def test_statistical_detector_raises_not_implemented():
    """StatisticalDetector.evaluate() must raise NotImplementedError."""
    from app.modules.detection.statistical import StatisticalDetector

    detector = StatisticalDetector()
    with pytest.raises(NotImplementedError):
        detector.evaluate(None, None)  # type: ignore[arg-type]


def test_ml_detector_raises_not_implemented():
    """MLDetector.evaluate() must raise NotImplementedError."""
    from app.modules.detection.ml_detector import MLDetector

    detector = MLDetector()
    with pytest.raises(NotImplementedError):
        detector.evaluate(None, None)  # type: ignore[arg-type]


def test_weighted_risk_scorer_raises_not_implemented():
    """WeightedRiskScorer.score() must raise NotImplementedError."""
    from app.modules.detection.risk_scoring import WeightedRiskScorer

    scorer = WeightedRiskScorer()
    with pytest.raises(NotImplementedError):
        scorer.score(None, [])  # type: ignore[arg-type]


def test_detector_names():
    """Every stub detector must expose a non-empty name property."""
    from app.modules.detection.ml_detector import MLDetector
    from app.modules.detection.rules import RuleDetector
    from app.modules.detection.statistical import StatisticalDetector

    for cls in (RuleDetector, StatisticalDetector, MLDetector):
        assert isinstance(cls().name, str)
        assert len(cls().name) > 0
