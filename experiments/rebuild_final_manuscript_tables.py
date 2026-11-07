"""Rebuild manuscript numeric tables from frozen result artifacts.

This script does not fit models or inspect new targets. Inputs are previously
saved study JSONs. Existing study outputs remain the source of record.
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "paper" / "tables"
ROW_END = " " + chr(92) * 2
SOURCES = {
    "heart5_stability": "results/generated/post_boundary_corrected_stability_heart5.json",
    "mendeley_stability": "results/generated/post_boundary_corrected_stability_mendeley.json",
    "heart5_linkage": "results/generated/post_boundary_corrected_linkage_heart5.json",
    "mendeley_linkage": "results/generated/post_boundary_corrected_linkage_mendeley.json",
    "angiocad_ablation": (
        "results/interpretability_posthoc_20261105/angiocad_feature_ablation/"
        "run_manifest.json"
    ),
    "selective_components": (
        "results/final_consolidation_20261106/selective_policy_components/"
        "selective_policy_component_audit.json"
    ),
    "nested_summary": "results/tables/nested_summary.csv",
    "nested_json_heart5": "results/master_directive_20261105_serial/heart5_nested_validation.json",
    "nested_json_mendeley": (
        "results/master_directive_20261105_serial/mendeley_nested_validation.json"
    ),
    "domain_guard_angiocad": "results/transfer_20261105_angiocad_domain_guard/study_metrics.json",
    "domain_guard_duke": "results/transfer_20261105_duke_acath_final/study_metrics.json",
    "validity_sensitivity": (
        "results/final_consolidation_20261106/validity_sensitivity_audit.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(key: str) -> dict[str, Any]:
    return json.loads((ROOT / SOURCES[key]).read_text(encoding="utf-8"))


def write(name: str, rows: list[str]) -> None:
    (TABLE_DIR / name).write_text("\n".join(rows).rstrip() + "\n", encoding="utf-8")


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def table_uncertainty() -> None:
    rows = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        "Dataset & Candidate & Conf.-error AUC & AURC & Conformal coverage & ECE" + ROW_END,
        r"\midrule",
    ]
    for dataset, source in (("Five States", "heart5_linkage"), ("Mendeley", "mendeley_linkage")):
        data = read_json(source)
        for candidate, label in (
            ("corrected_osec", "Corrected OSEC"),
            ("stable_osec", "Stable OSEC"),
        ):
            folds = data["per_seed"]
            def get_mean(metric: str) -> float:
                return mean([row[candidate][metric] for row in folds])

            rows.append(
                f"{dataset} & {label} & {get_mean('confidence_error_auc'):.3f} & "
                f"{get_mean('aurc'):.4f} & {get_mean('conformal_coverage'):.3f} & "
                f"{get_mean('ece_uniform'):.3f}" + ROW_END
            )
    rows.extend([r"\bottomrule", r"\end{tabular}"])
    write("uncertainty_evidence.tex", rows)


def table_stability() -> None:
    rows = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        "Dataset & Stable $\\Phi$ & One-shot $\\Phi$ & Difference & 95\\% bootstrap CI" + ROW_END,
        r"\midrule",
    ]
    for dataset, source in (
        ("Five States", "heart5_stability"),
        ("Mendeley", "mendeley_stability"),
    ):
        data = read_json(source)
        stable = data["methods"]["stable_xaih_drc"]["mean_repeat_nogueira_stability"]
        one_shot = data["methods"]["one_shot_xaih_drc"]["mean_repeat_nogueira_stability"]
        diff = data["paired_stability_difference"]
        ci = diff["bootstrap_ci"]
        rows.append(
            f"{dataset} & {stable:.3f} & {one_shot:.3f} & "
            f"{diff['stable_minus_one_shot_mean']:.3f} & "
            f"[{ci['low']:.3f}, {ci['high']:.3f}]" + ROW_END
        )
    rows.extend([r"\bottomrule", r"\end{tabular}"])
    write("stability_evidence.tex", rows)


def table_linkage() -> None:
    rows = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        "Dataset & Cross-seed $\\Phi$ & $\\Delta$ ROC-AUC & $\\Delta$ Conf.-AUC & "
        "$\\Delta$ AURC & $\\Delta$ ECE" + ROW_END,
        r"\midrule",
    ]
    for dataset, source in (("Five States", "heart5_linkage"), ("Mendeley", "mendeley_linkage")):
        data = read_json(source)
        diff = data["paired_reliability_differences"]
        values = [
            diff[name]["mean"]
            for name in ("roc_auc", "confidence_error_auc", "aurc", "ece_uniform")
        ]
        phi = data["stability"]["cross_seed_selected_set_nogueira"]
        rows.append(
            f"{dataset} & {phi:.3f} & {values[0]:+.4f} & {values[1]:+.4f} & "
            f"{values[2]:+.4f} & {values[3]:+.4f}" + ROW_END
        )
    rows.extend([r"\bottomrule", r"\end{tabular}"])
    write("stability_reliability_linkage.tex", rows)


def table_angiocad_ablation() -> None:
    features = read_json("angiocad_ablation")["features"]
    labels = {
        "age": ("Age", "Age-as-years assumed"),
        "sex": ("Sex", "Categorical"),
        "age+sex": ("Age + sex", "FBS excluded; age unit assumed"),
        "fbs": ("FBS", "mg/dL assumption"),
        "age+fbs": ("Age + FBS", "mg/dL and age-unit assumptions"),
        "sex+fbs": ("Sex + FBS", "mg/dL assumption"),
        "age+sex+fbs": ("Age + sex + FBS", "mg/dL and age-unit assumptions"),
    }
    rows = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Post-hoc source-calibrated AngioCAD feature ablation using frozen "
        r"UCI source partitions. Target-label results are descriptive, unadjusted "
        r"for seven comparisons, and are not fresh validation. FBS-containing rows "
        r"assume AngioCAD FBS is measured in mg/dL. Age + sex excludes FBS, but the "
        r"workbook does not state age units, so age-as-years remains provisional. "
        r"Intervals are class-stratified bootstrap intervals conditional on the "
        r"previously examined target cohort.}",
        r"\label{tab:angiocad-feature-ablation}",
        r"\scriptsize",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        "Features & Source-Platt ROC-AUC (95\\% CI) & Brier & 10-bin ECE & Unit status" + ROW_END,
        r"\midrule",
    ]
    for key, (label, unit) in labels.items():
        record = features[key]
        metrics = record["source_platt_metrics"]
        ci = record["conditional_bootstrap_95_ci"]["platt"]["roc_auc"]
        rows.append(
            f"{label} & {metrics['roc_auc']:.3f} "
            f"({ci['lower_95']:.3f}--{ci['upper_95']:.3f}) & "
            f"{metrics['brier_score']:.3f} & {metrics['ece_10_bins']:.3f} & {unit}" + ROW_END
        )
    rows.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])
    write("angiocad_feature_ablation.tex", rows)


def table_selective_components() -> None:
    studies = read_json("selective_components")["studies"]
    by_dataset = {study["dataset"]: study for study in studies}
    policies = [
        ("fixed_probability_0.5", "Fixed probability 0.5, no abstention"),
        ("conformal_singleton_only", "Conformal singleton only"),
        ("knn_domain_robust_only", "kNN detector only"),
        ("isolation_forest_domain_robust_only", "Isolation Forest only"),
        ("conformal_plus_knn_registered_combination", "Registered conformal + kNN"),
        ("unknown_domain_registry_gate", "Unknown-site registry gate"),
    ]
    records = {
        name: {row["policy"]: row for row in study["policies"]}
        for name, study in by_dataset.items()
    }

    def cell(dataset: str, key: str) -> tuple[str, str]:
        row = records[dataset][key]
        coverage = f"{row['coverage']:.1%}".replace("%", r"\%")
        if row["accepted_n"] == 0:
            return coverage, "No score emitted"
        error = f"{row['accepted_error_count']:,}/{row['accepted_n']:,}"
        if row["accepted_n"] < row["n"]:
            rate = f"{row['accepted_error_rate']:.1%}".replace("%", r"\%")
            error += f" ({rate})"
        counts = row.get("accepted_class_counts", {})
        if counts and (counts.get("0", 0) == 0 or counts.get("1", 0) == 0):
            error += "; one class"
        return coverage, error

    rows = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Post-hoc comparison of frozen selective-policy components. "
        r"AngioCAD was previously examined; Duke uses a different endpoint. "
        r"The registry blocks both unregistered cohorts. Target labels did not "
        r"select thresholds or policies.}",
        r"\label{tab:selective-policy-components}",
        r"\scriptsize",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        "Policy & AngioCAD coverage & AngioCAD errors & Duke coverage & Duke errors" + ROW_END,
        r"\midrule",
    ]
    for key, label in policies:
        angio_cov, angio_error = cell("AngioCAD", key)
        duke_cov, duke_error = cell("Duke ACATH", key)
        rows.append(
            f"{label} & {angio_cov} & {angio_error} & {duke_cov} & {duke_error}" + ROW_END
        )
    rows.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])
    write("selective_policy_components.tex", rows)


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    table_uncertainty()
    table_stability()
    table_linkage()
    table_angiocad_ablation()
    table_selective_components()
    table_names = [
        "nested_summary.tex",
        "validity_sensitivity_mendeley.tex",
        "validity_sensitivity_angiocad.tex",
        "angiocad_feature_ablation.tex",
        "uncertainty_evidence.tex",
        "stability_evidence.tex",
        "stability_reliability_linkage.tex",
        "selective_policy_components.tex",
        "domain_guard_transfer.tex",
    ]
    manifest = {
        "created_utc": datetime.now(UTC).isoformat(),
        "generation_claim": (
            "Numeric tables are generated or refreshed from the listed frozen result artifacts."
        ),
        "generator_sha256": sha256(Path(__file__)),
        "source_hashes": {key: sha256(ROOT / path) for key, path in SOURCES.items()},
        "table_hashes": {name: sha256(TABLE_DIR / name) for name in table_names},
    }
    output = TABLE_DIR / "final_numeric_table_manifest.json"
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Rebuilt 5 tables; hashed {len(table_names)} manuscript numeric tables in {output}")


if __name__ == "__main__":
    main()
