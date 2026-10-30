"""Tune priority tabular models and evaluate a prespecified OOF ensemble."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline

from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from cardiodiag.evaluation import evaluate_predictions
from cardiodiag.preprocessing import TrainingOnlyCleaner, make_tabular_preprocessor
from cardiodiag.provenance import collect_provenance


def _available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _models(seed: int) -> dict[str, tuple[Any, dict[str, list[Any]]]]:
    models: dict[str, tuple[Any, dict[str, list[Any]]]] = {
        "logistic": (
            LogisticRegression(max_iter=1500, class_weight="balanced", random_state=seed),
            {"model__C": [0.1, 1.0, 10.0]},
        ),
        "random_forest": (
            RandomForestClassifier(
                n_estimators=250, n_jobs=1, class_weight="balanced", random_state=seed
            ),
            {
                "model__max_depth": [None, 16],
                "model__min_samples_leaf": [1, 3],
                "model__max_features": ["sqrt"],
            },
        ),
        "hist_gradient_boosting": (
            HistGradientBoostingClassifier(random_state=seed),
            {
                "model__learning_rate": [0.04, 0.08],
                "model__max_iter": [200],
                "model__max_leaf_nodes": [15, 31],
                "model__min_samples_leaf": [30],
                "model__l2_regularization": [0.0, 1.0],
            },
        ),
    }
    if _available("xgboost"):
        from xgboost import XGBClassifier

        models["xgboost"] = (
            XGBClassifier(
                n_estimators=300,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                eval_metric="logloss",
                n_jobs=1,
                random_state=seed,
            ),
            {
                "model__max_depth": [3, 5],
                "model__min_child_weight": [1, 5],
                "model__gamma": [0.0],
                "model__reg_lambda": [1.0],
            },
        )
    if _available("lightgbm"):
        from lightgbm import LGBMClassifier

        models["lightgbm"] = (
            LGBMClassifier(
                n_estimators=300,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                verbosity=-1,
                n_jobs=1,
                random_state=seed,
            ),
            {
                "model__num_leaves": [15, 31],
                "model__max_depth": [-1],
                "model__min_child_samples": [30],
                "model__reg_lambda": [0.0],
            },
        )
    if _available("catboost"):
        from catboost import CatBoostClassifier

        models["catboost"] = (
            CatBoostClassifier(
                iterations=300,
                learning_rate=0.05,
                loss_function="Logloss",
                verbose=False,
                thread_count=1,
                random_seed=seed,
            ),
            {
                "model__depth": [4, 6],
                "model__l2_leaf_reg": [3.0],
                "model__random_strength": [0.0],
            },
        )
    return models


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


def run(dataset: Path, target: str, output: Path, seed: int = 42) -> dict[str, Any]:
    X, y = load_dataset(dataset, target)
    X, dropped = drop_identifier_columns(X)
    outer = list(
        StratifiedKFold(n_splits=3, shuffle=True, random_state=seed).split(X, y)
    )
    models = _models(seed)
    records: dict[str, Any] = {}
    outer_predictions: dict[str, np.ndarray] = {}
    for name, (model, grid) in models.items():
        folds: list[dict[str, Any]] = []
        predictions = np.full(len(y), np.nan)
        started_model = time.perf_counter()
        for fold, (train, test) in enumerate(outer):
            pipeline = _pipeline(X.iloc[train], model)
            search = GridSearchCV(
                pipeline,
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
                    "metrics": evaluate_predictions(y.iloc[test].to_numpy(), probabilities),
                }
            )
        pooled = evaluate_predictions(y.to_numpy(), predictions)
        records[name] = {
            "status": "completed",
            "folds": folds,
            "pooled_outer_metrics": pooled,
            "mean_metrics": {
                key: float(np.mean([f["metrics"][key] for f in folds]))
                for key in ("roc_auc", "pr_auc", "brier", "ece_uniform")
            },
            "total_seconds": time.perf_counter() - started_model,
        }
        outer_predictions[name] = predictions

    ensemble_members = [
        name
        for name in ("xgboost", "hist_gradient_boosting", "logistic")
        if name in outer_predictions
    ]
    ensemble_probabilities = np.mean(
        [outer_predictions[name] for name in ensemble_members], axis=0
    )
    ensemble_metrics = evaluate_predictions(y.to_numpy(), ensemble_probabilities)
    configuration = {
        "stage": "tuned_priority_models_and_prespecified_oof_ensemble",
        "outer_splits": 3,
        "inner_splits": 2,
        "seed": seed,
        "scoring": "roc_auc",
        "ensemble_members": ensemble_members,
        "ensemble_weights": [1.0 / len(ensemble_members)] * len(ensemble_members),
        "models_requested": list(models),
    }
    result = {
        "status": "completed",
        "dataset": str(dataset),
        "target": target,
        "dropped_identifier_columns": dropped,
        "dataset_summary": summarize_dataset(dataset, target).to_dict(),
        "configuration": configuration,
        "models": records,
        "ensemble": {
            "status": "completed",
            "evaluation": "outer out-of-fold predictions on identical shared folds",
            "metrics": ensemble_metrics,
        },
        "provenance": collect_provenance(
            dataset, target, "tuned_models_and_oof_ensemble", configuration
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
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run(args.dataset, args.target, args.output, args.seed)
    print(
        f"Wrote {len(result['models'])} tuned models and ensemble to {args.output}"
    )


if __name__ == "__main__":
    main()
