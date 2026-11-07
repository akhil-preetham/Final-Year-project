"""Stable, redundancy-aware feature selection used by AURA-ML."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.utils.validation import check_array, check_is_fitted, check_X_y


class AdaptiveStableSelector(BaseEstimator, TransformerMixin):
    """Select features using relevance, bootstrap stability, and redundancy.

    All quantities are estimated from the fitted training fold.  A feature must
    be relevant and stable; highly correlated candidates are greedily reduced
    in descending relevance order.  The selector is deliberately a candidate
    representation, not a guaranteed improvement.
    """

    def __init__(
        self,
        n_resamples: int = 4,
        stability_threshold: float = 0.5,
        max_features: int = 32,
        random_state: int = 42,
        redundancy_threshold: float = 0.95,
    ) -> None:
        self.n_resamples = n_resamples
        self.stability_threshold = stability_threshold
        self.max_features = max_features
        self.random_state = random_state
        self.redundancy_threshold = redundancy_threshold

    def fit(self, X: Any, y: Any) -> AdaptiveStableSelector:
        X, y = check_X_y(X, y, accept_sparse=False, dtype=float)
        if self.n_resamples < 2 or not 0 < self.stability_threshold <= 1:
            raise ValueError("invalid stability configuration")
        if self.max_features < 1:
            raise ValueError("max_features must be positive")
        self.n_features_in_ = X.shape[1]
        rng = np.random.default_rng(self.random_state)
        mi = mutual_info_classif(X, y, random_state=self.random_state)
        mi = _normalize(mi)
        selection_matrix = []
        for _ in range(self.n_resamples):
            indices = rng.integers(0, len(y), size=len(y))
            model = LogisticRegression(
                penalty="l1",
                solver="liblinear",
                C=0.2,
                max_iter=3000,
                tol=1e-3,
                class_weight="balanced",
                random_state=int(rng.integers(0, 2**31 - 1)),
            )
            model.fit(X[indices], y[indices])
            selection_matrix.append(np.abs(model.coef_[0]) > 1e-8)
        self.selection_matrix_ = np.asarray(selection_matrix, dtype=float)
        self.selection_frequency_ = self.selection_matrix_.mean(axis=0)
        coefficients = np.abs(model.coef_[0])
        self.relevance_ = 0.5 * mi + 0.5 * _normalize(coefficients)
        candidates = np.flatnonzero(self.selection_frequency_ >= self.stability_threshold)
        if candidates.size == 0:
            candidates = np.argsort(self.relevance_)[::-1][: min(self.max_features, X.shape[1])]
        ordered = candidates[np.argsort(self.relevance_[candidates])[::-1]]
        selected: list[int] = []
        correlation = np.corrcoef(X, rowvar=False) if X.shape[1] > 1 else np.ones((1, 1))
        for index in ordered:
            if len(selected) >= min(self.max_features, X.shape[1]):
                break
            if all(
                abs(correlation[index, previous]) < self.redundancy_threshold
                for previous in selected
            ):
                selected.append(int(index))
        if not selected:
            selected = [int(np.argmax(self.relevance_))]
        self.selected_indices_ = np.asarray(selected, dtype=int)
        self.support_ = np.zeros(X.shape[1], dtype=bool)
        self.support_[self.selected_indices_] = True
        return self

    def transform(self, X: Any) -> np.ndarray:
        check_is_fitted(self, ["support_", "selected_indices_"])
        X = check_array(X, accept_sparse=False, dtype=float)
        if X.shape[1] != self.n_features_in_:
            raise ValueError("feature width differs from fitted selector")
        return X[:, self.selected_indices_]

    def get_support(self, indices: bool = False) -> np.ndarray:
        check_is_fitted(self, ["support_"])
        return self.selected_indices_ if indices else self.support_

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        check_is_fitted(self, ["support_"])
        names = np.asarray(
            input_features
            if input_features is not None
            else [f"feature_{i}" for i in range(self.n_features_in_)],
            dtype=object,
        )
        return names[self.selected_indices_]


def _normalize(values: np.ndarray) -> np.ndarray:
    values = np.nan_to_num(np.asarray(values, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    maximum = float(values.max()) if values.size else 0.0
    return values / maximum if maximum > 0 else np.zeros_like(values)
