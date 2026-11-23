"""
CIC-DDoS2019 dataset loader for the offline evaluation pipeline.

Owner: Member 1.

IMPORTANT: This offline pipeline operates on FLOW-LEVEL features exported
by CICFlowMeter from the public CIC-DDoS2019 pcap files.  These features
(packet counts, flow duration, inter-arrival times, etc.) are fundamentally
different from the HTTP-window features used in the live pipeline
(``app/schemas/traffic.WindowFeatures``).  Models trained here CANNOT be
applied directly to live traffic windows without a feature-mapping step.

Dataset source: https://www.unb.ca/cic/datasets/ddos-2019.html
Cite: Sharafaldin et al., "Developing Realistic Distributed Denial of Service
(DDoS) Attack Dataset and Taxonomy", IEEE ICISSP 2019.

Usage::

    from benchmarks.cic_ddos2019_loader import load_cic_csv, time_aware_split

    df = load_cic_csv("data/CIC-DDoS2019/CSV/03-11/UDP.csv")
    X_train, X_test, y_train, y_test = time_aware_split(df)
"""

from __future__ import annotations

from pathlib import Path

# pandas and numpy are only available when requirements-ml.txt is installed.
# Import them lazily to keep the base image importable without ML deps.
try:
    import numpy as np  # noqa: F401
    import pandas as pd  # noqa: F401
    from pandas import DataFrame
except ImportError as e:  # noqa: F841
    raise ImportError(
        "ML dependencies not installed.  Run: pip install -r requirements-ml.txt"
    ) from e

# Label column name used in CIC-DDoS2019 CSV files.
_LABEL_COL = " Label"

# Value that indicates benign (normal) traffic in the label column.
_BENIGN_LABEL = "BENIGN"


def load_cic_csv(path: str | Path) -> DataFrame:
    """
    Load one CIC-DDoS2019 flow-level CSV file into a cleaned DataFrame.

    Steps performed:
      1. Read the CSV with pandas.
      2. Strip leading/trailing whitespace from column names.
      3. Drop rows with NaN or infinite values in any numeric column
         (CICFlowMeter sometimes exports division-by-zero artefacts).
      4. Encode the label column as a binary integer: 0 = BENIGN, 1 = ATTACK.
      5. Return the cleaned DataFrame with the binary label in a column
         named ``label``.

    Args:
        path: Absolute or relative path to a CIC-DDoS2019 CSV file.

    Returns:
        A cleaned ``DataFrame`` with numeric features and a binary ``label``
        column (0 = BENIGN, 1 = ATTACK).

    Raises:
        NotImplementedError: TODO(member1): implement the loading and cleaning logic.
    """
    raise NotImplementedError(
        "TODO(member1): load CSV, strip column names, drop NaN/inf rows, "
        "and encode BENIGN=0 / ATTACK=1 in a 'label' column"
    )


def time_aware_split(
    df: DataFrame,
    test_fraction: float = 0.2,
) -> tuple[DataFrame, DataFrame, DataFrame, DataFrame]:
    """
    Split the dataset into train/test sets respecting temporal order.

    A time-aware split prevents data leakage: the test set always contains
    data recorded AFTER the training set, mirroring real deployment conditions
    where the model is trained on historical data and evaluated on future data.

    Args:
        df:            Cleaned DataFrame from ``load_cic_csv()``.  Must contain
                       a ``Timestamp`` column (or equivalent) in a parseable
                       datetime format.
        test_fraction: Fraction of the data (by time) to hold out for testing.

    Returns:
        ``(X_train, X_test, y_train, y_test)`` where X* are feature DataFrames
        and y* are the corresponding binary label Series.

    Raises:
        NotImplementedError: TODO(member1): implement time-based splitting.
    """
    raise NotImplementedError(
        "TODO(member1): sort by timestamp, take last test_fraction rows as test set, "
        "return (X_train, X_test, y_train, y_test)"
    )
