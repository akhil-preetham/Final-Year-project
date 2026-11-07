"""Post-hoc AngioCAD sensitivity analysis excluding unit-ambiguous FBS.

This analysis is exploratory because the AngioCAD outcome was previously
examined. It repeats the CD-XD-004 source partitions and model/calibration
settings using age and sex only, then scores AngioCAD once. The original
CD-XD-004 result is not modified or replaced.
"""

from __future__ import annotations

import argparse
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
import run_angiocad_transfer as angio
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "validity_audit_20261105" / "angiocad_without_fbs"
FEATURES = ["age", "sex"]
NUMERIC = ["age"]
CATEGORICAL = ["sex"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent", add_indicator=True)),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [("numeric", numeric, NUMERIC), ("categorical", categorical, CATEGORICAL)],
        remainder="drop",
        sparse_threshold=0.0,
    )


def run(output_dir: Path = OUTPUT) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Refusing to overwrite sensitivity artifacts in {output_dir}")

    source_cohorts, source_audit = angio.transfer.source_feature_map()
    source_age_sex = {
        name: {
            **cohort,
            "X": cohort["X"][FEATURES].copy(),
        }
        for name, cohort in source_cohorts.items()
    }
    (
        fit_X,
        fit_y,
        fit_domains,
        cal_X,
        cal_y,
        cal_domains,
        splits,
    ) = angio.transfer.split_source_cohorts(source_age_sex)
    fit_weights = angio.shared.equal_domain_weights(fit_domains)
    cal_weights = angio.shared.equal_domain_weights(cal_domains)

    target_X_all, target_y, target_ids, target_audit = angio.load_angiocad()
    target_X = target_X_all[FEATURES].copy()

    preprocessor = build_preprocessor()
    fit_matrix = preprocessor.fit_transform(fit_X[FEATURES])
    cal_matrix = preprocessor.transform(cal_X[FEATURES])
    predictor = LogisticRegression(
        C=1.0, solver="liblinear", max_iter=5000, random_state=angio.SEED
    )
    predictor.fit(fit_matrix, fit_y, sample_weight=fit_weights)

    raw_cal = predictor.predict_proba(cal_matrix)[:, 1]
    cal_logits = np.log(np.clip(raw_cal, 1e-7, 1 - 1e-7) / np.clip(1 - raw_cal, 1e-7, 1.0)).reshape(
        -1, 1
    )
    calibrator = LogisticRegression(C=1e6, solver="lbfgs", max_iter=5000, random_state=angio.SEED)
    calibrator.fit(cal_logits, cal_y, sample_weight=cal_weights)

    detector = IsolationForest(
        n_estimators=300,
        max_samples="auto",
        contamination="auto",
        random_state=angio.SEED,
        n_jobs=1,
    )
    detector.fit(fit_matrix, sample_weight=fit_weights)
    cal_anomaly = -detector.score_samples(cal_matrix)
    threshold = angio.shared.weighted_quantile(cal_anomaly, cal_weights, 0.95)

    target_matrix = preprocessor.transform(target_X)
    raw_target = predictor.predict_proba(target_matrix)[:, 1]
    target_logits = np.log(
        np.clip(raw_target, 1e-7, 1 - 1e-7) / np.clip(1 - raw_target, 1e-7, 1.0)
    ).reshape(-1, 1)
    calibrated_target = calibrator.predict_proba(target_logits)[:, 1]
    target_anomaly = -detector.score_samples(target_matrix)
    flags = target_anomaly > threshold

    # The target outcomes enter only after every fitted object is frozen.
    raw_metrics = angio.shared.predictive_metrics(target_y, raw_target)
    calibrated_metrics = angio.shared.predictive_metrics(target_y, calibrated_target)
    predictive_intervals = angio.shared.bootstrap_predictive_intervals(
        target_y, raw_target, calibrated_target, seed=angio.SEED + 1000
    )
    ood_interval = angio.shared.bootstrap_ood_auc_interval(
        cal_anomaly, target_anomaly, seed=angio.SEED + 2000
    )
    domain_y = np.concatenate([np.zeros(len(cal_anomaly)), np.ones(len(target_anomaly))])
    domain_score = np.concatenate([cal_anomaly, target_anomaly])
    ood_auc = float(angio.shared.roc_auc_score(domain_y, domain_score))

    runner_path = Path(__file__).resolve()
    manifest: dict[str, Any] = {
        "study_id": "CD-XD-004-FBS-SENSITIVITY",
        "status": "post_hoc_exploratory_feature_unit_sensitivity",
        "run_timestamp_utc": datetime.now(UTC).isoformat(),
        "interpretation": (
            "Sensitivity to the undocumented AngioCAD FBS unit; excludes FBS in "
            "both source fitting and target scoring. Target outcomes were previously "
            "examined, so this is not confirmatory evidence."
        ),
        "included_features": FEATURES,
        "excluded_feature": "fbs",
        "source_archive_sha256": sha256_file(angio.transfer.SOURCE_ARCHIVE),
        "target_features_sha256": sha256_file(angio.FEATURES_FILE),
        "target_labels_sha256": sha256_file(angio.LABELS_FILE),
        "source_manifest_sha256": sha256_file(angio.SOURCE_MANIFEST),
        "target_manifest_sha256": sha256_file(angio.TARGET_MANIFEST),
        "original_protocol_sha256": sha256_file(angio.PROTOCOL),
        "runner_sha256": sha256_file(runner_path),
        "shared_source_code_sha256": sha256_file(Path(angio.transfer.__file__).resolve()),
        "source_cohort_order": list(angio.SOURCE_ORDER),
        "source_cohort_audit": source_audit,
        "target_cohort_audit": target_audit,
        "source_splits": splits,
        "source_fit_rows": int(len(fit_y)),
        "source_calibration_rows": int(len(cal_y)),
        "source_fit_class_counts": {str(k): int(v) for k, v in sorted(Counter(fit_y).items())},
        "source_calibration_class_counts": {
            str(k): int(v) for k, v in sorted(Counter(cal_y).items())
        },
        "model": {"family": "logistic_regression", "C": 1.0, "solver": "liblinear"},
        "calibrator": {
            "method": "source-only Platt scaling",
            "C": 1e6,
            "intercept": float(calibrator.intercept_[0]),
            "slope": float(calibrator.coef_[0, 0]),
        },
        "target_raw_metrics": raw_metrics,
        "target_calibrated_metrics": calibrated_metrics,
        "predictive_bootstrap_95_ci": predictive_intervals,
        "ood": {
            "method": "Isolation Forest fit on source-fit age/sex only",
            "source_calibration_false_alert_rate": float(
                np.average(cal_anomaly > threshold, weights=cal_weights)
            ),
            "target_alert_rate": float(flags.mean()),
            "source_vs_target_auroc": ood_auc,
            "source_vs_target_auroc_bootstrap_95_ci": ood_interval,
        },
        "software": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }
    target_predictions = pd.DataFrame(
        {
            "record_id": target_ids,
            "y_binary": target_y,
            "raw_probability": raw_target,
            "platt_probability": calibrated_target,
            "ood_anomaly_score": target_anomaly,
            "ood_threshold": threshold,
            "ood_flag": flags,
        }
    )
    source_predictions = pd.DataFrame(
        {
            "source_cohort": cal_domains,
            "y_binary": cal_y,
            "raw_probability": raw_cal,
            "platt_probability": calibrator.predict_proba(cal_logits)[:, 1],
            "ood_anomaly_score": cal_anomaly,
            "ood_threshold": threshold,
        }
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8"
    )
    target_predictions.to_csv(output_dir / "target_predictions.csv", index=False)
    source_predictions.to_csv(output_dir / "source_calibration_predictions.csv", index=False)
    print(f"Wrote post-hoc FBS sensitivity artifacts to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    with threadpool_limits(limits=1):
        run(arguments.output_dir)
