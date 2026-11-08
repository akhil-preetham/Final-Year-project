"""Compare nested-tuned OSEC meta-logistic C with fixed default C=1."""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedKFold, train_test_split

from experiments import run_duplicate_safe_sensitivity as duplicate_safe
from experiments import run_multi_dataset_evaluation as runner

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "final_research_20261108" / "osec_optimization_ablation"
LOCAL_PREDICTIONS = (
    ROOT
    / "results"
    / "final_research_20261108"
    / "predictions"
    / "osec_optimization_ablation"
    / "out_of_fold_predictions.csv"
)
SOURCE_PREDICTIONS = (
    ROOT
    / "results"
    / "final_research_20261108"
    / "predictions_source_order"
    / "training_validation_predictions.csv"
)
SOURCE_METRICS = (
    ROOT / "results" / "multi_dataset_evaluation_20261108" / "metrics" / "fold_metrics.csv"
)
DEDUP_SAFE_PREDICTIONS = duplicate_safe.LOCAL / "within_predictions.csv"
DEDUP_SAFE_METRICS = (
    ROOT
    / "results"
    / "final_research_20261108"
    / "metrics"
    / "duplicate_safe_within_fold_metrics.csv"
)
AFFECTED = {"uci_hungary", "uci_va_long_beach"}
DATASETS = (*runner.DATASET_SPECS, "uci_spectf_heart")
CONDITIONS = ("fixed_default_c_1", "nested_tuned_c")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def make_fixed_osec(X_development: pd.DataFrame, seed: int):
    """Build the unchanged OSEC pipeline with only meta-estimator C fixed."""

    estimator = runner.build_corrected_pipeline(X_development, variant="osec", seed=seed)
    estimator.set_params(model__final_estimator__C=1.0)
    return estimator


def _reference_predictions(dataset: str, fold: str) -> pd.DataFrame:
    if dataset in AFFECTED:
        predictions = pd.read_csv(DEDUP_SAFE_PREDICTIONS)
        subset = predictions[
            predictions.dataset.eq(dataset)
            & predictions.model.eq("osec")
            & predictions.fold.astype(str).eq(fold)
        ].copy()
        return subset.rename(columns={"probability_positive": "probability_tuned"})
    predictions = pd.read_csv(SOURCE_PREDICTIONS)
    subset = predictions[
        predictions.dataset.eq(dataset)
        & predictions.model.eq("osec")
        & predictions.fold.astype(str).eq(fold)
        & predictions.role.isin(["outer_test", "official_test"])
    ].copy()
    return subset.rename(columns={"probability_positive": "probability_tuned", "y_true": "y_true"})


def _selected_c(dataset: str, fold: str) -> tuple[float, float]:
    metric_path = DEDUP_SAFE_METRICS if dataset in AFFECTED else SOURCE_METRICS
    metrics = pd.read_csv(metric_path)
    subset = metrics[
        metrics.dataset.eq(dataset) & metrics.model.eq("osec") & metrics.fold.astype(str).eq(fold)
    ]
    if subset.empty:
        raise AssertionError(f"missing saved tuned OSEC metadata for {dataset}/{fold}")
    row = subset.iloc[0]
    params = json.loads(str(row.best_params))
    selected_c = float(params["model__final_estimator__C"])
    return selected_c, float(row.runtime_seconds)


def _score_rows(
    dataset: str,
    fold: str,
    condition: str,
    y: np.ndarray,
    probability: np.ndarray,
    selected_c: float,
    fit_seconds: float | None,
    reference_delta: float | None,
) -> dict[str, Any]:
    values = runner.evaluate_predictions(
        np.asarray(y, dtype=int), np.asarray(probability, dtype=float)
    )
    return {
        "dataset": dataset,
        "model": "osec",
        "fold": fold,
        "condition": condition,
        "selected_meta_estimator_c": selected_c,
        "n": len(y),
        **values,
        "log_loss": float(log_loss(y, probability, labels=[0, 1])),
        "fit_or_search_seconds": fit_seconds,
        "saved_tuned_prediction_max_abs_difference": reference_delta,
    }


