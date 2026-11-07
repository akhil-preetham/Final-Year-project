"""Download and audit a 2026 Mendeley heart dataset against Heart5."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from numbers import Real
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATASET_ID = "nt4y898vyh"
VERSION = 1
EXPECTED_FILE_SHA256 = "948420b084d8a3a0ca42b8419fce9aee175879e43f8aedf712377899a67aa49b"
API_ROOT = "https://data.mendeley.com/public-api"
RAW_PATH = ROOT / "data" / "external" / "mendeley_heart_disease_2026" / "heart.csv"
BASE_PATH = ROOT / "heart5.csv"
MANIFEST_PATH = ROOT / "data" / "manifests" / "mendeley_heart_disease_2026_external.json"
REPORT_PATH = (
    ROOT
    / "results"
    / "external_candidate_screen_20261105"
    / "mendeley_heart_disease_2026_overlap.json"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _request_json(url: str, *, accept: str = "application/json") -> Any:
    request = Request(
        url,
        headers={"Accept": accept, "User-Agent": "CARDIODIAG research provenance audit"},
    )
    with urlopen(request, timeout=45) as response:
        return json.load(response)


def download_source() -> tuple[bytes, dict[str, Any]]:
    """Retrieve the public Mendeley snapshot and exact file version."""

    snapshot_url = f"{API_ROOT}/datasets/{DATASET_ID}/snapshot/{VERSION}"
    snapshot = _request_json(snapshot_url)
    files_url = (
        f"{API_ROOT}/datasets/{DATASET_ID}/files?folder_id=root&version={VERSION}"
        "&%24start=0&%24limit=1000"
    )
    files = _request_json(
        files_url,
        accept="application/vnd.mendeley-public-dataset.1+json",
    )
    matches = [entry for entry in files if entry.get("filename") == "heart.csv"]
    if len(matches) != 1:
        raise ValueError(f"Expected one heart.csv in the source record; found {len(matches)}")
    file_record = matches[0]
    content = file_record["content_details"]
    download_request = Request(
        content["download_url"],
        headers={"User-Agent": "CARDIODIAG research provenance audit"},
    )
    with urlopen(download_request, timeout=60) as response:
        raw = response.read()
    expected = content.get("sha256_hash")
    if not expected or sha256_bytes(raw) != expected:
        raise ValueError("Downloaded file does not match the Mendeley API SHA-256")
    if expected != EXPECTED_FILE_SHA256:
        raise ValueError("Mendeley source file hash differs from the frozen audit protocol")
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_bytes(raw)
    return raw, {"snapshot": snapshot, "file_record": file_record}


def canonical_value(value: Any) -> tuple[str, str]:
    """Normalize CSV-inferred numeric types without changing category text."""

    if pd.isna(value):
        return ("null", "")
    if isinstance(value, Real) and not isinstance(value, bool):
        return ("number", format(float(value), ".12g"))
    return ("text", str(value).strip())


def row_multiset(frame: pd.DataFrame, columns: list[str]) -> Counter[tuple[tuple[str, str], ...]]:
    return Counter(
        tuple(canonical_value(value) for value in row)
        for row in frame.loc[:, columns].itertuples(index=False, name=None)
    )


def compare_rows(
    candidate: pd.DataFrame,
    baseline: pd.DataFrame,
    *,
    target: str = "HeartDisease",
) -> dict[str, Any]:
    """Compare full labeled rows and predictor-only rows as multisets."""

    if candidate.columns.has_duplicates or baseline.columns.has_duplicates:
        raise ValueError("Duplicate column names are not allowed")
    if target not in candidate.columns:
        raise ValueError(f"Missing target column {target!r}")
    if set(candidate.columns) != set(baseline.columns):
        raise ValueError("Candidate and baseline schemas differ")
    columns = list(baseline.columns)
    features = [column for column in columns if column != target]
    candidate_all = row_multiset(candidate, columns)
    baseline_all = row_multiset(baseline, columns)
    candidate_x = row_multiset(candidate, features)
    baseline_x = row_multiset(baseline, features)
    exact_labeled_pairs = sum((candidate_all & baseline_all).values())
    same_feature_pairs = sum((candidate_x & baseline_x).values())
    return {
        "candidate_rows": len(candidate),
        "baseline_rows": len(baseline),
        "feature_count": len(features),
        "exact_labeled_row_pairs": exact_labeled_pairs,
        "exact_feature_row_pairs": same_feature_pairs,
        "feature_matches_with_different_or_unpaired_labels": same_feature_pairs
        - exact_labeled_pairs,
        "candidate_rows_not_in_baseline": sum((candidate_all - baseline_all).values()),
        "baseline_rows_not_in_candidate": sum((baseline_all - candidate_all).values()),
        "same_labeled_row_multiset": candidate_all == baseline_all,
        "same_feature_row_multiset": candidate_x == baseline_x,
        "columns": columns,
    }


def run_audit(*, download: bool = False) -> dict[str, Any]:
    source_metadata: dict[str, Any] = {}
    if download:
        _, source_metadata = download_source()
    if not RAW_PATH.is_file():
        raise FileNotFoundError(f"Missing source file; rerun with --download: {RAW_PATH}")
    raw_hash = sha256_file(RAW_PATH)
    if raw_hash != EXPECTED_FILE_SHA256:
        raise ValueError("Local candidate file does not match the frozen Mendeley file hash")

    candidate = pd.read_csv(RAW_PATH)
    baseline = pd.read_csv(BASE_PATH)
    overlap = compare_rows(candidate, baseline)
    if len(candidate) != 918 or len(baseline) != 918:
        raise ValueError("Unexpected row count; inspect before interpreting overlap")
    if not overlap["same_labeled_row_multiset"]:
        raise ValueError("Candidate and Heart5 are not exact labeled-row duplicates")

    base = {
        "candidate": {
            "title": (
                "Heart Disease Clinical Dataset for Artificial Intelligence "
                "and Healthcare Research"
            ),
            "doi": "10.17632/nt4y898vyh.1",
            "version": VERSION,
            "published": "2026-06-22",
            "url": f"https://data.mendeley.com/datasets/{DATASET_ID}/{VERSION}",
            "license": "CC BY 4.0",
            "file": RAW_PATH.relative_to(ROOT).as_posix(),
            "sha256": raw_hash,
            "target_counts": {
                str(int(key)): int(value)
                for key, value in candidate["HeartDisease"].value_counts().sort_index().items()
            },
        },
        "baseline": {
            "file": BASE_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(BASE_PATH),
        },
        "overlap_audit": overlap,
        "interpretation": (
            "The Mendeley release is an exact row-for-row multiset duplicate of Heart5, "
            "including labels. It is not an independent cohort and is excluded from "
            "external validation. The audit establishes duplicate content, not the "
            "upstream authors' patient-level provenance."
        ),
        "external_validation_eligible": False,
        "audited_utc": datetime.now(UTC).isoformat(),
        "audit_code_sha256": sha256_file(Path(__file__).resolve()),
    }
    if source_metadata:
        snapshot = source_metadata["snapshot"]
        base["source_snapshot"] = {
            "id": snapshot.get("id"),
            "version": snapshot.get("version"),
            "doi": snapshot.get("doi"),
            "license": (snapshot.get("licence") or {}).get("short_name"),
            "api_expected_file_sha256": source_metadata["file_record"][
                "content_details"
            ].get("sha256_hash"),
        }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(base, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "source_url": base["candidate"]["url"],
        "doi": base["candidate"]["doi"],
        "license": "CC BY 4.0",
        "attribution": "Saha, A.; Arifen, R.; Azad, A. (2026), Mendeley Data, version 1.",
        "file_path": base["candidate"]["file"],
        "file_sha256": raw_hash,
        "baseline_path": base["baseline"]["file"],
        "baseline_sha256": base["baseline"]["sha256"],
        "audit_report_path": REPORT_PATH.relative_to(ROOT).as_posix(),
        "audit_report_sha256": sha256_file(REPORT_PATH),
        "rows": overlap["candidate_rows"],
        "exact_labeled_row_pairs": overlap["exact_labeled_row_pairs"],
        "same_labeled_row_multiset": overlap["same_labeled_row_multiset"],
        "role": "Duplicate-data provenance screen; excluded from external validation.",
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return base


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--download",
        action="store_true",
        help="Fetch the public Mendeley v1 file and verify its API SHA-256 before auditing.",
    )
    args = parser.parse_args()
    result = run_audit(download=args.download)
    overlap = result["overlap_audit"]
    print(
        "PASS: exact labeled-row duplicate",
        f"({overlap['exact_labeled_row_pairs']}/{overlap['candidate_rows']});",
        "excluded from external validation",
    )
    print(f"Report: {REPORT_PATH.relative_to(ROOT).as_posix()}")
    print(f"Manifest: {MANIFEST_PATH.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
