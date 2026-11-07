"""Adaptive, training-only preprocessing for AURA-ML."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler, StandardScaler

from .intelligence import profile_dataset


class AdaptiveTabularTransformer(BaseEstimator, TransformerMixin):
    """Choose a conservative preprocessing policy from training-fold evidence."""

    def __init__(
        self,
        adaptive: bool = True,
        categorical_min_frequency: float | int | None = None,
    ) -> None:
        self.adaptive = adaptive
        self.categorical_min_frequency = categorical_min_frequency

    def fit(self, X: pd.DataFrame, y: Any = None) -> AdaptiveTabularTransformer:
        if not isinstance(X, pd.DataFrame):
            raise TypeError("AdaptiveTabularTransformer expects a pandas DataFrame")
        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        configured = set(X.attrs.get("categorical_columns", []))
        numeric = list(X.select_dtypes(include=["number"]).columns)
        categorical = [
            column for column in X.columns if column not in numeric or column in configured
        ]
        numeric = [column for column in X.columns if column not in categorical]
        self.numeric_columns_ = numeric
        self.categorical_columns_ = categorical
        self.profile_ = profile_dataset(X, y)
        robust = self.adaptive and self.profile_.numeric_outlier_fraction >= 0.05
        scaler: Any = RobustScaler() if robust else StandardScaler()
        numeric_pipeline = Pipeline(
            [("imputer", SimpleImputer(strategy="median")), ("scaler", scaler)]
        )
        min_frequency = self.categorical_min_frequency
        if min_frequency is None and self.adaptive and self.profile_.high_cardinality_fraction > 0:
            min_frequency = 0.01
        categorical_pipeline = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "onehot",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        min_frequency=min_frequency,
                        sparse_output=False,
                    ),
                ),
            ]
        )
        self.preprocessor_ = ColumnTransformer(
            [
                ("numeric", numeric_pipeline, numeric),
                ("categorical", categorical_pipeline, categorical),
            ],
            remainder="drop",
            verbose_feature_names_out=False,
        )
        self.preprocessor_.fit(X, y)
        self.numeric_scaler_ = scaler
        self.policy_ = {
            "numeric_scaler": "robust" if robust else "standard",
            "categorical_min_frequency": min_frequency,
            "profile": self.profile_.to_dict(),
        }
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        self._check_fitted()
        if not isinstance(X, pd.DataFrame):
            raise TypeError("AdaptiveTabularTransformer expects a pandas DataFrame")
        return np.asarray(
            self.preprocessor_.transform(X.loc[:, self.feature_names_in_]), dtype=float
        )

    def transform_numeric(self, X: pd.DataFrame) -> np.ndarray:
        """Return cleaned/scaled numeric values for the nonlinear view."""

        self._check_fitted()
        if not self.numeric_columns_:
            return np.empty((len(X), 0), dtype=float)
        numeric_pipeline = self.preprocessor_.named_transformers_["numeric"]
        return np.asarray(numeric_pipeline.transform(X.loc[:, self.numeric_columns_]), dtype=float)

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        self._check_fitted()
        return self.preprocessor_.get_feature_names_out()

    def _check_fitted(self) -> None:
        if not hasattr(self, "preprocessor_"):
            raise RuntimeError("AdaptiveTabularTransformer must be fitted first")
