"""AURA-ML's bounded original-plus-nonlinear feature representation."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import SplineTransformer

from .preprocessing import AdaptiveTabularTransformer


class MultiViewRepresentation(BaseEstimator, TransformerMixin):
    """Represent a table as an original encoded view or a bounded multi-view.

    The multi-view appends low-degree splines of cleaned numeric variables to
    the original encoded view.  It does not create all pairwise interactions,
    keeping expansion linear in the number of numeric columns.
    """

    def __init__(self, view: str = "original", adaptive: bool = True, n_knots: int = 4) -> None:
        self.view = view
        self.adaptive = adaptive
        self.n_knots = n_knots

    def fit(self, X: pd.DataFrame, y: Any = None) -> MultiViewRepresentation:
        if self.view not in {"original", "multi"}:
            raise ValueError("view must be 'original' or 'multi'")
        self.transformer_ = AdaptiveTabularTransformer(adaptive=self.adaptive)
        self.transformer_.fit(X, y)
        self.spline_ = None
        if self.view == "multi" and self.transformer_.numeric_columns_ and len(X) >= 30:
            self.spline_ = SplineTransformer(
                n_knots=max(3, min(self.n_knots, 6)), degree=2, include_bias=False
            )
            self.spline_.fit(self.transformer_.transform_numeric(X), y)
        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if not hasattr(self, "transformer_"):
            raise RuntimeError("MultiViewRepresentation must be fitted first")
        base = self.transformer_.transform(X)
        if self.spline_ is None:
            return base
        spline = self.spline_.transform(self.transformer_.transform_numeric(X))
        return np.column_stack([base, spline])

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        if not hasattr(self, "transformer_"):
            raise RuntimeError("MultiViewRepresentation must be fitted first")
        names = list(self.transformer_.get_feature_names_out())
        if self.spline_ is not None:
            names.extend(f"spline_{i}" for i in range(self.spline_.n_features_out_))
        return np.asarray(names, dtype=object)

    @property
    def profile_(self) -> dict[str, Any]:
        if not hasattr(self, "transformer_"):
            raise RuntimeError("MultiViewRepresentation must be fitted first")
        return self.transformer_.policy_
