"""Render compact LaTeX tables and figure for the supplemental paper revision."""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "final_research_20261108"
PAPER = ROOT / "paper" / "multi_dataset_study_20261108_dedup_safe_ablation_calibration"


def _metric_difference_table(summary: pd.DataFrame) -> str:
    baseline = summary[summary.method.eq("uncalibrated")].set_index(["dataset", "model"])
    rows = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Method & $\Delta$ Brier & $\Delta$ log loss & $\Delta$ weighted ECE & Lower Brier "
        + r"\\",
        r"\midrule",
        r"Uncalibrated & 0.000 & 0.000 & 0.000 & -- " + r"\\",
    ]
    for method in ("platt", "isotonic", "beta", "temperature"):
        current = summary[summary.method.eq(method)].set_index(["dataset", "model"])
        deltas = {
            "brier": current.pooled_brier - baseline.pooled_brier,
            "log_loss": current.pooled_log_loss - baseline.pooled_log_loss,
            "ece": (
                current.pooled_ece_weighted_10_equal_width
                - baseline.pooled_ece_weighted_10_equal_width
            ),
        }
        improved = int((deltas["brier"] < 0).sum())
        rows.append(
            f"{method.title()} & {deltas['brier'].mean():+.3f} & "
            f"{deltas['log_loss'].mean():+.3f} & {deltas['ece'].mean():+.3f} & "
            f"{improved}/42 " + r"\\"
        )
    rows.extend([r"\bottomrule", r"\end{tabular}"])
    return "\n".join(rows) + "\n"


def _osec_table(summary: pd.DataFrame) -> str:
    rows = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Task & Fixed AUC & Tuned AUC & $\Delta$ AUC & $\Delta$ Brier " + r"\\",
        r"\midrule",
    ]
    display = {
        "uci_cleveland": "Cleveland",
        "uci_hungary": "Hungary$^{\dagger}$",
        "uci_switzerland": "Switzerland",
        "uci_va_long_beach": "VA Long Beach$^{\dagger}$",
        "uci_heart_failure_519": "Heart failure",
        "uci_mi_complications_579": "MI complications",
        "uci_spectf_heart": "SPECTF$^{\ddagger}$",
    }
    for dataset, label in display.items():
        subset = summary[summary.dataset.eq(dataset)].set_index("condition")
        fixed = subset.loc["fixed_default_c_1"]
        tuned = subset.loc["nested_tuned_c"]
        rows.append(
            f"{label} & {fixed.fold_mean_roc_auc:.3f} & {tuned.fold_mean_roc_auc:.3f} & "
            f"{fixed.fold_mean_roc_auc - tuned.fold_mean_roc_auc:+.3f} & "
            f"{fixed.fold_mean_brier - tuned.fold_mean_brier:+.3f} " + r"\\"
        )
    rows.extend([r"\bottomrule", r"\end{tabular}"])
    return "\n".join(rows) + "\n"


def main() -> None:
    calibration_root = RESULTS / "calibration_extension"
    osec_root = RESULTS / "osec_optimization_ablation"
    calibration = pd.read_csv(calibration_root / "summary_metrics.csv")
    osec = pd.read_csv(osec_root / "summary_metrics.csv")
    if calibration[["dataset", "model"]].drop_duplicates().shape[0] != 42:
        raise ValueError("expected seven tasks and six model variants in calibration summaries")
    if osec.dataset.nunique() != 7 or set(osec.condition.unique()) != {
        "fixed_default_c_1",
        "nested_tuned_c",
    }:
        raise ValueError("unexpected OSEC ablation task or condition coverage")
    (PAPER / "tables" / "calibration_comparison.tex").write_text(
        _metric_difference_table(calibration), encoding="utf-8"
    )
    (PAPER / "tables" / "osec_optimization_ablation.tex").write_text(
        _osec_table(osec), encoding="utf-8"
    )
    source_figure = calibration_root / "figures" / "calibration_brier_delta_by_task.pdf"
    target_figure = PAPER / "figures" / source_figure.name
    shutil.copy2(source_figure, target_figure)
    print(f"Wrote tables and figure to {PAPER.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
