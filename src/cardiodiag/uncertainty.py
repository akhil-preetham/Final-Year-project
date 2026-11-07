"""Split-conformal uncertainty and abstention for binary classifiers."""

from __future__ import annotations

from math import ceil
from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.utils.validation import check_is_fitted


class SplitConformalClassifier(BaseEstimator, ClassifierMixin):
    """Calibrate prediction sets on a dedicated calibration split.

    The estimator is fitted on development data and never refit on the
    calibration or evaluation labels. Under exchangeability, the resulting
    prediction sets have a finite-sample marginal coverage guarantee. Under
    dataset shift, coverage must be measured rather than assumed.
    """

    def __init__(self, estimator: Any, alpha: float = 0.1) -> None:
        self.estimator = estimator
        self.alpha = alpha

    def fit(self, X: Any, y: Any, X_cal: Any, y_cal: Any) -> SplitConformalClassifier:
        if not 0 < self.alpha < 1:
            raise ValueError("alpha must be in (0, 1)")
        self.estimator_ = clone(self.estimator)
        self.estimator_.fit(X, y)
        if not np.array_equal(np.asarray(self.estimator_.classes_), np.array([0, 1])):
            raise ValueError("SplitConformalClassifier requires binary classes encoded as 0 and 1")
        probabilities = np.asarray(self.estimator_.predict_proba(X_cal), dtype=float)
        y_cal = np.asarray(y_cal)
        if y_cal.ndim != 1 or y_cal.size == 0 or not np.all(np.isin(y_cal, [0, 1])):
            raise ValueError("y_cal must be a nonempty one-dimensional array of binary 0/1 labels")
        y_cal = y_cal.astype(int)
        if (
            probabilities.ndim != 2
            or probabilities.shape[1] != 2
            or not np.all(np.isfinite(probabilities))
            or np.any((probabilities < 0) | (probabilities > 1))
            or not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-6)
        ):
            raise ValueError("SplitConformalClassifier supports binary classifiers only")
        if probabilities.shape[0] != y_cal.shape[0]:
            raise ValueError("Calibration features and labels must have the same length")
        scores = 1.0 - probabilities[np.arange(len(y_cal)), y_cal]
        self.quantile_ = finite_sample_upper_quantile(scores, self.alpha)
        self.n_features_in_ = getattr(self.estimator_, "n_features_in_", None)
        return self

    def predict_proba(self, X: Any) -> np.ndarray:
        check_is_fitted(self, ["estimator_", "quantile_"])
        return self.estimator_.predict_proba(X)

    def predict_sets(self, X: Any) -> np.ndarray:
        probabilities = self.predict_proba(X)
        return (1.0 - probabilities) <= self.quantile_

    def predict(self, X: Any) -> np.ndarray:
        prediction_sets = self.predict_sets(X)
        predictions = np.full(prediction_sets.shape[0], -1, dtype=int)
        singleton = prediction_sets.sum(axis=1) == 1
        predictions[singleton] = np.argmax(prediction_sets[singleton], axis=1)
        return predictions

    def summarize(self, X: Any, y: Any) -> dict[str, float | int]:
        """Return coverage, abstention, and selective risk on labelled data."""

        y = np.asarray(y, dtype=int)
        if len(X) != len(y):
            raise ValueError("X and y must have the same number of rows")
        sets = self.predict_sets(X)
        predictions = self.predict(X)
        covered = sets[np.arange(len(y)), y]
        singleton = predictions != -1
        correct_singletons = singleton & (predictions == y)
        return {
            "n": int(len(y)),
            "coverage": float(covered.mean()),
            "singleton_coverage": float(singleton.mean()),
            "abstention_rate": float((~singleton).mean()),
            "selective_accuracy": float(correct_singletons.sum() / singleton.sum())
            if singleton.any()
            else 0.0,
            "selective_risk": float(1.0 - correct_singletons.sum() / singleton.sum())
            if singleton.any()
            else 1.0,
        }


