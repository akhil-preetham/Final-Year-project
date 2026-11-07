"""Check whether UCI Statlog adds patients beyond the Cleveland source."""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATLOG_ARCHIVE = ROOT / "data" / "external" / "uci_statlog_heart" / "statlog_heart.zip"
HEART_ARCHIVE = ROOT / "data" / "external" / "uci_heart_disease_45" / "heart_disease.zip"
OUTPUT = ROOT / "data" / "external" / "uci_statlog_heart" / "overlap_audit.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_statlog_rows() -> list[tuple[float, ...]]:
    with zipfile.ZipFile(STATLOG_ARCHIVE) as archive:
        lines = archive.read("heart.dat").decode("ascii").splitlines()
    rows = []
    for line in lines:
        if not line.strip():
            continue
        values = [float(value) for value in line.split()]
        if len(values) != 14:
            raise ValueError("Expected 13 predictors and one Statlog class")
        predictors = tuple(values[:13])
        binary_target = int(values[13] == 2.0)
        rows.append((*predictors, float(binary_target)))
    return rows


def load_cleveland_rows() -> list[tuple[float, ...]]:
    with zipfile.ZipFile(HEART_ARCHIVE) as archive:
        lines = archive.read("processed.cleveland.data").decode("ascii").splitlines()
    rows = []
    for line in lines:
        values = [value.strip() for value in line.split(",")]
        if len(values) != 14 or "?" in values:
            continue
        numeric = [float(value) for value in values]
        predictors = tuple(numeric[:13])
        binary_target = int(numeric[13] > 0)
        rows.append((*predictors, float(binary_target)))
    return rows


def main() -> None:
    for path in (STATLOG_ARCHIVE, HEART_ARCHIVE):
        if not path.is_file():
            raise FileNotFoundError(path)
    statlog = load_statlog_rows()
    cleveland = load_cleveland_rows()
    cleveland_set = set(cleveland)
    matched = sum(row in cleveland_set for row in statlog)
    cleveland_features = {}
    for row in cleveland:
        cleveland_features.setdefault(row[:13], set()).add(row[13])
    label_conflicts = sum(
        row[:13] in cleveland_features and row[13] not in cleveland_features[row[:13]]
        for row in statlog
    )
    if matched != len(statlog) or label_conflicts:
        raise AssertionError("Statlog is not a complete exact duplicate of Cleveland")
    report = {
        "dataset": "UCI Statlog (Heart)",
        "source_url": "https://archive.ics.uci.edu/static/public/145/statlog%2Bheart.zip",
        "source_page": "https://archive.ics.uci.edu/dataset/145/statlog%2Bheart",
        "doi": "10.24432/C57303",
        "license": "CC BY 4.0",
        "audited_utc": datetime.now(UTC).isoformat(),
        "audit_code_sha256": sha256_file(Path(__file__)),
        "statlog_archive_sha256": sha256_file(STATLOG_ARCHIVE),
        "cleveland_comparison_archive_sha256": sha256_file(HEART_ARCHIVE),
        "statlog_rows": len(statlog),
        "cleveland_complete_rows": len(cleveland),
        "exact_matching_rows_after_binary_target_harmonization": matched,
        "feature_match_label_conflicts": int(label_conflicts),
        "duplicate_fraction": matched / len(statlog) if statlog else None,
        "decision": "excluded as an unseen-site validation cohort because all rows match Cleveland",
        "matching_definition": (
            "Exact match on all 13 numerical features and binary outcome after mapping "
            "Cleveland num>0 to 1 and Statlog class 2 to 1."
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {matched}/{len(statlog)} Statlog records match Cleveland; wrote {OUTPUT}")


if __name__ == "__main__":
    main()