def _evaluate_fold(
    dataset: str,
    fold: str,
    X_dev: pd.DataFrame,
    y_dev: pd.Series,
    X_test: pd.DataFrame,
    y_test: np.ndarray,
    row_indices: np.ndarray,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    reference = _reference_predictions(dataset, fold)
    reference = reference.set_index("row_index")
    if set(reference.index.astype(int)) != set(np.asarray(row_indices, dtype=int).tolist()):
        raise AssertionError(f"Saved tuned OSEC test rows differ for {dataset}/{fold}")
    reference = reference.loc[np.asarray(row_indices, dtype=int)]
    if not np.array_equal(reference.y_true.to_numpy(dtype=int), np.asarray(y_test, dtype=int)):
        raise AssertionError(f"Saved tuned OSEC labels differ for {dataset}/{fold}")
    tuned_probability = reference.probability_tuned.to_numpy(dtype=float)
    selected_c, tuned_seconds = _selected_c(dataset, fold)

    start = time.perf_counter()
    fixed = make_fixed_osec(X_dev, seed)
    fixed.fit(X_dev, y_dev)
    fixed_probability = fixed.predict_proba(X_test)[:, 1]
    fixed_seconds = time.perf_counter() - start
    if not np.all(np.isfinite(fixed_probability)):
        raise AssertionError(f"fixed OSEC emitted non-finite probabilities: {dataset}/{fold}")

    metrics = [
        _score_rows(
            dataset,
            fold,
            "fixed_default_c_1",
            y_test,
            fixed_probability,
            1.0,
            fixed_seconds,
            None,
        ),
        _score_rows(
            dataset,
            fold,
            "nested_tuned_c",
            y_test,
            tuned_probability,
            selected_c,
            tuned_seconds,
            None,
        ),
    ]
    predictions: list[dict[str, Any]] = []
    for condition, probability in (
        ("fixed_default_c_1", fixed_probability),
        ("nested_tuned_c", tuned_probability),
    ):
        for index, label, value in zip(row_indices, y_test, probability, strict=True):
            predictions.append(
                {
                    "dataset": dataset,
                    "model": "osec",
                    "fold": fold,
                    "condition": condition,
                    "row_index": int(index),
                    "y_true": int(label),
                    "probability_positive": float(value),
                }
            )
    return metrics, predictions


def run() -> None:
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL_PREDICTIONS.parent.mkdir(parents=True, exist_ok=True)
    fold_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []

    for dataset in DATASETS:
        if dataset == "uci_spectf_heart":
            train = pd.read_csv(runner.PROCESSED / "uci_spectf_train.csv")
            test = pd.read_csv(runner.PROCESSED / "uci_spectf_test.csv")
            y_train = train.pop("OVERALL_DIAGNOSIS").astype(int)
            y_test = test.pop("OVERALL_DIAGNOSIS").to_numpy(dtype=int)
            model_index = runner.MODEL_VARIANTS.index("osec")
            seed = runner.SEED + 200 + model_index
            development_indices, _ = train_test_split(
                np.arange(len(train)),
                test_size=runner.CALIBRATION_FRACTION,
                random_state=seed,
                stratify=y_train,
            )
            X_dev = train.iloc[development_indices].copy()
            X_dev.attrs["categorical_columns"] = []
            rows, predictions = _evaluate_fold(
                dataset,
                "official_test",
                X_dev,
                y_train.iloc[development_indices],
                test,
                y_test,
                np.arange(len(test), dtype=int),
                seed,
            )
            fold_rows.extend(rows)
            prediction_rows.extend(predictions)
            print("OSEC ABLATION PASS uci_spectf_heart official_test", flush=True)
            continue

        if dataset in AFFECTED:
            X, y, spec, _, _, _ = duplicate_safe.load_deduplicated(dataset)
        else:
            X, y, spec = runner.load_task(dataset)
        categorical = list(spec["categorical"])
        outer = StratifiedKFold(
            n_splits=runner.OUTER_FOLDS,
            shuffle=True,
            random_state=runner.SEED,
        )
        for fold_number, (train_indices, test_indices) in enumerate(outer.split(X, y), start=1):
            fold = str(fold_number)
            fold_seed = runner.SEED + fold_number
            X_outer_train = runner.mark_categorical(X.iloc[train_indices], categorical)
            y_outer_train = y.iloc[train_indices]
            development_indices, _ = train_test_split(
                np.arange(len(X_outer_train)),
                test_size=runner.CALIBRATION_FRACTION,
                random_state=fold_seed,
                stratify=y_outer_train,
            )
            X_dev = runner.mark_categorical(X_outer_train.iloc[development_indices], categorical)
            y_dev = y_outer_train.iloc[development_indices]
            rows, predictions = _evaluate_fold(
                dataset,
                fold,
                X_dev,
                y_dev,
                X.iloc[test_indices].copy(),
                y.iloc[test_indices].to_numpy(dtype=int),
                np.asarray(test_indices, dtype=int),
                fold_seed,
            )
            fold_rows.extend(rows)
            prediction_rows.extend(predictions)
            print(f"OSEC ABLATION PASS {dataset} fold={fold}", flush=True)

    folds = pd.DataFrame(fold_rows)
    predictions = pd.DataFrame(prediction_rows)
    folds.to_csv(OUT / "fold_metrics.csv", index=False)
    predictions.to_csv(LOCAL_PREDICTIONS, index=False)
    summaries: list[dict[str, Any]] = []
    for (dataset, condition), subset in folds.groupby(["dataset", "condition"], sort=False):
        row: dict[str, Any] = {
            "dataset": dataset,
            "model": "osec",
            "condition": condition,
            "fold_count": int(len(subset)),
            "mean_selected_meta_estimator_c": float(subset.selected_meta_estimator_c.mean()),
            "mean_fit_or_search_seconds": float(subset.fit_or_search_seconds.mean()),
        }
        for metric in ("roc_auc", "pr_auc", "brier", "log_loss", "balanced_accuracy", "f1"):
            row[f"fold_mean_{metric}"] = float(subset[metric].mean())
            row[f"fold_sd_{metric}"] = (
                float(subset[metric].std(ddof=1)) if len(subset) > 1 else None
            )
        summaries.append(row)
    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT / "summary_metrics.csv", index=False)
    paired: list[dict[str, Any]] = []
    for dataset in DATASETS:
        subset = folds[folds.dataset.eq(dataset)]
        fixed = subset[subset.condition.eq("fixed_default_c_1")].set_index("fold")
        tuned = subset[subset.condition.eq("nested_tuned_c")].set_index("fold")
        common = fixed.index.intersection(tuned.index)
        for metric in ("roc_auc", "pr_auc", "brier", "log_loss", "balanced_accuracy", "f1"):
            delta = fixed.loc[common, metric].to_numpy(dtype=float) - tuned.loc[
                common, metric
            ].to_numpy(dtype=float)
            paired.append(
                {
                    "dataset": dataset,
                    "metric": metric,
                    "matched_fold_count": int(len(common)),
                    "fixed_minus_tuned_mean_delta": float(np.mean(delta)),
                    "fold_deltas": ";".join(f"{value:.8f}" for value in delta),
                    "interpretation": (
                        "descriptive matched-fold sensitivity; no significance test; "
                        "SPECTF has one official test split"
                    ),
                }
            )
    paired_frame = pd.DataFrame(paired)
    paired_frame.to_csv(OUT / "paired_fold_differences.csv", index=False)
    make_figure(summary)
    figure_path = OUT / "figures" / "osec_fixed_vs_tuned.png"
    manifest = {
        "study": "OSEC fixed-default versus inner-tuned meta-estimator C ablation",
        "status": "complete" if set(folds.dataset) == set(DATASETS) else "partial",
        "source_run_id": "20261107T202404Z",
        "datasets": list(DATASETS),
        "model": "unchanged OSEC stacking architecture; only final logistic C differs",
        "conditions": {
            "fixed_default_c_1": "final_estimator__C=1.0 without inner C search",
            "nested_tuned_c": "existing inner three-fold ROC-AUC search over C={0.1,1,10}",
        },
        "protocol": {
            "outer_partitions": "same saved seeded folds; SPECTF official 80/187 split",
            "calibration_partition": "reserved and excluded from fixed-model fitting",
            "hungary_va": "deduplicated before creating the matched folds",
            "test_labels_used_for_selection": False,
            "reference_tuned_probabilities": "loaded from saved source run or duplicate-safe rerun",
            "fold_comparisons": (
                "descriptive paired fold deltas; folds are not independent populations"
            ),
        },
        "counts": {
            "dataset_model_condition_fold_rows": len(folds),
            "dataset_condition_summaries": len(summary),
            "paired_deltas": len(paired_frame),
            "local_prediction_rows": len(predictions),
        },
        "inputs": {
            SOURCE_PREDICTIONS.relative_to(ROOT).as_posix(): sha256(SOURCE_PREDICTIONS),
            DEDUP_SAFE_PREDICTIONS.relative_to(ROOT).as_posix(): sha256(DEDUP_SAFE_PREDICTIONS),
            SOURCE_METRICS.relative_to(ROOT).as_posix(): sha256(SOURCE_METRICS),
            DEDUP_SAFE_METRICS.relative_to(ROOT).as_posix(): sha256(DEDUP_SAFE_METRICS),
        },
        "script": Path(__file__).relative_to(ROOT).as_posix(),
        "script_sha256": sha256(Path(__file__).resolve()),
        "software": {
            "python": sys.version,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "runtime_seconds": time.perf_counter() - started,
        "outputs": {
            "fold_metrics": "fold_metrics.csv",
            "summary_metrics": "summary_metrics.csv",
            "paired_fold_differences": "paired_fold_differences.csv",
            "predictions_local": LOCAL_PREDICTIONS.relative_to(ROOT).as_posix(),
            "figure": figure_path.relative_to(ROOT).as_posix(),
        },
    }
    for name in ("fold_metrics.csv", "summary_metrics.csv", "paired_fold_differences.csv"):
        manifest[f"{name}_sha256"] = sha256(OUT / name)
    manifest["predictions_sha256_local"] = sha256(LOCAL_PREDICTIONS)
    manifest["figure_sha256"] = sha256(figure_path)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))
    print(f"OSEC ablation outputs written to {OUT.relative_to(ROOT).as_posix()}")


