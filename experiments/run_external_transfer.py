"""Run the locked CD-XD-003 external-cohort transport stress test.

The model and reliability components are frozen using only the four UCI Heart
Disease source cohorts. The Z-Alizadeh Sani labels are used only after source
fitting, source-only probability calibration, and the OOD threshold are fixed.

Run from the repository root with:

    .venv/Scripts/python.exe experiments/run_external_transfer.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import zipfile
from collections import Counter
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import run_lodo_transfer as shared
import scipy
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ARCHIVE = ROOT / "data" / "external" / "uci_heart_disease_45" / "heart_disease.zip"
TARGET_ARCHIVE = ROOT / "data" / "external" / "uci_z_alizadeh_sani_412" / "z_alizadeh_sani.zip"
SOURCE_MANIFEST = ROOT / "data" / "manifests" / "uci_heart_disease_transfer_study.json"
TARGET_MANIFEST = ROOT / "data" / "manifests" / "uci_z_alizadeh_sani_external.json"
PROTOCOL = ROOT / "docs" / "TRANSFER_STUDY_PROTOCOL_20261105_ZAS.md"
OUTPUT = ROOT / "results" / "transfer_20261105_zas_external"
TARGET_WORKBOOK = "Z-Alizadeh sani dataset.xlsx"
SOURCE_ORDER = tuple(shared.COHORT_FILES)
SEED = 20261105
CALIBRATION_FRACTION = 0.20
FEATURES = ["age", "sex", "fbs"]
NUMERIC = ["age"]
CATEGORICAL = ["sex", "fbs"]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_target_features() -> tuple[pd.DataFrame, np.ndarray, dict[str, Any]]:
    with zipfile.ZipFile(TARGET_ARCHIVE) as archive:
        members = archive.namelist()
        if members != [TARGET_WORKBOOK]:
            raise ValueError(f"Unexpected workbook members in frozen target archive: {members}")
        workbook_bytes = archive.read(TARGET_WORKBOOK)
    workbook_sha = sha256_bytes(workbook_bytes)
    frame = pd.read_excel(BytesIO(workbook_bytes), engine="openpyxl")
    required = {"Age", "Sex", "FBS", "Cath"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Target workbook is missing required fields: {missing}")
    if frame.shape != (303, 56):
        raise ValueError(f"Unexpected Z-Alizadeh Sani shape {frame.shape}; expected (303, 56)")
    if frame.isna().any().any():
        raise ValueError("Target workbook contains missing cells; frozen protocol expects none")

    sex_values = set(frame["Sex"].astype(str).unique())
    if sex_values != {"Male", "Fmale"}:
        raise ValueError(f"Unexpected target Sex categories: {sorted(sex_values)}")
    target_values = set(frame["Cath"].astype(str).unique())
    if target_values != {"Cad", "Normal"}:
        raise ValueError(f"Unexpected target Cath categories: {sorted(target_values)}")

    external_sex = frame["Sex"].astype(str).map({"Male": "male", "Fmale": "female"})
    if external_sex.isna().any():
        raise ValueError("Target Sex recoding produced missing values")
    fbs_mg_dl = pd.to_numeric(frame["FBS"], errors="raise")
    features = pd.DataFrame(
        {
            "age": pd.to_numeric(frame["Age"], errors="raise").astype(float),
            "sex": external_sex,
            "fbs": np.where(fbs_mg_dl > 120, "gt_120_mg_dl", "le_120_mg_dl"),
        }
    )
    labels = frame["Cath"].map({"Normal": 0, "Cad": 1}).to_numpy(dtype=np.int8)
    target_audit = {
        "archive_member": TARGET_WORKBOOK,
        "workbook_sha256": workbook_sha,
        "rows": int(len(frame)),
        "columns_including_target": int(frame.shape[1]),
        "raw_predictor_columns": int(frame.shape[1] - 1),
        "missing_cells": int(frame.isna().sum().sum()),
        "raw_target_counts": {str(k): int(v) for k, v in sorted(Counter(frame["Cath"]).items())},
        "binary_target_counts": {str(k): int(v) for k, v in sorted(Counter(labels).items())},
        "sex_value_counts": {str(k): int(v) for k, v in sorted(Counter(frame["Sex"]).items())},
        "fbs_gt_120_count": int((fbs_mg_dl > 120).sum()),
        "fbs_at_or_below_120_count": int((fbs_mg_dl <= 120).sum()),
        "feature_names_after_harmonization": FEATURES,
        "feature_missing_counts": {str(k): int(v) for k, v in features.isna().sum().items()},
    }
    return features, labels, target_audit


def source_feature_map() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    source_cohorts, source_audit = shared.load_cohorts(SOURCE_ARCHIVE, zero_as_missing=False)
    mapped: dict[str, dict[str, Any]] = {}
    for cohort in SOURCE_ORDER:
        data = source_cohorts[cohort]
        frame = data["X"][["age", "sex", "fbs"]].copy()
        sex = pd.to_numeric(frame["sex"], errors="raise")
        fbs = pd.to_numeric(frame["fbs"], errors="raise")
        if not set(sex.dropna().unique()).issubset({0, 1}):
            raise ValueError(f"Unexpected sex encoding in source cohort {cohort}")
        if not set(fbs.dropna().unique()).issubset({0, 1}):
            raise ValueError(f"Unexpected fbs encoding in source cohort {cohort}")
        frame["sex"] = sex.map({0: "female", 1: "male"})
        frame["fbs"] = fbs.map({0: "le_120_mg_dl", 1: "gt_120_mg_dl"})
        frame["age"] = pd.to_numeric(frame["age"], errors="raise").astype(float)
        mapped[cohort] = {"X": frame[FEATURES], "y": data["y"], "row_index": data["row_index"]}
    return mapped, source_audit


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        [
            (
                "imputer",
                SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            ),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        [
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent", add_indicator=True, keep_empty_features=True
                ),
            ),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, NUMERIC),
            ("categorical", categorical_pipeline, CATEGORICAL),
        ],
        remainder="drop",
        sparse_threshold=0.0,
    )


def split_source_cohorts(
    cohorts: dict[str, dict[str, Any]],
) -> tuple[
    pd.DataFrame, np.ndarray, np.ndarray, pd.DataFrame, np.ndarray, np.ndarray, dict[str, Any]
]:
    fit_X: list[pd.DataFrame] = []
    fit_y: list[np.ndarray] = []
    fit_domains: list[np.ndarray] = []
    cal_X: list[pd.DataFrame] = []
    cal_y: list[np.ndarray] = []
    cal_domains: list[np.ndarray] = []
    splits: dict[str, Any] = {}
    for source_index, cohort in enumerate(SOURCE_ORDER):
        data = cohorts[cohort]
        indices = np.arange(len(data["y"]))
        fit_indices, cal_indices = train_test_split(
            indices,
            test_size=CALIBRATION_FRACTION,
            random_state=SEED + 100 + source_index,
            stratify=data["y"],
        )
        fit_X.append(data["X"].iloc[fit_indices].reset_index(drop=True))
        fit_y.append(data["y"][fit_indices])
        fit_domains.append(np.full(len(fit_indices), cohort, dtype=object))
        cal_X.append(data["X"].iloc[cal_indices].reset_index(drop=True))
        cal_y.append(data["y"][cal_indices])
        cal_domains.append(np.full(len(cal_indices), cohort, dtype=object))
        splits[cohort] = {
            "seed": SEED + 100 + source_index,
            "fit_row_indices": data["row_index"][fit_indices].astype(int).tolist(),
            "calibration_row_indices": data["row_index"][cal_indices].astype(int).tolist(),
            "fit_class_counts": {
                str(k): int(v) for k, v in sorted(Counter(data["y"][fit_indices]).items())
            },
            "calibration_class_counts": {
                str(k): int(v) for k, v in sorted(Counter(data["y"][cal_indices]).items())
            },
        }
    return (
        pd.concat(fit_X, ignore_index=True),
        np.concatenate(fit_y),
        np.concatenate(fit_domains),
        pd.concat(cal_X, ignore_index=True),
        np.concatenate(cal_y),
        np.concatenate(cal_domains),
        splits,
    )


def run_experiment(output_dir: Path) -> None:
    for path in (SOURCE_ARCHIVE, TARGET_ARCHIVE, SOURCE_MANIFEST, TARGET_MANIFEST, PROTOCOL):
        if not path.is_file():
            raise FileNotFoundError(f"Required frozen study input is missing: {path}")

    source_metadata = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    target_metadata = json.loads(TARGET_MANIFEST.read_text(encoding="utf-8"))
    source_archive_sha = sha256_file(SOURCE_ARCHIVE)
    target_archive_sha = sha256_file(TARGET_ARCHIVE)
    if source_archive_sha != source_metadata["archive_sha256"]:
        raise ValueError("UCI Heart Disease archive hash differs from its frozen manifest")
    if target_archive_sha != target_metadata["archive_sha256"]:
        raise ValueError("Z-Alizadeh Sani archive hash differs from its frozen manifest")

    source_cohorts, source_audit = source_feature_map()
    target_X, target_y, target_audit = load_target_features()
    if target_audit["workbook_sha256"] != target_metadata["workbook_sha256"]:
        raise ValueError("Z-Alizadeh Sani workbook hash differs from its frozen manifest")

    fit_X, fit_y, fit_domains, cal_X, cal_y, cal_domains, splits = split_source_cohorts(
        source_cohorts
    )
    fit_weights = shared.equal_domain_weights(fit_domains)
    cal_weights = shared.equal_domain_weights(cal_domains)

    preprocessor = build_preprocessor()
    fit_matrix = preprocessor.fit_transform(fit_X)
    cal_matrix = preprocessor.transform(cal_X)
    predictor = LogisticRegression(C=1.0, solver="liblinear", max_iter=5000, random_state=SEED)
    predictor.fit(fit_matrix, fit_y, sample_weight=fit_weights)

    raw_calibration_probabilities = predictor.predict_proba(cal_matrix)[:, 1]
    calibration_logits = np.log(
        np.clip(raw_calibration_probabilities, 1e-7, 1 - 1e-7)
        / np.clip(1 - raw_calibration_probabilities, 1e-7, 1.0)
    ).reshape(-1, 1)
    calibrator = LogisticRegression(C=1e6, solver="lbfgs", max_iter=5000, random_state=SEED)
    calibrator.fit(calibration_logits, cal_y, sample_weight=cal_weights)

    detector = IsolationForest(
        n_estimators=300,
        max_samples="auto",
        contamination="auto",
        random_state=SEED,
        n_jobs=1,
    )
    detector.fit(fit_matrix, sample_weight=fit_weights)
    calibration_anomaly_scores = -detector.score_samples(cal_matrix)
    ood_threshold = shared.weighted_quantile(calibration_anomaly_scores, cal_weights, 0.95)

    # Target features are transformed only after all source-only fits and thresholds are frozen.
    target_matrix = preprocessor.transform(target_X)
    raw_target_probabilities = predictor.predict_proba(target_matrix)[:, 1]
    target_logits = np.log(
        np.clip(raw_target_probabilities, 1e-7, 1 - 1e-7)
        / np.clip(1 - raw_target_probabilities, 1e-7, 1.0)
    ).reshape(-1, 1)
    calibrated_target_probabilities = calibrator.predict_proba(target_logits)[:, 1]
    target_anomaly_scores = -detector.score_samples(target_matrix)
    target_flags = target_anomaly_scores > ood_threshold

    # External labels enter only here, after the prediction and OOD pipeline is fixed.
    raw_metrics = shared.predictive_metrics(target_y, raw_target_probabilities)
    calibrated_metrics = shared.predictive_metrics(target_y, calibrated_target_probabilities)
    accepted = ~target_flags
    accepted_metrics = (
        shared.predictive_metrics(target_y[accepted], calibrated_target_probabilities[accepted])
        if accepted.any()
        else {"status": "no external rows accepted"}
    )
    flagged_metrics = (
        shared.predictive_metrics(
            target_y[target_flags], calibrated_target_probabilities[target_flags]
        )
        if target_flags.any()
        else {"status": "no external rows flagged"}
    )
    predictive_intervals = shared.bootstrap_predictive_intervals(
        target_y, raw_target_probabilities, calibrated_target_probabilities, seed=SEED + 1000
    )
    ood_interval = shared.bootstrap_ood_auc_interval(
        calibration_anomaly_scores, target_anomaly_scores, seed=SEED + 2000
    )
    domain_labels = np.concatenate(
        [np.zeros(len(calibration_anomaly_scores)), np.ones(len(target_anomaly_scores))]
    )
    domain_scores = np.concatenate([calibration_anomaly_scores, target_anomaly_scores])
    ood_auroc = float(shared.roc_auc_score(domain_labels, domain_scores))

    manifest = {
        "study_id": "CD-XD-003",
        "status": (
            "source_distinct_single_cohort_transport_stress_test_with_endpoint_boundary_mismatch"
        ),
        "run_timestamp_utc": datetime.now(UTC).isoformat(),
        "source_archive_path": str(SOURCE_ARCHIVE.relative_to(ROOT)),
        "source_archive_sha256": source_archive_sha,
        "source_manifest_sha256": sha256_file(SOURCE_MANIFEST),
        "target_archive_path": str(TARGET_ARCHIVE.relative_to(ROOT)),
        "target_archive_sha256": target_archive_sha,
        "target_workbook_sha256": target_audit["workbook_sha256"],
        "target_manifest_sha256": sha256_file(TARGET_MANIFEST),
        "protocol_path": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": sha256_file(PROTOCOL),
        "runner_path": str(Path(__file__).relative_to(ROOT)),
        "runner_sha256": sha256_file(Path(__file__)),
        "code_artifacts_sha256": {
            str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__)),
            str(Path(shared.__file__).resolve().relative_to(ROOT)): sha256_file(
                Path(shared.__file__).resolve()
            ),
        },
        "python_version": sys.version,
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scipy_version": scipy.__version__,
        "scikit_learn_version": sklearn.__version__,
        "source_cohort_order": list(SOURCE_ORDER),
        "source_cohort_audit": source_audit,
        "target_cohort_audit": target_audit,
        "feature_order": FEATURES,
        "feature_mapping": {
            "age": "Age in years; source age in years",
            "sex": "1=male, 0=female; external Male=1 and Fmale=0",
            "fbs": "binary FBS >120 mg/dL; apply same strict cutoff to external FBS",
        },
        "target_definition_mismatch": {
            "source": "UCI Heart Disease num=0 denotes <50%; num=1..4 denotes >50% narrowing",
            "external": "UCI Z-Alizadeh Sani Cath defines CAD as >=50% narrowing",
            "impact": (
                "near-equivalent but not identical endpoints; "
                "individual stenosis percentages unavailable"
            ),
        },
        "seed": SEED,
        "source_calibration_fraction": CALIBRATION_FRACTION,
        "bootstrap_replicates": shared.BOOTSTRAP_REPLICATES,
        "ece_bins": shared.ECE_BINS,
        "source_splits": splits,
        "source_fit_rows": int(len(fit_y)),
        "source_calibration_rows": int(len(cal_y)),
        "source_fit_class_counts": {str(k): int(v) for k, v in sorted(Counter(fit_y).items())},
        "source_calibration_class_counts": {
            str(k): int(v) for k, v in sorted(Counter(cal_y).items())
        },
        "source_fit_domain_counts": {
            str(k): int(v) for k, v in sorted(Counter(fit_domains).items())
        },
        "source_calibration_domain_counts": {
            str(k): int(v) for k, v in sorted(Counter(cal_domains).items())
        },
        "model": {
            "family": "logistic_regression",
            "C": 1.0,
            "solver": "liblinear",
            "max_iter": 5000,
        },
        "preprocessor": {
            "numeric": "source-fit median imputation and standard scaling",
            "categorical": "source-fit most-frequent imputation and one-hot encoding",
            "encoded_feature_count": int(fit_matrix.shape[1]),
        },
        "calibrator": {
            "method": "Platt logistic regression on source-only calibration logits",
            "C": 1e6,
            "intercept": float(calibrator.intercept_[0]),
            "slope": float(calibrator.coef_[0, 0]),
        },
        "raw_predictor_metrics": raw_metrics,
        "platt_calibrated_metrics": calibrated_metrics,
        "predictor_bootstrap_95_ci": predictive_intervals,
        "ood": {
            "method": "Isolation Forest fit on source-fit rows only",
            "score_definition": "negative score_samples; larger means more anomalous",
            "threshold_source_calibration_weighted_q95": float(ood_threshold),
            "source_calibration_false_alert_rate": float(
                np.average(calibration_anomaly_scores > ood_threshold, weights=cal_weights)
            ),
            "target_alert_rate": float(target_flags.mean()),
            "target_flagged_rows": int(target_flags.sum()),
            "target_accepted_rows": int(accepted.sum()),
            "target_coverage": float(accepted.mean()),
            "source_vs_target_ood_auroc": ood_auroc,
            "source_vs_target_ood_auroc_bootstrap_95_ci": ood_interval,
            "accepted_target_platt_metrics": accepted_metrics,
            "flagged_target_platt_metrics": flagged_metrics,
        },
        "interpretation_limits": [
            "One target site does not estimate general between-site variation.",
            "The endpoint threshold differs at exactly 50% stenosis.",
            "Public data contain no patient IDs for direct cross-dataset deduplication.",
            "Bootstrap intervals condition on the observed target class counts.",
            (
                "OOD flags and source-only probabilities are research outputs, not clinical "
                "safety signals."
            ),
        ],
    }

    external_predictions = pd.DataFrame(
        {
            "target_cohort": "z_alizadeh_sani",
            "row_index": np.arange(len(target_y)),
            "cath_raw": np.where(target_y == 1, "Cad", "Normal"),
            "y_binary": target_y,
            "raw_probability": raw_target_probabilities,
            "platt_probability": calibrated_target_probabilities,
            "ood_anomaly_score": target_anomaly_scores,
            "ood_threshold": ood_threshold,
            "ood_flag": target_flags,
            "accepted": accepted,
        }
    )
    source_calibration_predictions = pd.DataFrame(
        {
            "source_cohort": cal_domains,
            "row_index": np.concatenate(
                [
                    np.asarray(splits[cohort]["calibration_row_indices"], dtype=int)
                    for cohort in SOURCE_ORDER
                ]
            ),
            "y_binary": cal_y,
            "raw_probability": raw_calibration_probabilities,
            "platt_probability": calibrator.predict_proba(calibration_logits)[:, 1],
            "ood_anomaly_score": calibration_anomaly_scores,
            "ood_threshold": ood_threshold,
            "ood_flag": calibration_anomaly_scores > ood_threshold,
        }
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8"
    )
    external_predictions.to_csv(output_dir / "external_predictions.csv", index=False)
    source_calibration_predictions.to_csv(
        output_dir / "source_calibration_predictions.csv", index=False
    )
    print(f"Wrote CD-XD-003 manifest and predictions to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    with threadpool_limits(limits=1):
        run_experiment(arguments.output_dir)


if __name__ == "__main__":
    main()
