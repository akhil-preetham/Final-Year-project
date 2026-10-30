"""Metrics and uncertainty summaries for binary prediction experiments."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_predictions(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    threshold: float = 0.5,
    calibration_bins: int = 10,
) -> dict[str, float | int | list[float]]:
    """Return discrimination, classification, calibration, and sample metrics."""

    y_true = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    if y_true.shape[0] != probabilities.shape[0]:
        raise ValueError("y_true and probabilities must have the same length")
    if np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("probabilities must lie in [0, 1]")
    predicted = (probabilities >= threshold).astype(int)
    tn = int(np.sum((y_true == 0) & (predicted == 0)))
    fp = int(np.sum((y_true == 0) & (predicted == 1)))
    fn = int(np.sum((y_true == 1) & (predicted == 0)))
    tp = int(np.sum((y_true == 1) & (predicted == 1)))
    fraction_positive, mean_predicted = calibration_curve(
        y_true, probabilities, n_bins=calibration_bins, strategy="uniform"
    )
    return {
        "n": int(y_true.size),
        "positive_count": int(y_true.sum()),
        "prevalence": float(y_true.mean()),
        "accuracy": float(accuracy_score(y_true, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, predicted)),
        "precision": float(precision_score(y_true, predicted, zero_division=0)),
        "recall": float(recall_score(y_true, predicted, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if tn + fp else 0.0,
        "f1": float(f1_score(y_true, predicted, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "pr_auc": float(average_precision_score(y_true, probabilities)),
        "brier": float(brier_score_loss(y_true, probabilities)),
        "ece_uniform": float(
            np.mean(np.abs(fraction_positive - mean_predicted))
        )
        if fraction_positive.size
        else 0.0,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
    }


def bootstrap_metric_ci(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    metric: Callable[[np.ndarray, np.ndarray], float],
    n_bootstrap: int = 1000,
    random_state: int = 42,
) -> tuple[float, float, float]:
    """Compute a percentile bootstrap interval for paired predictions."""

    y_true = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    rng = np.random.default_rng(random_state)
    values: list[float] = []
    for _ in range(n_bootstrap):
        indices = rng.integers(0, len(y_true), size=len(y_true))
        sampled_y = y_true[indices]
        if np.unique(sampled_y).size < 2:
            continue
        values.append(float(metric(sampled_y, probabilities[indices])))
    if not values:
        raise ValueError("No valid bootstrap samples contained both classes")
    low, high = np.percentile(values, [2.5, 97.5])
    return float(metric(y_true, probabilities)), float(low), float(high)
