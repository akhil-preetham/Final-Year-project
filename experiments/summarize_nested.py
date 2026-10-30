"""Create manuscript-ready summary tables from nested-validation JSON."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

FIELDS = [
    "dataset",
    "candidate",
    "accuracy_mean",
    "accuracy_sd",
    "roc_auc_mean",
    "roc_auc_sd",
    "roc_auc_ci_low",
    "roc_auc_ci_high",
    "pr_auc_mean",
    "pr_auc_sd",
    "pr_auc_ci_low",
    "pr_auc_ci_high",
    "brier_mean",
    "brier_sd",
    "ece_mean",
    "ece_sd",
]


def rows_from_result(path: Path) -> list[dict[str, str | float]]:
    result = json.loads(path.read_text(encoding="utf-8"))
    dataset = result["config"]["dataset"]
    rows = []
    for candidate, payload in result["candidates"].items():
        mean = payload["fold_mean"]
        std = payload["fold_std"]
        ci = payload["bootstrap_ci"]
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "accuracy_mean": mean["accuracy"],
                "accuracy_sd": std["accuracy"],
                "roc_auc_mean": mean["roc_auc"],
                "roc_auc_sd": std["roc_auc"],
                "roc_auc_ci_low": ci["roc_auc"]["low"],
                "roc_auc_ci_high": ci["roc_auc"]["high"],
                "pr_auc_mean": mean["pr_auc"],
                "pr_auc_sd": std["pr_auc"],
                "pr_auc_ci_low": ci["pr_auc"]["low"],
                "pr_auc_ci_high": ci["pr_auc"]["high"],
                "brier_mean": mean["brier"],
                "brier_sd": std["brier"],
                "ece_mean": mean["ece_uniform"],
                "ece_sd": std["ece_uniform"],
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, nargs="+", required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    rows = [row for path in args.input for row in rows_from_result(path)]
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        (
            "| Dataset | Candidate | ROC-AUC mean±SD | ROC-AUC bootstrap 95% CI | "
            "PR-AUC mean±SD | Brier mean±SD | ECE mean±SD |"
        ),
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['candidate']} | "
            f"{row['roc_auc_mean']:.3f}±{row['roc_auc_sd']:.3f} | "
            f"[{row['roc_auc_ci_low']:.3f}, {row['roc_auc_ci_high']:.3f}] | "
            f"{row['pr_auc_mean']:.3f}±{row['pr_auc_sd']:.3f} | "
            f"{row['brier_mean']:.3f}±{row['brier_sd']:.3f} | "
            f"{row['ece_mean']:.3f}±{row['ece_sd']:.3f} |"
        )
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} summary rows")


if __name__ == "__main__":
    main()
