"""Split-conformal uncertainty and abstention for binary classifiers."""

from __future__ import annotations

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
        probabilities = self.estimator_.predict_proba(X_cal)
        y_cal = np.asarray(y_cal, dtype=int)
        if probabilities.shape[0] != y_cal.shape[0]:
            raise ValueError("Calibration features and labels must have the same length")
        if probabilities.shape[1] != 2:
            raise ValueError("SplitConformalClassifier supports binary classifiers only")
        scores = 1.0 - probabilities[np.arange(len(y_cal)), y_cal]
        quantile_level = min(1.0, np.ceil((len(scores) + 1) * (1 - self.alpha)) / len(scores))
        self.quantile_ = float(np.quantile(scores, quantile_level, method="higher"))
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