def make_figure(summary: pd.DataFrame) -> None:
    figure_dir = OUT / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    datasets = list(summary.dataset.drop_duplicates())
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    colors = {"fixed_default_c_1": "#4477AA", "nested_tuned_c": "#CC6677"}
    labels = {"fixed_default_c_1": "Fixed C=1", "nested_tuned_c": "Inner-tuned C"}
    for axis, metric, title in (
        (axes[0], "fold_mean_roc_auc", "Outer-test ROC-AUC"),
        (axes[1], "fold_mean_brier", "Outer-test Brier score"),
    ):
        x = np.arange(len(datasets))
        width = 0.36
        for index, condition in enumerate(CONDITIONS):
            values = (
                summary[summary.condition.eq(condition)]
                .set_index("dataset")
                .reindex(datasets)[metric]
            )
            axis.bar(
                x + (index - 0.5) * width,
                values,
                width,
                color=colors[condition],
                label=labels[condition],
            )
        axis.set_xticks(x, datasets, rotation=45, ha="right")
        axis.set_title(title)
        axis.grid(axis="y", alpha=0.2)
    axes[0].set_ylim(0, 1)
    axes[1].set_ylim(bottom=0)
    axes[0].set_ylabel("Fold mean")
    axes[1].set_ylabel("Fold mean")
    axes[0].legend(frameon=False)
    fig.suptitle("OSEC meta-estimator tuning ablation")
    fig.savefig(figure_dir / "osec_fixed_vs_tuned.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    run()
