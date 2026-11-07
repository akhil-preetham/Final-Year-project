"""Run bounded CLIN-ADAPT coordination ablations on development datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cardiodiag.data import drop_identifier_columns, load_dataset
from clin_adapt.nested import NestedConfig, run_nested_validation
from clin_adapt.registry import available_model_specs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--outer-splits", type=int, default=2)
    parser.add_argument("--inner-splits", type=int, default=2)
    parser.add_argument("--max-workers", type=int, default=4)
    args = parser.parse_args()
    X, y = load_dataset(args.dataset, args.target)
    X, _ = drop_identifier_columns(X)
    specs = available_model_specs()
    catboost = [spec for spec in specs if spec.name == "catboost"]
    no_fusion_config = NestedConfig(
        outer_splits=args.outer_splits,
        inner_splits=args.inner_splits,
        max_workers=args.max_workers,
        store_predictions=False,
        allow_fusion=False,
        max_ensemble_size=1,
    )
    full_config = NestedConfig(
        outer_splits=args.outer_splits,
        inner_splits=args.inner_splits,
        max_workers=args.max_workers,
        store_predictions=False,
    )
    runs = {
        "single_catboost": run_nested_validation(X, y, catboost, no_fusion_config),
        "full_portfolio_no_fusion": run_nested_validation(X, y, specs, no_fusion_config),
        "full_portfolio_casl": run_nested_validation(X, y, specs, full_config),
    }
    summary = {
        "status": "completed",
        "dataset": args.dataset,
        "target": args.target,
        "protocol": "bounded 2x2 development ablation; not a confirmatory claim",
        "runs": {
            name: {
                "pooled_metrics": result["pooled_metrics"],
                "runtime_seconds": result["runtime_seconds"],
                "selected_by_fold": [
                    fold["coordination"]["selected_names"] for fold in result["folds"]
                ],
                "configuration": result["configuration"],
            }
            for name, result in runs.items()
        },
        "interpretation": (
            "Ablation evidence is development-only and must not be used as "
            "external validation or novelty proof."
        ),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({"output": str(output), "runs": list(runs)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
