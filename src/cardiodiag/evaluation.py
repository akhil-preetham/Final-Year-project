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


def uniform_bin_calibration_errors(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    bins: int = 10,
) -> tuple[float, float]:
    """Return macro-bin and sample-weighted ECE for equal-width bins.

    The first value is the legacy unweighted mean across occupied bins. The
    second weights each bin's absolute calibration gap by its sample share.
    """
    y_true = np.asarray(y_true)
    probabilities = np.asarray(probabilities, dtype=float)
    if y_true.ndim != 1 or probabilities.ndim != 1 or y_true.shape != probabilities.shape:
        raise ValueError("y_true and probabilities must be equal-length one-dimensional arrays")
    if y_true.size == 0:
        raise ValueError("calibration metrics require at least one observation")
    if not np.all(np.isin(y_true, [0, 1])):
        raise ValueError("y_true must contain binary labels 0 and 1")
    y_true = y_true.astype(int)
    if bins < 1:
        raise ValueError("bins must be a positive integer")
    if not np.all(np.isfinite(probabilities)) or np.any(
        (probabilities < 0) | (probabilities > 1)
    ):
        raise ValueError("probabilities must be finite and lie in [0, 1]")

    observed, predicted = calibration_curve(
        y_true, probabilities, n_bins=bins, strategy="uniform"
    )
    bin_edges = np.linspace(0.0, 1.0, bins + 1)
    bin_ids = np.searchsorted(bin_edges[1:-1], probabilities)
    counts = np.bincount(bin_ids, minlength=bins)
    occupied_counts = counts[counts > 0]
    gaps = np.abs(observed - predicted)
    macro_ece = float(gaps.mean())
    weighted_ece = float(np.dot(occupied_counts / y_true.size, gaps))
    return macro_ece, weighted_ece


def evaluate_predictions(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    threshold: float = 0.5,
    calibration_bins: int = 10,
) -> dict[str, float | int | list[float]]:
    """Return discrimination, classification, calibration, and sample metrics."""

    y_true = np.asarray(y_true)
    probabilities = np.asarray(probabilities, dtype=float)
    if y_true.ndim != 1 or probabilities.ndim != 1 or y_true.shape != probabilities.shape:
        raise ValueError("y_true and probabilities must be equal-length one-dimensional arrays")
    if y_true.size == 0:
        raise ValueError("predictions must contain at least one observation")
    if not np.all(np.isin(y_true, [0, 1])):
        raise ValueError("y_true must contain binary labels 0 and 1")
    y_true = y_true.astype(int)
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must lie in [0, 1]")
    if calibration_bins < 1:
        raise ValueError("calibration_bins must be a positive integer")
    if not np.all(np.isfinite(probabilities)) or np.any(
        (probabilities < 0) | (probabilities > 1)
    ):
        raise ValueError("probabilities must be finite and lie in [0, 1]")
    predicted = (probabilities >= threshold).astype(int)
    tn = int(np.sum((y_true == 0) & (predicted == 0)))
    fp = int(np.sum((y_true == 0) & (predicted == 1)))
    fn = int(np.sum((y_true == 1) & (predicted == 0)))
    tp = int(np.sum((y_true == 1) & (predicted == 1)))
    ece_macro, ece_weighted = uniform_bin_calibration_errors(
        y_true, probabilities, bins=calibration_bins
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
        "ece_uniform": ece_macro,
        "ece_weighted_uniform": ece_weighted,
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

    y_true = np.asarray(y_true)
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
