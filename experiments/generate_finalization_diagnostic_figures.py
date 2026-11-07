"""Generate supplemental figures from frozen finalization evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures" / "finalization_20261107"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(fig: plt.Figure, name: str) -> Path:
    path = OUT / name
    fig.savefig(path, dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)
    return path


def reliability() -> tuple[list[Path], list[Path]]:
    inputs = []
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    datasets = [("Five States", "heart5"), ("Mendeley", "mendeley")]
    colors = {"corrected_osec": "#4C78A8", "stable_osec": "#E45756"}
    for dataset, key in datasets:
        path = (
            ROOT
            / "results"
            / "finalization_20261107"
            / "conformal_corrected"
            / f"{key}_uncertainty_10seeds.json"
        )
        inputs.append(path)
        data = load(path)["candidates"]
        x_base = 0 if key == "heart5" else 1
        for j, (candidate, label) in enumerate(
            (("corrected_osec", "Corrected OSEC"), ("stable_osec", "Stable OSEC"))
        ):
            metrics = data[candidate]
            x = x_base + (j - 0.5) * 0.26
            for metric, offset, marker, mlabel in (
                ("ece_uniform", -0.06, "o", "Macro-bin ECE"),
                ("ece_weighted_uniform", 0.06, "s", "Weighted ECE"),
            ):
                point = metrics[metric]
                low, high = point["bootstrap_ci"]["low"], point["bootstrap_ci"]["high"]
                axes[0].errorbar(
                    x + offset,
                    point["mean"],
                    yerr=[[point["mean"] - low], [high - point["mean"]]],
                    fmt=marker,
                    color=colors[candidate],
                    capsize=3,
                    label=f"{label}, {mlabel}" if key == "heart5" else None,
                )
            point = metrics["conformal_coverage"]
            low, high = point["bootstrap_ci"]["low"], point["bootstrap_ci"]["high"]
            axes[1].errorbar(
                x,
                point["mean"],
                yerr=[[point["mean"] - low], [high - point["mean"]]],
                fmt="o",
                color=colors[candidate],
                capsize=3,
                label=label if key == "heart5" else None,
            )
    axes[0].set_xticks([0, 1], [x[0] for x in datasets])
    axes[0].set_ylabel("Expected calibration error")
    axes[0].set_title("Calibration across ten internal splits")
    axes[0].grid(axis="y", alpha=0.2)
    axes[0].legend(fontsize=7, frameon=False, ncol=2)
    axes[1].axhline(0.9, color="#555555", linestyle="--", linewidth=1, label="Nominal 90%")
    axes[1].set_xticks([0, 1], [x[0] for x in datasets])
    axes[1].set_ylim(0.84, 0.95)
    axes[1].set_ylabel("Empirical prediction-set coverage")
    axes[1].set_title("Corrected finite-sample conformal coverage")
    axes[1].grid(axis="y", alpha=0.2)
    axes[1].legend(fontsize=8, frameon=False)
    fig.suptitle(
        "Repeated internal source-side reliability; points are means, bars are "
        "descriptive bootstrap intervals"
    )
    fig.tight_layout()
    return [save(fig, "corrected_reliability.png")], inputs


def selective() -> tuple[list[Path], list[Path]]:
    path = ROOT / "results" / "selective_audit_20261106_run3" / "risk_coverage_audit.json"
    audit = load(path)
    fig, axis = plt.subplots(figsize=(7.5, 5))
    colors = {"AngioCAD": "#4C78A8", "Duke": "#E45756"}
    for study in audit["studies"]:
        label = study["dataset"]
        points = study["risk_coverage_curve"]
        x = np.array([row["coverage"] for row in points])
        y = np.array([row["selective_risk"] for row in points])
        low = np.array([row["risk_wilson_95"][0] for row in points])
        high = np.array([row["risk_wilson_95"][1] for row in points])
        color = colors["AngioCAD"] if label == "AngioCAD" else colors["Duke"]
        axis.plot(x, y, marker="o", markersize=3, color=color, label=f"{label} (n={study['n']})")
        axis.fill_between(x, low, high, color=color, alpha=0.15)
    axis.set(
        xlim=(0, 1),
        ylim=(0, 1),
        xlabel="Accepted coverage",
        ylabel="Selective risk at fixed probability cutoff 0.5",
    )
    axis.set_title("Post hoc risk-coverage from frozen target predictions")
    axis.grid(alpha=0.2)
    axis.legend(frameon=False)
    axis.text(
        0.02,
        0.98,
        "Wilson 95% intervals, conditional on each cohort.\n"
        "Duke endpoint differs from source; both targets were previously examined.",
        transform=axis.transAxes,
        va="top",
        fontsize=8,
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"},
    )
    fig.tight_layout()
    out = [save(fig, "posthoc_target_risk_coverage.png")]
    fig2, axis2 = plt.subplots(figsize=(7.5, 5))
    for study in audit["studies"]:
        label = study["dataset"]
        points = study["risk_coverage_curve"]
        x = np.array([row["coverage"] for row in points])
        y = np.array([row["selective_risk"] for row in points])
        low = np.array([row["risk_wilson_95"][0] for row in points])
        high = np.array([row["risk_wilson_95"][1] for row in points])
        color = colors["AngioCAD"] if label == "AngioCAD" else colors["Duke"]
        axis2.plot(x, y, marker="o", markersize=3, color=color, label=f"{label} (n={study['n']})")
        axis2.fill_between(x, low, high, color=color, alpha=0.15)
    axis2.set(
        xlim=(0, 1),
        ylim=(0, 0.5),
        xlabel="Accepted coverage",
        ylabel="Selective risk at fixed probability cutoff 0.5",
    )
    axis2.set_title("Post hoc risk-coverage (detail view)")
    axis2.grid(alpha=0.2)
    axis2.legend(frameon=False)
    axis2.text(
        0.02,
        0.98,
        "Upper risk values clipped for readability; full range is shown in the companion figure.",
        transform=axis2.transAxes,
        va="top",
        fontsize=8,
    )
    fig2.tight_layout()
    out.append(save(fig2, "posthoc_target_risk_coverage_detail.png"))
    return out, [path]


def ood() -> tuple[list[Path], list[Path]]:
    records = [
        (
            "Z-Alizadeh Sani\nCD-XD-003",
            ROOT
            / "results"
            / "finalization_20261107"
            / "corrected_quantile_transfer"
            / "CD-XD-003"
            / "run_manifest.json",
            "source_vs_target_ood_auroc",
            "source_vs_target_ood_auroc_bootstrap_95_ci",
        ),
        (
            "AngioCAD IF\nCD-XD-004",
            ROOT
            / "results"
            / "finalization_20261107"
            / "corrected_quantile_transfer"
            / "CD-XD-004"
            / "run_manifest.json",
            "source_vs_target_ood_auroc",
            "source_vs_target_ood_auroc_bootstrap_95_ci",
        ),
    ]
    values = []
    inputs = []
    for label, path, metric, ci_key in records:
        data = load(path)
        inputs.append(path)
        ood = data["ood"]
        ci = ood[ci_key]
        values.append((label, ood[metric], ci["lower_95"], ci["upper_95"]))
    guard_path = (
        ROOT
        / "results"
        / "finalization_20261107"
        / "corrected_quantile_transfer"
        / "CD-XD-006"
        / "study_metrics.json"
    )
    guard = load(guard_path)["ood"]
    inputs.append(guard_path)
    knn = guard["knn_domain_robust"]
    ci = knn["target_auroc_bootstrap_95_ci"]
    values.append(
        ("AngioCAD kNN\nCD-XD-006", knn["target_vs_source_auroc"], ci["lower_95"], ci["upper_95"])
    )
    fig, axis = plt.subplots(figsize=(7.5, 4.5))
    y = np.arange(len(values))
    points = np.array([row[1] for row in values])
    low = np.array([row[2] for row in values])
    high = np.array([row[3] for row in values])
    axis.errorbar(
        points, y, xerr=[points - low, high - points], fmt="o", color="#4C78A8", capsize=4
    )
    axis.axvline(0.5, linestyle="--", color="#555555", label="Chance separation")
    axis.set_yticks(y, [row[0] for row in values])
    axis.invert_yaxis()
    axis.set_xlim(0.45, 0.7)
    axis.set_xlabel("Source-versus-target OOD AUROC (95% conditional bootstrap CI)")
    axis.set_title("Feature-only cohort-shift separation is weak")
    axis.grid(axis="x", alpha=0.2)
    axis.legend(frameon=False)
    fig.tight_layout()
    return [save(fig, "ood_separation_summary.png")], inputs


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    generated = []
    inputs = []
    files, source = reliability()
    generated.extend(files)
    inputs.extend(source)
    files, source = selective()
    generated.extend(files)
    inputs.extend(source)
    files, source = ood()
    generated.extend(files)
    inputs.extend(source)
    script = Path(__file__)
    generated.extend(path.with_suffix(".pdf") for path in list(generated))
    manifest = {
        "status": "complete",
        "interpretation": (
            "All target-labelled diagnostics are retrospective and descriptive; "
            "no target labels were used for fitting, calibration, thresholding, "
            "or method selection."
        ),
        "inputs": [{"path": str(p.relative_to(ROOT)), "sha256": sha256(p)} for p in inputs],
        "generator_sha256": sha256(script),
        "outputs": [{"path": str(p.relative_to(ROOT)), "sha256": sha256(p)} for p in generated],
    }
    manifest_path = OUT / "finalization_diagnostics_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(generated)} finalization figures in {OUT}")


if __name__ == "__main__":
    main()
