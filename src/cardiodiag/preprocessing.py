"""Training-only preprocessing for mixed clinical tabular data."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class TrainingOnlyCleaner(BaseEstimator, TransformerMixin):
    """Impute and optionally replace numeric outliers using training data only.

    The transformer deliberately does not use ``y``. This prevents the target-aware
    class-specific imputation used in the historical notebook from entering the
    corrected prediction pipeline.
    """

    def __init__(
        self,
        lower_quantile: float = 0.01,
        upper_quantile: float = 0.99,
        outlier_strategy: str = "median",
        categorical_columns: list[str] | tuple[str, ...] | None = None,
    ) -> None:
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile
        self.outlier_strategy = outlier_strategy
        self.categorical_columns = categorical_columns

    def fit(self, X: pd.DataFrame, y: object = None) -> TrainingOnlyCleaner:
        if not isinstance(X, pd.DataFrame):
            raise TypeError("TrainingOnlyCleaner expects a pandas DataFrame")
        if not 0 <= self.lower_quantile < self.upper_quantile <= 1:
            raise ValueError("Quantiles must satisfy 0 <= lower < upper <= 1")
        if self.outlier_strategy not in {"median", "clip", "none"}:
            raise ValueError("outlier_strategy must be 'median', 'clip', or 'none'")

        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        configured_categorical = set(self.categorical_columns or ())
        missing_categorical = configured_categorical - set(X.columns)
        if missing_categorical:
            raise ValueError(
                "Configured categorical columns are missing: "
                f"{sorted(missing_categorical)}"
            )
        self.categorical_columns_ = [
            column
            for column in X.columns
            if column in configured_categorical or not np.issubdtype(X[column].dtype, np.number)
        ]
        self.numeric_columns_ = [
            column for column in X.columns if column not in self.categorical_columns_
        ]
        numeric = X[self.numeric_columns_].apply(pd.to_numeric, errors="coerce")
        self.numeric_medians_ = numeric.median().fillna(0.0)
        self.lower_bounds_ = numeric.quantile(self.lower_quantile).fillna(self.numeric_medians_)
        self.upper_bounds_ = numeric.quantile(self.upper_quantile).fillna(self.numeric_medians_)
        self.categorical_modes_ = {
            column: X[column].mode(dropna=True).iloc[0] if X[column].notna().any() else "missing"
            for column in self.categorical_columns_
        }
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        self._check_is_fitted()
        if not isinstance(X, pd.DataFrame):
            raise TypeError("TrainingOnlyCleaner expects a pandas DataFrame")
        missing = set(self.feature_names_in_) - set(X.columns)
        if missing:
            raise ValueError(f"Input is missing fitted columns: {sorted(missing)}")
        result = X.loc[:, self.feature_names_in_].copy()
        for column in self.numeric_columns_:
            values = pd.to_numeric(result[column], errors="coerce")
            values = values.fillna(self.numeric_medians_[column])
            if self.outlier_strategy == "median":
                mask = (values < self.lower_bounds_[column]) | (values > self.upper_bounds_[column])
                values = values.mask(mask, self.numeric_medians_[column])
            elif self.outlier_strategy == "clip":
                values = values.clip(self.lower_bounds_[column], self.upper_bounds_[column])
            result[column] = values
        for column in self.categorical_columns_:
            result[column] = result[column].fillna(self.categorical_modes_[column]).astype(object)
        return result

    def get_feature_names_out(self, input_features: Iterable[str] | None = None) -> np.ndarray:
        self._check_is_fitted()
        return np.asarray(self.feature_names_in_, dtype=object)

    def _check_is_fitted(self) -> None:
        if not hasattr(self, "feature_names_in_"):
            raise RuntimeError("TrainingOnlyCleaner must be fitted before transform")


def make_tabular_preprocessor(
    numeric_columns: list[str], categorical_columns: list[str]
) -> ColumnTransformer:
    """Build a deterministic mixed-type transformer for a fitted training fold."""

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
