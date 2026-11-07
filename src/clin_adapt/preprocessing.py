"""Training-only mixed-type pipelines for CLIN-ADAPT candidates."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from cardiodiag.preprocessing import TrainingOnlyCleaner

from .registry import ModelSpec


def build_clinical_pipeline(X: pd.DataFrame, spec: ModelSpec, seed: int = 42) -> Pipeline:
    """Build a complete candidate pipeline from the training-side schema."""

    categorical = list(X.attrs.get("categorical_columns", ()))
    categorical = [column for column in categorical if column in X.columns]
    numeric = [
        column
        for column in X.columns
        if column not in categorical and pd.api.types.is_numeric_dtype(X[column])
    ]
    fallback_categorical = [
        column for column in X.columns if column not in numeric and column not in categorical
    ]
    categorical.extend(fallback_categorical)
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler() if spec.preprocessing == "scaled" else "passthrough"),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    transformer = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric),
            ("categorical", categorical_pipeline, categorical),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    estimator: Any = spec.build(seed)
    if spec.name == "ridge_classifier":
        estimator = CalibratedClassifierCV(estimator=estimator, method="sigmoid", cv=3)
    return Pipeline(
        steps=[
            (
                "training_only_cleaner",
                TrainingOnlyCleaner(categorical_columns=categorical, outlier_strategy="none"),
            ),
            ("preprocessor", transformer),
            ("model", estimator),
        ]
    )


def copy_schema(source: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    """Copy explicit schema metadata after a pandas row slice."""

    target.attrs = dict(source.attrs)
    return target
