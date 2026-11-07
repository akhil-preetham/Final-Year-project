"""Fail-closed check before including dataset records in a release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "registry" / "datasets.json"
APPROVED_STATUS = "approved_for_redistribution"


def check_dataset_ids(dataset_ids: list[str], registry_path: Path = REGISTRY) -> None:
    """Raise when any requested dataset lacks explicit redistribution approval."""
    registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    records = {record["id"]: record for record in registry.get("datasets", [])}
    failures: list[str] = []
    for dataset_id in dataset_ids:
        record = records.get(dataset_id)
        if record is None:
            failures.append(f"{dataset_id}: not present in registry")
        elif record.get("redistribution") != APPROVED_STATUS:
            failures.append(
                f"{dataset_id}: redistribution status is "
                f"{record.get('redistribution', 'missing')!r}"
            )
    if failures:
        raise ValueError("Dataset release blocked: " + "; ".join(failures))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_ids", nargs="+", help="Registry IDs proposed for redistribution")
    args = parser.parse_args()
    check_dataset_ids(args.dataset_ids)
    print("All requested dataset IDs have explicit redistribution approval.")


if __name__ == "__main__":
    main()
