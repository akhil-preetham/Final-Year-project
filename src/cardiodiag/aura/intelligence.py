"""Training-fold dataset intelligence for AURA-ML.

The profile is descriptive rather than a predictor.  It is computed on the
currently available training rows only and is therefore safe to use inside an
outer fold.  Target-derived quantities are optional and must be computed from
training labels by the caller.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DatasetProfile:
    """Compact profile used to select preprocessing and representation policy."""

    n_rows: int
    n_features: int
    numeric_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    missing_fraction: float
    high_cardinality_fraction: float
    numeric_outlier_fraction: float
    numeric_skewness: float
    redundant_pair_fraction: float
    sample_feature_ratio: float
    class_prevalence: float | None
    imbalance_ratio: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def profile_dataset(
    X: pd.DataFrame,
    y: pd.Series | np.ndarray | None = None,
    correlation_threshold: float = 0.95,
) -> DatasetProfile:
    """Profile a pandas table without inspecting rows outside ``X``.

    Numeric/categorical roles are taken from the dataframe dtypes.  Callers
    using coded categorical columns should attach the repository's explicit
    schema or pass those columns in a normalized dataframe before profiling.
    """

    if not isinstance(X, pd.DataFrame):
        raise TypeError("profile_dataset expects a pandas DataFrame")
    if X.shape[1] == 0:
        raise ValueError("AURA-ML requires at least one feature")
    configured_categorical = set(X.attrs.get("categorical_columns", []))
    numeric = tuple(
        column
        for column in X.select_dtypes(include=["number"]).columns
        if column not in configured_categorical
    )
    categorical = tuple(column for column in X.columns if column not in numeric)
    missing_fraction = float(X.isna().to_numpy(dtype=float).mean())
    high_cardinality = [
        column
        for column in categorical
        if X[column].nunique(dropna=True) > max(20, int(0.05 * len(X)))
    ]

    outlier_rates: list[float] = []
    skewness: list[float] = []
    for column in numeric:
        values = pd.to_numeric(X[column], errors="coerce").dropna().to_numpy(float)
        if values.size == 0:
            continue
        q1, q3 = np.quantile(values, [0.25, 0.75])
        iqr = q3 - q1
        outlier_rates.append(
            float(np.mean((values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)))
            if iqr > 0
            else 0.0
        )
        skewness.append(float(pd.Series(values).skew()) if values.size > 2 else 0.0)

    redundant_fraction = 0.0
    if len(numeric) > 1:
        correlation = X[list(numeric)].apply(pd.to_numeric, errors="coerce").corr().abs()
        upper = correlation.to_numpy()[np.triu_indices(len(numeric), k=1)]
        redundant_fraction = float(np.mean(upper >= correlation_threshold)) if upper.size else 0.0

    prevalence: float | None = None
    imbalance: float | None = None
    if y is not None:
        labels = np.asarray(y, dtype=int)
        if labels.size != len(X):
            raise ValueError("y must have one value per row of X")
        counts = np.bincount(labels, minlength=2)
        if counts.sum() and np.all(counts > 0):
            prevalence = float(counts[1] / counts.sum())
            imbalance = float(counts.max() / counts.min())

    return DatasetProfile(
        n_rows=int(len(X)),
        n_features=int(X.shape[1]),
        numeric_features=numeric,
        categorical_features=categorical,
        missing_fraction=missing_fraction,
        high_cardinality_fraction=float(len(high_cardinality) / max(1, len(categorical))),
        numeric_outlier_fraction=float(np.mean(outlier_rates)) if outlier_rates else 0.0,
        numeric_skewness=float(np.mean(np.abs(skewness))) if skewness else 0.0,
        redundant_pair_fraction=redundant_fraction,
        sample_feature_ratio=float(len(X) / max(1, X.shape[1])),
        class_prevalence=prevalence,
        imbalance_ratio=imbalance,
    )
