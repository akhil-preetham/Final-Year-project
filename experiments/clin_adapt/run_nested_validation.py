"""Run the CLIN-ADAPT provisional CASL nested benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from clin_adapt.nested import NestedConfig, run_nested_validation
from clin_adapt.registry import discover_model_registry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--outer-splits", type=int, default=3)
    parser.add_argument("--inner-splits", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=float, default=None)
    parser.add_argument("--no-predictions", action="store_true")
    parser.add_argument("--models", nargs="*", default=None)
    args = parser.parse_args()
    X, y = load_dataset(args.dataset, args.target)
    X, dropped = drop_identifier_columns(X)
    registry = discover_model_registry(args.seed)
    specs = [spec for spec in registry if spec.status != "unavailable"]
    if args.models:
        requested = set(args.models)
        specs = [spec for spec in specs if spec.name in requested]
        if not specs:
            raise SystemExit("No requested models are available")
    config = NestedConfig(
        outer_splits=args.outer_splits,
        inner_splits=args.inner_splits,
        seed=args.seed,
        max_workers=args.max_workers,
        timeout_seconds=args.timeout_seconds,
        store_predictions=not args.no_predictions,
    )
    output = Path(args.output)
    checkpoint = output.with_suffix(output.suffix + ".checkpoint.json")
    result = run_nested_validation(X, y, specs, config=config, checkpoint_path=str(checkpoint))
    result["dataset_summary"] = summarize_dataset(args.dataset, args.target).to_dict()
    result["dropped_identifier_columns"] = dropped
    result["requested_models"] = [spec.name for spec in specs]
    result["registry_snapshot"] = [spec.to_dict() for spec in registry]
    result["artifact_role"] = (
        "CLIN-ADAPT within-dataset development benchmark; not external validation"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output),
                "roc_auc": result["pooled_metrics"]["roc_auc"],
                "selected_folds": [
                    fold["coordination"]["selected_names"] for fold in result["folds"]
                ],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
