"""Input validation helpers for the offline CARDIODIAG research demo."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pandas as pd

from cardiodiag.domain_guard import DomainAwareSelectivePredictor


def load_verified_predictor(bundle_path: str | Path) -> DomainAwareSelectivePredictor:
    """Load a bundle only when its adjacent demo manifest hash matches."""

    path = Path(bundle_path)
    manifest_path = path.with_name("domain_guard_demo_manifest.json")
    if not path.is_file():
        raise ValueError(f"model bundle not found: {path}")
    if not manifest_path.is_file():
        raise ValueError(f"model integrity manifest not found: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("model integrity manifest is unreadable") from exc
    expected_hash = manifest.get("model_bundle_sha256")
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if not isinstance(expected_hash, str) or expected_hash != actual_hash:
        raise ValueError("model bundle SHA-256 does not match its demo manifest")
    return DomainAwareSelectivePredictor.load(path)


def build_input_frame(
    predictor: DomainAwareSelectivePredictor, values: Mapping[str, Any]
) -> pd.DataFrame:
    """Validate exactly the model's declared schema and return one ordered row.

    The broad numeric bounds are data-entry sanity guards, not clinical reference
    intervals. They are deliberately labelled that way in the desktop UI.
    """

    expected = tuple(predictor.features)
    received = tuple(values)
    if set(received) != set(expected):
        missing = sorted(set(expected) - set(received))
        unexpected = sorted(set(received) - set(expected))
        raise ValueError(f"Input schema mismatch; missing={missing}, unexpected={unexpected}")

    row: dict[str, float | str] = {}
    for name in expected:
        value = values[name]
        if name in predictor.numeric_features:
            try:
                numeric = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{name} must be a finite number") from exc
            if not pd.notna(numeric) or numeric in (float("inf"), float("-inf")):
                raise ValueError(f"{name} must be a finite number")
            if name == "age" and not 1 <= numeric <= 120:
                raise ValueError("age must be between 1 and 120 years (demo input guard)")
            if name == "chol" and not 1 <= numeric <= 1000:
                raise ValueError("chol must be between 1 and 1000 mg/dL (demo input guard)")
            row[name] = numeric
        else:
            category = str(value).strip().lower()
            allowed = predictor.allowed_categories.get(name, [])
            if not category:
                raise ValueError(f"{name} is required")
            if allowed and category not in allowed:
                raise ValueError(f"unsupported value for {name}; allowed values: {allowed}")
            row[name] = category

    return pd.DataFrame([{name: row[name] for name in expected}], columns=expected)


def run_research_demo_prediction(
    predictor: DomainAwareSelectivePredictor,
    values: Mapping[str, Any],
    domain_id: str | None,
) -> dict[str, Any]:
    """Execute the frozen fail-closed research policy on one explicitly typed row."""

    frame = build_input_frame(predictor, values)
    return predictor.predict(frame, domain_id)[0]
