"""Run matched, training-only selector and class-weight ablations.

All ablation candidates use the same outer partitions and inner folds. The
existing frozen experiment artifacts remain untouched. Row-level predictions
and resumable checkpoints are written beneath git-ignored results paths.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import GridSearchCV, StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cardiodiag.evaluation import evaluate_predictions  # noqa: E402
from cardiodiag.experiments import build_corrected_pipeline  # noqa: E402
from cardiodiag.feature_selection import one_shot_selection_mask  # noqa: E402

RUNNER_PATH = ROOT / "experiments" / "run_multi_dataset_evaluation.py"
_spec = importlib.util.spec_from_file_location("cardiodiag_multi_eval_runner", RUNNER_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to load experiment runner at {RUNNER_PATH}")
runner = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = runner
_spec.loader.exec_module(runner)

FINAL_RESULTS = ROOT / "results" / "final_research_20261108"
ASSIGNMENTS_PATH = (
    ROOT
    / "results"
    / "multi_dataset_evaluation_20261108"
    / "predictions"
    / "20261107T202404Z"
    / "fold_assignments.csv"
)
OUTPUT_DIR = FINAL_RESULTS / "ablation_extension"
LOCAL_PREDICTIONS_DIR = FINAL_RESULTS / "predictions" / "ablation_extension"
LOCAL_CHECKPOINT_DIR = FINAL_RESULTS / "checkpoints" / "ablation_extension"

TASKS = (
    "uci_cleveland",
    "uci_hungary",
    "uci_switzerland",
    "uci_va_long_beach",
    "uci_heart_failure_519",
    "uci_mi_complications_579",
    "uci_spectf_heart",
)
CANDIDATES = (
    ("none", "balanced"),
    ("none", "unweighted"),
    ("one_shot", "balanced"),
    ("one_shot", "unweighted"),
    ("stable", "balanced"),
    ("stable", "unweighted"),
)
C_GRID = [0.1, 1.0, 10.0]
# This prior script version completed all Cleveland fits before a summary-schema
# error. Model configuration and inputs are unchanged; only metric aggregation
# is corrected in this version.
COMPATIBLE_CHECKPOINT_SCRIPT_HASHES = {
    "b946873920cd82cef99ff71961cb2b38d9239c4919890eae3cc1251e8abef2e7"
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jsonable(value), indent=2, allow_nan=False) + "\n", encoding="utf-8")


class OneShotSelector(BaseEstimator, TransformerMixin):
    """Single training-fold relevance pass used as a matched selector baseline."""

    def __init__(
        self,
        relevance_threshold: float = 0.02,
        fallback_top_k: int = 8,
        random_state: int = 42,
    ) -> None:
        self.relevance_threshold = relevance_threshold
        self.fallback_top_k = fallback_top_k
        self.random_state = random_state

    def fit(self, X: Any, y: Any) -> OneShotSelector:
        matrix = np.asarray(X, dtype=float)
        self.support_ = one_shot_selection_mask(
            matrix,
            np.asarray(y, dtype=int),
            relevance_threshold=self.relevance_threshold,
            fallback_top_k=min(self.fallback_top_k, matrix.shape[1]),
            random_state=self.random_state,
        )
        self.n_features_in_ = matrix.shape[1]
        return self

    def transform(self, X: Any) -> np.ndarray:
        if not hasattr(self, "support_"):
            raise RuntimeError("OneShotSelector must be fitted before transform")
        matrix = np.asarray(X, dtype=float)
        if matrix.ndim != 2 or matrix.shape[1] != self.n_features_in_:
            raise ValueError("Input feature count does not match the fitted selector")
        return matrix[:, self.support_]

    def get_support(self) -> np.ndarray:
        if not hasattr(self, "support_"):
            raise RuntimeError("OneShotSelector must be fitted before get_support")
        return self.support_


def load_task_data(dataset: str) -> tuple[pd.DataFrame, pd.Series, dict[str, Any], list[int]]:
    X, y, spec = runner.load_task(dataset)
    original_rows = list(range(len(X)))
    if dataset in {"uci_hungary", "uci_va_long_beach"}:
        duplicate_groups = X.groupby(list(X.columns), dropna=False, sort=False).indices
        keep = np.ones(len(X), dtype=bool)
        for indices in duplicate_groups.values():
            indices = np.asarray(indices, dtype=int)
            if len(indices) <= 1:
                continue
            labels = set(y.iloc[indices].astype(int).tolist())
            if len(labels) != 1:
                raise ValueError(f"Conflicting-label exact duplicates in {dataset}: {indices}")
            keep[indices[1:]] = False
        original_rows = np.flatnonzero(keep).astype(int).tolist()
        X = runner.mark_categorical(X.iloc[keep].reset_index(drop=True), list(spec["categorical"]))
        y = y.iloc[keep].reset_index(drop=True)
        if X.duplicated(keep=False).any():
            raise AssertionError(f"Exact duplicates remain in duplicate-safe {dataset}")
    return X, y, spec, original_rows


def split_records(
    dataset: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, list[dict]]:
    """Return feature/label data and shared outer assignment rows."""
    if dataset == "uci_spectf_heart":
        train = pd.read_csv(runner.PROCESSED / "uci_spectf_train.csv")
        test = pd.read_csv(runner.PROCESSED / "uci_spectf_test.csv")
        y_train = train.pop("OVERALL_DIAGNOSIS").astype(int)
        y_test = test.pop("OVERALL_DIAGNOSIS").astype(int)
        train.attrs["categorical_columns"] = []
        test.attrs["categorical_columns"] = []
        assignments = pd.read_csv(ASSIGNMENTS_PATH)
        assignments = assignments[
            assignments.dataset.eq(dataset) & assignments.model.eq("logistic")
        ]
        folds = []
        for fold, rows in assignments.groupby("fold", sort=False):
            train_rows = rows[rows.split_role.eq("development")].row_index.astype(int).tolist()
            test_rows = rows[rows.split_role.eq("official_test")].row_index.astype(int).tolist()
            folds.append(
                {
                    "fold": str(fold),
                    "seed": int(rows.split_seed.iloc[0]),
                    "train_rows": train_rows,
                    "test_rows": test_rows,
                    "source_rows": train_rows + [len(train) + index for index in test_rows],
                    "X_train": train,
                    "y_train": y_train,
                    "X_test": test,
                    "y_test": y_test,
                    "official_test": True,
                }
            )
        return train, test, y_train, y_test, folds

    X, y, spec, original_rows = load_task_data(dataset)
    if dataset in {"uci_hungary", "uci_va_long_beach"}:
        assignment_rows = runner.build_nested_assignments(dataset, X, y)
        assignments = pd.DataFrame(assignment_rows)
    else:
        assignments = pd.read_csv(ASSIGNMENTS_PATH)
        assignments = assignments[assignments.dataset.eq(dataset) & assignments.model.isna()]
    folds = []
    for fold, rows in assignments.groupby("fold", sort=False):
        dev_rows = rows[rows.split_role.eq("development")].row_index.astype(int).tolist()
        test_role = "official_test" if rows.split_role.eq("official_test").any() else "outer_test"
        test_rows = rows[rows.split_role.eq(test_role)].row_index.astype(int).tolist()
        if not dev_rows or not test_rows:
            raise ValueError(f"Missing development/test assignments for {dataset} fold {fold}")
        folds.append(
            {
                "fold": str(fold),
                "seed": int(rows.split_seed.iloc[0]),
                "train_rows": dev_rows,
                "test_rows": test_rows,
                "source_rows": [original_rows[index] for index in dev_rows + test_rows],
                "X_train": X,
                "y_train": y,
                "X_test": X,
                "y_test": y,
                "official_test": test_role == "official_test",
            }
        )
    return X, X, y, y, folds


def make_pipeline(X_train: pd.DataFrame, dataset: str, selector: str, class_weight: str, seed: int):
    X_train = X_train.copy()
    if dataset == "uci_spectf_heart":
        X_train.attrs["categorical_columns"] = []
    base = build_corrected_pipeline(
        X_train,
        variant="logistic",
        seed=seed,
        use_stable_selector=(selector == "stable"),
    )
    if selector == "one_shot":
        one_shot = OneShotSelector(
            relevance_threshold=0.02,
            fallback_top_k=8,
            random_state=seed,
        )
        base.steps.insert(-1, ("one_shot_xaih_drc", one_shot))
    elif selector not in {"none", "stable"}:
        raise ValueError(f"Unsupported selector: {selector}")
    base.set_params(model__class_weight="balanced" if class_weight == "balanced" else None)
    return base


def selected_feature_count(estimator: Any, selector: str) -> int:
    dimension = len(estimator.named_steps["preprocessor"].get_feature_names_out())
    if selector == "stable":
        return int(estimator.named_steps["stable_xaih_drc"].get_support().sum())
    if selector == "one_shot":
        return int(estimator.named_steps["one_shot_xaih_drc"].get_support().sum())
    return dimension


def full_metrics(y_true: np.ndarray, probability: np.ndarray) -> dict[str, float | int]:
    from sklearn.metrics import cohen_kappa_score, matthews_corrcoef

    metrics = evaluate_predictions(y_true, probability)
    predicted = (probability >= 0.5).astype(int)
    tn = int(np.sum((y_true == 0) & (predicted == 0)))
    fp = int(np.sum((y_true == 0) & (predicted == 1)))
    fn = int(np.sum((y_true == 1) & (predicted == 0)))
    tp = int(np.sum((y_true == 1) & (predicted == 1)))
    metrics.update(
        {
            "mcc": float(matthews_corrcoef(y_true, predicted)),
            "cohen_kappa": float(cohen_kappa_score(y_true, predicted)),
            "false_positive_rate": float(fp / (fp + tn)) if fp + tn else 0.0,
            "false_negative_rate": float(fn / (fn + tp)) if fn + tp else 0.0,
        }
    )
    return metrics


def run_fold(dataset: str, candidate: tuple[str, str], fold: dict[str, Any]) -> dict[str, Any]:
    selector, class_weight = candidate
    X_train_all = fold["X_train"]
    y_train_all = fold["y_train"]
    X_train = X_train_all.iloc[fold["train_rows"]].copy()
    X_test = fold["X_test"].iloc[fold["test_rows"]].copy()
    y_train = y_train_all.iloc[fold["train_rows"]].astype(int)
    y_test = fold["y_test"].iloc[fold["test_rows"]].astype(int).to_numpy()
    if dataset == "uci_spectf_heart":
        X_train.attrs["categorical_columns"] = []
    seed = int(fold["seed"])
    estimator = make_pipeline(X_train, dataset, selector, class_weight, seed)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    search = GridSearchCV(
        estimator,
        param_grid={"model__C": C_GRID},
        scoring="roc_auc",
        cv=cv,
        n_jobs=1,
        refit=True,
        return_train_score=False,
        error_score="raise",
    )
    started = time.perf_counter()
    search.fit(X_train, y_train)
    fitted = search.best_estimator_
    probabilities = fitted.predict_proba(X_test)[:, 1]
    metrics = full_metrics(y_test, probabilities)
    train_probability = fitted.predict_proba(X_train)[:, 1]
    train_metrics = evaluate_predictions(y_train.to_numpy(), train_probability)
    return {
        "dataset": dataset,
        "fold": fold["fold"],
        "selector": selector,
        "class_weight": class_weight,
        "candidate": f"{selector}__{class_weight}",
        "outer_protocol": "official SPECTF test" if fold["official_test"] else "saved outer test",
        "seed": seed,
        "development_n": len(X_train),
        "test_n": len(X_test),
        "test_positive_count": int(y_test.sum()),
        "best_C": float(search.best_params_["model__C"]),
        "inner_cv_roc_auc": float(search.best_score_),
        "selected_feature_count": selected_feature_count(fitted, selector),
        "resubstitution_train_roc_auc": float(train_metrics["roc_auc"]),
        "train_minus_test_roc_auc": float(train_metrics["roc_auc"] - metrics["roc_auc"]),
        "runtime_seconds": float(time.perf_counter() - started),
        "y_true": y_test.astype(int).tolist(),
        "probability_positive": probabilities.astype(float).tolist(),
        "test_row_indices": fold["test_rows"],
        "source_row_indices": fold["source_rows"][len(fold["train_rows"]) :],
        **metrics,
    }


def checkpoint_path(dataset: str, candidate: tuple[str, str], fold: str) -> Path:
    selector, class_weight = candidate
    safe_fold = fold.replace("/", "_")
    return LOCAL_CHECKPOINT_DIR / f"{dataset}__{selector}__{class_weight}__{safe_fold}.json"


def load_or_run_fold(
    dataset: str,
    candidate: tuple[str, str],
    fold: dict[str, Any],
    source_hashes: dict[str, str],
    script_hash: str,
) -> dict[str, Any]:
    path = checkpoint_path(dataset, candidate, fold["fold"])
    if path.exists():
        cached = json.loads(path.read_text(encoding="utf-8"))
        if (
            cached.get("script_sha256") not in {script_hash, *COMPATIBLE_CHECKPOINT_SCRIPT_HASHES}
            or cached.get("source_hashes") != source_hashes
            or cached.get("seed") != int(fold["seed"])
        ):
            raise RuntimeError(f"Checkpoint provenance mismatch: {path}")
        return cached["result"]
    result = run_fold(dataset, candidate, fold)
    write_json(
        path,
        {
            "script_sha256": script_hash,
            "source_hashes": source_hashes,
            "seed": int(fold["seed"]),
            "result": result,
        },
    )
    return result


def summarize(
    fold_frame: pd.DataFrame, prediction_frame: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    metric_names = (
        "accuracy",
        "balanced_accuracy",
        "precision",
        "recall",
        "specificity",
        "f1",
        "roc_auc",
        "pr_auc",
        "brier",
        "ece_uniform",
        "mcc",
        "cohen_kappa",
        "false_positive_rate",
        "false_negative_rate",
    )
    for (dataset, selector, class_weight), folds in fold_frame.groupby(
        ["dataset", "selector", "class_weight"], sort=False
    ):
        preds = prediction_frame[
            prediction_frame.dataset.eq(dataset)
            & prediction_frame.selector.eq(selector)
            & prediction_frame.class_weight.eq(class_weight)
        ]
        y = preds.y_true.to_numpy(dtype=int)
        p = preds.probability_positive.to_numpy(dtype=float)
        pooled = full_metrics(y, p)
        row: dict[str, Any] = {
            "dataset": dataset,
            "selector": selector,
            "class_weight": class_weight,
            "candidate": f"{selector}__{class_weight}",
            "fold_count": len(folds),
            "n_evaluated": len(preds),
            "mean_selected_feature_count": float(folds.selected_feature_count.mean()),
            "mean_runtime_seconds": float(folds.runtime_seconds.mean()),
            "mean_inner_cv_roc_auc": float(folds.inner_cv_roc_auc.mean()),
            "mean_train_minus_test_roc_auc": float(folds.train_minus_test_roc_auc.mean()),
            "pooled_roc_auc": float(pooled["roc_auc"]),
            "pooled_pr_auc": float(pooled["pr_auc"]),
            "pooled_brier": float(pooled["brier"]),
        }
        for name in metric_names:
            row[f"fold_mean_{name}"] = float(folds[name].mean())
            row[f"fold_sd_{name}"] = float(folds[name].std(ddof=1)) if len(folds) > 1 else None
            row[f"pooled_{name}"] = float(pooled[name])
        summary_rows.append(row)
    summary = pd.DataFrame(summary_rows)

    comparisons = []
    compare_to = {
        "none__unweighted": "none__balanced",
        "one_shot__balanced": "none__balanced",
        "one_shot__unweighted": "none__unweighted",
        "stable__balanced": "none__balanced",
        "stable__unweighted": "none__unweighted",
    }
    for dataset in fold_frame.dataset.unique():
        dataset_folds = fold_frame[fold_frame.dataset.eq(dataset)]
        for candidate, baseline in compare_to.items():
            sel, weight = candidate.split("__")
            base_sel, base_weight = baseline.split("__")
            candidate_rows = dataset_folds[
                dataset_folds.selector.eq(sel) & dataset_folds.class_weight.eq(weight)
            ].set_index("fold")
            baseline_rows = dataset_folds[
                dataset_folds.selector.eq(base_sel) & dataset_folds.class_weight.eq(base_weight)
            ].set_index("fold")
            common = candidate_rows.index.intersection(baseline_rows.index)
            if not len(common):
                continue
            auc_delta = candidate_rows.loc[common, "roc_auc"].to_numpy(
                dtype=float
            ) - baseline_rows.loc[common, "roc_auc"].to_numpy(dtype=float)
            brier_delta = candidate_rows.loc[common, "brier"].to_numpy(
                dtype=float
            ) - baseline_rows.loc[common, "brier"].to_numpy(dtype=float)
            comparisons.append(
                {
                    "dataset": dataset,
                    "candidate": candidate,
                    "baseline": baseline,
                    "matched_fold_count": len(common),
                    "fold_auc_deltas": ";".join(f"{v:.8f}" for v in auc_delta),
                    "mean_fold_auc_delta": float(np.mean(auc_delta)),
                    "mean_fold_brier_delta": float(np.mean(brier_delta)),
                    "interpretation": (
                        "descriptive paired fold sensitivity; CV folds are not "
                        "independent populations"
                    ),
                }
            )
    return summary, pd.DataFrame(comparisons)


def make_figures(summary: pd.DataFrame, comparisons: pd.DataFrame) -> None:
    figure_dir = OUTPUT_DIR / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    datasets = list(summary.dataset.drop_duplicates())
    candidate_order = [f"{selector}__{weight}" for selector, weight in CANDIDATES]
    pretty = {
        "none__balanced": "None / balanced",
        "none__unweighted": "None / unweighted",
        "one_shot__balanced": "One-shot / balanced",
        "one_shot__unweighted": "One-shot / unweighted",
        "stable__balanced": "Stable / balanced",
        "stable__unweighted": "Stable / unweighted",
    }
    fig, axes = plt.subplots(4, 2, figsize=(13, 16), constrained_layout=True)
    axes_flat = axes.ravel()
    for axis, dataset in zip(axes_flat, datasets, strict=False):
        subset = (
            summary[summary.dataset.eq(dataset)].set_index("candidate").reindex(candidate_order)
        )
        axis.bar(range(len(candidate_order)), subset.fold_mean_roc_auc)
        axis.set_title(dataset)
        axis.set_ylabel("Mean outer-test ROC-AUC")
        axis.set_ylim(0, 1)
        axis.set_xticks(
            range(len(candidate_order)),
            [pretty[key] for key in candidate_order],
            rotation=35,
            ha="right",
            fontsize=8,
        )
        axis.grid(axis="y", alpha=0.2)
    for axis in axes_flat[len(datasets) :]:
        axis.set_visible(False)
    fig.suptitle("Matched logistic feature-selection and class-weight ablation")
    fig.savefig(figure_dir / "matched_ablation_auc.png", dpi=180)
    plt.close(fig)

    selected = comparisons[comparisons.candidate.str.contains("one_shot|stable", regex=True)]
    piv = selected.pivot(index="dataset", columns="candidate", values="mean_fold_auc_delta")
    fig, axis = plt.subplots(figsize=(10, 5), constrained_layout=True)
    image = axis.imshow(
        piv.to_numpy(dtype=float),
        cmap="coolwarm",
        vmin=-0.15,
        vmax=0.15,
        aspect="auto",
    )
    axis.set_xticks(range(len(piv.columns)), piv.columns, rotation=30, ha="right")
    axis.set_yticks(range(len(piv.index)), piv.index)
    axis.set_title("Paired mean fold ROC-AUC change versus no-selection baseline")
    fig.colorbar(image, ax=axis, label="AUC difference")
    fig.savefig(figure_dir / "matched_ablation_auc_delta.png", dpi=180)
    plt.close(fig)


def run(datasets: list[str]) -> None:
    if not ASSIGNMENTS_PATH.exists():
        raise FileNotFoundError(f"Frozen fold assignments are missing: {ASSIGNMENTS_PATH}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    assignments_hash = sha256(ASSIGNMENTS_PATH)
    script_hash = sha256(Path(__file__).resolve())
    all_fold_rows = []
    all_prediction_rows = []
    input_hashes: dict[str, dict[str, str]] = {}

    for dataset in datasets:
        if dataset == "uci_spectf_heart":
            input_paths = [
                runner.PROCESSED / "uci_spectf_train.csv",
                runner.PROCESSED / "uci_spectf_test.csv",
            ]
        else:
            input_paths = [Path(runner.DATASET_SPECS[dataset]["path"])]
        source_hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in input_paths}
        input_hashes[dataset] = source_hashes
        _, _, _, _, folds = split_records(dataset)
        for candidate in CANDIDATES:
            for fold in folds:
                result = load_or_run_fold(dataset, candidate, fold, source_hashes, script_hash)
                metrics = {
                    key: value
                    for key, value in result.items()
                    if key
                    not in {
                        "y_true",
                        "probability_positive",
                        "test_row_indices",
                        "source_row_indices",
                    }
                }
                metrics.update(
                    full_metrics(
                        np.asarray(result["y_true"], dtype=int),
                        np.asarray(result["probability_positive"], dtype=float),
                    )
                )
                all_fold_rows.append(metrics)
                for local_pos, (label, probability) in enumerate(
                    zip(result["y_true"], result["probability_positive"], strict=True)
                ):
                    all_prediction_rows.append(
                        {
                            "dataset": dataset,
                            "fold": result["fold"],
                            "selector": result["selector"],
                            "class_weight": result["class_weight"],
                            "row_index": result["test_row_indices"][local_pos],
                            "source_row_index": result["source_row_indices"][local_pos],
                            "y_true": label,
                            "probability_positive": probability,
                        }
                    )
                print(
                    f"ABLATION PASS {dataset} {candidate[0]} {candidate[1]} fold={fold['fold']}",
                    flush=True,
                )

    folds_frame = pd.DataFrame(all_fold_rows)
    predictions_frame = pd.DataFrame(all_prediction_rows)
    summary, comparisons = summarize(folds_frame, predictions_frame)
    folds_output = OUTPUT_DIR / "fold_metrics.csv"
    summary_output = OUTPUT_DIR / "summary_metrics.csv"
    comparisons_output = OUTPUT_DIR / "paired_fold_differences.csv"
    predictions_output = LOCAL_PREDICTIONS_DIR / "out_of_fold_predictions.csv"
    folds_frame.to_csv(folds_output, index=False)
    summary.to_csv(summary_output, index=False)
    comparisons.to_csv(comparisons_output, index=False)
    predictions_frame.to_csv(predictions_output, index=False)
    make_figures(summary, comparisons)

    manifest = {
        "study": "CARDIODIAG matched selector and class-weight ablation extension",
        "status": "complete" if set(datasets) == set(TASKS) else "partial_dataset_subset",
        "generated_local_date": time.strftime("%Y-%m-%d"),
        "source_run_id": "20261107T202404Z",
        "data_source_hashes": input_hashes,
        "fold_assignments": ASSIGNMENTS_PATH.relative_to(ROOT).as_posix(),
        "fold_assignments_sha256": assignments_hash,
        "script": Path(__file__).relative_to(ROOT).as_posix(),
        "script_sha256": script_hash,
        "source_code_hashes": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in (
                ROOT / "src" / "cardiodiag" / "experiments.py",
                ROOT / "src" / "cardiodiag" / "feature_selection.py",
                ROOT / "src" / "cardiodiag" / "preprocessing.py",
                ROOT / "src" / "cardiodiag" / "models.py",
                RUNNER_PATH,
            )
        },
        "software": {
            "python": sys.version,
            "scikit_learn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
        "datasets": datasets,
        "candidate_grid": [
            {"selector": selector, "class_weight": weight} for selector, weight in CANDIDATES
        ],
        "protocol": {
            "outer_partitions": (
                "reuses frozen 3-fold development/calibration/test assignments; "
                "SPECTF reuses official test split"
            ),
            "hungary_and_va": (
                "exact predictor duplicates removed before regenerating shared seeded folds"
            ),
            "inner_validation": "3-fold stratified shuffled CV within development rows only",
            "selection_metric": "ROC-AUC",
            "logistic_C_grid": C_GRID,
            "one_shot_selector": (
                "one pass of the existing training-only relevance score; threshold 0.02, "
                "fallback at most 8 features"
            ),
            "stable_selector": (
                "existing StableXAIHDRC with default 6 resamples and training-only "
                "relevance; no test data used"
            ),
            "class_weight_ablation": (
                "downstream LogisticRegression class_weight balanced versus None; "
                "the selector's internal relevance model remains balanced by definition"
            ),
            "target_labels_used_for_selection": False,
            "fold_comparisons": (
                "descriptive paired fold deltas; folds are not treated as independent populations"
            ),
            "calibration_rows": (
                "kept outside model fitting as in the saved partition; this ablation "
                "reports classification metrics only"
            ),
        },
        "counts": {
            "datasets": len(datasets),
            "candidates": len(CANDIDATES),
            "fold_rows": len(folds_frame),
            "summary_rows": len(summary),
            "paired_comparisons": len(comparisons),
            "prediction_rows_local_only": len(predictions_frame),
        },
        "outputs": {
            "fold_metrics": folds_output.relative_to(ROOT).as_posix(),
            "summary_metrics": summary_output.relative_to(ROOT).as_posix(),
            "paired_fold_differences": comparisons_output.relative_to(ROOT).as_posix(),
            "figures": (OUTPUT_DIR / "figures").relative_to(ROOT).as_posix(),
            "row_level_predictions": predictions_output.relative_to(ROOT).as_posix(),
            "row_level_predictions_are_git_ignored": True,
        },
        "limitations": [
            (
                "The historical target-aware or leakage-prone preprocessing is not recreated "
                "as a comparator because its exact fold-level protocol is unavailable and "
                "it would not be a valid evaluation baseline."
            ),
            (
                "The experiment isolates LogisticRegression class weighting and feature "
                "selection; class-weight effects are not generalized to every classifier."
            ),
            (
                "The result is a sensitivity study on legacy, previously examined datasets, "
                "not independent external validation."
            ),
        ],
    }
    for key, path in (
        ("fold_metrics_sha256", folds_output),
        ("summary_metrics_sha256", summary_output),
        ("paired_fold_differences_sha256", comparisons_output),
        ("predictions_sha256_local", predictions_output),
    ):
        manifest[key] = sha256(path)
    write_json(OUTPUT_DIR / "manifest.json", manifest)
    print(json.dumps(manifest["counts"], indent=2))
    print(f"Ablation outputs written to {OUTPUT_DIR.relative_to(ROOT).as_posix()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets", nargs="+", choices=TASKS, default=list(TASKS))
    args = parser.parse_args()
    run(list(dict.fromkeys(args.datasets)))


if __name__ == "__main__":
    main()
