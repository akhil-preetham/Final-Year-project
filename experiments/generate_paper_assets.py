"""Generate the LaTeX nested-validation table from the stored CSV summary."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/tables/nested_summary.csv"))
    parser.add_argument(
        "--output", type=Path, default=Path("paper/tables/nested_summary.tex")
    )
    args = parser.parse_args()
    rows = list(csv.DictReader(args.input.open(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        r"\begin{tabular}{llrrrrr}",
        r"\toprule",
        r"Dataset & Candidate & ROC-AUC & PR-AUC & Brier & ECE & ROC-AUC CI \\",
        r"\midrule",
    ]
    for row in rows:
        dataset = row["dataset"].replace("_", r"\_")
        candidate = row["candidate"].replace("_", r"\_")
        lines.append(
            f"{dataset} & {candidate} & {float(row['roc_auc_mean']):.3f} "
            f"$\\pm$ {float(row['roc_auc_sd']):.3f} & "
            f"{float(row['pr_auc_mean']):.3f} & {float(row['brier_mean']):.3f} & "
            f"{float(row['ece_mean']):.3f} & "
            f"[{float(row['roc_auc_ci_low']):.3f}, {float(row['roc_auc_ci_high']):.3f}] \\\\" 
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
