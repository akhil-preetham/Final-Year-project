"""One-command internal research stage runner.

This command performs only development-data work. It never evaluates an
external dataset and never changes the final research claim automatically.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from cardiodiag.nested_validation import run_nested_validation

DATASETS = [
    (Path("heart5.csv"), "HeartDisease", "heart5"),
    (Path("MendeleyCardiovascular_Disease_Dataset.csv"), "target", "mendeley"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("results/generated"))
    parser.add_argument("--outer-splits", type=int, default=3)
    parser.add_argument("--inner-splits", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for dataset, target, name in DATASETS:
        output = args.output_dir / f"{name}_nested_validation.json"
        result = run_nested_validation(
            dataset,
            target,
            outer_splits=args.outer_splits,
            outer_repeats=1,
            inner_splits=args.inner_splits,
            seed=args.seed,
        )
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        artifacts.append(str(output))
    manifest = {
        "stage": "internal_nested_validation",
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "external_validation": False,
        "parameters": {
            "outer_splits": args.outer_splits,
            "inner_splits": args.inner_splits,
            "seed": args.seed,
        },
        "artifacts": artifacts,
        "next_gate": "review nested metrics and complete/freeze an independent external manifest",
    }
    manifest_path = args.output_dir / "internal_stage_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Completed internal stage; wrote {len(artifacts)} result files and {manifest_path}")


if __name__ == "__main__":
    main()
