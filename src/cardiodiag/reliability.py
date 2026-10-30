"""Calibration, selective-risk, and feature-stability summaries."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.optimize import minimize
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_auc_score


def calibration_summary(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    bins: int = 10,
) -> dict[str, float | int | list[float]]:
    """Return Brier, ECE, and logistic calibration intercept/slope."""

    y_true = np.asarray(y_true, dtype=float)
    probabilities = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
    if y_true.shape != probabilities.shape:
        raise ValueError("y_true and probabilities must have the same shape")
    if np.unique(y_true).size < 2:
        raise ValueError("Calibration requires both outcome classes")
    observed, predicted = calibration_curve(
        y_true, probabilities, n_bins=bins, strategy="uniform"
    )
    ece = float(np.mean(np.abs(observed - predicted))) if observed.size else 0.0
    logit = np.log(probabilities / (1.0 - probabilities))

    def objective(parameters: np.ndarray) -> float:
        linear = parameters[0] + parameters[1] * logit
        loss = np.logaddexp(0.0, linear) - y_true * linear
        return float(np.mean(loss))

    fit = minimize(objective, x0=np.array([0.0, 1.0]), method="BFGS")
    return {
        "n": int(y_true.size),
        "brier": float(np.mean((y_true - probabilities) ** 2)),
        "ece_uniform": ece,
        "calibration_intercept": float(fit.x[0]),
        "calibration_slope": float(fit.x[1]),
        "reliability_observed": observed.astype(float).tolist(),
        "reliability_predicted": predicted.astype(float).tolist(),
    }


def selective_risk_curve(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    coverages: list[float] | None = None,
) -> list[dict[str, float | int]]:
    """Compute risk/coverage using confidence-ranked abstention."""

    y_true = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    if y_true.shape != probabilities.shape:
        raise ValueError("y_true and probabilities must have the same shape")
    coverages = coverages or [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    confidence = np.maximum(probabilities, 1.0 - probabilities)
    predicted = (probabilities >= 0.5).astype(int)
    order = np.argsort(-confidence)
    output = []
    for coverage in coverages:
        if not 0 < coverage <= 1:
            raise ValueError("coverages must be in (0, 1]")
        count = max(1, int(np.ceil(coverage * len(y_true))))
        selected = order[:count]
        risk = float(np.mean(predicted[selected] != y_true[selected]))
        output.append(
            {
                "coverage": float(count / len(y_true)),
                "selected_n": int(count),
                "risk": risk,
                "selective_accuracy": float(1.0 - risk),
                "minimum_confidence": float(confidence[selected].min()),
            }
        )
    return output


def uncertainty_evidence(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    coverages: list[float] | None = None,
) -> dict[str, float | int | list[dict[str, float | int]]]:
    """Summarize whether confidence ranks correct predictions above errors.

    These are empirical diagnostics, not proof that a model understands its own
    uncertainty. Higher ``confidence_error_auc`` and lower ``aurc`` indicate
    better ranking of correct predictions, while the monotonicity count records
    finite-sample violations in the risk/coverage curve.
    """

    y_true = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    if y_true.shape != probabilities.shape:
        raise ValueError("y_true and probabilities must have the same shape")
    if y_true.size == 0:
        raise ValueError("uncertainty evidence requires at least one observation")
    if np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("probabilities must lie in [0, 1]")

    predicted = (probabilities >= 0.5).astype(int)
    confidence = np.maximum(probabilities, 1.0 - probabilities)
    correct = (predicted == y_true).astype(int)
    order = np.argsort(-confidence)
    cumulative_risk = np.cumsum(1 - correct[order]) / np.arange(1, len(y_true) + 1)
    curve = selective_risk_curve(y_true, probabilities, coverages=coverages)
    violations = sum(
        left["risk"] > right["risk"]
        for left, right in zip(curve, curve[1:])
    )
    return {
        "n": int(y_true.size),
        "confidence_error_auc": (
            float(roc_auc_score(correct, confidence))
            if np.unique(correct).size == 2
            else 1.0
        ),
        "aurc": float(np.mean(cumulative_risk)),
        "risk_monotonicity_violations": int(violations),
        "selective_risk": curve,
    }


def nogueira_stability(selection_matrix: np.ndarray) -> float:
    """Compute the chance-corrected stability of repeated selected sets.

    ``selection_matrix`` has one row per perturbation and one column per
    candidate feature. The statistic is based on the variance of each feature's
    inclusion indicator relative to the expected variance at the observed mean
    selection size. It is useful for comparing selectors on the same feature
    universe and is not a guarantee about future samples.
    """

    matrix = np.asarray(selection_matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] < 2 or matrix.shape[1] < 1:
        raise ValueError("selection_matrix must have at least two rows and one column")
    if not np.all(np.isin(matrix, [0.0, 1.0])):
        raise ValueError("selection_matrix must contain only 0/1 indicators")
    mean_selection_rate = float(matrix.mean())
    denominator = mean_selection_rate * (1.0 - mean_selection_rate)
    if denominator == 0.0:
        return 1.0
    variance = np.var(matrix, axis=0, ddof=1)
    return float(np.clip(1.0 - np.mean(variance) / denominator, -1.0, 1.0))


def bootstrap_mean_ci(
    values: np.ndarray | list[float],
    n_bootstrap: int = 2000,
    confidence: float = 0.95,
    random_state: int = 42,
) -> tuple[float, float, float]:
    """Return a percentile bootstrap interval for a mean of repeated estimates."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size < 2:
        raise ValueError("values must contain at least two repeated estimates")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0, 1)")
    if n_bootstrap < 1:
        raise ValueError("n_bootstrap must be positive")
    rng = np.random.default_rng(random_state)
    means = np.empty(n_bootstrap, dtype=float)
    for index in range(n_bootstrap):
        sample = rng.choice(array, size=array.size, replace=True)
        means[index] = sample.mean()
    tail = (1.0 - confidence) / 2.0
    low, high = np.quantile(means, [tail, 1.0 - tail])
    return float(array.mean()), float(low), float(high)


def selector_stability_summary(
    selector: Any, feature_names: list[str]
) -> list[dict[str, float | bool | str]]:
    """Serialize feature selection frequency and mean relevance."""

    if len(feature_names) != len(selector.selection_frequency_):
        raise ValueError("feature_names must match the fitted selector width")
    return [
        {
            "feature": name,
            "selected": bool(selector.support_[index]),
            "selection_frequency": float(selector.selection_frequency_[index]),
            "mean_relevance": float(selector.mean_relevance_[index]),
        }
        for index, name in enumerate(feature_names)
    ]
