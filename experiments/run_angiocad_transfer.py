"""Run the locked CD-XD-004 AngioCAD external validation.

All fitted components are trained or calibrated using only the four UCI Heart
Disease source cohorts. AngioCAD labels are used only after source fitting and
threshold selection.

Run from the repository root with:

    .venv/Scripts/python.exe experiments/run_angiocad_transfer.py
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import run_external_transfer as transfer
import run_lodo_transfer as shared
import scipy
import sklearn
from openpyxl import load_workbook
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = ROOT / "data" / "external" / "angiocad_zenodo_15826856"
FEATURES_FILE = TARGET_DIR / "AngioCAD_Features.xlsx"
LABELS_FILE = TARGET_DIR / "AngioCAD_Labels.xlsx"
SOURCE_MANIFEST = ROOT / "data" / "manifests" / "uci_heart_disease_transfer_study.json"
TARGET_MANIFEST = ROOT / "data" / "manifests" / "angiocad_external.json"
PROTOCOL = ROOT / "docs" / "TRANSFER_STUDY_PROTOCOL_20261105_ANGIOCAD.md"
OUTPUT = ROOT / "results" / "transfer_20261105_angiocad_external"
SEED = transfer.SEED
SOURCE_ORDER = transfer.SOURCE_ORDER
FEATURES = transfer.FEATURES
ARTERY_COLUMNS = [
    "LM",
    "Prox LAD",
    "Mid LAD",
    "Dist LAD",
    "1st dig",
    "2nd dig",
    "Prox LCX",
    "Mid LCX",
    "Dist LCX",
    "OM",
    "Prox RCA",
    "Mid RCA",
    "Dist RCA",
    "PDA",
    "PLB",
]
POSITIVE_STENOSIS_BINS = {"51-75", "76-90", "91-99", "100"}
NEGATIVE_STENOSIS_BINS = {"NL", "1-25", "26-50"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_angiocad() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, dict[str, Any]]:
    features_raw = pd.read_excel(FEATURES_FILE, engine="openpyxl")
    labels_raw = pd.read_excel(LABELS_FILE, engine="openpyxl")
    feature_sheet = load_workbook(FEATURES_FILE, read_only=True, data_only=True)["Main"]
    label_sheet = load_workbook(LABELS_FILE, read_only=True, data_only=True)["Labels"]
    expected_feature_columns = {"ID", "Age", "Sex", "FBS"}
    expected_label_columns = {"ID", *ARTERY_COLUMNS}
    if not expected_feature_columns.issubset(features_raw.columns):
        raise ValueError("AngioCAD clinical features workbook is missing required fields")
    if not expected_label_columns.issubset(labels_raw.columns):
        raise ValueError("AngioCAD artery labels workbook is missing required fields")
    if features_raw.shape != (377, 60) or labels_raw.shape != (413, 18):
        raise ValueError(
            f"Unexpected AngioCAD workbook shapes: {features_raw.shape}, {labels_raw.shape}"
        )

    features = features_raw.loc[features_raw["ID"].notna()].copy()
    labels = labels_raw.loc[labels_raw["ID"].notna()].copy()
    if features["ID"].duplicated().any() or labels["ID"].duplicated().any():
        raise ValueError("AngioCAD workbooks contain duplicate nonblank IDs")
    if len(features) != 377 or len(labels) != 413:
        raise ValueError("AngioCAD nonblank-ID counts differ from the frozen schema audit")
    if labels[ARTERY_COLUMNS].isna().any().any():
        raise ValueError("A nonblank AngioCAD patient row has missing artery labels")

    matched = (
        features[["ID", "Age", "Sex", "FBS"]]
        .merge(
            labels[["ID", *ARTERY_COLUMNS]],
            on="ID",
            how="inner",
            validate="one_to_one",
            sort=False,
        )
        .sort_values("ID", kind="stable")
    )
    if len(matched) != 377 or not set(features["ID"]).issubset(set(labels["ID"])):
        raise ValueError("AngioCAD feature/label IDs no longer match the frozen audit")

    category_frame = matched[ARTERY_COLUMNS].astype("string").apply(lambda col: col.str.strip())
    categories = set(category_frame.stack().dropna().unique())
    allowed = POSITIVE_STENOSIS_BINS | NEGATIVE_STENOSIS_BINS
    if categories != allowed:
        raise ValueError(f"Unexpected AngioCAD stenosis label categories: {sorted(categories)}")
    binary_target = category_frame.isin(POSITIVE_STENOSIS_BINS).any(axis=1).to_numpy(dtype=np.int8)
    if not np.all(
        binary_target | category_frame.isin(NEGATIVE_STENOSIS_BINS).all(axis=1).to_numpy(dtype=bool)
    ):
        raise ValueError("An AngioCAD target row does not satisfy the frozen threshold rule")

    sex_values = set(matched["Sex"].dropna().astype(str).str.strip().str.lower().unique())
    if sex_values != {"male", "female"}:
        raise ValueError(f"Unexpected AngioCAD sex categories: {sorted(sex_values)}")
    sex = matched["Sex"].astype("string").str.strip().str.lower()
    fbs = pd.to_numeric(matched["FBS"], errors="raise")
    fbs_category = pd.Series(index=matched.index, dtype="object")
    observed_fbs = fbs.notna()
    fbs_category.loc[observed_fbs] = np.where(
        fbs.loc[observed_fbs] > 120, "gt_120_mg_dl", "le_120_mg_dl"
    )
    external_X = pd.DataFrame(
        {
            "age": pd.to_numeric(matched["Age"], errors="raise").astype(float),
            "sex": sex,
            "fbs": fbs_category,
        },
        index=matched.index,
    )[FEATURES].reset_index(drop=True)

    record_ids = matched["ID"].astype(int).to_numpy()
    audit = {
        "feature_file_sha256": sha256_file(FEATURES_FILE),
        "label_file_sha256": sha256_file(LABELS_FILE),
        "feature_workbook_shape_including_blank_rows": [
            int(feature_sheet.max_row),
            int(feature_sheet.max_column),
        ],
        "label_workbook_shape_including_blank_rows": [
            int(label_sheet.max_row),
            int(label_sheet.max_column),
        ],
        "feature_nonblank_unique_ids": int(len(features)),
        "label_nonblank_unique_ids": int(len(labels)),
        "matched_unique_ids": int(len(matched)),
        "label_ids_without_features": int(len(set(labels["ID"]) - set(features["ID"]))),
        "blank_feature_rows": int(feature_sheet.max_row - 1 - len(features_raw)),
        "blank_label_rows": int(label_sheet.max_row - 1 - len(labels_raw)),
        "raw_artery_category_counts": {
            str(key): int(value) for key, value in sorted(Counter(category_frame.stack()).items())
        },
        "target_definition": (
            "1 if any of 15 artery labels is 51-75, 76-90, 91-99, or 100; "
            "0 if every artery label is NL, 1-25, or 26-50"
        ),
        "target_counts": {
            str(key): int(value) for key, value in sorted(Counter(binary_target).items())
        },
        "sex_category_counts": {
            str(key): int(value) for key, value in sorted(Counter(sex.dropna()).items())
        },
        "external_fbs_gt_120_count": int((fbs > 120).sum()),
        "external_fbs_le_120_count": int((fbs <= 120).sum()),
        "external_fbs_observed_min_assumed_mg_dl": float(fbs.min()),
        "external_fbs_observed_max_assumed_mg_dl": float(fbs.max()),
        "feature_missing_counts_after_id_match": {
            str(key): int(value) for key, value in external_X.isna().sum().items()
        },
        "target_feature_file_ids_without_labels": 0,
        "record_ids_sorted_before_prediction": True,
    }
    return external_X, binary_target, record_ids, audit


def run_experiment(output_dir: Path) -> None:
    for path in (FEATURES_FILE, LABELS_FILE, SOURCE_MANIFEST, TARGET_MANIFEST, PROTOCOL):
        if not path.is_file():
            raise FileNotFoundError(f"Required frozen study input is missing: {path}")

    source_metadata = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    target_metadata = json.loads(TARGET_MANIFEST.read_text(encoding="utf-8"))
    if target_metadata["files"]["clinical_features"]["sha256"] != sha256_file(FEATURES_FILE):
        raise ValueError("AngioCAD feature workbook hash differs from its frozen manifest")
    if target_metadata["files"]["artery_labels"]["sha256"] != sha256_file(LABELS_FILE):
        raise ValueError("AngioCAD label workbook hash differs from its frozen manifest")
    if sha256_file(transfer.SOURCE_ARCHIVE) != source_metadata["archive_sha256"]:
        raise ValueError("UCI Heart Disease archive hash differs from its frozen manifest")

    source_cohorts, source_audit = transfer.source_feature_map()
    target_X, target_y, target_ids, target_audit = load_angiocad()
    fit_X, fit_y, fit_domains, cal_X, cal_y, cal_domains, splits = transfer.split_source_cohorts(
        source_cohorts
    )
    fit_weights = shared.equal_domain_weights(fit_domains)
    cal_weights = shared.equal_domain_weights(cal_domains)

    preprocessor = transfer.build_preprocessor()
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

    target_matrix = preprocessor.transform(target_X)
    raw_target_probabilities = predictor.predict_proba(target_matrix)[:, 1]
    target_logits = np.log(
        np.clip(raw_target_probabilities, 1e-7, 1 - 1e-7)
        / np.clip(1 - raw_target_probabilities, 1e-7, 1.0)
    ).reshape(-1, 1)
    calibrated_target_probabilities = calibrator.predict_proba(target_logits)[:, 1]
    target_anomaly_scores = -detector.score_samples(target_matrix)
    target_flags = target_anomaly_scores > ood_threshold

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
        "study_id": "CD-XD-004",
        "status": "source_distinct_endpoint_aligned_external_cohort_evaluation",
        "run_timestamp_utc": datetime.now(UTC).isoformat(),
        "source_archive_path": str(transfer.SOURCE_ARCHIVE.relative_to(ROOT)),
        "source_archive_sha256": sha256_file(transfer.SOURCE_ARCHIVE),
        "source_manifest_sha256": sha256_file(SOURCE_MANIFEST),
        "target_feature_file": str(FEATURES_FILE.relative_to(ROOT)),
        "target_feature_file_sha256": sha256_file(FEATURES_FILE),
        "target_label_file": str(LABELS_FILE.relative_to(ROOT)),
        "target_label_file_sha256": sha256_file(LABELS_FILE),
        "target_manifest_sha256": sha256_file(TARGET_MANIFEST),
        "protocol_path": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": sha256_file(PROTOCOL),
        "runner_path": str(Path(__file__).relative_to(ROOT)),
        "runner_sha256": sha256_file(Path(__file__)),
        "code_artifacts_sha256": {
            str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__)),
            str(Path(transfer.__file__).resolve().relative_to(ROOT)): sha256_file(
                Path(transfer.__file__).resolve()
            ),
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
            "sex": "Source 1=male and 0=female; AngioCAD Male/Female normalized to categories",
            "fbs": (
                "Workbook omits the unit; numeric values 55-514 are assumed to be mg/dL. "
                "Apply the source strict >120 mg/dL threshold."
            ),
        },
        "endpoint_compatibility": {
            "source": "UCI Heart Disease num=0 is <50% narrowing; num=1..4 is >50% narrowing",
            "external": (
                "AngioCAD positive if any artery segment is 51% or greater; "
                "negative if all segments are at most 50%"
            ),
            "impact": (
                "The target's ordinal bins have no exactly-50% category; "
                "this aligns the >50% source endpoint."
            ),
        },
        "cross_dataset_overlap_limit": (
            "Collection site differs from all four source cohorts; source and target files do not "
            "support person-level cross-dataset linkage."
        ),
        "seed": SEED,
        "source_calibration_fraction": transfer.CALIBRATION_FRACTION,
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
            "One external hospital does not estimate population-level between-site variance.",
            (
                "Only 377 of 413 labeled patients had a matching clinical feature "
                "row in the public workbooks."
            ),
            "The external cohort is angiography-referred and has a high positive fraction.",
            "Cross-dataset patient-level duplicate exclusion is not possible from public IDs.",
            "Bootstrap intervals condition on observed target class counts.",
            "Probabilities and OOD flags are research outputs, not clinical safety signals.",
        ],
    }

    external_predictions = pd.DataFrame(
        {
            "target_cohort": "angiocad",
            "record_id": target_ids,
            "row_index": np.arange(len(target_y)),
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
    print(f"Wrote CD-XD-004 manifest and predictions to {output_dir}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    with threadpool_limits(limits=1):
        run_experiment(arguments.output_dir)


if __name__ == "__main__":
    main()
