"""
Optional Isolation Forest ML detector — stub implementation.

Owner: Member 2.
# TODO(member2): implement MLDetector (disabled by default via ML_DETECTOR_ENABLED)
"""

from __future__ import annotations

from app.modules.detection.interfaces import Detector
from app.schemas.detection import SignalEvidence
from app.schemas.traffic import BaselineProfile, WindowFeatures


class MLDetector(Detector):
    """
    Optional anomaly detector using a pre-trained Isolation Forest model.

    This detector is disabled by default (``Settings.ML_DETECTOR_ENABLED=false``)
    because it requires a trained model artifact produced by the offline
    benchmark pipeline (``benchmarks/train_evaluate.py``).

    When enabled:
      - Load the serialised ``IsolationForest`` model from disk using
        ``joblib.load`` (path from a new ``Settings.ML_MODEL_PATH`` field).
      - Convert ``WindowFeatures`` to a 1-row numpy array matching the
        training feature order.
      - Return a single ``SignalEvidence`` with the anomaly score.

    TODO(member2):
      - Train the model in benchmarks/train_evaluate.py.
      - Add ``ML_MODEL_PATH`` to Settings.
      - Implement ``evaluate()`` here.
    """

    @property
    def name(self) -> str:
        return "MLDetector"

    def evaluate(
        self,
        features: WindowFeatures,
        baseline: BaselineProfile | None,
    ) -> list[SignalEvidence]:
        """
        Raises:
            NotImplementedError: TODO(member2): load IsolationForest model and score window.
        """
        raise NotImplementedError(
            "TODO(member2): load trained IsolationForest model and score WindowFeatures; "
            "only run when ML_DETECTOR_ENABLED=true"
        )
