"""Prepare licensed UCI clinical datasets for separate, leakage-aware tasks.

Raw downloads remain outside Git under data/external/. Prepared CSV files are
written under data/processed/, which is ignored by the repository release rules.
"""

from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "external"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "new_datasets_20261107"
MI_LATE_ADMISSION_COLUMNS = {93, 94, 95, 100, 101, 102, 103, 104, 105}
MI_PROXY_FIELDS = {"K_SH_POST", "O_L_POST"}
MI_TARGET_FIELDS = set(range(113, 125))


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def summarize(frame: pd.DataFrame, target: str, **details: Any) -> dict[str, Any]:
    return {
        "rows": int(len(frame)),
        "predictor_count": int(frame.shape[1] - 1),
        "target": target,
        "target_counts": {
            str(key): int(value)
            for key, value in frame[target].value_counts().sort_index().items()
        },
        "missing_cells": int(frame.isna().sum().sum()),
        "predictor_missing_fraction": {
            column: float(value)
            for column, value in frame.drop(columns=[target]).isna().mean().sort_values(
                ascending=False
            ).items()
        },
        **details,
    }


def prepare_heart_failure(output_dir: Path) -> dict[str, Any]:
    source = RAW / "uci_heart_failure_519" / "heart_failure_clinical_records_dataset.csv"
    frame = pd.read_csv(source)
    expected_columns = {
        "age",
        "anaemia",
        "creatinine_phosphokinase",
        "diabetes",
        "ejection_fraction",
        "high_blood_pressure",
        "platelets",
        "serum_creatinine",
        "serum_sodium",
        "sex",
        "smoking",
        "time",
        "DEATH_EVENT",
    }
    if set(frame.columns) != expected_columns:
        raise ValueError(f"Unexpected UCI 519 columns: {list(frame.columns)}")
    frame = frame.rename(columns={"DEATH_EVENT": "death_event"})
    if frame["death_event"].isna().any() or not set(frame["death_event"].unique()).issubset(
        {0, 1}
    ):
        raise ValueError("UCI 519 death_event must be complete and binary")
    if frame["time"].isna().any():
        raise ValueError("UCI 519 follow-up time unexpectedly contains missing values")
    time_range = [int(frame["time"].min()), int(frame["time"].max())]
    prepared = frame.drop(columns=["time"])
    destination = output_dir / "uci_heart_failure_519_binary_event.csv"
    prepared.to_csv(destination, index=False)
    return summarize(
        prepared,
        "death_event",
        source_path=str(source.relative_to(ROOT)),
        source_sha256=file_sha256(source),
        prepared_path=str(destination.relative_to(ROOT)),
        prepared_sha256=file_sha256(destination),
        source_followup_time_days_min_max=time_range,
        excluded_predictors=["time"],
        exclusion_reason=(
            "Follow-up duration is outcome-proximal and not a baseline clinical predictor."
        ),
        interpretation=(
            "Binary classification of death recorded by the end of each patient's available "
            "follow-up; the source does not define one common prediction horizon. This is not "
            "a time-to-event model."
        ),
    )


def _category_text(value: Any) -> Any:
    if pd.isna(value):
        return pd.NA
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value).strip()
    if number.is_integer():
        return str(int(number))
    return str(number)


def prepare_mi(output_dir: Path) -> dict[str, Any]:
    source = RAW / "uci_mi_complications_579" / "MI.data"
    schema_path = ROOT / "data" / "manifests" / "uci_mi_complications_579.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    variables = schema["variables"]
    names = [item["name"] for item in variables]
    raw = pd.read_csv(source, header=None, names=names, na_values=["?"], low_memory=False)
    if raw.shape != (1700, 124):
        raise ValueError(f"Unexpected UCI 579 raw shape: {raw.shape}")

    by_column = {int(item["column_1based"]): item for item in variables}
    target_source = "LET_IS"
    if target_source not in raw or raw[target_source].isna().any():
        raise ValueError("UCI 579 lethal-outcome target is missing")
    target_values = set(pd.to_numeric(raw[target_source], errors="raise").astype(int).unique())
    if not target_values.issubset(set(range(8))):
        raise ValueError(f"Unexpected UCI 579 LET_IS values: {sorted(target_values)}")

    admission_columns = [
        column
        for column in range(2, 113)
        if column not in MI_LATE_ADMISSION_COLUMNS
        and by_column[column]["role"] == "Feature"
        and by_column[column]["name"] not in MI_PROXY_FIELDS
    ]
    feature_names = [by_column[column]["name"] for column in admission_columns]
    features = raw[feature_names].copy()
    for column in admission_columns:
        variable = by_column[column]
        name = variable["name"]
        if variable["type"] == "Categorical":
            features[name] = features[name].map(_category_text).astype("object")
        else:
            features[name] = pd.to_numeric(features[name], errors="coerce")
    target = pd.to_numeric(raw[target_source], errors="raise").astype(int).gt(0).astype(int)
    prepared = features.assign(any_lethal_outcome=target)
    destination = output_dir / "uci_mi_complications_579_admission_binary.csv"
    prepared.to_csv(destination, index=False)
    excluded_late = [by_column[column]["name"] for column in sorted(MI_LATE_ADMISSION_COLUMNS)]
    excluded_outcomes = [
        item["name"] for item in variables if int(item["column_1based"]) in MI_TARGET_FIELDS
    ]
    return summarize(
        prepared,
        "any_lethal_outcome",
        source_path=str(source.relative_to(ROOT)),
        source_sha256=file_sha256(source),
        prepared_path=str(destination.relative_to(ROOT)),
        prepared_sha256=file_sha256(destination),
        source_columns=int(raw.shape[1]),
        source_missing_cells=int(raw.isna().sum().sum()),
        admission_timepoint="hospital admission, using UCI's allowed-column list",
        source_excluded_later_observed_columns=excluded_late,
        excluded_identifier=["ID"],
        excluded_contemporaneous_outcome_proxy_fields=sorted(MI_PROXY_FIELDS),
        excluded_all_source_outcome_columns=excluded_outcomes,
        categorical_source_fields=[
            name
            for column, name in zip(admission_columns, feature_names, strict=True)
            if by_column[column]["type"] == "Categorical"
        ],
        high_missingness_fields_over_50_percent=[
            column
            for column, fraction in prepared.drop(columns=["any_lethal_outcome"])
            .isna()
            .mean()
            .items()
            if fraction > 0.5
        ],
        interpretation=(
            "Exploratory binary classification of any recorded lethal outcome (LET_IS > 0). "
            "The UCI record does not specify one common outcome horizon; this is not a CAD "
            "diagnosis or external validation of CARDIODIAG."
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "created_utc_date": "2026-11-07",
        "preparation_code": "experiments/prepare_new_public_datasets.py",
        "release_policy": "Raw and row-level prepared data are excluded from Git/public release.",
        "datasets": {
            "uci_heart_failure_519": prepare_heart_failure(output_dir),
            "uci_mi_complications_579": prepare_mi(output_dir),
        },
    }
    summary_path = output_dir / "preparation_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote prepared datasets and summary to {output_dir}")
    for key, value in summary["datasets"].items():
        print(
            f"{key}: n={value['rows']}, predictors={value['predictor_count']}, "
            f"target_counts={value['target_counts']}"
        )


if __name__ == "__main__":
    main()
