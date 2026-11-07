"""Audit feature-distribution shift without making cross-dataset claims."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATASETS = {
    "heart5": (Path("heart5.csv"), "HeartDisease"),
    "mendeley": (Path("MendeleyCardiovascular_Disease_Dataset.csv"), "target"),
    "cardiovascular_70k": (
        Path("data/kaggle_cardiovascular_70k/cardio_train.csv"),
        "cardio",
    ),
}

PAIRWISE_FEATURES = {
    ("heart5", "mendeley"): {
        "Age": ("age", "numeric"),
        "Sex": ("gender", "categorical"),
        "ChestPainType": ("chestpain", "categorical"),
        "RestingBP": ("restingBP", "numeric"),
        "Cholesterol": ("serumcholestrol", "numeric"),
        "FastingBS": ("fastingbloodsugar", "categorical"),
        "RestingECG": ("restingrelectro", "categorical"),
        "MaxHR": ("maxheartrate", "numeric"),
        "ExerciseAngina": ("exerciseangia", "categorical"),
        "Oldpeak": ("oldpeak", "numeric"),
        "ST_Slope": ("slope", "categorical"),
    },
    ("heart5", "cardiovascular_70k"): {
        "Age": ("age", "age_days_to_years"),
        "Sex": ("gender", "categorical"),
    },
    ("mendeley", "cardiovascular_70k"): {
        "age": ("age", "age_days_to_years"),
        "gender": ("gender", "categorical"),
    },
}


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=None, engine="python")


def _psi(left: pd.Series, right: pd.Series, bins: int = 10) -> float:
    values = pd.concat([left, right]).astype(float)
    edges = np.unique(np.quantile(values, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    left_counts = np.histogram(left, bins=edges)[0].astype(float)
    right_counts = np.histogram(right, bins=edges)[0].astype(float)
    left_share = (left_counts + 1e-6) / (left_counts.sum() + 1e-6 * len(left_counts))
    right_share = (right_counts + 1e-6) / (right_counts.sum() + 1e-6 * len(right_counts))
    return float(np.sum((right_share - left_share) * np.log(right_share / left_share)))


def _numeric_summary(left: pd.Series, right: pd.Series) -> dict[str, float]:
    left = pd.to_numeric(left, errors="coerce")
    right = pd.to_numeric(right, errors="coerce")
    left = left.dropna()
    right = right.dropna()
    pooled_sd = np.sqrt((left.var(ddof=1) + right.var(ddof=1)) / 2)
    return {
        "source_mean": float(left.mean()),
        "target_mean": float(right.mean()),
        "standardized_mean_difference": float(
            (right.mean() - left.mean()) / pooled_sd if pooled_sd > 0 else 0.0
        ),
        "ks_statistic": float(ks_2samp(left, right).statistic),
        "ks_p_value": float(ks_2samp(left, right).pvalue),
        "psi": _psi(left, right),
    }


def _categorical_summary(left: pd.Series, right: pd.Series) -> dict[str, object]:
    left = left.astype("string").fillna("<missing>")
    right = right.astype("string").fillna("<missing>")
    categories = sorted(set(left) | set(right))
    left_share = left.value_counts(normalize=True).reindex(categories, fill_value=0)
    right_share = right.value_counts(normalize=True).reindex(categories, fill_value=0)
    left_safe = left_share + 1e-6
    right_safe = right_share + 1e-6
    return {
        "categories": categories,
        "source_share": left_share.to_dict(),
        "target_share": right_share.to_dict(),
        "psi": float(np.sum((right_safe - left_safe) * np.log(right_safe / left_safe))),
    }


def _domain_auc(
    source: pd.DataFrame,
    target: pd.DataFrame,
    numeric: list[str],
    categorical: list[str],
) -> float:
    combined = pd.concat([source, target], ignore_index=True)
    labels = np.r_[np.zeros(len(source)), np.ones(len(target))]
    combined[categorical] = combined[categorical].astype("string")
    transformer = ColumnTransformer(
        [
            ("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric),
            (
                "categorical",
                make_pipeline(
                    SimpleImputer(strategy="most_frequent"),
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ),
                categorical,
            ),
        ]
    )
    model = make_pipeline(transformer, LogisticRegression(max_iter=1000, random_state=42))
    scores = cross_val_score(
        model,
        combined,
        labels,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring="roc_auc",
    )
    return float(np.mean(scores))


def main() -> None:
    output = Path("results/generated/dataset_shift.json")
    loaded = {name: _read(path) for name, (path, _) in DATASETS.items()}
    result: dict[str, object] = {
        "protocol": "distribution-only shift audit; labels excluded from all calculations",
        "datasets": {
            name: {
                "path": str(path),
                "rows": int(len(loaded[name])),
                "target": target,
                "missing_cells": int(loaded[name].isna().sum().sum()),
            }
            for name, (path, target) in DATASETS.items()
        },
        "pairs": {},
        "interpretation": [
            (
                "PSI, KS, standardized mean differences, missingness, and domain AUC "
                "describe covariate shift only."
            ),
            (
                "They do not establish label shift or concept shift because target "
                "relationships are not compared."
            ),
            (
                "Feature mappings to the 70K dataset are intentionally narrow and "
                "are not approved for predictive transfer."
            ),
        ],
    }
    for (source_name, target_name), mapping in PAIRWISE_FEATURES.items():
        source = loaded[source_name].copy()
        target = loaded[target_name].copy()
        source_view = pd.DataFrame(index=source.index)
        target_view = pd.DataFrame(index=target.index)
        numeric: list[str] = []
        categorical: list[str] = []
        summaries: dict[str, object] = {}
        for source_column, (target_column, kind) in mapping.items():
            source_values = source[source_column]
            target_values = target[target_column]
            if kind == "age_days_to_years":
                if target_name == "cardiovascular_70k":
                    target_values = pd.to_numeric(target_values, errors="coerce") / 365.25
                source_values = pd.to_numeric(source_values, errors="coerce")
                kind = "numeric"
            source_view[source_column] = source_values
            target_view[source_column] = target_values
            if kind == "numeric":
                numeric.append(source_column)
                summaries[source_column] = _numeric_summary(source_values, target_values)
            else:
                categorical.append(source_column)
                summaries[source_column] = _categorical_summary(source_values, target_values)
        result["pairs"][f"{source_name}_to_{target_name}"] = {
            "features": mapping,
            "feature_summaries": summaries,
            "missingness_shift": {
                column: {
                    "source_rate": float(source_view[column].isna().mean()),
                    "target_rate": float(target_view[column].isna().mean()),
                }
                for column in mapping
            },
            "domain_classifier_auc": _domain_auc(source_view, target_view, numeric, categorical),
            "predictive_transfer_authorized": False,
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote distribution-shift audit to {output}")


if __name__ == "__main__":
    main()
