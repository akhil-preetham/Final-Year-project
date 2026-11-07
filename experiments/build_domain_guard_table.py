"""Generate the manuscript's domain-guard comparison table from saved metrics."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ANGIO = ROOT / "results" / "transfer_20261105_angiocad_domain_guard" / "study_metrics.json"
DUKE = ROOT / "results" / "transfer_20261105_duke_acath_final" / "study_metrics.json"
TABLE = ROOT / "paper" / "tables" / "domain_guard_transfer.tex"
MANIFEST = ROOT / "paper" / "tables" / "domain_guard_transfer_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def auc_interval(metrics: dict[str, Any]) -> str:
    ci = metrics["target_bootstrap_95_ci"]["platt"]["roc_auc"]
    metric_key = (
        "platt_calibrated_metrics_on_target"
        if "platt_calibrated_metrics_on_target" in metrics
        else "source_platt_calibrated_metrics_on_target"
    )
    return f"{metrics[metric_key]['roc_auc']:.3f} ({ci['lower_95']:.3f}--{ci['upper_95']:.3f})"


def escape_latex_percent(value: str) -> str:
    return value.replace("%", r"\%")


def build_table(angio: dict[str, Any], duke: dict[str, Any]) -> str:
    angio_raw = angio["raw_source_model_metrics_on_target"]
    angio_cal = angio["platt_calibrated_metrics_on_target"]
    duke_raw = duke["raw_source_model_metrics_on_target"]
    duke_cal = duke["source_platt_calibrated_metrics_on_target"]
    angio_conformal = angio["conformal"]["target_summary"]
    duke_conformal = duke["conformal"]["target_summary"]
    angio_combined = angio["conformal"]["combined_selective_summary"]
    duke_combined = duke["combined_abstention"]["target_summary"]
    angio_knn = angio["ood"]["knn_domain_robust"]["target_vs_source_auroc"]
    angio_if = angio["ood"]["isolation_forest_domain_robust"]["target_vs_source_auroc"]
    duke_knn = duke["ood"]["primary_knn_domain_robust"]["target_vs_source_auroc"]
    duke_if = duke["ood"]["isolation_forest_domain_robust"]["target_vs_source_auroc"]
    rows = [
        ("Endpoint", ">50% aligned", "$\\geq$75% mismatch"),
        ("ROC-AUC (95% bootstrap CI)", auc_interval(angio), auc_interval(duke)),
        (
            "Brier score (raw / Platt)",
            f"{angio_raw['brier_score']:.3f} / {angio_cal['brier_score']:.3f}",
            f"{duke_raw['brier_score']:.3f} / {duke_cal['brier_score']:.3f}",
        ),
        (
            "10-bin ECE (raw / Platt)",
            f"{angio_raw['ece_10_bins']:.3f} / {angio_cal['ece_10_bins']:.3f}",
            f"{duke_raw['ece_10_bins']:.3f} / {duke_cal['ece_10_bins']:.3f}",
        ),
        (
            "90% conformal set coverage",
            f"{angio_conformal['empirical_set_coverage']:.1%}",
            f"{duke_conformal['empirical_set_coverage']:.1%}",
        ),
        (
            "Singleton-set coverage",
            f"{angio_conformal['singleton_coverage']:.1%}",
            f"{duke_conformal['singleton_coverage']:.1%}",
        ),
        (
            "Combined automatic coverage",
            f"{angio_combined['coverage']:.1%}",
            f"{duke_combined['coverage']:.1%}",
        ),
        (
            "Errors among automatic outputs",
            f"{angio_combined['accepted_error_count']}/{angio_combined['accepted_n']}",
            f"{duke_combined['accepted_error_count']}/{duke_combined['accepted_n']} "
            f"({duke_combined['accepted_error_rate']:.1%})",
        ),
        (
            "OOD AUROC (kNN / IF)",
            f"{angio_knn:.3f} / {angio_if:.3f}",
            f"{duke_knn:.3f} / {duke_if:.3f}",
        ),
        (
            "Registry-gate automatic coverage",
            f"{angio['domain_registry_gate']['coverage']:.1%}",
            f"{duke['domain_registry_gate']['coverage']:.1%}",
        ),
    ]
    body = "\n".join(
        " & ".join(escape_latex_percent(cell) for cell in row) + r" \\" for row in rows
    )
    return (
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\caption{Source-only transfer and abstention results. AngioCAD was "
        "previously examined; Duke uses a different stenosis threshold. The "
        "registry gate withholds scores for both unregistered target sites.}\n"
        "\\label{tab:domain-guard-transfer}\n"
        "\\begin{tabular}{lcc}\n"
        "\\toprule\n"
        "Metric & AngioCAD ($n=377$) & Duke ACATH ($n=3{,}504$) \\\\\n"
        "\\midrule\n"
        f"{body}\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table*}\n"
    )


def main() -> None:
    for path in (ANGIO, DUKE):
        if not path.is_file():
            raise FileNotFoundError(f"Saved experiment metrics are missing: {path}")
    angio = read_json(ANGIO)
    duke = read_json(DUKE)
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    TABLE.write_text(build_table(angio, duke), encoding="utf-8")
    manifest = {
        "created_utc": datetime.now(UTC).isoformat(),
        "input_hashes": {str(path.relative_to(ROOT)): sha256_file(path) for path in (ANGIO, DUKE)},
        "generator_hash": sha256_file(Path(__file__)),
        "table_hash": sha256_file(TABLE),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {TABLE}")


if __name__ == "__main__":
    main()
