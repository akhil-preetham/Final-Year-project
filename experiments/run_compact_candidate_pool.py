"""Evaluate a compact model pool with shared folds and leakage-safe ensembles."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    StackingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from cardiodiag.evaluation import evaluate_predictions
from cardiodiag.preprocessing import TrainingOnlyCleaner, make_tabular_preprocessor
from cardiodiag.provenance import collect_provenance


def _available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _candidate_specs(seed: int, include_local: bool) -> dict[str, tuple[Any, dict[str, list[Any]]]]:
    specs: dict[str, tuple[Any, dict[str, list[Any]]]] = {
        "logistic": (
            LogisticRegression(max_iter=1500, class_weight="balanced", random_state=seed),
            {"model__C": [0.1, 1.0, 10.0]},
        ),
        "elastic_net": (
            LogisticRegression(
                penalty="elasticnet",
                solver="saga",
                max_iter=2000,
                class_weight="balanced",
                random_state=seed,
            ),
            {"model__C": [0.1, 1.0], "model__l1_ratio": [0.2, 0.8]},
        ),
        "random_forest": (
            RandomForestClassifier(
                n_estimators=200, n_jobs=1, class_weight="balanced", random_state=seed
            ),
            {"model__max_depth": [None, 16], "model__min_samples_leaf": [1, 3]},
        ),
        "extra_trees": (
            ExtraTreesClassifier(
                n_estimators=200, n_jobs=1, class_weight="balanced", random_state=seed
            ),
            {"model__max_depth": [None, 16], "model__min_samples_leaf": [1, 3]},
        ),
        "hist_gradient_boosting": (
            HistGradientBoostingClassifier(random_state=seed),
            {
                "model__learning_rate": [0.04, 0.08],
                "model__max_iter": [150],
                "model__max_leaf_nodes": [15, 31],
                "model__min_samples_leaf": [30],
            },
        ),
        "gaussian_nb": (GaussianNB(), {"model__var_smoothing": [1e-9, 1e-8]}),
        "lda": (LinearDiscriminantAnalysis(), {}),
    }
    if include_local:
        specs["rbf_svm"] = (
            SVC(C=1.0, kernel="rbf", probability=True, random_state=seed),
            {"model__C": [0.5, 2.0], "model__gamma": ["scale", 0.1]},
        )
        specs["knn"] = (
            KNeighborsClassifier(),
            {"model__n_neighbors": [5, 15], "model__weights": ["uniform", "distance"]},
        )
    if _available("xgboost"):
        from xgboost import XGBClassifier

        specs["xgboost"] = (
            XGBClassifier(
                n_estimators=250,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                eval_metric="logloss",
                n_jobs=1,
                random_state=seed,
            ),
            {"model__max_depth": [3, 5], "model__min_child_weight": [1, 5]},
        )
    if _available("lightgbm"):
        from lightgbm import LGBMClassifier

        specs["lightgbm"] = (
            LGBMClassifier(
                n_estimators=250,
                learning_rate=0.05,
                verbosity=-1,
                n_jobs=1,
                random_state=seed,
            ),
            {"model__num_leaves": [15, 31], "model__min_child_samples": [30]},
        )
    if _available("catboost"):
        from catboost import CatBoostClassifier

        specs["catboost"] = (
            CatBoostClassifier(
                iterations=250,
                learning_rate=0.05,
                loss_function="Logloss",
                verbose=False,
                thread_count=1,
                random_seed=seed,
            ),
            {"model__depth": [4, 6], "model__l2_leaf_reg": [3.0]},
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
            ("cleaner", TrainingOnlyCleaner(categorical_columns=tuple(categorical))),
            ("preprocessor", make_tabular_preprocessor(numeric, categorical)),
            ("model", model),
        ]
    )


def _metrics(y: pd.Series, probabilities: np.ndarray) -> dict[str, Any]:
    result = evaluate_predictions(y.to_numpy(), probabilities)
    result["log_loss"] = float(log_loss(y, probabilities, labels=[0, 1]))
    return result


def _fit_candidate(
    X: pd.DataFrame,
    y: pd.Series,
    outer: list[tuple[np.ndarray, np.ndarray]],
    model: Any,
    grid: dict[str, list[Any]],
) -> tuple[dict[str, Any], np.ndarray]:
    predictions = np.full(len(y), np.nan)
    folds = []
    started_model = time.perf_counter()
    for fold, (train, test) in enumerate(outer):
        search = GridSearchCV(
            _pipeline(X.iloc[train], model),
            grid,
            scoring="roc_auc",
            cv=2,
            n_jobs=1,
            refit=True,
            error_score="raise",
        )
        started = time.perf_counter()
        search.fit(X.iloc[train], y.iloc[train])
        probabilities = search.predict_proba(X.iloc[test])[:, 1]
        predictions[test] = probabilities
        folds.append(
            {
                "fold": fold,
                "train_n": len(train),
                "test_n": len(test),
                "best_params": search.best_params_,
                "inner_best_score": float(search.best_score_),
                "fit_seconds": time.perf_counter() - started,
                "metrics": _metrics(y.iloc[test], probabilities),
            }
        )
    return (
        {
            "status": "completed",
            "folds": folds,
            "pooled_outer_metrics": _metrics(y, predictions),
            "mean_metrics": {
                key: float(np.mean([f["metrics"][key] for f in folds]))
                for key in ("roc_auc", "pr_auc", "brier", "ece_uniform", "log_loss")
            },
            "total_seconds": time.perf_counter() - started_model,
        },
        predictions,
    )


def _fit_stacking(
    X: pd.DataFrame,
    y: pd.Series,
    outer: list[tuple[np.ndarray, np.ndarray]],
    specs: dict[str, tuple[Any, dict[str, list[Any]]]],
) -> tuple[dict[str, Any], np.ndarray]:
    member_names = [name for name in ("catboost", "xgboost", "logistic") if name in specs]
    predictions = np.full(len(y), np.nan)
    folds = []
    started_model = time.perf_counter()
    for fold, (train, test) in enumerate(outer):
        members = [
            (name, clone(specs[name][0]))
            for name in member_names
        ]
        stack = _pipeline(
            X.iloc[train],
            StackingClassifier(
                estimators=members,
                final_estimator=LogisticRegression(C=1.0, max_iter=1000),
                cv=2,
                stack_method="predict_proba",
                n_jobs=1,
            ),
        )
        started = time.perf_counter()
        stack.fit(X.iloc[train], y.iloc[train])
        probabilities = stack.predict_proba(X.iloc[test])[:, 1]
        predictions[test] = probabilities
        folds.append(
            {
                "fold": fold,
                "train_n": len(train),
                "test_n": len(test),
                "members": member_names,
                "fit_seconds": time.perf_counter() - started,
                "metrics": _metrics(y.iloc[test], probabilities),
            }
        )
    return (
        {
            "status": "completed",
            "members": member_names,
            "training_protocol": "outer-training OOF base predictions with inner cv=2",
            "folds": folds,
            "pooled_outer_metrics": _metrics(y, predictions),
            "mean_metrics": {
                key: float(np.mean([f["metrics"][key] for f in folds]))
                for key in ("roc_auc", "pr_auc", "brier", "ece_uniform", "log_loss")
            },
            "total_seconds": time.perf_counter() - started_model,
        },
        predictions,
    )


def run(dataset: Path, target: str, output: Path, seed: int = 42) -> dict[str, Any]:
    X, y = load_dataset(dataset, target)
    X, dropped = drop_identifier_columns(X)
    include_local = len(X) <= 5000
    outer = list(StratifiedKFold(n_splits=3, shuffle=True, random_state=seed).split(X, y))
    specs = _candidate_specs(seed, include_local)
    records: dict[str, Any] = {}
    predictions: dict[str, np.ndarray] = {}
    for name, (model, grid) in specs.items():
        try:
            records[name], predictions[name] = _fit_candidate(X, y, outer, model, grid)
        except Exception as error:
            records[name] = {"status": "failed", "error": f"{type(error).__name__}: {error}"}

    skipped = {}
    if not include_local:
        skipped = {
            "rbf_svm": (
                "Skipped above 5000 rows: kernel probability fitting is not "
                "computationally bounded."
            ),
            "knn": (
                "Skipped above 5000 rows: all-pairs neighbour prediction is "
                "not computationally bounded."
            ),
        }
    ensemble_members = [
        name
        for name in ("catboost", "xgboost", "hist_gradient_boosting", "logistic")
        if name in predictions
    ]
    ensemble_predictions = np.mean([predictions[name] for name in ensemble_members], axis=0)
    records["soft_voting"] = {
        "status": "completed",
        "members": ensemble_members,
        "weights": [1.0 / len(ensemble_members)] * len(ensemble_members),
        "evaluation": "fixed weights on shared outer out-of-fold predictions",
        "pooled_outer_metrics": _metrics(y, ensemble_predictions),
    }
    records["stacking"], stack_predictions = _fit_stacking(X, y, outer, specs)
    records["stacking"]["pooled_outer_metrics"] = _metrics(y, stack_predictions)
    configuration = {
        "stage": "compact_candidate_pool",
        "outer_splits": 3,
        "inner_splits": 2,
        "seed": seed,
        "scoring": "roc_auc",
        "local_models_included": include_local,
        "models_requested": list(specs),
        "skipped_models": skipped,
    }
    result = {
        "status": "completed",
        "dataset": str(dataset),
        "target": target,
        "dropped_identifier_columns": dropped,
        "dataset_summary": summarize_dataset(dataset, target).to_dict(),
        "configuration": configuration,
        "models": records,
        "provenance": collect_provenance(dataset, target, "compact_candidate_pool", configuration),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run(args.dataset, args.target, args.output, args.seed)
    print(f"Wrote compact candidate pool to {args.output} ({len(result['models'])} records)")


if __name__ == "__main__":
    main()
