"""Compare source-calibration probability maps on held-out CARDIODIAG folds.

Calibration maps are fitted only on the saved calibration partition and scored
only on the corresponding held-out evaluation partition. Hungary and VA use
the duplicate-safe splits; their missing calibration probabilities are
reconstructed with the frozen split/model-selection protocol and checked
against saved duplicate-safe test predictions.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.optimize import minimize, minimize_scalar
from scipy.special import expit, logit
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

from cardiodiag.reliability import calibration_summary
from experiments import run_duplicate_safe_sensitivity as duplicate_safe
from experiments import run_multi_dataset_evaluation as runner

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "final_research_20261108" / "calibration_extension"
SOURCE_PREDICTIONS = (
    ROOT
    / "results"
    / "final_research_20261108"
    / "predictions_source_order"
    / "training_validation_predictions.csv"
)
DEDUP_SAFE_PREDICTIONS = duplicate_safe.LOCAL / "within_predictions.csv"
LOCAL_PREDICTIONS = (
    ROOT
    / "results"
    / "final_research_20261108"
    / "predictions"
    / "calibration_extension"
    / "calibration_predictions.csv"
)
METHODS = ("uncalibrated", "platt", "isotonic", "beta", "temperature")
DATASETS = (*runner.DATASET_SPECS, "uci_spectf_heart")
EPS = 1e-7


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def clip_probabilities(probability: np.ndarray) -> np.ndarray:
    values = np.asarray(probability, dtype=float)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError("probabilities must be a finite one-dimensional array")
    if np.any((values < 0) | (values > 1)):
        raise ValueError("probabilities must lie in [0, 1]")
    return np.clip(values, EPS, 1.0 - EPS)


def fit_calibrator(
    method: str, probability: np.ndarray, y_true: np.ndarray
) -> tuple[Callable[[np.ndarray], np.ndarray], dict[str, float | str]]:
    """Fit one calibration map using calibration-partition predictions only."""

    p = clip_probabilities(probability)
    y = np.asarray(y_true, dtype=int)
    if y.ndim != 1 or y.shape != p.shape or not np.all(np.isin(y, [0, 1])):
        raise ValueError("binary calibration labels must match the probability vector")
    if np.unique(y).size != 2:
        raise ValueError("calibration requires both outcome classes")
    if method == "uncalibrated":
        return lambda values: np.asarray(values, dtype=float), {"method": method}
    if method == "platt":
        model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=2000)
        model.fit(logit(p).reshape(-1, 1), y)
        return (
            lambda values: model.predict_proba(logit(clip_probabilities(values)).reshape(-1, 1))[
                :, 1
            ],
            {
                "method": method,
                "intercept": float(model.intercept_[0]),
                "slope": float(model.coef_[0, 0]),
            },
        )
    if method == "isotonic":
        model = IsotonicRegression(y_min=EPS, y_max=1.0 - EPS, out_of_bounds="clip").fit(p, y)
        return lambda values: model.predict(clip_probabilities(values)), {
            "method": method,
            "threshold_count": int(len(model.X_thresholds_)),
        }
    if method == "beta":
        design = np.column_stack([np.log(p), -np.log1p(-p)])

        def objective(parameters: np.ndarray) -> float:
            fitted = expit(design @ parameters[:2] + parameters[2])
            fitted = np.clip(fitted, EPS, 1.0 - EPS)
            return float(-np.mean(y * np.log(fitted) + (1 - y) * np.log1p(-fitted)))

        fitted = minimize(
            objective,
            x0=np.asarray([1.0, 1.0, 0.0]),
            method="L-BFGS-B",
            bounds=[(0.0, None), (0.0, None), (None, None)],
        )
        if not fitted.success:
            raise RuntimeError(f"beta calibration optimization failed: {fitted.message}")
        parameters = fitted.x.copy()

        def beta_map(values: np.ndarray) -> np.ndarray:
            clipped = clip_probabilities(values)
            features = np.column_stack([np.log(clipped), -np.log1p(-clipped)])
            return expit(features @ parameters[:2] + parameters[2])

        return beta_map, {
            "method": method,
            "a": float(parameters[0]),
            "b": float(parameters[1]),
            "intercept": float(parameters[2]),
        }
    if method == "temperature":
        logits = logit(p)

        def objective(log_temperature: float) -> float:
            calibrated = expit(logits / np.exp(log_temperature))
            calibrated = np.clip(calibrated, EPS, 1.0 - EPS)
            return float(-np.mean(y * np.log(calibrated) + (1 - y) * np.log1p(-calibrated)))

        fitted = minimize_scalar(objective, bounds=(-3.0, 3.0), method="bounded")
        if not fitted.success:
            raise RuntimeError(f"temperature scaling optimization failed: {fitted.message}")
        temperature = float(np.exp(fitted.x))
        return (
            lambda values: expit(logit(clip_probabilities(values)) / temperature),
            {"method": method, "temperature": temperature},
        )
    raise ValueError(f"unknown calibration method: {method}")


def _deduplicate_calibration_predictions() -> pd.DataFrame:
    """Recreate the omitted duplicate-safe calibration-side probabilities."""

    saved_test = pd.read_csv(DEDUP_SAFE_PREDICTIONS)
    records: list[dict[str, Any]] = []
    for dataset in ("uci_hungary", "uci_va_long_beach"):
        X, y, _, kept, _, _ = duplicate_safe.load_deduplicated(dataset)
        outer = StratifiedKFold(n_splits=runner.OUTER_FOLDS, shuffle=True, random_state=runner.SEED)
        for model in runner.MODEL_VARIANTS:
            for fold, (train_indices, test_indices) in enumerate(outer.split(X, y), start=1):
                fold_seed = runner.SEED + fold
                X_train = runner.mark_categorical(
                    X.iloc[train_indices], list(X.attrs.get("categorical_columns", []))
                )
                y_train = y.iloc[train_indices]
                dev_indices, cal_indices = train_test_split(
                    np.arange(len(X_train)),
                    test_size=runner.CALIBRATION_FRACTION,
                    random_state=fold_seed,
                    stratify=y_train,
                )
                X_dev = runner.mark_categorical(
                    X_train.iloc[dev_indices], list(X.attrs.get("categorical_columns", []))
                )
                X_cal = X_train.iloc[cal_indices].copy()
                y_cal = y_train.iloc[cal_indices].to_numpy(dtype=int)
                estimator = runner.fit_search(
                    X_dev, y_train.iloc[dev_indices], model, fold_seed
                ).best_estimator_
                cal_probability = estimator.predict_proba(X_cal)[:, 1]
                test_probability = estimator.predict_proba(X.iloc[test_indices])[:, 1]
                matched = saved_test[
                    saved_test.dataset.eq(dataset)
                    & saved_test.model.eq(model)
                    & saved_test.fold.eq(fold)
                ].set_index("row_index")
                test_indices_int = np.asarray(test_indices, dtype=int)
                if set(matched.index.astype(int)) != set(test_indices_int.tolist()):
                    raise AssertionError(
                        f"Duplicate-safe test rows differ for {dataset}/{model}/{fold}"
                    )
                saved_probabilities = matched.loc[
                    test_indices_int, "probability_positive"
                ].to_numpy(dtype=float)
                maximum_difference = float(np.max(np.abs(saved_probabilities - test_probability)))
                if maximum_difference > 1e-10:
                    raise AssertionError(
                        f"Recreated held-out predictions differ for {dataset}/{model}/{fold}: "
                        f"{maximum_difference}"
                    )
                for role, indices, labels, probabilities in (
                    ("conformal_calibration", train_indices[cal_indices], y_cal, cal_probability),
                    (
                        "outer_test",
                        test_indices_int,
                        y.iloc[test_indices_int].to_numpy(dtype=int),
                        test_probability,
                    ),
                ):
                    for index, label, prediction in zip(
                        indices, labels, probabilities, strict=True
                    ):
                        records.append(
                            {
                                "dataset": dataset,
                                "model": model,
                                "fold": str(fold),
                                "row_index": int(index),
                                "original_row_index": int(kept[int(index)]),
                                "role": role,
                                "y_true": int(label),
                                "probability_positive": float(prediction),
                                "duplicate_safe_protocol": True,
                                "reproduced_test_max_abs_difference": maximum_difference,
                            }
                        )
                print(
                    f"DUPLICATE-SAFE CALIBRATION PASS {dataset} {model} fold={fold} "
                    f"test_delta={maximum_difference:.2g}",
                    flush=True,
                )
    return pd.DataFrame(records)


def load_partitions() -> pd.DataFrame:
    source = pd.read_csv(SOURCE_PREDICTIONS)
    source = source[source.dataset.isin(DATASETS)].copy()
    source = source[
        source.role.isin(["conformal_calibration", "outer_test", "official_test"])
    ].copy()
    source["fold"] = source.fold.astype(str)
    source["duplicate_safe_protocol"] = False
    source["reproduced_test_max_abs_difference"] = np.nan
    clean = source[~source.dataset.isin(["uci_hungary", "uci_va_long_beach"])]
    affected = _deduplicate_calibration_predictions()
    all_rows = pd.concat([clean, affected], ignore_index=True)
    if set(all_rows.dataset.unique()) != set(DATASETS):
        raise AssertionError("Calibration comparison does not cover all registered tasks")
    return all_rows


def metric_values(y: np.ndarray, probability: np.ndarray) -> dict[str, float | int]:
    y = np.asarray(y, dtype=int)
    p = clip_probabilities(probability)
    calibration = calibration_summary(y, p, bins=10)
    return {
        "n": int(len(y)),
        "positive_count": int(y.sum()),
        "prevalence": float(y.mean()),
        "roc_auc": float(roc_auc_score(y, p)) if np.unique(y).size == 2 else float("nan"),
        "average_precision": float(average_precision_score(y, p)),
        "brier": float(np.mean((y - p) ** 2)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "ece_macro_10_equal_width": float(calibration["ece_uniform"]),
        "ece_weighted_10_equal_width": float(calibration["ece_weighted_uniform"]),
        "calibration_intercept": float(calibration["calibration_intercept"]),
        "calibration_slope": float(calibration["calibration_slope"]),
    }


def evaluate(
    partitions: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    fold_metrics: list[dict[str, Any]] = []
    predictions: list[dict[str, Any]] = []
    parameters: list[dict[str, Any]] = []
    group_columns = ["dataset", "model", "fold"]
    for (dataset, model, fold), group in partitions.groupby(group_columns, sort=False):
        calibration = group[group.role.eq("conformal_calibration")]
        evaluation = group[group.role.isin(["outer_test", "official_test"])]
        if calibration.empty or evaluation.empty:
            raise AssertionError(f"missing calibration/evaluation rows: {dataset}/{model}/{fold}")
        # SPECTF's official train and test files each use their own zero-based indices.
        if dataset != "uci_spectf_heart" and set(calibration.row_index.astype(int)) & set(
            evaluation.row_index.astype(int)
        ):
            raise AssertionError(f"calibration/test row overlap: {dataset}/{model}/{fold}")
        y_cal = calibration.y_true.to_numpy(dtype=int)
        p_cal = calibration.probability_positive.to_numpy(dtype=float)
        y_test = evaluation.y_true.to_numpy(dtype=int)
        p_test = evaluation.probability_positive.to_numpy(dtype=float)
        for method in METHODS:
            mapper, params = fit_calibrator(method, p_cal, y_cal)
            calibrated = clip_probabilities(mapper(p_test))
            fit_probability = clip_probabilities(mapper(p_cal))
            scores = metric_values(y_test, calibrated)
            cal_scores = metric_values(y_cal, fit_probability)
            fold_metrics.append(
                {
                    "dataset": dataset,
                    "model": model,
                    "fold": fold,
                    "method": method,
                    "calibration_n": len(calibration),
                    "calibration_positive_count": int(y_cal.sum()),
                    "evaluation_split": ",".join(sorted(evaluation.role.unique())),
                    "evaluation_n": len(evaluation),
                    "duplicate_safe_protocol": bool(group.duplicate_safe_protocol.any()),
                    "reproduced_test_max_abs_difference": (
                        float(group.reproduced_test_max_abs_difference.max())
                        if group.duplicate_safe_protocol.any()
                        else None
                    ),
                    **{f"test_{key}": value for key, value in scores.items()},
                    **{
                        f"calibration_resubstitution_{key}": value
                        for key, value in cal_scores.items()
                    },
                }
            )
            parameters.append(
                {
                    "dataset": dataset,
                    "model": model,
                    "fold": fold,
                    **params,
                }
            )
            for position, (_, row) in enumerate(evaluation.reset_index(drop=True).iterrows()):
                predictions.append(
                    {
                        "dataset": dataset,
                        "model": model,
                        "fold": fold,
                        "method": method,
                        "row_index": int(row.row_index),
                        "y_true": int(y_test[position]),
                        "probability_raw": float(p_test[position]),
                        "probability_calibrated": float(calibrated[position]),
                    }
                )
    folds = pd.DataFrame(fold_metrics)
    prediction_frame = pd.DataFrame(predictions)
    summaries: list[dict[str, Any]] = []
    for (dataset, model, method), fold_frame in folds.groupby(
        ["dataset", "model", "method"], sort=False
    ):
        subset = prediction_frame[
            prediction_frame.dataset.eq(dataset)
            & prediction_frame.model.eq(model)
            & prediction_frame.method.eq(method)
        ]
        pooled = metric_values(
            subset.y_true.to_numpy(dtype=int),
            subset.probability_calibrated.to_numpy(dtype=float),
        )
        row: dict[str, Any] = {
            "dataset": dataset,
            "model": model,
            "method": method,
            "fold_count": int(len(fold_frame)),
            "duplicate_safe_protocol": bool(fold_frame.duplicate_safe_protocol.any()),
            **{f"pooled_{key}": value for key, value in pooled.items()},
        }
        for metric in (
            "roc_auc",
            "average_precision",
            "brier",
            "log_loss",
            "ece_macro_10_equal_width",
            "ece_weighted_10_equal_width",
        ):
            values = fold_frame[f"test_{metric}"]
            row[f"fold_mean_{metric}"] = float(values.mean())
            row[f"fold_sd_{metric}"] = float(values.std(ddof=1)) if len(values) > 1 else None
        summaries.append(row)
    summary = pd.DataFrame(summaries)
    paired: list[dict[str, Any]] = []
    for dataset in DATASETS:
        for model in runner.MODEL_VARIANTS:
            frame = folds[folds.dataset.eq(dataset) & folds.model.eq(model)]
            baseline = frame[frame.method.eq("uncalibrated")].set_index("fold")
            for method in METHODS:
                if method == "uncalibrated":
                    continue
                current = frame[frame.method.eq(method)].set_index("fold")
                common = baseline.index.intersection(current.index)
                for metric in ("roc_auc", "brier", "log_loss", "ece_weighted_10_equal_width"):
                    delta = current.loc[common, f"test_{metric}"].to_numpy(
                        dtype=float
                    ) - baseline.loc[common, f"test_{metric}"].to_numpy(dtype=float)
                    paired.append(
                        {
                            "dataset": dataset,
                            "model": model,
                            "method": method,
                            "baseline": "uncalibrated",
                            "metric": metric,
                            "matched_fold_count": len(common),
                            "mean_fold_delta": float(np.mean(delta)),
                            "fold_deltas": ";".join(f"{item:.8f}" for item in delta),
                            "interpretation": (
                                "descriptive paired fold comparison; calibration is never selected "
                                "from evaluation labels and folds are not independent populations"
                            ),
                        }
                    )
    return folds, summary, pd.DataFrame(paired), prediction_frame, pd.DataFrame(parameters)


def make_figures(predictions: pd.DataFrame, summary: pd.DataFrame) -> list[str]:
    figure_dir = OUT / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    labels = {
        "uncalibrated": "Raw",
        "platt": "Platt",
        "isotonic": "Isotonic",
        "beta": "Beta",
        "temperature": "Temperature",
    }
    colors = dict(zip(METHODS, plt.cm.tab10.colors, strict=False))
    for dataset in DATASETS:
        fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=False)
        for axis, model in zip(axes.flat, runner.MODEL_VARIANTS, strict=True):
            subset = predictions[predictions.dataset.eq(dataset) & predictions.model.eq(model)]
            for method in METHODS:
                rows = subset[subset.method.eq(method)]
                observed, predicted = calibration_curve(
                    rows.y_true.to_numpy(dtype=int),
                    rows.probability_calibrated.to_numpy(dtype=float),
                    n_bins=10,
                    strategy="uniform",
                )
                axis.plot(
                    predicted,
                    observed,
                    marker="o",
                    linewidth=1.1,
                    markersize=3,
                    color=colors[method],
                    label=labels[method],
                )
            axis.plot([0, 1], [0, 1], linestyle="--", color="black", linewidth=0.8)
            axis.set_title(runner.MODEL_LABELS[model])
            axis.set(
                xlim=(0, 1),
                ylim=(0, 1),
                xlabel="Mean predicted probability",
                ylabel="Observed fraction",
            )
            axis.grid(alpha=0.2)
        axes.flat[-1].axis("off")
        handles, legend_labels = axes.flat[0].get_legend_handles_labels()
        fig.legend(
            handles,
            legend_labels,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.015),
            ncol=5,
        )
        fig.suptitle(f"Source-fitted calibration comparison: {dataset}")
        fig.tight_layout(rect=(0, 0.09, 1, 0.95))
        path = figure_dir / f"calibration_reliability_{dataset}.png"
        fig.savefig(path, dpi=180)
        plt.close(fig)
        paths.append(path.relative_to(ROOT).as_posix())

    raw = summary[summary.method.eq("uncalibrated")].set_index(["dataset", "model"])
    heatmap_values = np.empty((len(DATASETS), len(METHODS) - 1), dtype=float)
    methods = [method for method in METHODS if method != "uncalibrated"]
    for row_index, dataset in enumerate(DATASETS):
        for column_index, method in enumerate(methods):
            current = summary[summary.dataset.eq(dataset) & summary.method.eq(method)].set_index(
                "model"
            )
            baseline = raw.xs(dataset, level="dataset")
            common_models = current.index.intersection(baseline.index)
            heatmap_values[row_index, column_index] = float(
                (
                    current.loc[common_models, "pooled_brier"]
                    - baseline.loc[common_models, "pooled_brier"]
                ).mean()
            )
    limit = max(float(np.max(np.abs(heatmap_values))), 0.01)
    fig, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
    image = axis.imshow(
        heatmap_values,
        cmap="coolwarm",
        vmin=-limit,
        vmax=limit,
        aspect="auto",
    )
    axis.set_xticks(range(len(methods)), [method.title() for method in methods])
    axis.set_yticks(range(len(DATASETS)), list(DATASETS))
    axis.set_title("Pooled Brier change versus uncalibrated predictions")
    for row_index in range(len(DATASETS)):
        for column_index in range(len(methods)):
            axis.text(
                column_index,
                row_index,
                f"{heatmap_values[row_index, column_index]:+.3f}",
                ha="center",
                va="center",
                fontsize=8,
            )
    fig.colorbar(image, ax=axis, label="Brier difference (negative is lower)")
    heatmap_pdf = figure_dir / "calibration_brier_delta_by_task.pdf"
    fig.savefig(heatmap_pdf)
    fig.savefig(heatmap_pdf.with_suffix(".png"), dpi=180)
    plt.close(fig)
    paths.extend(
        [
            heatmap_pdf.relative_to(ROOT).as_posix(),
            heatmap_pdf.with_suffix(".png").relative_to(ROOT).as_posix(),
        ]
    )
    return paths


def main() -> None:
    started = time.perf_counter()
    if not SOURCE_PREDICTIONS.is_file() or not DEDUP_SAFE_PREDICTIONS.is_file():
        raise FileNotFoundError("Saved primary and duplicate-safe prediction inputs are required")
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL_PREDICTIONS.parent.mkdir(parents=True, exist_ok=True)
    partitions = load_partitions()
    folds, summary, paired, predictions, parameters = evaluate(partitions)
    prediction_input = partitions[
        partitions.role.isin(["conformal_calibration", "outer_test", "official_test"])
    ].copy()
    prediction_input.to_csv(
        LOCAL_PREDICTIONS.with_name("calibration_inputs_local.csv"), index=False
    )
    predictions.to_csv(LOCAL_PREDICTIONS, index=False)
    folds.to_csv(OUT / "fold_metrics.csv", index=False)
    summary.to_csv(OUT / "summary_metrics.csv", index=False)
    paired.to_csv(OUT / "paired_fold_differences.csv", index=False)
    parameters.to_csv(OUT / "fitted_calibration_parameters.csv", index=False)
    figures = make_figures(predictions, summary)
    manifest = {
        "study": "CARDIODIAG held-out calibration map comparison",
        "status": "complete",
        "source_run_id": "20261107T202404Z",
        "datasets": list(DATASETS),
        "models": list(runner.MODEL_VARIANTS),
        "methods": list(METHODS),
        "protocol": {
            "fit_partition": (
                "dedicated conformal_calibration predictions from the source-side saved split"
            ),
            "evaluation_partition": "matched outer_test; SPECTF official_test",
            "test_labels_used_for_calibrator_fit_or_method_selection": False,
            "hungary_va": (
                "exact predictor duplicates removed before partitions; missing calibration "
                "predictions recreated with the frozen nested split and model search; "
                "reconstructed test probabilities "
                "must match saved duplicate-safe outputs within 1e-10"
            ),
            "metrics": (
                "ROC-AUC, average precision, Brier, log loss, macro and weighted "
                "equal-width ECE, calibration intercept/slope"
            ),
            "fold_comparisons": (
                "descriptive paired deltas; folds are not independent populations"
            ),
            "important_limitation": (
                "the same calibration rows used to fit probability maps must not also be used to "
                "claim unchanged split-conformal coverage after recalibration; conformal results "
                "remain those of the original uncalibrated protocol"
            ),
            "isotonic_limitation": (
                "may overfit small calibration partitions; included as a sensitivity comparator"
            ),
        },
        "counts": {
            "fold_method_rows": len(folds),
            "summary_rows": len(summary),
            "paired_metric_deltas": len(paired),
            "prediction_rows_local": len(predictions),
            "reconstructed_duplicate_safe_rows": int(partitions.duplicate_safe_protocol.sum()),
        },
        "inputs": {
            SOURCE_PREDICTIONS.relative_to(ROOT).as_posix(): sha256(SOURCE_PREDICTIONS),
            DEDUP_SAFE_PREDICTIONS.relative_to(ROOT).as_posix(): sha256(DEDUP_SAFE_PREDICTIONS),
            "experiments/run_multi_dataset_evaluation.py": sha256(
                ROOT / "experiments/run_multi_dataset_evaluation.py"
            ),
            "experiments/run_duplicate_safe_sensitivity.py": sha256(
                ROOT / "experiments/run_duplicate_safe_sensitivity.py"
            ),
        },
        "script": Path(__file__).relative_to(ROOT).as_posix(),
        "script_sha256": sha256(Path(__file__).resolve()),
        "software": {
            "python": sys.version,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "outputs": {
            "fold_metrics": "fold_metrics.csv",
            "summary_metrics": "summary_metrics.csv",
            "paired_fold_differences": "paired_fold_differences.csv",
            "calibration_parameters": "fitted_calibration_parameters.csv",
            "local_predictions": LOCAL_PREDICTIONS.relative_to(ROOT).as_posix(),
            "figures": figures,
            "figure_sha256": {path: sha256(ROOT / path) for path in figures},
        },
        "runtime_seconds": time.perf_counter() - started,
    }
    for name in (
        "fold_metrics.csv",
        "summary_metrics.csv",
        "paired_fold_differences.csv",
        "fitted_calibration_parameters.csv",
    ):
        manifest[f"{name}_sha256"] = sha256(OUT / name)
    manifest["local_predictions_sha256"] = sha256(LOCAL_PREDICTIONS)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))
    print(f"Calibration extension written to {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
