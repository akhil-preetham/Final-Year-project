"""Write the resolved CLIN-ADAPT model registry without installing packages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clin_adapt.registry import discover_model_registry
from clin_adapt.resources import detect_runtime_resources


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/clin_adapt/model_registry.json")
    args = parser.parse_args()
    specs = discover_model_registry()
    payload = {
        "status": "completed",
        "registry_version": "clin-adapt-registry-v1",
        "runtime_resources": detect_runtime_resources(),
        "models": [spec.to_dict() for spec in specs],
        "available_models": [spec.name for spec in specs if spec.status != "unavailable"],
        "unavailable_models": [spec.name for spec in specs if spec.status == "unavailable"],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output),
                "available": len(payload["available_models"]),
                "unavailable": len(payload["unavailable_models"]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
