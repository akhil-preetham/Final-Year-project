"""Run the endpoint-aligned source-only model with a fail-closed site gate."""

from __future__ import annotations

import hashlib
import json
import platform
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import matplotlib
import numpy as np
import pandas as pd
import run_angiocad_transfer as angio
import run_duke_transfer as framework
import run_lodo_transfer as shared
import scipy
import sklearn
from matplotlib import pyplot as plt
from sklearn.calibration import calibration_curve
from threadpoolctl import threadpool_limits

from cardiodiag.domain_guard import DomainAwareSelectivePredictor
from cardiodiag.reliability import uncertainty_evidence
from cardiodiag.uncertainty import conformal_selective_summary

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ARCHIVE = ROOT / "data" / "external" / "uci_heart_disease_45" / "heart_disease.zip"
SOURCE_MANIFEST = ROOT / "data" / "manifests" / "uci_heart_disease_transfer_study.json"
TARGET_MANIFEST = ROOT / "data" / "manifests" / "angiocad_external.json"
TARGET_FEATURES = ROOT / "data" / "external" / "angiocad_zenodo_15826856" / "AngioCAD_Features.xlsx"
TARGET_LABELS = ROOT / "data" / "external" / "angiocad_zenodo_15826856" / "AngioCAD_Labels.xlsx"
PROTOCOL = ROOT / "docs" / "TRANSFER_STUDY_PROTOCOL_20261105_ANGIOCAD_DOMAIN_GUARD.md"
OUTPUT = ROOT / "results" / "transfer_20261105_angiocad_domain_guard"
FEATURES = ["age", "sex", "fbs"]
NUMERIC = ["age"]
CATEGORICAL = ["sex", "fbs"]
SOURCE_ORDER = tuple(shared.COHORT_FILES)
SEED = framework.SEED


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_source() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    raw, audit = shared.load_cohorts(SOURCE_ARCHIVE, zero_as_missing=False)
    output: dict[str, dict[str, Any]] = {}
    for name in SOURCE_ORDER:
        frame = raw[name]["X"][FEATURES].copy()
        sex = pd.to_numeric(frame["sex"], errors="raise")
        fbs = pd.to_numeric(frame["fbs"], errors="raise")
        if not set(sex.dropna().unique()).issubset({0, 1}):
            raise ValueError(f"Unexpected source sex encoding in {name}")
        if not set(fbs.dropna().unique()).issubset({0, 1}):
            raise ValueError(f"Unexpected source fbs encoding in {name}")
        frame["sex"] = sex.map({0: "female", 1: "male"})
        frame["fbs"] = fbs.map({0: "le_120_mg_dl", 1: "gt_120_mg_dl"})
        frame["age"] = pd.to_numeric(frame["age"], errors="raise").astype(float)
        output[name] = {
            "X": frame[FEATURES].reset_index(drop=True),
            "y": raw[name]["y"].astype(np.int8),
            "row_index": raw[name]["row_index"].astype(int),
        }
    return output, audit


