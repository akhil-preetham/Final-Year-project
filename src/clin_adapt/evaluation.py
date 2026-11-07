"""Metrics used by CLIN-ADAPT experiments."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_binary_predictions(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, float | int]:
    """Return discrimination, classification and probability metrics."""

    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    if y.ndim != 1 or p.ndim != 1 or len(y) != len(p):
        raise ValueError("y_true and probabilities must be aligned one-dimensional arrays")
    if np.unique(y).size != 2 or np.any((p < 0) | (p > 1)):
        raise ValueError("binary y and probabilities in [0, 1] are required")
    pred = (p >= threshold).astype(int)
    tn = int(np.sum((y == 0) & (pred == 0)))
    fp = int(np.sum((y == 0) & (pred == 1)))
    fn = int(np.sum((y == 1) & (pred == 0)))
    tp = int(np.sum((y == 1) & (pred == 1)))
    return {
        "n": int(len(y)),
        "positive_count": int(y.sum()),
        "prevalence": float(y.mean()),
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if tn + fp else 0.0,
        "f1": float(f1_score(y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, p)),
        "pr_auc": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
    }


def utility(metrics: dict[str, float | int], calibration_weight: float = 0.25) -> float:
    """Conservative validation utility; higher is better."""

    return float(metrics["roc_auc"]) - calibration_weight * float(metrics["brier"])
