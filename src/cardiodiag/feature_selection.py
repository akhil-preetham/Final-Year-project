"""Stable, training-only XAI-guided dimensionality reduction."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.utils.validation import check_array, check_is_fitted, check_X_y


class StableXAIHDRC(BaseEstimator, TransformerMixin):
    """Resample-stable XAIH-DRC approximation fitted only on training data.

    For each inner resample, the transformer combines absolute point-biserial
    correlation with model-based permutation importance. A feature is retained
    when its selection frequency and mean relevance exceed prespecified
    thresholds. The implementation intentionally keeps the selected columns in
    their original transformed space; optional PCA is exposed as a separate,
    explicitly configured step rather than silently replacing interpretable
    features.
    """

    def __init__(
        self,
        n_resamples: int = 8,
        stability_threshold: float = 0.75,
        relevance_threshold: float = 0.02,
        fallback_top_k: int = 5,
        random_state: int = 42,
        relevance_validation_fraction: float = 0.25,
    ) -> None:
        self.n_resamples = n_resamples
        self.stability_threshold = stability_threshold
        self.relevance_threshold = relevance_threshold
        self.fallback_top_k = fallback_top_k
        self.random_state = random_state
        self.relevance_validation_fraction = relevance_validation_fraction

    def fit(self, X: Any, y: Any) -> StableXAIHDRC:
        X, y = check_X_y(X, y, accept_sparse=False, dtype=float)
        if self.n_resamples < 2:
            raise ValueError("n_resamples must be at least 2")
        if not 0 < self.stability_threshold <= 1:
            raise ValueError("stability_threshold must be in (0, 1]")
        if self.fallback_top_k < 1:
            raise ValueError("fallback_top_k must be positive")
        if not 0 < self.relevance_validation_fraction < 1:
            raise ValueError("relevance_validation_fraction must be in (0, 1)")
        rng = np.random.default_rng(self.random_state)
        if np.unique(y).size != 2:
            raise ValueError("StableXAIHDrC currently supports binary targets only")
        indices = np.arange(len(y))
        fit_indices, validation_indices = train_test_split(
            indices,
            test_size=self.relevance_validation_fraction,
            stratify=y,
            random_state=self.random_state,
        )
        self.relevance_fit_indices_ = fit_indices
        self.relevance_validation_indices_ = validation_indices
        class_indices = [fit_indices[y[fit_indices] == label] for label in np.unique(y)]

        selection = []
        relevance = []
        bootstrap_indices = []
        for _ in range(self.n_resamples):
            sampled = np.concatenate(
                [
                    rng.choice(class_index, size=len(class_index), replace=True)
                    for class_index in class_indices
                ]
            )
            rng.shuffle(sampled)
            bootstrap_indices.append(sampled)
            combined = _combined_relevance(
                X[sampled],
                y[sampled],
                X[validation_indices],
                y[validation_indices],
                random_state=int(rng.integers(0, 2**31 - 1)),
            )
            relevance.append(combined)
            selection.append(combined >= self.relevance_threshold)

        self.bootstrap_indices_ = tuple(bootstrap_indices)
        self.selection_matrix_ = np.asarray(selection, dtype=float)
        self.selection_frequency_ = self.selection_matrix_.mean(axis=0)
        self.mean_relevance_ = np.asarray(relevance, dtype=float).mean(axis=0)
        stable = (self.selection_frequency_ >= self.stability_threshold) & (
            self.mean_relevance_ >= self.relevance_threshold
        )
        if not stable.any():
            ranking = np.argsort(self.mean_relevance_)[::-1]
            stable[ranking[: min(self.fallback_top_k, X.shape[1])]] = True
        self.support_ = stable
        self.selected_indices_ = np.flatnonzero(stable)
        self.n_features_in_ = X.shape[1]
        self.feature_names_in_ = np.asarray(
            [f"feature_{i}" for i in range(X.shape[1])], dtype=object
        )
        return self

    def transform(self, X: Any) -> np.ndarray:
        check_is_fitted(self, ["support_", "selected_indices_"])
        X = check_array(X, accept_sparse=False, dtype=float)
        if X.shape[1] != self.n_features_in_:
            raise ValueError(f"Expected {self.n_features_in_} features, got {X.shape[1]}")
        return X[:, self.selected_indices_]

    def get_support(self, indices: bool = False) -> np.ndarray:
        check_is_fitted(self, ["support_"])
        return self.selected_indices_ if indices else self.support_

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        check_is_fitted(self, ["support_"])
        names = (
            self.feature_names_in_
            if input_features is None
            else np.asarray(input_features, dtype=object)
        )
        return names[self.selected_indices_]

    @staticmethod
    def _absolute_correlation(X: np.ndarray, y: np.ndarray) -> np.ndarray:
        y_centered = y - y.mean()
        x_centered = X - X.mean(axis=0)
        numerator = np.abs(np.sum(x_centered * y_centered[:, None], axis=0))
        denominator = np.sqrt(np.sum(x_centered**2, axis=0) * np.sum(y_centered**2))
        return np.divide(
            numerator,
            denominator,
            out=np.zeros_like(numerator),
            where=denominator > 0,
        )


def one_shot_selection_mask(
    X: Any,
    y: Any,
    relevance_threshold: float = 0.02,
    fallback_top_k: int = 5,
    random_state: int = 42,
) -> np.ndarray:
    """Return a single-pass selection mask for a stability comparator.

    This is an analysis baseline, not a replacement for ``StableXAIHDRC``. It
    applies the same correlation/permutation relevance score once to the full
    training fold. Comparing it with the resampled selector makes the claim
    "the selected set is more stable" falsifiable rather than descriptive.
    """

    X, y = check_X_y(X, y, accept_sparse=False, dtype=float)
    if fallback_top_k < 1:
        raise ValueError("fallback_top_k must be positive")
    if not 0 <= relevance_threshold:
        raise ValueError("relevance_threshold must be non-negative")
    if np.unique(y).size != 2:
        raise ValueError("one_shot_selection_mask currently supports binary targets only")

    indices = np.arange(len(y))
    fit_indices, validation_indices = train_test_split(
        indices,
        test_size=0.25,
        stratify=y,
        random_state=random_state,
    )
    relevance = _combined_relevance(
        X[fit_indices],
        y[fit_indices],
        X[validation_indices],
        y[validation_indices],
        random_state=random_state,
    )
    selected = relevance >= relevance_threshold
    if not selected.any():
        ranking = np.argsort(relevance)[::-1]
        selected[ranking[: min(fallback_top_k, X.shape[1])]] = True
    return selected


def _combined_relevance(
    X_fit: np.ndarray,
    y_fit: np.ndarray,
    X_validation: np.ndarray,
    y_validation: np.ndarray,
    random_state: int,
) -> np.ndarray:
    """Compute relevance from a fit sample and untouched validation observations."""

    corr = StableXAIHDRC._absolute_correlation(X_validation, y_validation)
    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=random_state,
    )
    model.fit(X_fit, y_fit)
    importance = permutation_importance(
        model,
        X_validation,
        y_validation,
        scoring="roc_auc",
        n_repeats=2,
        random_state=random_state,
    ).importances_mean
    importance = np.maximum(importance, 0.0)
    if importance.max() > 0:
        importance = importance / importance.max()
    return 0.5 * corr + 0.5 * importance
