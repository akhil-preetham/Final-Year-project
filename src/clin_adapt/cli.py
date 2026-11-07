"""Small CLIN-ADAPT command-line utilities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cardiodiag.data import load_dataset, summarize_dataset

from .profiling import profile_clinical_dataset
from .registry import discover_model_registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="clin-adapt")
    subparsers = parser.add_subparsers(dest="command", required=True)
    registry = subparsers.add_parser("registry")
    registry.add_argument("--output", default="results/clin_adapt/model_registry.json")
    profile = subparsers.add_parser("profile")
    profile.add_argument("--dataset", required=True)
    profile.add_argument("--target", required=True)
    profile.add_argument("--output", default="results/clin_adapt/profile.json")
    args = parser.parse_args(argv)
    if args.command == "registry":
        payload = {
            "status": "completed",
            "registry_version": "clin-adapt-registry-v1",
            "models": [spec.to_dict() for spec in discover_model_registry()],
        }
    else:
        X, y = load_dataset(args.dataset, args.target)
        payload = {
            "dataset_summary": summarize_dataset(args.dataset, args.target).to_dict(),
            "profile": profile_clinical_dataset(X, y).to_dict(),
        }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
