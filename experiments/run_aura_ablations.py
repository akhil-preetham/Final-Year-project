"""Run prespecified AURA-ML component ablations on development datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_aura_nested import run

from cardiodiag.aura import AURAConfig

ABLATIONS = {
    "full": {},
    "without_intelligence": {"use_intelligence": False},
    "without_adaptive_preprocessing": {"use_intelligence": False},
    "without_multiview": {"use_multiview": False},
    "without_feature_selection": {"use_feature_selection": False},
    "without_dynamic_fusion": {"use_fusion": False},
    "without_reliability_weighting": {"use_reliability": False},
    "without_calibration": {"use_calibration": False},
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--outer-splits", type=int, default=2)
    parser.add_argument("--inner-splits", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    configuration = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in vars(args).items()
    }
    rows = []
    args.output.mkdir(parents=True, exist_ok=True)
    for name, changes in ABLATIONS.items():
        config = AURAConfig(
            inner_splits=args.inner_splits,
            seed=args.seed,
            **changes,
        )
        artifact = args.output / f"{name}.json"
        if artifact.exists():
            result = json.loads(artifact.read_text(encoding="utf-8"))
        else:
            result = run(
                args.dataset,
                args.target,
                artifact,
                args.outer_splits,
                args.inner_splits,
                args.seed,
                config,
            )
        metrics = result["aura_ml"]["pooled_outer_metrics"]
        rows.append(
            {
                "ablation": name,
                "artifact": str(artifact).replace("\\", "/"),
                "runtime_seconds": result["execution"]["runtime_seconds"],
                **{
                    key: metrics[key]
                    for key in ("accuracy", "roc_auc", "pr_auc", "brier", "ece_uniform")
                },
            }
        )
        (args.output / "summary.json").write_text(
            json.dumps(
                {
                    "status": "in_progress",
                    "configuration": configuration,
                    "completed_ablations": rows,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    summary = {"status": "completed", "configuration": configuration, "ablations": rows}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} AURA-ML ablation artifacts to {args.output}")


if __name__ == "__main__":
    main()
