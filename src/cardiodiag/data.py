"""Dataset loading, validation, and provenance helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class DatasetSummary:
    """Small, serializable summary used by audit and experiment manifests."""

    path: str
    sha256: str
    rows: int
    columns: list[str]
    missing_by_column: dict[str, int]
    duplicate_rows: int
    target: str
    target_counts: dict[str, int]
    numeric_features: list[str]
    categorical_features: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_dataset(path: str | Path, target: str) -> tuple[pd.DataFrame, pd.Series]:
    """Load a CSV and validate that its target is present and binary."""

    csv_path = Path(path)
    frame = _read_csv(csv_path)
    if target not in frame.columns:
        raise ValueError(f"Target column {target!r} is missing from {csv_path}")
    if frame[target].isna().any():
        raise ValueError(f"Target column {target!r} contains missing values")
    target_values = set(frame[target].dropna().unique())
    if not target_values.issubset({0, 1}):
        raise ValueError(f"Target must be binary 0/1; got {sorted(target_values)}")
    features = frame.drop(columns=[target])
    categorical, numeric = feature_schema(features, target)
    features.attrs["categorical_columns"] = categorical
    features.attrs["numeric_columns"] = numeric
    features.attrs["feature_schema_source"] = (
        "explicit local schema" if categorical else "dtype fallback"
    )
    return features, frame[target].astype(int)


def drop_identifier_columns(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Remove obvious record identifiers before model fitting."""

    identifier_names = {"id", "patientid", "patient_id", "subject_id", "record_id"}
    dropped = [column for column in frame.columns if column.lower() in identifier_names]
    cleaned = frame.drop(columns=dropped)
    for key in ("categorical_columns", "numeric_columns"):
        if key in frame.attrs:
            cleaned.attrs[key] = [
                column for column in frame.attrs[key] if column in cleaned.columns
            ]
    if "feature_schema_source" in frame.attrs:
        cleaned.attrs["feature_schema_source"] = frame.attrs["feature_schema_source"]
    return cleaned, dropped


def feature_schema(frame: pd.DataFrame, target: str) -> tuple[list[str], list[str]]:
    """Return explicit feature types for the supplied benchmark schemas.

    Integer-coded categories in the Mendeley file are not continuous clinical
    measurements. The schema is declared by column name and target so that
    preprocessing does not infer geometry from storage dtype. Unknown datasets
    retain a conservative dtype fallback and must provide their own schema
    before being used for external evaluation.
    """

    known_categorical = {
        "HeartDisease": {
            "Sex",
            "ChestPainType",
            "FastingBS",
            "RestingECG",
            "ExerciseAngina",
            "ST_Slope",
        },
        "target": {
            "gender",
            "chestpain",
            "fastingbloodsugar",
            "restingrelectro",
            "exerciseangia",
            "slope",
            "noofmajorvessels",
        },
        "cardio": {
            "gender",
            "cholesterol",
            "gluc",
            "smoke",
            "alco",
            "active",
        },
    }
    identifier_names = {"id", "patientid", "patient_id", "subject_id", "record_id"}
    configured = known_categorical.get(target, set()).intersection(frame.columns)
    categorical = [column for column in frame.columns if column in configured]
    numeric = [
        column
        for column in frame.columns
        if (
            column not in configured
            and column.lower() not in identifier_names
            and pd.api.types.is_numeric_dtype(frame[column])
        )
    ]
    fallback_categorical = [
        column
        for column in frame.columns
        if (
            column not in numeric
            and column not in categorical
            and column.lower() not in identifier_names
        )
    ]
    categorical.extend(fallback_categorical)
    return categorical, numeric


def summarize_dataset(path: str | Path, target: str) -> DatasetSummary:
    """Create a deterministic summary without changing the source file."""

    csv_path = Path(path)
    raw = csv_path.read_bytes()
    frame = _read_csv(csv_path)
    if target not in frame.columns:
        raise ValueError(f"Target column {target!r} is missing from {csv_path}")
    counts = frame[target].value_counts(dropna=False).sort_index()
    categorical, numeric = feature_schema(frame.drop(columns=[target]), target)
    return DatasetSummary(
        path=str(csv_path),
        sha256=sha256(raw).hexdigest(),
        rows=len(frame),
        columns=list(frame.columns),
        missing_by_column={column: int(value) for column, value in frame.isna().sum().items()},
        duplicate_rows=int(frame.duplicated().sum()),
        target=target,
        target_counts={str(key): int(value) for key, value in counts.items()},
        numeric_features=numeric,
        categorical_features=categorical,
    )


def _read_csv(path: Path) -> pd.DataFrame:
    """Read comma- or semicolon-delimited project datasets without rewriting them."""

    return pd.read_csv(path, sep=None, engine="python")
