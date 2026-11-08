# ruff: noqa: E501
"""Reproduce the frozen-run diagnostics omitted from the primary artifact tables."""

from __future__ import annotations

import hashlib
import io
import json
import platform
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from threadpoolctl import threadpool_info

from cardiodiag.experiments import build_corrected_pipeline
from experiments.run_multi_dataset_evaluation import (
    CALIBRATION_FRACTION,
    DATASET_SPECS,
    OUTER_FOLDS,
    PROCESSED,
    SEED,
    load_task,
    mark_categorical,
    ood_scores,
)
from experiments.run_multi_dataset_evaluation import (
    RESULTS as SOURCE_RESULTS,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "final_research_20261108"
CHECKPOINTS = OUT / "checkpoints_source_order_v2"
PREDICTIONS = OUT / "predictions_source_order"
RUN_ID = "20261107T202404Z"
SOURCE_PREDICTIONS = SOURCE_RESULTS / "predictions" / RUN_ID
SOURCE_METRICS = SOURCE_RESULTS / "metrics"
ALPHAS = (0.20, 0.10, 0.05)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jsonable(obj), indent=2, allow_nan=False) + "\n", encoding="utf-8")


def metrics(y: np.ndarray, p: np.ndarray) -> dict[str, Any]:
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = sklearn.metrics.confusion_matrix(y, pred, labels=[0, 1]).ravel()
    spec = float(tn / (tn + fp)) if tn + fp else 0.0
    sens = float(tp / (tp + fn)) if tp + fn else 0.0
    return {
        "n": int(len(y)),
        "positive_count": int(y.sum()),
        "prevalence": float(y.mean()),
        "accuracy": float(sklearn.metrics.accuracy_score(y, pred)),
        "balanced_accuracy": float(sklearn.metrics.balanced_accuracy_score(y, pred)),
        "precision": float(sklearn.metrics.precision_score(y, pred, zero_division=0)),
        "sensitivity": sens,
        "recall": sens,
        "specificity": spec,
        "f1": float(sklearn.metrics.f1_score(y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, p)) if np.unique(y).size == 2 else None,
        "pr_auc": float(average_precision_score(y, p)) if y.sum() else None,
        "brier": float(sklearn.metrics.brier_score_loss(y, p)),
        "log_loss": float(sklearn.metrics.log_loss(y, p, labels=[0, 1])),
        "mcc": float(sklearn.metrics.matthews_corrcoef(y, pred)),
        "cohen_kappa": float(sklearn.metrics.cohen_kappa_score(y, pred)),
        "false_positive_rate": float(1.0 - spec),
        "false_negative_rate": float(1.0 - sens),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def conformal_q(y: np.ndarray, p: np.ndarray, alpha: float) -> float:
    score = 1.0 - np.where(np.asarray(y, dtype=int) == 1, p, 1.0 - p)
    rank = int(np.ceil((len(score) + 1) * (1.0 - alpha)))
    return 1.0 if rank > len(score) else float(np.sort(score)[rank - 1])


def make_sets(p: np.ndarray, q: float) -> list[list[int]]:
    result = []
    for value in np.asarray(p, dtype=float):
        labels = []
        if value <= q:
            labels.append(0)
        if 1.0 - value <= q:
            labels.append(1)
        result.append(labels)
    return result


def summarize_sets(y: np.ndarray, sets: list[list[int]], alpha: float) -> dict[str, Any]:
    y = np.asarray(y, dtype=int)
    size = np.asarray([len(s) for s in sets], dtype=int)
    covered = np.asarray([int(label in s) for label, s in zip(y, sets, strict=True)])
    out = {
        "nominal_coverage": 1.0 - alpha,
        "alpha": alpha,
        "empirical_coverage": float(covered.mean()),
        "average_set_size": float(size.mean()),
        "singleton_rate": float(np.mean(size == 1)),
        "empty_set_rate": float(np.mean(size == 0)),
        "n": int(len(y)),
    }
    for cls in (0, 1):
        mask = y == cls
        out[f"class_{cls}_n"] = int(mask.sum())
        out[f"class_{cls}_coverage"] = float(covered[mask].mean()) if mask.any() else None
    return out


def load_spectf():
    train = pd.read_csv(PROCESSED / "uci_spectf_train.csv")
    test = pd.read_csv(PROCESSED / "uci_spectf_test.csv")
    y_train = train.pop("OVERALL_DIAGNOSIS").astype(int)
    y_test = test.pop("OVERALL_DIAGNOSIS").astype(int)
    train.attrs["categorical_columns"] = []
    return train, y_train, test, y_test


def feature_frame(dataset: str) -> pd.DataFrame:
    spec = DATASET_SPECS[dataset]
    x = pd.read_csv(spec["path"])
    x.drop(columns=[str(spec["target"])], inplace=True)
    return mark_categorical(x, list(spec["categorical"]))


def cached(path: Path, script_hash: str) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("script_sha256") != script_hash or value.get("source_run_id") != RUN_ID:
        raise RuntimeError(f"Checkpoint does not match current protocol: {path}")
    return value


def run_within(script_hash: str):
    fm = pd.read_csv(SOURCE_METRICS / "fold_metrics.csv")
    assn = pd.read_csv(SOURCE_PREDICTIONS / "fold_assignments.csv")
    pred = pd.read_csv(SOURCE_PREDICTIONS / "out_of_fold_and_official_predictions.csv")
    loaded = {}
    train_rows, conf_rows, runtime_rows, pred_rows = [], [], [], []

    for _, s in fm.iterrows():
        ds, model, fold = str(s.dataset), str(s.model), str(s.fold)
        name = f"within__{ds}__{model}__{fold}.json"
        cache_path = CHECKPOINTS / name
        old = cached(cache_path, script_hash)
        if old is not None:
            train_rows.extend(old["training_validation"])
            conf_rows.extend(old["conformal"])
            runtime_rows.append(old["runtime"])
            pred_rows.extend(old["predictions"])
            continue

        if ds not in loaded:
            if ds == "uci_spectf_heart":
                loaded[ds] = load_spectf()
            else:
                x, y, _ = load_task(ds)
                loaded[ds] = (x, y, None, None)
        xall, yall, xofficial, yofficial = loaded[ds]

        if ds == "uci_spectf_heart":
            # The frozen assignment manifest calls this partition
            # ``official_split`` while fold_metrics calls its evaluation
            # partition ``official_test``. Select by dataset/model only.
            a = assn[(assn.dataset.astype(str) == ds) & (assn.model.astype(str) == model)]
        else:
            a = assn[(assn.dataset.astype(str) == ds) & (assn.fold.astype(str) == fold)]
        dev = a.loc[a.split_role == "development", "row_index"].astype(int).to_numpy()
        cal = a.loc[a.split_role == "conformal_calibration", "row_index"].astype(int).to_numpy()
        if ds == "uci_spectf_heart":
            seed = int(s.split_seed)
            dev, cal = train_test_split(
                np.arange(len(xall)),
                test_size=CALIBRATION_FRACTION,
                random_state=seed,
                stratify=yall,
            )
            assert set(dev) == set(a.loc[a.split_role == "development", "row_index"].astype(int))
            assert set(cal) == set(
                a.loc[a.split_role == "conformal_calibration", "row_index"].astype(int)
            )
            xdev = mark_categorical(xall.iloc[dev].copy(), [])
            ydev = yall.iloc[dev].reset_index(drop=True)
            xcal = xall.iloc[cal].copy()
            ycal = yall.iloc[cal].to_numpy(dtype=int)
        else:
            outer = StratifiedKFold(n_splits=OUTER_FOLDS, shuffle=True, random_state=SEED)
            outer_train, _ = list(outer.split(xall, yall))[int(fold) - 1]
            seed = SEED + int(fold)
            dev_local, cal_local = train_test_split(
                np.arange(len(outer_train)),
                test_size=CALIBRATION_FRACTION,
                random_state=seed,
                stratify=yall.iloc[outer_train],
            )
            dev, cal = outer_train[dev_local], outer_train[cal_local]
            assert set(dev) == set(a.loc[a.split_role == "development", "row_index"].astype(int))
            assert set(cal) == set(
                a.loc[a.split_role == "conformal_calibration", "row_index"].astype(int)
            )
            cats = list(xall.attrs.get("categorical_columns", []))
            xdev = mark_categorical(xall.iloc[dev].copy(), cats)
            ydev = yall.iloc[dev].reset_index(drop=True)
            xcal = xall.iloc[cal].copy()
            ycal = yall.iloc[cal].to_numpy(dtype=int)

        saved = pred[
            (pred.dataset.astype(str) == ds)
            & (pred.model.astype(str) == model)
            & (pred.fold.astype(str) == fold)
        ].sort_values("row_index")
        test_indices = saved.row_index.astype(int).to_numpy()
        if ds == "uci_spectf_heart":
            xtest = xofficial.iloc[test_indices].copy()
            ytest = yofficial.iloc[test_indices].to_numpy(dtype=int)
        else:
            xtest = xall.iloc[test_indices].copy()
            ytest = yall.iloc[test_indices].to_numpy(dtype=int)
        psaved = saved.probability_positive.to_numpy(dtype=float)
        ysaved = saved.y_true.to_numpy(dtype=int)
        assert np.array_equal(ytest, ysaved)

        est = build_corrected_pipeline(xdev, variant=model, seed=seed)
        est.set_params(**json.loads(str(s.best_params)))
        t0 = time.perf_counter()
        est.fit(xdev, ydev)
        fit_s = time.perf_counter() - t0
        t0 = time.perf_counter()
        pdev = est.predict_proba(xdev)[:, 1]
        pcal = est.predict_proba(xcal)[:, 1]
        pcheck = est.predict_proba(xtest)[:, 1]
        prediction_s = time.perf_counter() - t0
        max_diff = float(np.max(np.abs(pcheck - psaved))) if len(psaved) else 0.0
        mt, mv = metrics(ydev.to_numpy(dtype=int), pdev), metrics(ysaved, psaved)
        train_row = {
            "dataset": ds,
            "model": model,
            "fold": fold,
            "training_scope": "development-fold resubstitution",
            "validation_scope": "untouched outer test fold or official test",
            "train_n": len(ydev),
            "validation_n": len(ysaved),
            **{
                f"train_{k}": v
                for k, v in mt.items()
                if k not in {"n", "positive_count", "prevalence"}
            },
            **{
                f"validation_{k}": v
                for k, v in mv.items()
                if k not in {"n", "positive_count", "prevalence"}
            },
            "train_prevalence": float(ydev.mean()),
            "validation_prevalence": float(ysaved.mean()),
            "inner_validation_roc_auc_selected": float(s.inner_validation_roc_auc_best),
            "inner_training_roc_auc_at_selected": float(s.inner_training_roc_auc_at_best)
            if pd.notna(s.inner_training_roc_auc_at_best)
            else None,
            "train_minus_outer_validation_roc_auc": float(mt["roc_auc"] - mv["roc_auc"]),
            "train_minus_outer_validation_accuracy": float(mt["accuracy"] - mv["accuracy"]),
            "train_minus_outer_validation_f1": float(mt["f1"] - mv["f1"]),
            "train_minus_outer_validation_log_loss": float(mt["log_loss"] - mv["log_loss"]),
            "saved_outer_auc_matches": bool(abs(float(mv["roc_auc"]) - float(s.roc_auc)) < 1e-10),
            "refit_probability_max_abs_difference": max_diff,
            "refit_prediction_reproduced": bool(max_diff < 1e-8),
            "best_params": s.best_params,
            "split_seed": seed,
        }
        train_rows.append(train_row)
        conf_group = []
        for alpha in ALPHAS:
            q = conformal_q(ycal, pcal, alpha)
            sets = make_sets(psaved, q)
            row = {
                "dataset": ds,
                "model": model,
                "fold": fold,
                "calibration_n": len(ycal),
                "calibration_positive_count": int(ycal.sum()),
                "threshold": q,
                **summarize_sets(ysaved, sets, alpha),
                "evaluation_scope": "saved outer test or official test",
            }
            conf_rows.append(row)
            conf_group.append(row)

        _, ood_test, _, ood_q = ood_scores(est, xdev, xcal, xtest)
        old_ood = saved.ood_score.to_numpy(dtype=float)
        ood_diff = float(np.max(np.abs(ood_test - old_ood))) if len(old_ood) else 0.0
        buff = io.BytesIO()
        joblib.dump(est, buff, compress=0)
        for _ in range(3):
            est.predict_proba(xtest)
        times = []
        for _ in range(25):
            t0 = time.perf_counter()
            est.predict_proba(xtest)
            times.append(time.perf_counter() - t0)
        batch_ms = float(np.median(times) * 1000.0)
        runtime = {
            "scope": "fixed selected configuration; no hyperparameter search",
            "dataset": ds,
            "model": model,
            "fold": fold,
            "primary_search_fit_calibration_seconds": float(s.runtime_seconds),
            "diagnostic_refit_seconds": float(fit_s),
            "development_and_calibration_predict_seconds": float(prediction_s),
            "inference_batch_median_ms": batch_ms,
            "inference_microseconds_per_row": float(batch_ms * 1000.0 / max(1, len(xtest))),
            "serialized_pipeline_bytes_uncompressed": len(buff.getvalue()),
            "ood_q95_reproduced": bool(abs(float(s.ood_threshold_calibration_q95) - ood_q) < 1e-8),
            "ood_test_scores_reproduced": bool(ood_diff < 1e-8),
            "ood_test_score_max_abs_difference": ood_diff,
            "development_rows": len(xdev),
            "calibration_rows": len(xcal),
            "evaluation_rows": len(xtest),
        }
        runtime_rows.append(runtime)
        local_rows = []
        for role, idxs, labels, probs in (
            ("development_resubstitution", dev, ydev.to_numpy(dtype=int), pdev),
            ("outer_test", test_indices, ysaved, psaved),
            ("conformal_calibration", cal, ycal, pcal),
        ):
            for idx, label, prob in zip(idxs, labels, probs, strict=True):
                local_rows.append(
                    {
                        "dataset": ds,
                        "model": model,
                        "fold": fold,
                        "row_index": int(idx),
                        "role": role,
                        "y_true": int(label),
                        "probability_positive": float(prob),
                    }
                )
        pred_rows.extend(local_rows)
        write_json(
            cache_path,
            {
                "source_run_id": RUN_ID,
                "script_sha256": script_hash,
                "training_validation": [train_row],
                "conformal": conf_group,
                "runtime": runtime,
                "predictions": local_rows,
            },
        )
        print(f"WITHIN PASS {ds} {model} fold={fold} refit_diff={max_diff:.2g}", flush=True)
    return train_rows, conf_rows, runtime_rows, pred_rows


def run_cross_ood(script_hash: str):
    cm = pd.read_csv(SOURCE_METRICS / "cross_dataset_metrics.csv")
    assignments = pd.read_csv(SOURCE_PREDICTIONS / "cross_dataset_split_assignments.csv")
    source_cache, target_cache = {}, {}
    rows, score_rows = [], []
    for _, s in cm.iterrows():
        source, target, model = str(s.source_dataset), str(s.target_dataset), str(s.model)
        key = f"cross_ood__{source}__{target}__{model}.json"
        path = CHECKPOINTS / key
        old = cached(path, script_hash)
        if old is not None:
            rows.append(old["metric"])
            score_rows.extend(old["scores"])
            continue
        if source not in source_cache:
            source_cache[source] = load_task(source)
        if target not in target_cache:
            target_cache[target] = feature_frame(target)
        xs, ys, spec = source_cache[source]
        xt = target_cache[target]
        group = assignments[
            (assignments.source_dataset.astype(str) == source)
            & (assignments.target_dataset.astype(str) == target)
            & (assignments.model.astype(str) == model)
        ]
        seed = int(s.split_seed)
        dev, cal = train_test_split(
            np.arange(len(xs)),
            test_size=CALIBRATION_FRACTION,
            random_state=seed,
            stratify=ys,
        )
        assert set(dev) == set(
            group.loc[group.split_role == "source_development", "row_index"].astype(int)
        )
        assert set(cal) == set(
            group.loc[group.split_role == "source_calibration", "row_index"].astype(int)
        )
        xdev = mark_categorical(xs.iloc[dev].copy(), list(spec["categorical"]))
        ydev = ys.iloc[dev].reset_index(drop=True)
        xcal = xs.iloc[cal].copy()
        params = json.loads(str(s.best_params))
        est = build_corrected_pipeline(xdev, variant=model, seed=seed)
        est.set_params(**params)
        t0 = time.perf_counter()
        est.fit(xdev, ydev)
        cal_score, target_score, alerts, threshold = ood_scores(est, xdev, xcal, xt)
        elapsed = time.perf_counter() - t0
        domain_y = np.r_[np.zeros(len(cal_score), dtype=int), np.ones(len(target_score), dtype=int)]
        domain_score = np.r_[cal_score, target_score]
        auc_value = float(roc_auc_score(domain_y, domain_score))
        ap_value = float(average_precision_score(domain_y, domain_score))
        metric = {
            "source_dataset": source,
            "target_dataset": target,
            "model": model,
            "source_calibration_n": int(len(cal_score)),
            "target_feature_n": int(len(target_score)),
            "support_method": "mean 5-nearest-neighbor distance after source-fitted preprocessing",
            "source_calibration_q95_threshold": threshold,
            "source_calibration_alert_rate": float(np.mean(cal_score > threshold)),
            "target_alert_rate_sensitivity": float(np.mean(alerts)),
            "domain_detection_roc_auc": auc_value,
            "domain_detection_average_precision": ap_value,
            "saved_roc_auc_max_abs_difference": abs(
                auc_value - float(s.target_ood_detection_roc_auc)
            ),
            "saved_roc_auc_reproduced": bool(
                abs(auc_value - float(s.target_ood_detection_roc_auc)) < 1e-8
            ),
            "refit_and_score_seconds": float(elapsed),
            "target_outcome_labels_used": False,
            "interpretation": "Average precision depends on the sampled source-calibration/target mixture and is not population-prevalence calibrated.",
        }
        scores = [
            {
                "source_dataset": source,
                "target_dataset": target,
                "model": model,
                "domain_label_target": 0,
                "row_index": int(i),
                "ood_score": float(v),
            }
            for i, v in zip(cal, cal_score, strict=True)
        ] + [
            {
                "source_dataset": source,
                "target_dataset": target,
                "model": model,
                "domain_label_target": 1,
                "row_index": int(i),
                "ood_score": float(v),
            }
            for i, v in enumerate(target_score)
        ]
        rows.append(metric)
        score_rows.extend(scores)
        write_json(
            path,
            {
                "source_run_id": RUN_ID,
                "script_sha256": script_hash,
                "metric": metric,
                "scores": scores,
            },
        )
        print(
            f"CROSS-OOD PASS {source} to {target} {model} auc={auc_value:.3f} ap={ap_value:.3f}",
            flush=True,
        )
    return rows, score_rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    PREDICTIONS.mkdir(parents=True, exist_ok=True)
    script_hash = sha256(Path(__file__).resolve())
    training, conformal, runtime, local_predictions = run_within(script_hash)
    cross_ood, cross_scores = run_cross_ood(script_hash)
    pd.DataFrame(training).to_csv(OUT / "training_validation_metrics.csv", index=False)
    pd.DataFrame(conformal).to_csv(OUT / "conformal_levels_metrics.csv", index=False)
    pd.DataFrame(runtime).to_csv(OUT / "runtime_metrics.csv", index=False)
    pd.DataFrame(cross_ood).to_csv(OUT / "cross_dataset_ood_metrics.csv", index=False)
    pd.DataFrame(local_predictions).to_csv(
        PREDICTIONS / "training_validation_predictions.csv", index=False
    )
    pd.DataFrame(cross_scores).to_csv(PREDICTIONS / "cross_dataset_ood_scores.csv", index=False)
    source_files = [
        SOURCE_METRICS / "fold_metrics.csv",
        SOURCE_METRICS / "cross_dataset_metrics.csv",
        SOURCE_PREDICTIONS / "fold_assignments.csv",
        SOURCE_PREDICTIONS / "out_of_fold_and_official_predictions.csv",
        SOURCE_PREDICTIONS / "cross_dataset_split_assignments.csv",
        SOURCE_RESULTS / "datasets" / "dataset_manifest.json",
        Path(__file__).resolve(),
    ]
    input_data = [spec["path"] for spec in DATASET_SPECS.values()] + [
        PROCESSED / "uci_spectf_train.csv",
        PROCESSED / "uci_spectf_test.csv",
    ]
    hashes = {p.relative_to(ROOT).as_posix(): sha256(p) for p in source_files + input_data}
    tv = pd.DataFrame(training)
    co = pd.DataFrame(cross_ood)
    manifest = {
        "study": "CARDIODIAG completion diagnostics",
        "run_id": "completion_diagnostics_20261108",
        "source_run_id": RUN_ID,
        "generated_utc": datetime.now(UTC).isoformat(),
        "protocol": {
            "saved_best_hyperparameters_reused": True,
            "outer_test_labels_used_for_selection": False,
            "cross_target_outcome_labels_used_for_ood": False,
            "within_task_fit_scope": "saved development fold; calibration and test remain held out",
            "conformal_levels": [0.80, 0.90, 0.95],
            "ood_threshold_quantile": 0.95,
        },
        "source_files_sha256": hashes,
        "counts": {
            "within_task_model_folds": len(tv),
            "conformal_rows": len(conformal),
            "cross_ood_model_transfers": len(co),
            "within_task_probability_reproductions_passed": int(
                tv.refit_prediction_reproduced.sum()
            ),
            "within_task_primary_auc_matches": int(tv.saved_outer_auc_matches.sum()),
            "cross_ood_auc_reproductions_passed": int(co.saved_roc_auc_reproduced.sum()),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "logical_cpus": __import__("os").cpu_count(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "scipy": scipy.__version__,
            "threadpools": threadpool_info(),
            "peak_memory_instrumented": False,
        },
        "row_level_outputs_are_local": True,
        "local_row_level_paths": [
            "predictions_source_order/training_validation_predictions.csv",
            "predictions_source_order/cross_dataset_ood_scores.csv",
            "checkpoints_source_order/",
        ],
    }
    write_json(OUT / "completion_diagnostics_manifest.json", manifest)
    print(json.dumps(manifest["counts"], indent=2), flush=True)
    print(f"Aggregate diagnostics written under {OUT}", flush=True)


if __name__ == "__main__":
    main()
