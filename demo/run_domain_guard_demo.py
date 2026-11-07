"""Demonstrate classification, uncertainty, OOD, and unknown-site gating."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from cardiodiag.domain_guard import DomainAwareSelectivePredictor

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE = ROOT / "results" / "transfer_20261105_duke_acath_final" / "model_bundle.joblib"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    predictor = DomainAwareSelectivePredictor.load(args.bundle)
    accepted_values = {
        "age": 35.0,
        "sex": "female",
        "chol": 180.0,
        "fbs": "le_120_mg_dl",
    }
    uncertain_values = {
        "age": 55.0,
        "sex": "male",
        "chol": 220.0,
        "fbs": "le_120_mg_dl",
    }
    outside_support_values = {
        "age": 100.0,
        "sex": "male",
        "chol": 1000.0,
        "fbs": "gt_120_mg_dl",
    }

    def make_example(values: dict[str, float | str]) -> pd.DataFrame:
        return pd.DataFrame([{name: values[name] for name in predictor.features}])

    examples = {
        "registered_classified": make_example(accepted_values),
        "registered_uncertain": make_example(uncertain_values),
        "registered_outside_support": make_example(outside_support_values),
    }
    registered_domain = (
        "cleveland"
        if "cleveland" in predictor.source_domains
        else sorted(predictor.source_domains)[0]
    )
    output = {
        "synthetic_example_only": True,
        "registered_domain": registered_domain,
        "registered_source_classified": predictor.predict(
            examples["registered_classified"], registered_domain
        )[0],
        "registered_source_uncertain": predictor.predict(
            examples["registered_uncertain"], registered_domain
        )[0],
        "registered_source_outside_support": predictor.predict(
            examples["registered_outside_support"], registered_domain
        )[0],
        "new_unseen_domain": predictor.predict(
            examples["registered_classified"], "synthetic_new_site"
        )[0],
        "message": (
            "Synthetic cases demonstrate an accepted in-domain prediction, "
            "uncertainty abstention, out-of-support abstention, and unknown-site "
            "abstention. Every abstention withholds the probability; out-of-support "
            "rows also omit the conformal set."
        ),
    }
    classified = output["registered_source_classified"]
    uncertain = output["registered_source_uncertain"]
    outside = output["registered_source_outside_support"]
    unknown = output["new_unseen_domain"]
    if classified["action"] != "classify" or classified["probability"] is None:
        raise RuntimeError("Registered in-support classification demonstration failed")
    if uncertain["action"] != "abstain" or uncertain["probability"] is not None:
        raise RuntimeError("Uncertain-case abstention demonstration failed")
    if outside["action"] != "abstain" or outside["probability"] is not None:
        raise RuntimeError("Out-of-support safety gate failed")
    if outside["prediction_set"]:
        raise RuntimeError("Out-of-support gate exposed a conformal set")
    if unknown["action"] != "abstain" or unknown["probability"] is not None:
        raise RuntimeError("Unknown-domain safety gate failed")
    output_path = args.output or (args.bundle.parent / "domain_guard_demo.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = output_path.with_name(f"{output_path.stem}_manifest.json")
    output["result_file"] = str(output_path.resolve())
    output["manifest_file"] = str(manifest_path.resolve())
    serialized = json.dumps(output, indent=2, sort_keys=True) + "\n"
    output_path.write_text(serialized, encoding="utf-8")
    manifest = {
        "created_utc": datetime.now(UTC).isoformat(),
        "model_bundle": str(args.bundle.resolve()),
        "model_bundle_sha256": hashlib.sha256(args.bundle.read_bytes()).hexdigest(),
        "demo_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "synthetic_inputs": {
            name: frame.to_dict(orient="records") for name, frame in examples.items()
        },
        "result_file": str(output_path.resolve()),
        "result_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(serialized, end="")


if __name__ == "__main__":
    main()
