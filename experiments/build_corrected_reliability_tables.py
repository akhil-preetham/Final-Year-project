"""Build versioned reliability tables from the corrected ten-seed artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "finalization_20261107" / "conformal_corrected"
TABLES = ROOT / "paper" / "tables"
ROW_END = " " + chr(92) * 2


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    sources = {
        "heart5": RESULTS / "heart5_linkage_10seeds.json",
        "mendeley": RESULTS / "mendeley_linkage_10seeds.json",
    }
    data = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in sources.items()}
    uncertainty = [
        r"\begin{tabular}{llrrrrr}", r"\toprule",
        "Dataset & Candidate & Conf.-error AUC & AURC & Conformal coverage & "
        "Macro-bin ECE & Weighted ECE" + ROW_END,
        r"\midrule",
    ]
    for key, dataset in (("heart5", "Five States"), ("mendeley", "Mendeley")):
        candidates = (("corrected_osec", "Corrected OSEC"), ("stable_osec", "Stable OSEC"))
        for candidate, label in candidates:
            rows = [seed[candidate] for seed in data[key]["per_seed"]]

            def avg(metric: str) -> float:
                return mean([row[metric] for row in rows])

            uncertainty.append(
                f"{dataset} & {label} & {avg('confidence_error_auc'):.3f} & "
                f"{avg('aurc'):.4f} & {avg('conformal_coverage'):.3f} & "
                f"{avg('ece_uniform'):.3f} & {avg('ece_weighted_uniform'):.3f}" + ROW_END
            )
    uncertainty.extend([r"\bottomrule", r"\end{tabular}"])
    uncertainty_path = TABLES / "uncertainty_evidence_conformal_corrected.tex"
    uncertainty_path.write_text("\n".join(uncertainty) + "\n", encoding="utf-8")

    linkage = [
        r"\begin{tabular}{lrrrrrr}", r"\toprule",
        "Dataset & Cross-seed $\\Phi$ & $\\Delta$ ROC-AUC & $\\Delta$ Conf.-AUC & "
        "$\\Delta$ AURC & $\\Delta$ Macro ECE & $\\Delta$ Weighted ECE" + ROW_END,
        r"\midrule",
    ]
    for key, dataset in (("heart5", "Five States"), ("mendeley", "Mendeley")):
        artifact = data[key]
        diff = artifact["paired_reliability_differences"]
        vals = [diff[name]["mean"] for name in (
            "roc_auc", "confidence_error_auc", "aurc", "ece_uniform", "ece_weighted_uniform"
        )]
        phi = artifact["stability"]["cross_seed_selected_set_nogueira"]
        linkage.append(
            f"{dataset} & {phi:.3f} & {vals[0]:+.4f} & {vals[1]:+.4f} & "
            f"{vals[2]:+.4f} & {vals[3]:+.4f} & {vals[4]:+.4f}" + ROW_END
        )
    linkage.extend([r"\bottomrule", r"\end{tabular}"])
    linkage_path = TABLES / "stability_reliability_linkage_conformal_corrected.tex"
    linkage_path.write_text("\n".join(linkage) + "\n", encoding="utf-8")

    script_path = Path(__file__)
    manifest = {
        "protocol": (
            "Corrected finite-sample split-conformal quantile; ten paired seeds "
            "42-51; internal source-side benchmarks."
        ),
        "sources": {
            key: {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}
            for key, path in sources.items()
        },
        "generator_sha256": digest(script_path),
        "outputs": {
            str(path.relative_to(ROOT)): digest(path)
            for path in (uncertainty_path, linkage_path)
        },
    }
    (TABLES / "conformal_corrected_table_manifest_20261107.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
