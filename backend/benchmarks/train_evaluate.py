"""
Offline model training and evaluation for the CIC-DDoS2019 benchmark.

Owner: Member 2.

IMPORTANT: This pipeline trains on FLOW-LEVEL CIC-DDoS2019 features, which
are different from the HTTP-window features used in the live pipeline.
Models trained here (Random Forest, Isolation Forest, Gaussian Naive Bayes)
CANNOT be directly reused for live scoring without a feature-mapping step.

The Isolation Forest trained here may be adapted for the live MLDetector
(``app/modules/detection/ml_detector.py``) but requires retraining on live
``WindowFeatures`` vectors first.

Usage::

    from benchmarks.train_evaluate import train_random_forest, evaluate_model
    from benchmarks.cic_ddos2019_loader import load_cic_csv, time_aware_split

    df = load_cic_csv("data/CIC-DDoS2019/CSV/03-11/UDP.csv")
    X_tr, X_te, y_tr, y_te = time_aware_split(df)

    model = train_random_forest(X_tr, y_tr)
    metrics = evaluate_model(model, X_te, y_te)
    print_metrics(metrics)
"""

from __future__ import annotations

from typing import Any

try:
    import numpy as np  # noqa: F401
    import pandas as pd  # noqa: F401
    from pandas import DataFrame, Series
except ImportError as e:
    raise ImportError(
        "ML dependencies not installed.  Run: pip install -r requirements-ml.txt"
    ) from e

# Type alias for any fitted sklearn estimator.
Estimator = Any


def train_random_forest(
    X_train: DataFrame,
    y_train: Series,
    n_estimators: int = 100,
    random_state: int = 42,
) -> Estimator:
    """
    Train a Random Forest classifier on the CIC-DDoS2019 flow-level features.

    Args:
        X_train:      Feature matrix (numeric columns only).
        y_train:      Binary label series (0 = BENIGN, 1 = ATTACK).
        n_estimators: Number of trees.
        random_state: Seed for reproducibility.

    Returns:
        A fitted ``sklearn.ensemble.RandomForestClassifier`` instance.

    Raises:
        NotImplementedError: TODO(member2): train Random Forest classifier.
    """
    raise NotImplementedError(
        "TODO(member2): fit sklearn RandomForestClassifier and return the fitted model"
    )


def train_isolation_forest(
    X_train: DataFrame,
    contamination: float = 0.1,
    random_state: int = 42,
) -> Estimator:
    """
    Train an Isolation Forest anomaly detector on the flow-level features.

    Isolation Forest is unsupervised; labels are not used during training.
    The resulting model can optionally be adapted for the live
    ``MLDetector`` (requires retraining on live window features).

    Args:
        X_train:       Feature matrix.
        contamination: Expected fraction of anomalies in the training data.
        random_state:  Seed for reproducibility.

    Returns:
        A fitted ``sklearn.ensemble.IsolationForest`` instance.

    Raises:
        NotImplementedError: TODO(member2): train Isolation Forest model.
    """
    raise NotImplementedError(
        "TODO(member2): fit sklearn IsolationForest and return the fitted model"
    )


def train_gaussian_naive_bayes(
    X_train: DataFrame,
    y_train: Series,
) -> Estimator:
    """
    Train a Gaussian Naive Bayes classifier on the flow-level features.

    Args:
        X_train: Feature matrix.
        y_train: Binary label series.

    Returns:
        A fitted ``sklearn.naive_bayes.GaussianNB`` instance.

    Raises:
        NotImplementedError: TODO(member2): train Gaussian Naive Bayes classifier.
    """
    raise NotImplementedError(
        "TODO(member2): fit sklearn GaussianNB and return the fitted model"
    )


def evaluate_model(
    model: Estimator,
    X_test: DataFrame,
    y_test: Series,
) -> dict[str, float]:
    """
    Evaluate a fitted classifier and return standard detection metrics.

    Metrics returned:
      - ``precision``: TP / (TP + FP)
      - ``recall``:    TP / (TP + FN)  — also called detection rate.
      - ``f1``:        Harmonic mean of precision and recall.
      - ``fpr``:       False-positive rate = FP / (FP + TN).
                       Key metric: high FPR means legitimate traffic blocked.

    Args:
        model:  A fitted sklearn estimator with a ``predict`` method.
        X_test: Feature matrix for the test split.
        y_test: True binary labels for the test split.

    Returns:
        Dict with keys: ``precision``, ``recall``, ``f1``, ``fpr``.

    Raises:
        NotImplementedError: TODO(member2): compute evaluation metrics.
    """
    raise NotImplementedError(
        "TODO(member2): call model.predict(X_test), compute precision/recall/f1/fpr "
        "using sklearn.metrics and return as dict"
    )


def print_metrics(metrics: dict[str, float], model_name: str = "Model") -> None:
    """
    Print a formatted metrics table to stdout.

    Args:
        metrics:    Dict from ``evaluate_model()``.
        model_name: Label to print in the header.

    Raises:
        NotImplementedError: TODO(member2): implement formatted metrics output.
    """
    raise NotImplementedError(
        "TODO(member2): format and print precision/recall/f1/fpr metrics table"
    )
