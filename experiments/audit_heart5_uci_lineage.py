"""Audit row-level compatibility between Heart5 and the licensed UCI cohorts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "heart5.csv"
ARCHIVE_PATH = ROOT / "data" / "external" / "uci_heart_disease_45" / "heart_disease.zip"
EXPECTED_ARCHIVE_SHA256 = "b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc"
REPORT_PATH = ROOT / "results" / "data_provenance_audits" / "heart5_uci_lineage.json"
ROW_MAP_PATH = ROOT / "results" / "data_provenance_audits" / "heart5_uci_row_map.csv"

COHORT_FILES = {
    "cleveland": "processed.cleveland.data",
    "hungary": "processed.hungarian.data",
    "switzerland": "processed.switzerland.data",
    "va_long_beach": "processed.va.data",
}
FIELD_INDEX = {
    "Age": 0,
    "Sex": 1,
    "ChestPainType": 2,
    "RestingBP": 3,
    "Cholesterol": 4,
    "FastingBS": 5,
    "RestingECG": 6,
    "MaxHR": 7,
    "ExerciseAngina": 8,
    "Oldpeak": 9,
    "ST_Slope": 10,
    "HeartDisease": 13,
}
FEATURE_COLUMNS = tuple(FIELD_INDEX)
CATEGORY_MAPS = {
    "Sex": {0: "F", 1: "M"},
    "ChestPainType": {1: "TA", 2: "ATA", 3: "NAP", 4: "ASY"},
    "RestingECG": {0: "Normal", 1: "ST", 2: "LVH"},
    "ExerciseAngina": {0: "N", 1: "Y"},
    "ST_Slope": {1: "Up", 2: "Flat", 3: "Down"},
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value: Any) -> tuple[str, str] | None:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        return ("text", value.strip())
    return ("number", format(float(value), ".12g"))


def load_uci_records(archive_path: Path = ARCHIVE_PATH) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with ZipFile(archive_path) as archive:
        available = set(archive.namelist())
        for cohort, filename in COHORT_FILES.items():
            if filename not in available:
                raise ValueError(f"Missing UCI source file {filename}")
            frame = pd.read_csv(
                archive.open(filename),
                header=None,
                na_values="?",
            )
            for row_number, row in enumerate(frame.itertuples(index=False, name=None), 1):
                values: dict[str, Any] = {}
                for field, index in FIELD_INDEX.items():
                    value = row[index]
                    if pd.isna(value):
                        values[field] = None
                    elif field == "HeartDisease":
                        values[field] = int(float(value) > 0)
                    elif field in CATEGORY_MAPS:
                        mapped = CATEGORY_MAPS[field].get(int(float(value)))
                        values[field] = mapped
                    else:
                        values[field] = float(value)
                records.append(
                    {
                        "cohort": cohort,
                        "source_row": row_number,
                        "values": values,
                    }
                )
    return records


def source_row_matches(
    heart5_row: dict[str, Any],
    source_values: dict[str, Any],
    *,
    fields: tuple[str, ...] = FEATURE_COLUMNS,
) -> bool:
    """Treat a missing UCI field as unknown; compare every observed field."""

    for field in fields:
        source_value = source_values[field]
        if source_value is None:
            continue
        if normalize(heart5_row[field]) != normalize(source_value):
            return False
    return True


def audit_lineage(
    heart5: pd.DataFrame,
    source_records: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if set(heart5.columns) != set(FEATURE_COLUMNS):
        raise ValueError("Heart5 schema differs from the frozen 12-column map")
    if heart5[list(FEATURE_COLUMNS)].isna().any().any():
        raise ValueError("Heart5 contains missing values; audit assumptions need review")

    distribution: Counter[int] = Counter()
    unique_by_cohort: Counter[str] = Counter()
    row_map: list[dict[str, Any]] = []
    for index, row in enumerate(
        heart5.loc[:, FEATURE_COLUMNS].to_dict(orient="records"), start=1
    ):
        hits = [
            record
            for record in source_records
            if source_row_matches(row, record["values"])
        ]
        distribution[len(hits)] += 1
        if len(hits) == 1:
            unique_by_cohort[hits[0]["cohort"]] += 1
        status = "unique" if len(hits) == 1 else "ambiguous" if hits else "unmatched"
        row_map.append(
            {
                "heart5_row": index,
                "match_count": len(hits),
                "match_status": status,
                "candidate_source_rows": ";".join(
                    f"{record['cohort']}:{record['source_row']}" for record in hits
                ),
            }
        )

    result = {
        "heart5_rows": len(heart5),
        "uci_source_rows": len(source_records),
        "heart5_rows_with_at_least_one_compatible_uci_record": sum(
            count for match_count, count in distribution.items() if match_count > 0
        ),
        "unique_source_row_matches": distribution.get(1, 0),
        "ambiguous_source_row_matches": sum(
            count for match_count, count in distribution.items() if match_count > 1
        ),
        "unmatched_heart5_rows": distribution.get(0, 0),
        "match_count_distribution": {
            str(key): value for key, value in sorted(distribution.items())
        },
        "unique_matches_by_cohort": dict(sorted(unique_by_cohort.items())),
        "match_rule": (
            "For each Heart5 row, compare all 12 mapped fields including binary label "
            "against each of 920 processed UCI source rows. A source '?' value is "
            "treated as unknown and omitted from that comparison; all observed values "
            "must match."
        ),
        "limitation": (
            "Compatibility supports the documented UCI lineage but is not a patient-ID "
            "linkage audit. Missing source fields can make a row ambiguous, and the "
            "audit does not establish how Heart5 imputed values absent in its source row."
        ),
    }
    return result, row_map


def run_audit() -> dict[str, Any]:
    archive_hash = sha256_file(ARCHIVE_PATH)
    if archive_hash != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("UCI source archive hash differs from its frozen manifest")
    heart5 = pd.read_csv(BASE_PATH)
    source_records = load_uci_records()
    result, row_map = audit_lineage(heart5, source_records)
    if result["unmatched_heart5_rows"] != 0:
        raise ValueError("At least one Heart5 row has no compatible UCI source record")

    ROW_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ROW_MAP_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row_map[0]))
        writer.writeheader()
        writer.writerows(row_map)
    report = {
        "audit_id": "CD-DATA-002",
        "assessed_utc": datetime.now(UTC).isoformat(),
        "heart5": {
            "path": BASE_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(BASE_PATH),
        },
        "uci_source": {
            "url": "https://archive.ics.uci.edu/dataset/45/heart%2Bdisease",
            "doi": "10.24432/C52P4X",
            "license": "CC BY 4.0",
            "archive_path": ARCHIVE_PATH.relative_to(ROOT).as_posix(),
            "archive_sha256": archive_hash,
            "source_cohort_rows": {
                record["cohort"]: sum(
                    1 for item in source_records if item["cohort"] == record["cohort"]
                )
                for record in source_records
            },
        },
        "lineage_audit": result,
        "row_map": {
            "path": ROW_MAP_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(ROW_MAP_PATH),
        },
        "audit_code_sha256": sha256_file(Path(__file__).resolve()),
        "interpretation": (
            "All Heart5 rows are source-compatible with UCI records. This supports "
            "attribution to the UCI cohorts, but it does not make Heart5 an independent "
            "cohort and does not establish person-level linkage beyond the source row map."
        ),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    result = run_audit()
    audit = result["lineage_audit"]
    print(
        "PASS: Heart5 rows compatible with UCI source records:",
        f"{audit['heart5_rows_with_at_least_one_compatible_uci_record']}/"
        f"{audit['heart5_rows']};",
        f"unique={audit['unique_source_row_matches']};",
        f"ambiguous={audit['ambiguous_source_row_matches']};",
        f"unmatched={audit['unmatched_heart5_rows']}",
    )
    print(f"Report: {REPORT_PATH.relative_to(ROOT).as_posix()}")
    print(f"Row map: {ROW_MAP_PATH.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