def finite_sample_upper_quantile(values: Any, alpha: float) -> float:
    """Return the split-conformal upper quantile using the finite-sample rank.

    If the requested rank is larger than the calibration sample, ``inf`` is
    returned. This is conservative and preserves the finite-sample rule.
    """

    scores = np.asarray(values, dtype=float)
    if scores.ndim != 1 or scores.size == 0:
        raise ValueError("values must be a nonempty one-dimensional array")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    if not np.all(np.isfinite(scores)):
        raise ValueError("values must contain only finite scores")
    rank = ceil((scores.size + 1) * (1 - alpha))
    if rank > scores.size:
        return float("inf")
    return float(np.partition(scores, rank - 1)[rank - 1])


def domain_robust_threshold(
    values: Any,
    domains: Any,
    alpha: float,
) -> tuple[float, dict[str, float]]:
    """Use the largest domain-specific conformal upper quantile.

    This protects against poorer calibration in one observed source domain.
    It does not provide a distribution-free guarantee for a new domain unless
    that domain is exchangeable with one represented in calibration data.
    """

    scores = np.asarray(values, dtype=float)
    groups = np.asarray(domains)
    if scores.ndim != 1 or groups.ndim != 1 or scores.size != groups.size:
        raise ValueError("values and domains must be one-dimensional arrays of equal length")
    if scores.size == 0:
        raise ValueError("values and domains must not be empty")
    if any(_is_missing_group(group) for group in groups):
        raise ValueError("domains must not contain missing values")
    thresholds = {
        str(group): finite_sample_upper_quantile(scores[groups == group], alpha)
        for group in np.unique(groups)
    }
    return max(thresholds.values()), thresholds


def _is_missing_group(value: Any) -> bool:
    """Check scalar group labels without imposing a pandas dependency."""

    if value is None:
        return True
    try:
        return bool(np.isnan(value))
    except (TypeError, ValueError):
        return value.__class__.__name__ == "NAType"


def conformal_prediction_sets(probabilities: Any, threshold: float) -> np.ndarray:
    """Build binary label sets from calibrated probabilities and one threshold."""

    probability_matrix = np.asarray(probabilities, dtype=float)
    if (
        probability_matrix.ndim != 2
        or probability_matrix.shape[1] != 2
        or probability_matrix.shape[0] == 0
    ):
        raise ValueError("probabilities must have shape (n_samples, 2)")
    if not np.all(np.isfinite(probability_matrix)) or np.any(
        (probability_matrix < 0) | (probability_matrix > 1)
    ):
        raise ValueError("probabilities must be finite and lie in [0, 1]")
    if not np.allclose(probability_matrix.sum(axis=1), 1.0, atol=1e-6):
        raise ValueError("each probability row must sum to one")
    if threshold < 0 or np.isnan(threshold):
        raise ValueError("threshold must be nonnegative")
    return (1.0 - probability_matrix) <= threshold


def conformal_selective_summary(
    y_true: Any,
    prediction_sets: Any,
) -> dict[str, float | int]:
    """Summarize marginal set coverage and errors among singleton predictions."""

    labels = np.asarray(y_true, dtype=int)
    sets = np.asarray(prediction_sets, dtype=bool)
    if sets.ndim != 2 or sets.shape != (labels.size, 2) or labels.size == 0:
        raise ValueError("prediction_sets must have shape (len(y_true), 2)")
    if not np.all(np.isin(labels, [0, 1])):
        raise ValueError("y_true must contain binary labels 0 and 1")
    included = sets[np.arange(labels.size), labels]
    sizes = sets.sum(axis=1)
    singleton = sizes == 1
    predictions = np.argmax(sets, axis=1)
    errors = singleton & (predictions != labels)
    accepted = int(singleton.sum())
    return {
        "n": int(labels.size),
        "empirical_set_coverage": float(included.mean()),
        "singleton_coverage": float(singleton.mean()),
        "abstention_rate": float(1.0 - singleton.mean()),
        "mean_set_size": float(sizes.mean()),
        "selective_risk": float(errors.sum() / accepted) if accepted else 1.0,
        "accepted_errors": int(errors.sum()),
        "accepted_n": accepted,
    }
