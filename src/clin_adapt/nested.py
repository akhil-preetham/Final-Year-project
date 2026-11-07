"""Leakage-controlled nested validation for the CLIN-ADAPT pilot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from .adaptive_learning import CASLConfig, CASLCoordinator
from .calibration import apply_calibrator, choose_calibration, fit_full_calibrator
from .evaluation import evaluate_binary_predictions
from .parallel_engine import ParallelExecutionEngine
from .preprocessing import build_clinical_pipeline, copy_schema
from .profiling import profile_clinical_dataset
from .registry import ModelSpec
from .resources import detect_runtime_resources


@dataclass(frozen=True)
class NestedConfig:
    outer_splits: int = 3
    inner_splits: int = 2
    seed: int = 42
    max_workers: int = 4
    timeout_seconds: float | None = None
    retries: int = 0
    store_predictions: bool = True
    calibration: bool = True
    allow_fusion: bool = True
    max_ensemble_size: int = 3
    minimum_fusion_improvement: float = 0.002
    protocol_version: str = "CLIN-ADAPT-NESTED-v1"


def run_nested_validation(
    X: pd.DataFrame,
    y: pd.Series | np.ndarray,
    specs: list[ModelSpec],
    config: NestedConfig | None = None,
    checkpoint_path: str | None = None,
) -> dict[str, Any]:
    """Run inner candidate discovery in parallel and outer evaluation.

    Candidate preprocessing, model selection, coordination and calibration are
    fitted only within each outer-training partition.  The function is intended
    for compatible within-dataset benchmark tasks; it does not convert
    incompatible local cohorts into cross-dataset validation.
    """

    config = config or NestedConfig()
    if config.outer_splits < 2 or config.inner_splits < 2:
        raise ValueError("outer_splits and inner_splits must be at least two")
    labels = np.asarray(y, dtype=int)
    if len(X) != len(labels) or np.unique(labels).size != 2:
        raise ValueError("X and binary y must be aligned")
    X = copy_schema(X.copy(), X.copy())
    profile = profile_clinical_dataset(X, labels).to_dict()
    outer_cv = StratifiedKFold(config.outer_splits, shuffle=True, random_state=config.seed)
    coordinator = CASLCoordinator(
        CASLConfig(
            max_ensemble_size=config.max_ensemble_size if config.allow_fusion else 1,
            minimum_fusion_improvement=config.minimum_fusion_improvement,
        )
    )
    folds: list[dict[str, Any]] = []
    all_y: list[np.ndarray] = []
    all_p: list[np.ndarray] = []
    started_total = perf_counter()
    for outer_fold, (train_idx, test_idx) in enumerate(outer_cv.split(X, labels)):
        outer_train = copy_schema(X.iloc[train_idx].copy(), X.iloc[train_idx].copy())
        outer_test = copy_schema(X.iloc[test_idx].copy(), X.iloc[test_idx].copy())
        y_train = labels[train_idx]
        y_test = labels[test_idx]
        inner_jobs = {
            spec.name: _make_inner_job(outer_train, y_train, spec, config) for spec in specs
        }
        engine = ParallelExecutionEngine(
            max_workers=config.max_workers,
            timeout_seconds=config.timeout_seconds,
            retries=config.retries,
            checkpoint_path=checkpoint_path,
        )
        inner_results, execution_records = engine.run(inner_jobs)
        prediction_map = {
            name: result["oof_predictions"]
            for name, result in inner_results.items()
            if result.get("oof_predictions") is not None
        }
        if not prediction_map:
            raise RuntimeError(f"No candidate completed outer fold {outer_fold}")
        decision = coordinator.decide(y_train, prediction_map)
        selected_inner = np.column_stack(
            [prediction_map[name] for name in decision.selected_names]
        ) @ np.asarray(decision.weights)
        if config.calibration:
            calibration_method, calibrated_inner, calibration_briers = choose_calibration(
                y_train, selected_inner, seed=config.seed + outer_fold
            )
            calibrator = fit_full_calibrator(calibration_method, selected_inner, y_train)
        else:
            calibration_method, calibrated_inner, calibration_briers, calibrator = (
                "none",
                selected_inner,
                {"none": float(evaluate_binary_predictions(y_train, selected_inner)["brier"])},
                None,
            )
        del calibrated_inner
        outer_predictions: dict[str, np.ndarray] = {}
        fit_errors: list[dict[str, Any]] = []
        fit_start = perf_counter()
        spec_map = {spec.name: spec for spec in specs}
        for name in decision.selected_names:
            try:
                pipeline = build_clinical_pipeline(
                    outer_train, spec_map[name], config.seed + outer_fold
                )
                pipeline.fit(outer_train, y_train)
                outer_predictions[name] = pipeline.predict_proba(outer_test)[:, 1]
            except Exception as exc:
                fit_errors.append(
                    {"candidate": name, "type": type(exc).__name__, "message": str(exc)}
                )
        if not outer_predictions:
            raise RuntimeError(
                f"Selected candidates failed on outer fold {outer_fold}: {fit_errors}"
            )
        successful_names = [
            name for name in decision.selected_names if name in outer_predictions
        ]
        successful_weights = np.asarray(
            [
                decision.weights[index]
                for index, name in enumerate(decision.selected_names)
                if name in outer_predictions
            ]
        )
        successful_weights = successful_weights / successful_weights.sum()
        raw_outer = np.column_stack(
            [outer_predictions[name] for name in successful_names]
        ) @ successful_weights
        probabilities = apply_calibrator(calibrator, calibration_method, raw_outer)
        metrics = evaluate_binary_predictions(y_test, probabilities)
        all_y.append(y_test)
        all_p.append(probabilities)
        fold_record: dict[str, Any] = {
            "outer_fold": outer_fold,
            "train_n": int(len(train_idx)),
            "test_n": int(len(test_idx)),
            "profile": profile,
            "coordination": decision.to_dict(),
            "calibration_method": calibration_method,
            "calibration_briers": calibration_briers,
            "metrics": metrics,
            "execution_records": [record.to_dict() for record in execution_records],
            "failure_diagnoses": coordinator.diagnose_failures(
                [record.to_dict() for record in execution_records]
            ),
            "fit_errors": fit_errors,
            "selected_fit_seconds": perf_counter() - fit_start,
        }
        if config.store_predictions:
            fold_record["y_test"] = y_test.tolist()
            fold_record["probabilities"] = probabilities.tolist()
        folds.append(fold_record)
    pooled_y = np.concatenate(all_y)
    pooled_p = np.concatenate(all_p)
    return {
        "status": "completed",
        "method": "CLIN-ADAPT provisional CASL coordinator",
        "configuration": asdict(config),
        "profile": profile,
        "candidate_registry": [spec.to_dict() for spec in specs],
        "runtime_resources": detect_runtime_resources(),
        "folds": folds,
        "pooled_metrics": evaluate_binary_predictions(pooled_y, pooled_p),
        "runtime_seconds": perf_counter() - started_total,
        "interpretation": (
            "Within-dataset nested benchmark only; no cross-dataset or novelty claim."
        ),
    }


def _make_inner_job(
    X: pd.DataFrame,
    y: np.ndarray,
    spec: ModelSpec,
    config: NestedConfig,
):
    def job() -> dict[str, Any]:
        started = perf_counter()
        cv = StratifiedKFold(config.inner_splits, shuffle=True, random_state=config.seed)
        predictions = np.full(len(y), np.nan, dtype=float)
        folds: list[dict[str, Any]] = []
        for inner_fold, (train_idx, valid_idx) in enumerate(cv.split(X, y)):
            train = copy_schema(X.iloc[train_idx].copy(), X.iloc[train_idx].copy())
            valid = copy_schema(X.iloc[valid_idx].copy(), X.iloc[valid_idx].copy())
            pipeline = build_clinical_pipeline(train, spec, config.seed + inner_fold)
            pipeline.fit(train, y[train_idx])
            fold_p = pipeline.predict_proba(valid)[:, 1]
            predictions[valid_idx] = fold_p
            folds.append(
                {
                    "inner_fold": inner_fold,
                    "metrics": evaluate_binary_predictions(y[valid_idx], fold_p),
                }
            )
        if np.isnan(predictions).any():
            raise RuntimeError("incomplete inner out-of-fold predictions")
        return {
            "name": spec.name,
            "folds": folds,
            "metrics": evaluate_binary_predictions(y, predictions),
            "oof_predictions": predictions,
            "runtime_seconds": perf_counter() - started,
        }

    return job
