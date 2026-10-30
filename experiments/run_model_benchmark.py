"""Run a bounded, leakage-controlled model benchmark on one dataset."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline

from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from cardiodiag.evaluation import evaluate_predictions
from cardiodiag.preprocessing import TrainingOnlyCleaner, make_tabular_preprocessor
from cardiodiag.provenance import collect_provenance


def _xgboost_available() -> bool:
    return importlib.util.find_spec("xgboost") is not None


def _candidate_specs(seed: int) -> dict[str, tuple[Any, dict[str, list[Any]]]]:
    specs: dict[str, tuple[Any, dict[str, list[Any]]]] = {
        "dummy": (
            DummyClassifier(strategy="prior"),
            {"model__strategy": ["prior"]},
        ),
        "logistic": (
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed),
            {"model__C": [1.0]},
        ),
        "lda": (LinearDiscriminantAnalysis(), {}),
        "gaussian_nb": (GaussianNB(), {"model__var_smoothing": [1e-9, 1e-8]}),
        "random_forest": (
            RandomForestClassifier(
                n_estimators=150, n_jobs=1, class_weight="balanced", random_state=seed
            ),
            {"model__max_depth": [None, 12]},
        ),
        "extra_trees": (
            ExtraTreesClassifier(
                n_estimators=150, n_jobs=1, class_weight="balanced", random_state=seed
            ),
            {"model__max_depth": [None, 12]},
        ),
        "hist_gradient_boosting": (
            HistGradientBoostingClassifier(random_state=seed),
            {"model__max_iter": [100], "model__max_leaf_nodes": [15, 31]},
        ),
        "gradient_boosting": (
            GradientBoostingClassifier(random_state=seed),
            {"model__n_estimators": [100], "model__max_depth": [2, 3]},
        ),
        "adaboost": (
            AdaBoostClassifier(random_state=seed),
            {"model__n_estimators": [100], "model__learning_rate": [0.05, 0.1]},
        ),
        "mlp": (
            MLPClassifier(
                hidden_layer_sizes=(64,),
                max_iter=100,
                early_stopping=True,
                random_state=seed,
            ),
            {"model__alpha": [1e-4, 1e-3]},
        ),
    }
    if _xgboost_available():
        from xgboost import XGBClassifier

        specs["xgboost"] = (
            XGBClassifier(
                n_estimators=150,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                eval_metric="logloss",
                n_jobs=1,
                random_state=seed,
            ),
            {"model__max_depth": [3, 4]},
        )
    return specs


def _pipeline(X: pd.DataFrame, model: Any) -> Pipeline:
    categorical = list(X.attrs.get("categorical_columns", []))
    numeric = list(X.attrs.get("numeric_columns", []))
    if not categorical and not numeric:
        numeric = X.select_dtypes(include=["number"]).columns.tolist()
        categorical = [column for column in X.columns if column not in numeric]
    return Pipeline(
        [
            (
                "cleaner",
                TrainingOnlyCleaner(categorical_columns=tuple(categorical)),
            ),
            ("preprocessor", make_tabular_preprocessor(numeric, categorical)),
            ("model", model),
        ]
    )


def run_benchmark(
    dataset: Path,
    target: str,
    output: Path,
    stage: str,
    sample_size: int | None,
    outer_splits: int,
    inner_splits: int,
    seed: int,
) -> dict[str, Any]:
    X, y = load_dataset(dataset, target)
    X, dropped = drop_identifier_columns(X)
    if sample_size is not None and sample_size < len(X):
        rng = np.random.default_rng(seed)
        positions = np.sort(rng.choice(len(X), size=sample_size, replace=False))
        X = X.iloc[positions]
        y = y.iloc[positions]
    specs = _candidate_specs(seed)
    outer = StratifiedKFold(n_splits=outer_splits, shuffle=True, random_state=seed)
    records: list[dict[str, Any]] = []
    skipped: dict[str, str] = {}
    for name, (model, grid) in specs.items():
        fold_records: list[dict[str, Any]] = []
        started_model = time.perf_counter()
        try:
            for fold, (train, test) in enumerate(outer.split(X, y)):
                estimator = _pipeline(X.iloc[train], model)
                search = GridSearchCV(
                    estimator,
                    grid,
                    scoring="roc_auc",
                    cv=inner_splits,
                    n_jobs=1,
                    refit=True,
                    error_score="raise",
                )
                started = time.perf_counter()
                search.fit(X.iloc[train], y.iloc[train])
                fit_seconds = time.perf_counter() - started
                probabilities = search.predict_proba(X.iloc[test])[:, 1]
                metrics = evaluate_predictions(y.iloc[test].to_numpy(), probabilities)
                metrics["roc_auc"] = float(roc_auc_score(y.iloc[test], probabilities))
                metrics["pr_auc"] = float(average_precision_score(y.iloc[test], probabilities))
                fold_records.append(
                    {
                        "fold": fold,
                        "train_n": len(train),
                        "test_n": len(test),
                        "best_params": search.best_params_,
                        "inner_best_score": float(search.best_score_),
                        "fit_seconds": fit_seconds,
                        "metrics": metrics,
                    }
                )
            records.append(
                {
                    "model": name,
                    "status": "completed",
                    "folds": fold_records,
                    "mean_metrics": {
                        key: float(np.mean([f["metrics"][key] for f in fold_records]))
                        for key in ("roc_auc", "pr_auc", "brier", "ece_uniform")
                    },
                    "total_seconds": time.perf_counter() - started_model,
                }
            )
        except Exception as error:
            skipped[name] = f"{type(error).__name__}: {error}"
    configuration = {
        "stage": stage,
        "sample_size": sample_size,
        "outer_splits": outer_splits,
        "inner_splits": inner_splits,
        "seed": seed,
        "scoring": "roc_auc",
        "models_requested": list(specs),
    }
    result = {
        "status": "completed",
        "dataset": str(dataset),
        "target": target,
        "dropped_identifier_columns": dropped,
        "dataset_summary": summarize_dataset(dataset, target).to_dict(),
        "configuration": configuration,
        "models": records,
        "skipped_models": skipped,
        "provenance": collect_provenance(
            dataset, target, "model_benchmark", configuration
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stage", choices=("screening", "primary"), default="screening")
    parser.add_argument("--sample-size", type=int, default=10000)
    parser.add_argument("--outer-splits", type=int, default=3)
    parser.add_argument("--inner-splits", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run_benchmark(
        args.dataset,
        args.target,
        args.output,
        args.stage,
        args.sample_size,
        args.outer_splits,
        args.inner_splits,
        args.seed,
    )
    print(f"Wrote benchmark to {args.output}")


if __name__ == "__main__":
    main()
