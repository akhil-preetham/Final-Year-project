"""Run nested internal validation for the supplied benchmark datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cardiodiag.nested_validation import run_nested_validation
from cardiodiag.provenance import collect_provenance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--outer-splits", type=int, default=3)
    parser.add_argument("--outer-repeats", type=int, default=1)
    parser.add_argument("--inner-splits", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run_nested_validation(
        args.dataset,
        args.target,
        outer_splits=args.outer_splits,
        outer_repeats=args.outer_repeats,
        inner_splits=args.inner_splits,
        seed=args.seed,
    )
    result["provenance"] = collect_provenance(
        dataset=args.dataset,
        target=args.target,
        experiment_type="nested_validation",
        configuration={
            "outer_splits": args.outer_splits,
            "outer_repeats": args.outer_repeats,
            "inner_splits": args.inner_splits,
            "seed": args.seed,
            "scoring": result["config"]["scoring"],
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote nested-validation results to {args.output}")


if __name__ == "__main__":
    main()
