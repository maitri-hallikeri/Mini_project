# Benchmarks — Offline CIC-DDoS2019 Evaluation Pipeline

## ⚠️ Important: Two separate pipelines

This directory contains the **offline flow-level evaluation** pipeline.
It is completely separate from the **live HTTP-window pipeline** in `app/`.

| Dimension | Offline benchmark (this folder) | Live pipeline (`app/`) |
|---|---|---|
| Data source | CIC-DDoS2019 CSV files | Nginx access log |
| Feature type | Flow-level (CICFlowMeter) | HTTP window aggregates |
| Feature schema | Pandas DataFrame | `schemas.traffic.WindowFeatures` |
| Purpose | Tune and compare classifiers | Detect attacks in production |
| Models | RF, Isolation Forest, GNB | Optional: `MLDetector` |

**Models trained here cannot be directly reused in the live `MLDetector`**
without retraining on live `WindowFeatures` vectors.

---

## Owners

| File | Owner |
|---|---|
| `cic_ddos2019_loader.py` | Member 1 |
| `train_evaluate.py` | Member 2 |

---

## Dataset

Download from: https://www.unb.ca/cic/datasets/ddos-2019.html

Place extracted CSV files under `backend/data/CIC-DDoS2019/CSV/`.
The `.gitignore` excludes `backend/data/*` so large data files are not committed.

---

## Setup

```bash
# From backend/
pip install -r requirements-ml.txt
```

---

## Usage (once stubs are implemented)

```python
from benchmarks.cic_ddos2019_loader import load_cic_csv, time_aware_split
from benchmarks.train_evaluate import (
    train_random_forest, train_isolation_forest,
    train_gaussian_naive_bayes, evaluate_model, print_metrics
)

df = load_cic_csv("data/CIC-DDoS2019/CSV/03-11/UDP.csv")
X_tr, X_te, y_tr, y_te = time_aware_split(df)

for train_fn, name in [
    (lambda X, y: train_random_forest(X, y), "Random Forest"),
    (lambda X, y: train_gaussian_naive_bayes(X, y), "Gaussian NB"),
]:
    model = train_fn(X_tr, y_tr)
    metrics = evaluate_model(model, X_te, y_te)
    print_metrics(metrics, name)

# Isolation Forest is unsupervised (no y needed):
iso = train_isolation_forest(X_tr)
print_metrics(evaluate_model(iso, X_te, y_te), "Isolation Forest")
```

---

## Evaluation metrics

| Metric | Why it matters |
|---|---|
| Precision | Fraction of flagged flows that are real attacks |
| Recall | Fraction of real attacks detected |
| F1 | Balance of precision and recall |
| **FPR** | **Fraction of benign flows wrongly flagged** — key for availability |