def make_figure(
    path: Path,
    y: np.ndarray,
    probability: np.ndarray,
    model: dict[str, Any],
    output: dict[str, np.ndarray],
) -> None:
    figure, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    risk = uncertainty_evidence(y, probability)["selective_risk"]
    axes[0].plot(
        [item["coverage"] for item in risk],
        [item["risk"] for item in risk],
        marker="o",
        color="#286090",
    )
    axes[0].set(title="Confidence-ranked risk/coverage", xlabel="Coverage", ylabel="Error rate")
    axes[0].set_xlim(0.45, 1.01)
    axes[0].set_ylim(0, 1)
    axes[0].grid(alpha=0.25)

    source = model["knn_cal_scores"]
    target = output["knn_support_score"]
    bins = np.histogram_bin_edges(np.concatenate([source, target]), bins=30)
    axes[1].hist(source, bins=bins, density=True, alpha=0.6, label="Source conformal split")
    axes[1].hist(target, bins=bins, density=True, alpha=0.5, label="AngioCAD")
    axes[1].axvline(
        model["knn_threshold"], color="#a33", linestyle="--", label="95% source threshold"
    )
    axes[1].set(title="Feature support", xlabel="Mean 10-NN distance", ylabel="Density")
    axes[1].legend(fontsize=8)

    observed, predicted = calibration_curve(y, probability, n_bins=10, strategy="uniform")
    axes[2].plot([0, 1], [0, 1], linestyle="--", color="grey", label="Ideal")
    axes[2].plot(predicted, observed, marker="o", color="#397b46", label="AngioCAD")
    axes[2].set(
        title="Target reliability", xlabel="Mean predicted risk", ylabel="Observed event rate"
    )
    axes[2].set_xlim(0, 1)
    axes[2].set_ylim(0, 1)
    axes[2].legend(fontsize=8)
    figure.suptitle("CD-XD-006: source-only transfer to AngioCAD", y=1.02)
    figure.tight_layout()
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def run_experiment(output_dir: Path) -> None:
    inputs = (
        SOURCE_ARCHIVE,
        SOURCE_MANIFEST,
        TARGET_MANIFEST,
        TARGET_FEATURES,
        TARGET_LABELS,
        PROTOCOL,
    )
    for path in inputs:
        if not path.is_file():
            raise FileNotFoundError(f"Required study input is missing: {path}")
    source_meta = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    target_meta = json.loads(TARGET_MANIFEST.read_text(encoding="utf-8"))
    if source_meta["archive_sha256"] != sha256_file(SOURCE_ARCHIVE):
        raise ValueError("UCI source archive hash differs from its registered manifest")
    for key, path in (
        ("clinical_features", TARGET_FEATURES),
        ("artery_labels", TARGET_LABELS),
    ):
        if target_meta["files"][key]["sha256"] != sha256_file(path):
            raise ValueError(f"AngioCAD {key} file hash differs from its registered manifest")

    cohorts, source_audit = load_source()
    target_X, target_y, record_ids, target_audit = angio.load_angiocad()
    lodo_folds, lodo_predictions = framework.score_lodo(
        cohorts,
        feature_names=FEATURES,
        numeric_features=NUMERIC,
        categorical_features=CATEGORICAL,
    )
    model = framework.train_source_model(
        cohorts,
        SOURCE_ORDER,
        feature_names=FEATURES,
        numeric_features=NUMERIC,
        categorical_features=CATEGORICAL,
    )
    prediction = framework.score_features(model, target_X)
    raw_probability = prediction["raw_probability"]
    probability = prediction["calibrated_probability"]
    sets = np.column_stack([prediction["conformal_set_0"], prediction["conformal_set_1"]])
    source_cal = model["calibration_predictions"]
    source_cal_metrics = shared.predictive_metrics(
        source_cal["label"].to_numpy(), source_cal["calibrated_probability"].to_numpy()
    )
    raw_metrics = shared.predictive_metrics(target_y, raw_probability)
    calibrated_metrics = shared.predictive_metrics(target_y, probability)
    conformal_summary = conformal_selective_summary(target_y, sets)
    combined = framework.summarize_combined(target_y, probability, prediction)
    knn_summary = framework.summarize_detector(
        model["knn_cal_scores"], prediction["knn_support_score"], model["knn_threshold"]
    )
    forest_summary = framework.summarize_detector(
        model["forest_cal_scores"],
        prediction["isolation_forest_score"],
        model["forest_threshold"],
    )
    bootstrap = shared.bootstrap_predictive_intervals(
        target_y, raw_probability, probability, seed=SEED + 3000
    )
    knn_auc_ci = shared.bootstrap_ood_auc_interval(
        model["knn_cal_scores"], prediction["knn_support_score"], seed=SEED + 4000
    )
    deploy_bundle = framework.create_deployment_bundle(
        model,
        target_definition=(
            "UCI num > 0 (>50%); AngioCAD positive if any of 15 artery bins exceeds 50%."
        ),
    )
    guarded = DomainAwareSelectivePredictor(deploy_bundle).predict(
        target_X, domain_id="angiocad_isfahan"
    )
    gate_counts = dict(Counter(row["action"] for row in guarded))
    gate_reasons = dict(Counter(row["reason"] for row in guarded))

    metrics = {
        "study_id": "CD-XD-006",
        "status": "post-hoc source-only replay; AngioCAD was previously examined in CD-XD-004",
        "target_dataset": "AngioCAD, Shahid Chamran Heart Center, Isfahan",
        "target_rows": int(len(target_y)),
        "target_class_counts": {str(k): int(v) for k, v in sorted(Counter(target_y).items())},
        "target_audit": target_audit,
        "source_calibration_metrics": source_cal_metrics,
        "raw_source_model_metrics_on_target": raw_metrics,
        "platt_calibrated_metrics_on_target": calibrated_metrics,
        "target_bootstrap_95_ci": bootstrap,
        "conformal": {
            "alpha": framework.CONFORMAL_ALPHA,
            "source_thresholds": model["conformal_by_domain"],
            "target_summary": conformal_summary,
            "combined_selective_summary": combined,
        },
        "ood": {
            "knn_domain_robust": {
                **knn_summary,
                "source_domain_thresholds": model["knn_thresholds"],
                "target_auroc_bootstrap_95_ci": knn_auc_ci,
            },
            "isolation_forest_domain_robust": {
                **forest_summary,
                "source_domain_thresholds": model["forest_thresholds"],
            },
        },
        "domain_registry_gate": {
            "target_domain_id": "angiocad_isfahan",
            "registered_source_domains": list(SOURCE_ORDER),
            "action_counts": gate_counts,
            "reason_counts": gate_reasons,
            "coverage": float(gate_counts.get("classify", 0) / len(target_y)),
            "scoring_scope": (
                "All probability predictions in this run are exploratory evaluation outputs."
            ),
        },
        "source_domain_lodo": {
            "folds": lodo_folds,
            "macro_summary": framework.macro_summary(lodo_folds),
        },
        "limitations": [
            (
                "AngioCAD outcome labels were inspected in the prior CD-XD-004 study; "
                "this is not a fresh final holdout."
            ),
            (
                "36 labeled AngioCAD IDs have no matching clinical-feature record; "
                "this analysis has 377 matched patients."
            ),
            (
                "FBS units are undocumented in the feature workbook; mg/dL is inferred "
                "from the observed range."
            ),
            (
                "Feature-level OOD detection is evaluated, not presumed effective; "
                "unknown domains are blocked by trusted site metadata."
            ),
            "This prototype does not establish clinical safety, utility, or readiness.",
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir = output_dir / "figures"
    figure_dir.mkdir(exist_ok=True)
    target_predictions = pd.DataFrame(
        {
            "target_row_index": np.arange(len(target_y)),
            "public_record_id": record_ids,
            "label_for_scoring": target_y,
            "domain_gate_action": [row["action"] for row in guarded],
            "domain_gate_reason": [row["reason"] for row in guarded],
            "deployment_probability": [row["probability"] for row in guarded],
            "deployment_prediction": [row["prediction"] for row in guarded],
            **{f"exploratory_{name}": values for name, values in prediction.items()},
        }
    )
    cal_predictions = model["calibration_predictions"].copy()
    cal_predictions["conformal_include_0"] = (
        cal_predictions["calibrated_probability"] <= model["conformal_threshold"]
    )
    cal_predictions["conformal_include_1"] = (
        1.0 - cal_predictions["calibrated_probability"] <= model["conformal_threshold"]
    )
    (output_dir / "study_metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    target_predictions.to_csv(output_dir / "target_predictions.csv", index=False)
    cal_predictions.to_csv(output_dir / "source_conformal_predictions.csv", index=False)
    model["platt_predictions"].to_csv(
        output_dir / "source_probability_calibration_predictions.csv", index=False
    )
    lodo_predictions.to_csv(output_dir / "lodo_source_predictions.csv", index=False)
    joblib.dump(deploy_bundle, output_dir / "model_bundle.joblib", compress=3)
    make_figure(
        figure_dir / "angiocad_transport_reliability.png", target_y, probability, model, prediction
    )

    code_paths = [
        Path(__file__),
        ROOT / "experiments" / "run_duke_transfer.py",
        ROOT / "experiments" / "run_angiocad_transfer.py",
        ROOT / "experiments" / "run_lodo_transfer.py",
        ROOT / "src" / "cardiodiag" / "domain_guard.py",
        ROOT / "src" / "cardiodiag" / "uncertainty.py",
    ]
    outputs = [
        output_dir / "study_metrics.json",
        output_dir / "target_predictions.csv",
        output_dir / "source_conformal_predictions.csv",
        output_dir / "source_probability_calibration_predictions.csv",
        output_dir / "lodo_source_predictions.csv",
        output_dir / "model_bundle.joblib",
        figure_dir / "angiocad_transport_reliability.png",
    ]
    manifest = {
        "study_id": "CD-XD-006",
        "created_utc": datetime.now(UTC).isoformat(),
        "seed": SEED,
        "status": metrics["status"],
        "features": FEATURES,
        "source_domains": SOURCE_ORDER,
        "source_partition_fractions": {
            "fit": 1
            - framework.PROBABILITY_CALIBRATION_FRACTION
            - framework.CONFORMAL_CALIBRATION_FRACTION,
            "probability_calibration": framework.PROBABILITY_CALIBRATION_FRACTION,
            "conformal_and_ood_calibration": framework.CONFORMAL_CALIBRATION_FRACTION,
        },
        "source_splits": model["splits"],
        "source_fit_counts": {
            str(k): int(v) for k, v in sorted(Counter(model["fit_domains"]).items())
        },
        "probability_calibration_counts": {
            str(k): int(v) for k, v in sorted(Counter(model["platt_domains"]).items())
        },
        "conformal_calibration_counts": {
            str(k): int(v) for k, v in sorted(Counter(model["cal_domains"]).items())
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "scipy": scipy.__version__,
        },
        "input_hashes": {str(path.relative_to(ROOT)): sha256_file(path) for path in inputs},
        "code_hashes": {str(path.relative_to(ROOT)): sha256_file(path) for path in code_paths},
        "output_hashes": {str(path.relative_to(ROOT)): sha256_file(path) for path in outputs},
        "target_labels_used_for": (
            "Scoring and post-hoc evaluation only; no fitting, calibration, or threshold selection."
        ),
    }
    (output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote CD-XD-006 source-only results to {output_dir}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        run_experiment(args.output_dir)


if __name__ == "__main__":
    main()
