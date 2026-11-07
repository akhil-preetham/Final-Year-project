"""Run a prespecified post-hoc age/sex/FBS ablation on frozen source splits.

All model fitting and Platt calibration use only the existing CD-XD-004 UCI
source partitions. AngioCAD labels are held aside until every subset has
produced predictions. This is an exploratory analysis of an already examined
target and must not be used to select a model or claim fresh validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import run_angiocad_transfer as angio
import run_external_transfer as transfer
import run_lodo_transfer as shared
from scipy.stats import ks_2samp
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "interpretability_posthoc_20261105" / "angiocad_feature_ablation"
FEATURE_ORDER = ("age", "sex", "fbs")
FEATURE_SUBSETS = (
    ("age",),
    ("sex",),
    ("age", "sex"),
    ("fbs",),
    ("age", "fbs"),
    ("sex", "fbs"),
    ("age", "sex", "fbs"),
)
REFERENCE_SUBSET = ("age", "sex")
BOOTSTRAP_REPLICATES = 1000


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_preprocessor(features: tuple[str, ...]) -> ColumnTransformer:
    transformers = []
    numeric = [name for name in features if name == "age"]
    categorical = [name for name in features if name in {"sex", "fbs"}]
    if numeric:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric,
            )
        )
    if categorical:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    [
                        (
                            "imputer",
                            SimpleImputer(strategy="most_frequent", add_indicator=True),
                        ),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical,
            )
        )
    if not transformers or any(name not in FEATURE_ORDER for name in features):
        raise ValueError(f"Invalid feature subset: {features}")
    return ColumnTransformer(transformers, remainder="drop", sparse_threshold=0.0)


def _fit_and_score_subset(
    features: tuple[str, ...],
    fit_X: pd.DataFrame,
    fit_y: np.ndarray,
    fit_domains: np.ndarray,
    cal_X: pd.DataFrame,
    cal_y: np.ndarray,
    cal_domains: np.ndarray,
    target_X: pd.DataFrame,
    seed: int,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    preprocessor = _build_preprocessor(features)
    selected = list(features)
    fit_matrix = preprocessor.fit_transform(fit_X.loc[:, selected])
    cal_matrix = preprocessor.transform(cal_X.loc[:, selected])
    target_matrix = preprocessor.transform(target_X.loc[:, selected])
    predictor = LogisticRegression(C=1.0, solver="liblinear", max_iter=5000, random_state=seed)
    predictor.fit(fit_matrix, fit_y, sample_weight=shared.equal_domain_weights(fit_domains))
    raw_cal = predictor.predict_proba(cal_matrix)[:, 1]
    raw_target = predictor.predict_proba(target_matrix)[:, 1]
    cal_logits = np.log(np.clip(raw_cal, 1e-7, 1 - 1e-7) / np.clip(1 - raw_cal, 1e-7, 1.0))
    target_logits = np.log(np.clip(raw_target, 1e-7, 1 - 1e-7) / np.clip(1 - raw_target, 1e-7, 1.0))
    calibrator = LogisticRegression(C=1e6, solver="lbfgs", max_iter=5000, random_state=seed)
    calibrator.fit(
        cal_logits.reshape(-1, 1), cal_y, sample_weight=shared.equal_domain_weights(cal_domains)
    )
    calibrated_target = calibrator.predict_proba(target_logits.reshape(-1, 1))[:, 1]
    metrics = {
        "features": list(features),
        "unit_status": (
            "assumed_mg_per_dl_sensitivity_only"
            if "fbs" in features
            else "fbs_excluded_age_sex_subset_age_year_mapping_unverified"
        ),
        "calibrator": {
            "intercept": float(calibrator.intercept_[0]),
            "slope": float(calibrator.coef_[0, 0]),
        },
        "source_only_fit": True,
        "target_labels_used_for_fit_calibration_or_thresholds": False,
    }
    return metrics, raw_target, calibrated_target


def _paired_bootstrap_delta(
    y: np.ndarray,
    candidate: np.ndarray,
    reference: np.ndarray,
    metric_name: str,
    seed: int,
) -> dict[str, float]:
    metric = shared.roc_auc_score if metric_name == "roc_auc" else shared.brier_score_loss
    class_indices = [np.flatnonzero(y == value) for value in (0, 1)]
    if any(len(indices) == 0 for indices in class_indices):
        raise ValueError("Paired class-stratified bootstrap requires both classes")
    point = float(metric(y, candidate) - metric(y, reference))
    rng = np.random.default_rng(seed)
    values = np.empty(BOOTSTRAP_REPLICATES, dtype=float)
    for index in range(BOOTSTRAP_REPLICATES):
        sample = np.concatenate(
            [rng.choice(indices, size=len(indices), replace=True) for indices in class_indices]
        )
        values[index] = float(
            metric(y[sample], candidate[sample]) - metric(y[sample], reference[sample])
        )
    return {
        "candidate_minus_age_sex_point": point,
        "conditional_class_stratified_bootstrap_lower_95": float(np.quantile(values, 0.025)),
        "conditional_class_stratified_bootstrap_upper_95": float(np.quantile(values, 0.975)),
        "replicates": BOOTSTRAP_REPLICATES,
        "multiplicity_adjusted": False,
    }


def _summarize_values(values: pd.Series) -> dict[str, Any]:
    numeric = pd.to_numeric(values, errors="coerce")
    return {
        "n": int(numeric.notna().sum()),
        "missing_rate": float(numeric.isna().mean()),
        "mean": float(numeric.mean()),
        "standard_deviation": float(numeric.std(ddof=1)),
        "median": float(numeric.median()),
        "q25": float(numeric.quantile(0.25)),
        "q75": float(numeric.quantile(0.75)),
    }


def _feature_distribution_audit(
    source_cohorts: dict[str, dict[str, Any]],
    target_X: pd.DataFrame,
    target_y: np.ndarray,
) -> dict[str, Any]:
    source_X = pd.concat(
        [cohort["X"].loc[:, list(FEATURE_ORDER)] for cohort in source_cohorts.values()]
    )
    source_y = np.concatenate([cohort["y"] for cohort in source_cohorts.values()])
    result: dict[str, Any] = {
        "analysis_scope": "descriptive; no target-feature or target-label adaptation",
        "source_rows": int(len(source_X)),
        "target_rows": int(len(target_X)),
        "source_positive_fraction": float(source_y.mean()),
        "target_positive_fraction_for_context_only": float(target_y.mean()),
        "feature_summaries": {},
        "target_feature_summary_by_label": {},
        "mappings": {
            "age": (
                "UCI age is in years. AngioCAD numeric age is provisionally treated as years, "
                "but its feature workbook does not state the unit."
            ),
            "sex": "AngioCAD male/female normalized to the UCI male/female convention.",
            "fbs": (
                "Not accepted as a unit-verified primary predictor. Existing source/target "
                "binary mapping assumes AngioCAD numeric FBS is mg/dL and thresholds >120."
            ),
            "26-50": (
                "This is an AngioCAD stenosis-label category, not an age interval. "
                "Patient age remains numeric; exact 50% stenosis cannot be isolated "
                "inside the negative 26-50 label bin."
            ),
        },
    }
    for feature in FEATURE_ORDER:
        source_values = source_X[feature]
        target_values = target_X[feature]
        if feature == "age":
            source_stats = _summarize_values(source_values)
            target_stats = _summarize_values(target_values)
            pooled_sd = float(
                np.sqrt(
                    (
                        pd.to_numeric(source_values).var(ddof=1)
                        + pd.to_numeric(target_values).var(ddof=1)
                    )
                    / 2
                )
            )
            target_minus_source = float(target_stats["mean"] - source_stats["mean"])
            result["feature_summaries"][feature] = {
                "source": source_stats,
                "target": target_stats,
                "standardized_mean_difference": (
                    target_minus_source / pooled_sd if pooled_sd else 0.0
                ),
                "ks_statistic": float(
                    ks_2samp(
                        pd.to_numeric(source_values).dropna(),
                        pd.to_numeric(target_values).dropna(),
                    ).statistic
                ),
                "interpretation": (
                    "covariate difference conditional on the age-as-years mapping; "
                    "no causal or clinical meaning"
                ),
            }
        else:
            categories = sorted(set(source_values.dropna()) | set(target_values.dropna()))
            source_shares = source_values.value_counts(normalize=True).reindex(
                categories, fill_value=0.0
            )
            target_shares = target_values.value_counts(normalize=True).reindex(
                categories, fill_value=0.0
            )
            result["feature_summaries"][feature] = {
                "source_missing_rate": float(source_values.isna().mean()),
                "target_missing_rate": float(target_values.isna().mean()),
                "source_category_share": {
                    str(key): float(value) for key, value in source_shares.items()
                },
                "target_category_share": {
                    str(key): float(value) for key, value in target_shares.items()
                },
                "total_variation_distance": float(
                    0.5 * np.abs(source_shares.to_numpy() - target_shares.to_numpy()).sum()
                ),
                "interpretation": (
                    "FBS distribution is conditional on an unverified unit assumption."
                    if feature == "fbs"
                    else "category share difference only"
                ),
            }
        result["target_feature_summary_by_label"][feature] = {}
        for label in (0, 1):
            values = target_values[target_y == label]
            if feature == "age":
                result["target_feature_summary_by_label"][feature][str(label)] = _summarize_values(
                    values
                )
            else:
                result["target_feature_summary_by_label"][feature][str(label)] = {
                    str(key): int(value) for key, value in values.value_counts(dropna=False).items()
                }
    result["target_feature_summary_by_label_note"] = (
        "Retrospective AngioCAD label associations are descriptive only; this target "
        "was previously examined. FBS associations inherit the undocumented-unit assumption."
    )
    return result


def run(output_dir: Path = OUTPUT) -> None:
    expected_outputs = {
        "run_manifest.json",
        "target_predictions.csv",
        "feature_distribution_audit.json",
        "reproduction_manifest.json",
    }
    if output_dir.exists():
        unexpected = {path.name for path in output_dir.iterdir()} - expected_outputs
        if unexpected:
            raise FileExistsError(
                f"Refusing to overwrite unexpected artifacts in {output_dir}: {sorted(unexpected)}"
            )
    source_cohorts, source_audit = transfer.source_feature_map()
    fit_X, fit_y, fit_domains, cal_X, cal_y, cal_domains, splits = transfer.split_source_cohorts(
        source_cohorts
    )
    target_X, target_y, target_ids, target_audit = angio.load_angiocad()

    # Labels are loaded for provenance but are withheld from every fit/calibration
    # call and are used for scoring only after every subset prediction is frozen.
    rows: dict[str, dict[str, Any]] = {}
    raw_predictions: dict[str, np.ndarray] = {}
    calibrated_predictions: dict[str, np.ndarray] = {}
    for index, features in enumerate(FEATURE_SUBSETS):
        key = "+".join(features)
        summary, raw, calibrated = _fit_and_score_subset(
            features,
            fit_X,
            fit_y,
            fit_domains,
            cal_X,
            cal_y,
            cal_domains,
            target_X,
            seed=transfer.SEED + 1000 + index,
        )
        rows[key] = summary
        raw_predictions[key] = raw
        calibrated_predictions[key] = calibrated

    # Score only after all seven prediction vectors have been created.
    reference_key = "+".join(REFERENCE_SUBSET)
    for key, features in zip(rows, FEATURE_SUBSETS, strict=True):
        rows[key]["raw_metrics"] = shared.predictive_metrics(target_y, raw_predictions[key])
        rows[key]["source_platt_metrics"] = shared.predictive_metrics(
            target_y, calibrated_predictions[key]
        )
        rows[key]["conditional_bootstrap_95_ci"] = shared.bootstrap_predictive_intervals(
            target_y,
            raw_predictions[key],
            calibrated_predictions[key],
            seed=transfer.SEED + 2000 + FEATURE_SUBSETS.index(features),
        )
    for key, features in zip(rows, FEATURE_SUBSETS, strict=True):
        if key == reference_key:
            continue
        rows[key]["paired_target_bootstrap_vs_age_sex"] = {
            "roc_auc": _paired_bootstrap_delta(
                target_y,
                calibrated_predictions[key],
                calibrated_predictions[reference_key],
                "roc_auc",
                seed=transfer.SEED + 3000 + FEATURE_SUBSETS.index(features),
            ),
            "brier_score": _paired_bootstrap_delta(
                target_y,
                calibrated_predictions[key],
                calibrated_predictions[reference_key],
                "brier_score",
                seed=transfer.SEED + 4000 + FEATURE_SUBSETS.index(features),
            ),
        }
    rows[reference_key]["paired_target_bootstrap_vs_age_sex"] = {
        "reference": True,
        "note": "No target-based model selection is permitted from these post-hoc comparisons.",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    feature_audit_path = output_dir / "feature_distribution_audit.json"
    feature_audit_path.write_text(
        json.dumps(
            _feature_distribution_audit(source_cohorts, target_X, target_y),
            indent=2,
            allow_nan=False,
        ),
        encoding="utf-8",
    )
    manifest = {
        "analysis_id": "CD-XD-004-FEATURE-ABLATION-POSTHOC",
        "status": "exploratory_posthoc_target_scoring",
        "interpretation": (
            "All seven nonempty subsets of the three already registered predictors were fixed "
            "before this run. Fits, imputation, scaling, and Platt calibration use only the "
            "existing UCI source fit/calibration partitions. AngioCAD was previously examined; "
            "these target-label metrics are descriptive, unadjusted for multiple comparisons, "
            "and are not fresh confirmation or a basis for model selection. FBS-containing "
            "subsets rely on an unverified mg/dL assumption and are sensitivity analyses only."
        ),
        "frozen_inputs": {
            "source_archive_sha256": _sha256(transfer.SOURCE_ARCHIVE),
            "target_features_sha256": _sha256(angio.FEATURES_FILE),
            "target_labels_sha256": _sha256(angio.LABELS_FILE),
            "protocol_sha256": _sha256(angio.PROTOCOL),
            "runner_sha256": _sha256(Path(__file__).resolve()),
        },
        "generated_artifacts": {
            "feature_distribution_audit_sha256": _sha256(feature_audit_path),
        },
        "feature_subsets_fixed_in_advance": [list(x) for x in FEATURE_SUBSETS],
        "fbs_excluded_reference_subset": list(REFERENCE_SUBSET),
        "age_unit_status": (
            "AngioCAD feature workbook does not state units; age-as-years is a provisional mapping."
        ),
        "source_fit_rows": int(len(fit_y)),
        "source_calibration_rows": int(len(cal_y)),
        "source_cohort_audit": source_audit,
        "target_cohort_audit": target_audit,
        "source_splits": splits,
        "features": rows,
        "software": {"numpy": np.__version__, "pandas": pd.__version__},
    }
    predictions = pd.DataFrame(
        {
            "public_record_id": target_ids,
            "label_for_scoring_only": target_y,
            **{
                f"{key}_raw_probability": probability
                for key, probability in raw_predictions.items()
            },
            **{
                f"{key}_source_platt_probability": probability
                for key, probability in calibrated_predictions.items()
            },
        }
    )
    predictions_path = output_dir / "target_predictions.csv"
    predictions.to_csv(predictions_path, index=False)
    manifest["generated_artifacts"]["target_predictions_sha256"] = _sha256(predictions_path)
    manifest_path = output_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8")
    reproduction_manifest = {
        "analysis_id": manifest["analysis_id"],
        "runner_sha256": manifest["frozen_inputs"]["runner_sha256"],
        "frozen_input_sha256": manifest["frozen_inputs"],
        "generated_artifact_sha256": {
            path.name: _sha256(path)
            for path in (manifest_path, predictions_path, feature_audit_path)
        },
    }
    (output_dir / "reproduction_manifest.json").write_text(
        json.dumps(reproduction_manifest, indent=2, allow_nan=False), encoding="utf-8"
    )
    print(f"Wrote post-hoc AngioCAD feature ablation to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    run(args.output_dir)
