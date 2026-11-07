from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import LogisticRegression

from cardiodiag.uncertainty import SplitConformalClassifier


class FixedProbabilityClassifier(ClassifierMixin, BaseEstimator):
    """Small deterministic estimator for checking calibration order statistics."""

    def fit(self, X: np.ndarray, y: np.ndarray) -> FixedProbabilityClassifier:
        self.classes_ = np.array([0, 1])
        self.n_features_in_ = X.shape[1]
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return X


def test_split_conformal_classifier_can_abstain() -> None:
    rng = np.random.default_rng(4)
    X = rng.normal(size=(80, 2))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    estimator = LogisticRegression(max_iter=1000)
    conformal = SplitConformalClassifier(estimator, alpha=0.1).fit(
        X[:50], y[:50], X[50:65], y[50:65]
    )

    summary = conformal.summarize(X[65:], y[65:])

    assert summary["n"] == 15
    assert 0 <= summary["coverage"] <= 1
    assert 0 <= summary["abstention_rate"] <= 1


def test_split_conformal_rejects_non_binary_estimator() -> None:
    rng = np.random.default_rng(5)
    X = rng.normal(size=(30, 2))
    y = np.arange(30) % 3

    try:
        SplitConformalClassifier(LogisticRegression(max_iter=1000)).fit(
            X[:20], y[:20], X[20:], y[20:]
        )
    except ValueError as error:
        assert "binary" in str(error)
    else:
        raise AssertionError("Expected a binary-class error")


def test_split_conformal_uses_finite_sample_order_statistic() -> None:
    scores = np.arange(20, dtype=float) / 100
    X_train = np.array([[0.8, 0.2], [0.2, 0.8]])
    X_cal = np.column_stack([scores, 1.0 - scores])
    y_train = np.array([0, 1])
    y_cal = np.ones(20, dtype=int)

    model = SplitConformalClassifier(FixedProbabilityClassifier(), alpha=0.2).fit(
        X_train, y_train, X_cal, y_cal
    )

    # ceil((n + 1)(1 - alpha)) = 17, so use zero-based order statistic 16.
    assert np.isclose(model.quantile_, scores[16])


def test_split_conformal_uses_infinite_cutoff_when_calibration_rank_exceeds_sample() -> None:
    X_train = np.array([[0.8, 0.2], [0.2, 0.8]])
    X_cal = np.array([[0.8, 0.2], [0.7, 0.3], [0.3, 0.7], [0.2, 0.8]])
    model = SplitConformalClassifier(FixedProbabilityClassifier(), alpha=0.1).fit(
        X_train, np.array([0, 1]), X_cal, np.array([0, 0, 1, 1])
    )

    assert np.isinf(model.quantile_)
    assert model.predict_sets(X_cal).all()


def test_split_conformal_rejects_non_binary_calibration_labels() -> None:
    X_train = np.array([[0.8, 0.2], [0.2, 0.8]])
    with np.testing.assert_raises_regex(ValueError, "binary 0/1"):
        SplitConformalClassifier(FixedProbabilityClassifier()).fit(
            X_train,
            np.array([0, 1]),
            X_train,
            np.array([0.5, 1.0]),
        )

