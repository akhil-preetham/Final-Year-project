"""Leakage-safe clinical tabular dataset profiling."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ClinicalDatasetProfile:
    """Descriptive profile computed only from the supplied training partition."""

    n_rows: int
    n_features: int
    numeric_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    missing_fraction: float
    missing_feature_fraction: float
    duplicate_row_fraction: float
    class_prevalence: float | None
    imbalance_ratio: float | None
    high_cardinality_fraction: float
    outlier_fraction: float
    mean_abs_skewness: float
    redundant_pair_fraction: float
    constant_feature_fraction: float
    profile_version: str = "clin-adapt-profile-v1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def vector(self) -> np.ndarray:
        """Return numeric meta-features for future task-level routing."""

        return np.asarray(
            [
                self.n_rows,
                self.n_features,
                self.missing_fraction,
                self.missing_feature_fraction,
                self.duplicate_row_fraction,
                self.class_prevalence if self.class_prevalence is not None else 0.5,
                self.imbalance_ratio if self.imbalance_ratio is not None else 1.0,
                self.high_cardinality_fraction,
                self.outlier_fraction,
                self.mean_abs_skewness,
                self.redundant_pair_fraction,
                self.constant_feature_fraction,
            ],
            dtype=float,
        )


def profile_clinical_dataset(
    X: pd.DataFrame,
    y: pd.Series | np.ndarray | None = None,
    categorical_columns: list[str] | tuple[str, ...] | None = None,
) -> ClinicalDatasetProfile:
    """Profile one training partition without using external rows or labels.

    ``categorical_columns`` is explicit because integer-coded clinical fields
    must not be treated as continuous merely because of storage dtype.
    """

    if not isinstance(X, pd.DataFrame) or X.shape[1] == 0:
        raise ValueError("X must be a non-empty pandas DataFrame")
    configured = set(categorical_columns or X.attrs.get("categorical_columns", ()))
    numeric = tuple(
        column
        for column in X.columns
        if column not in configured and pd.api.types.is_numeric_dtype(X[column])
    )
    categorical = tuple(column for column in X.columns if column not in numeric)
    missing_by_feature = X.isna().mean()
    high_cardinality = [
        column
        for column in categorical
        if X[column].nunique(dropna=True) > max(20, int(0.05 * len(X)))
    ]
    outlier_rates: list[float] = []
    skewness: list[float] = []
    constant = 0
    for column in numeric:
        values = pd.to_numeric(X[column], errors="coerce").dropna().to_numpy(float)
        if np.unique(values).size <= 1:
            constant += 1
        if values.size:
            q1, q3 = np.quantile(values, [0.25, 0.75])
            iqr = q3 - q1
            outlier_rates.append(
                float(np.mean((values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)))
                if iqr
                else 0.0
            )
            skewness.append(float(pd.Series(values).skew()) if values.size > 2 else 0.0)
    redundant = 0.0
    if len(numeric) > 1:
        corr = X[list(numeric)].apply(pd.to_numeric, errors="coerce").corr().abs().to_numpy()
        upper = corr[np.triu_indices(len(numeric), k=1)]
        redundant = float(np.mean(upper >= 0.95)) if upper.size else 0.0
    prevalence: float | None = None
    imbalance: float | None = None
    if y is not None:
        labels = np.asarray(y, dtype=int)
        if labels.size != len(X) or np.unique(labels).size != 2:
            raise ValueError("y must align with X and contain both binary classes")
        counts = np.bincount(labels, minlength=2)
        prevalence = float(counts[1] / counts.sum())
        imbalance = float(counts.max() / counts.min())
    return ClinicalDatasetProfile(
        n_rows=int(len(X)),
        n_features=int(X.shape[1]),
        numeric_features=numeric,
        categorical_features=categorical,
        missing_fraction=float(X.isna().to_numpy(dtype=float).mean()),
        missing_feature_fraction=float(np.mean(missing_by_feature > 0)),
        duplicate_row_fraction=float(X.duplicated().mean()),
        class_prevalence=prevalence,
        imbalance_ratio=imbalance,
        high_cardinality_fraction=float(len(high_cardinality) / max(1, len(categorical))),
        outlier_fraction=float(np.mean(outlier_rates)) if outlier_rates else 0.0,
        mean_abs_skewness=float(np.mean(np.abs(skewness))) if skewness else 0.0,
        redundant_pair_fraction=redundant,
        constant_feature_fraction=float(constant / max(1, len(numeric))),
    )
