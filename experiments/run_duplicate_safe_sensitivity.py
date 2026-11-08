"""Re-evaluate affected cohorts and transfers after exact-row deduplication.

The frozen primary run is never overwritten. Duplicate rows are removed before
outer, inner, calibration, source, and target partitions are formed. Row-level
predictions and checkpoints remain ignored local artifacts.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy
import sklearn
from threadpoolctl import threadpool_info, threadpool_limits

from experiments import run_multi_dataset_evaluation as runner

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "final_research_20261108"
LOCAL = OUT / "duplicate_safe_local"
CHECKPOINTS = LOCAL / "checkpoints"
RESULTS = runner.RESULTS
RUN = RESULTS / "predictions" / "20261107T202404Z"
CAD = list(runner.UCI_CAD_DATASETS)
MODELS = list(runner.MODEL_VARIANTS)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def jsonable(v: Any) -> Any:
    if isinstance(v, dict):
        return {str(k): jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    if isinstance(v, np.generic):
        return v.item()
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, Path):
        return v.as_posix()
    if isinstance(v, float) and not np.isfinite(v):
        return None
    return v


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jsonable(obj), indent=2, allow_nan=False) + "\n", encoding="utf-8")


def load_deduplicated(dataset: str):
    X, y, spec = runner.load_task(dataset)
    original_indices = np.arange(len(X), dtype=int)
    groups = X.groupby(list(X.columns), dropna=False, sort=False).indices
    duplicate_groups = [sorted(map(int, ix)) for ix in groups.values() if len(ix) > 1]
    audit_rows = []
    keep = np.ones(len(X), dtype=bool)
    for group_no, indices in enumerate(duplicate_groups, start=1):
        labels = sorted(set(y.iloc[indices].astype(int).tolist()))
        if len(labels) != 1:
            raise ValueError(f"Conflicting labels for exact duplicate group {dataset}:{indices}")
        keep[indices[1:]] = False
        audit_rows.append(
            {
                "dataset": dataset,
                "group_id": group_no,
                "original_row_indices": ";".join(map(str, indices)),
                "group_size": len(indices),
                "label": labels[0],
                "duplicate_rows_removed": len(indices) - 1,
                "action": "retain first row; remove duplicates before any split",
            }
        )
    selected = original_indices[keep]
    Xnew = runner.mark_categorical(X.iloc[keep].reset_index(drop=True), list(spec["categorical"]))
    ynew = y.iloc[keep].reset_index(drop=True)
    if Xnew.duplicated(keep=False).any():
        raise AssertionError(f"Exact predictor duplicates remain after deduplication: {dataset}")
    return Xnew, ynew, spec, selected, audit_rows, len(X)


def cached(path: Path, source_hash: str) -> dict | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("source_run_id") != "20261107T202404Z"
        or value.get("script_sha256") != source_hash
    ):
        raise RuntimeError(f"Duplicate-safe checkpoint mismatch: {path}")
    return value


def audit_frozen_partition_boundaries(audit_rows: list[dict]) -> pd.DataFrame:
    assignments = pd.read_csv(RUN / "fold_assignments.csv")
    rows = []
    for group in audit_rows:
        indices = [int(value) for value in group["original_row_indices"].split(";")]
        subset = assignments[
            assignments.dataset.eq(group["dataset"])
            & assignments.row_index.isin(indices)
            & assignments.model.isna()
        ]
        for fold, fold_rows in subset.groupby("fold", sort=False):
            roles = {
                int(row.row_index): str(row.split_role) for row in fold_rows.itertuples(index=False)
            }
            labels = [roles.get(index, "missing_assignment") for index in indices]
            role_set = set(labels)
            rows.append(
                {
                    "dataset": group["dataset"],
                    "duplicate_group_id": group["group_id"],
                    "fold": str(fold),
                    "original_row_indices": group["original_row_indices"],
                    "row_roles": ";".join(labels),
                    "crossed_development_and_outer_test": (
                        "development" in role_set and "outer_test" in role_set
                    ),
                    "crossed_calibration_and_outer_test": (
                        "conformal_calibration" in role_set and "outer_test" in role_set
                    ),
                    "crossed_development_and_calibration": (
                        "development" in role_set and "conformal_calibration" in role_set
                    ),
                }
            )
    return pd.DataFrame(rows)


def audit_remaining_tasks() -> list[dict]:
    rows = []
    for ds in ("uci_heart_failure_519", "uci_mi_complications_579"):
        X, y, _ = runner.load_task(ds)
        groups = X.groupby(list(X.columns), dropna=False, sort=False).indices
        for ix in groups.values():
            if len(ix) > 1:
                labels = sorted(set(y.iloc[list(ix)].astype(int).tolist()))
                rows.append(
                    {
                        "dataset": ds,
                        "group_id": len(rows) + 1,
                        "original_row_indices": ";".join(map(str, sorted(map(int, ix)))),
                        "group_size": int(len(ix)),
                        "label": ";".join(map(str, labels)),
                        "duplicate_rows_removed": int(len(ix) - 1),
                        "action": "audit only; source manifest indicates no duplicates",
                    }
                )
    spectf = pd.read_csv(runner.PROCESSED / "uci_spectf_all.csv")
    target = spectf.pop("OVERALL_DIAGNOSIS").astype(int)
    groups = spectf.groupby(list(spectf.columns), dropna=False, sort=False).indices
    for ix in groups.values():
        if len(ix) > 1:
            labels = sorted(set(target.iloc[list(ix)].astype(int).tolist()))
            rows.append(
                {
                    "dataset": "uci_spectf_heart",
                    "group_id": len(rows) + 1,
                    "original_row_indices": ";".join(map(str, sorted(map(int, ix)))),
                    "group_size": int(len(ix)),
                    "label": ";".join(map(str, labels)),
                    "duplicate_rows_removed": int(len(ix) - 1),
                    "action": "audit only; source manifest indicates no duplicates",
                }
            )
    return rows


def run_within(data: dict[str, dict], script_hash: str):
    fold_rows, prediction_rows, conf_rows, assignments = [], [], [], []
    original_metrics = pd.read_csv(RESULTS / "metrics" / "model_metrics.csv")
    for ds in ("uci_hungary", "uci_va_long_beach"):
        entry = data[ds]
        X, y, kept, n_original = (
            entry["X"],
            entry["y"],
            entry["kept"],
            entry["n_original"],
        )
        for model in MODELS:
            cp = CHECKPOINTS / f"within__{ds}__{model}.json"
            old = cached(cp, script_hash)
            if old:
                fold_rows.extend(old["fold_metrics"])
                prediction_rows.extend(old["predictions"])
                conf_rows.extend(old["conformal_metrics"])
                assignments.extend(old["assignments"])
                continue
            fm, preds, conf = runner.run_nested_model(ds, X, y, model)
            assn = runner.build_nested_assignments(ds, X, y)
            for row in fm:
                row["original_n"] = n_original
                row["deduplicated_n"] = len(X)
                row["duplicate_rows_removed"] = n_original - len(X)
            for row in preds:
                row["original_row_index"] = int(kept[int(row["row_index"])])
                row["row_index"] = int(row["row_index"])
                row["duplicate_safe_protocol"] = True
            for row in assn:
                row["original_row_index"] = int(kept[int(row["row_index"])])
            base = original_metrics[
                (original_metrics.dataset == ds) & (original_metrics.model == model)
            ].iloc[0]
            summary = {
                "dataset": ds,
                "model": model,
                "duplicate_safe_n": len(X),
                "duplicate_rows_removed": n_original - len(X),
                "duplicate_safe_outer_mean_roc_auc": float(np.mean([r["roc_auc"] for r in fm])),
                "duplicate_safe_outer_sd_roc_auc": float(
                    np.std([r["roc_auc"] for r in fm], ddof=1)
                ),
                "frozen_outer_mean_roc_auc": float(base["fold_mean_roc_auc"]),
                "frozen_minus_duplicate_safe_auc": float(
                    base["fold_mean_roc_auc"] - np.mean([r["roc_auc"] for r in fm])
                ),
                "duplicate_safe_pooled_roc_auc": float(
                    runner.roc_auc_score(
                        [r["y_true"] for r in preds], [r["probability_positive"] for r in preds]
                    )
                ),
                "fold_group_split": "stratified 3-fold CV after exact-row deduplication",
                "inner_selection": "original 3-fold stratified CV, duplicate-free development data",
            }
            write_json(
                cp,
                {
                    "source_run_id": "20261107T202404Z",
                    "script_sha256": script_hash,
                    "fold_metrics": fm,
                    "predictions": preds,
                    "conformal_metrics": conf,
                    "assignments": assn,
                    "summary": summary,
                },
            )
            fold_rows.extend(fm)
            prediction_rows.extend(preds)
            conf_rows.extend(conf)
            assignments.extend(assn)
            print(f"WITHIN DEDUP PASS {ds} {model}", flush=True)
    return fold_rows, prediction_rows, conf_rows, assignments


def run_cross(data: dict[str, dict], script_hash: str):
    metrics, predictions, assignments = [], [], []
    for source in CAD:
        for target in CAD:
            if source == target:
                continue
            for model in MODELS:
                cp = CHECKPOINTS / f"cross__{source}__{target}__{model}.json"
                old = cached(cp, script_hash)
                if old:
                    metrics.append(old["metric"])
                    predictions.extend(old["predictions"])
                    assignments.extend(old["assignments"])
                    continue
                xs, ys, ss, skeep = (
                    data[source]["X"],
                    data[source]["y"],
                    data[source]["spec"],
                    data[source]["kept"],
                )
                xt, yt, ts, tkeep = (
                    data[target]["X"],
                    data[target]["y"],
                    data[target]["spec"],
                    data[target]["kept"],
                )
                row, pred_rows, assign_rows = runner.run_cross_pair(
                    source,
                    target,
                    (xs, ys, ss),
                    (xt, yt, ts),
                    model,
                )
                row.update(
                    {
                        "source_rows_after_exact_deduplication": len(xs),
                        "source_duplicate_rows_removed": int(data[source]["n_original"] - len(xs)),
                        "target_rows_after_exact_deduplication": len(xt),
                        "target_duplicate_rows_removed": int(data[target]["n_original"] - len(xt)),
                        "duplicate_safe_protocol": True,
                    }
                )
                for p in pred_rows:
                    p["target_original_row_index"] = (
                        int(tkeep[int(p.get("target_row_index", p.get("row_index", 0)))])
                        if "target_row_index" in p or "row_index" in p
                        else None
                    )
                for a in assign_rows:
                    if a.get("source_dataset") == source and a.get("split_role", "").startswith(
                        "source_"
                    ):
                        a["source_original_row_index"] = int(skeep[int(a["row_index"])])
                    elif a.get("target_dataset") == target:
                        a["target_original_row_index"] = int(tkeep[int(a["row_index"])])
                write_json(
                    cp,
                    {
                        "source_run_id": "20261107T202404Z",
                        "script_sha256": script_hash,
                        "metric": row,
                        "predictions": pred_rows,
                        "assignments": assign_rows,
                    },
                )
                metrics.append(row)
                predictions.extend(pred_rows)
                assignments.extend(assign_rows)
                print(f"CROSS DEDUP PASS {source} to {target} {model}", flush=True)
    return metrics, predictions, assignments


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    script_hash = sha256(Path(__file__).resolve())
    data = {}
    audit_rows = []
    for ds in CAD:
        X, y, spec, kept, audit, n_original = load_deduplicated(ds)
        data[ds] = {
            "X": X,
            "y": y,
            "spec": spec,
            "kept": kept,
            "audit": audit,
            "n_original": n_original,
        }
        audit_rows.extend(audit)
    all_audit_rows = audit_rows + audit_remaining_tasks()
    pd.DataFrame(all_audit_rows).to_csv(OUT / "duplicate_audit.csv", index=False)
    partition_audit = audit_frozen_partition_boundaries(audit_rows)
    partition_audit.to_csv(OUT / "duplicate_partition_audit.csv", index=False)
    start = time.perf_counter()
    with threadpool_limits(limits=1):
        within = run_within(data, script_hash)
        cross = run_cross(data, script_hash)
    wfolds, wpreds, wconf, wasgn = within
    cross_metrics, cpreds, cassgn = cross
    cross_df = pd.DataFrame(cross_metrics)
    primary_cross = pd.read_csv(RESULTS / "metrics" / "cross_dataset_metrics.csv")
    cross_df = cross_df.merge(
        primary_cross[
            [
                "source_dataset",
                "target_dataset",
                "model",
                "target_roc_auc",
                "target_ood_detection_roc_auc",
                "target_ood_alert_rate",
            ]
        ],
        on=["source_dataset", "target_dataset", "model"],
        how="left",
        suffixes=("", "_frozen"),
    )
    cross_df["frozen_minus_duplicate_safe_target_auc"] = (
        cross_df.target_roc_auc_frozen - cross_df.target_roc_auc
    )
    cross_df["frozen_minus_duplicate_safe_domain_ood_auc"] = (
        cross_df.target_ood_detection_roc_auc_frozen - cross_df.target_ood_detection_roc_auc
    )
    # Recalculate within-task summary metrics from the duplicate-safe saved predictions.
    summary_rows = []
    for (ds, model), g in pd.DataFrame(wpreds).groupby(["dataset", "model"], sort=False):
        base = pd.DataFrame(wfolds)
        b = base[(base.dataset == ds) & (base.model == model)]
        p = g.probability_positive.to_numpy(dtype=float)
        y = g.y_true.to_numpy(dtype=int)
        summary_rows.append(
            {
                "dataset": ds,
                "model": model,
                "duplicate_safe_n": int(len(g)),
                "duplicate_safe_fold_mean_roc_auc": float(b.roc_auc.mean()),
                "duplicate_safe_fold_sd_roc_auc": float(b.roc_auc.std(ddof=1)),
                "duplicate_safe_pooled_roc_auc": float(runner.roc_auc_score(y, p)),
                "duplicate_safe_fold_mean_accuracy": float(b.accuracy.mean()),
                "duplicate_safe_fold_mean_sensitivity": float(b.recall.mean()),
                "duplicate_safe_fold_mean_specificity": float(b.specificity.mean()),
                "duplicate_safe_fold_mean_f1": float(b.f1.mean()),
                "duplicate_safe_fold_mean_pr_auc": float(b.pr_auc.mean()),
                "all_exact_predictor_duplicates_removed_before_splitting": True,
            }
        )
    within_df = pd.DataFrame(summary_rows)
    frozen = pd.read_csv(RESULTS / "metrics" / "model_metrics.csv")
    within_df = within_df.merge(
        frozen[
            [
                "dataset",
                "model",
                "fold_mean_roc_auc",
                "fold_mean_accuracy",
                "fold_mean_recall",
                "fold_mean_specificity",
                "fold_mean_f1",
                "fold_mean_pr_auc",
            ]
        ],
        on=["dataset", "model"],
        how="left",
    )
    within_df["frozen_minus_duplicate_safe_auc"] = (
        within_df.fold_mean_roc_auc - within_df.duplicate_safe_fold_mean_roc_auc
    )
    within_df.to_csv(OUT / "duplicate_safe_within_model_metrics.csv", index=False)
    pd.DataFrame(wfolds).to_csv(OUT / "duplicate_safe_within_fold_metrics.csv", index=False)
    pd.DataFrame(wconf).to_csv(OUT / "duplicate_safe_conformal_metrics.csv", index=False)
    cross_df.to_csv(OUT / "duplicate_safe_cross_dataset_metrics.csv", index=False)
    # Row-level predictions/checkpoint assignments remain ignored and local.
    pd.DataFrame(wpreds).to_csv(LOCAL / "within_predictions.csv", index=False)
    pd.DataFrame(cpreds).to_csv(LOCAL / "cross_predictions.csv", index=False)
    pd.DataFrame(wasgn).to_csv(LOCAL / "within_assignments.csv", index=False)
    pd.DataFrame(cassgn).to_csv(LOCAL / "cross_assignments.csv", index=False)
    verification = {
        "source_run_id": "20261107T202404Z",
        "analysis": "exact predictor-row deduplication sensitivity; frozen outputs preserved",
        "generated_utc": datetime.now(UTC).isoformat(),
        "datasets": {
            ds: {
                "n_before": data[ds]["n_original"],
                "n_after": len(data[ds]["X"]),
                "duplicate_rows_removed": data[ds]["n_original"] - len(data[ds]["X"]),
                "duplicate_groups": data[ds]["audit"],
                "source_file_sha256": sha256(data[ds]["spec"]["path"]),
            }
            for ds in CAD
        },
        "frozen_partition_boundary_audit": partition_audit.to_dict(orient="records"),
        "exact_duplicate_groups_across_all_evaluated_tasks": len(all_audit_rows),
        "counts": {
            "within_task_models": len(within_df),
            "within_task_folds": len(wfolds),
            "cross_transfer_models": len(cross_metrics),
            "all_exact_duplicates_absent_after_deduplication": all(
                not d["X"].duplicated(keep=False).any() for d in data.values()
            ),
            "target_outcomes_used_for_ood_or_model_selection": False,
        },
        "runtime_seconds": time.perf_counter() - start,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "scipy": scipy.__version__,
            "threadpools": threadpool_info(),
            "peak_memory_instrumented": False,
        },
        "row_level_outputs_are_local": True,
        "analysis_script_sha256": script_hash,
    }
    write_json(OUT / "duplicate_safe_manifest.json", verification)
    print(json.dumps(verification["counts"], indent=2), flush=True)
    print(f"Duplicate-safe sensitivity written under {OUT}", flush=True)


if __name__ == "__main__":
    main()
