"""Run a bounded internal comparison and write JSON results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cardiodiag.experiments import run_repeated_experiments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    args = parser.parse_args()
    variants = [
        ("logistic", False),
        ("ovec", False),
        ("osec", False),
        ("logistic", True),
        ("osec", True),
    ]
    results = run_repeated_experiments(args.dataset, args.target, variants, args.seeds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} experiment records to {args.output}")


if __name__ == "__main__":
    main()
