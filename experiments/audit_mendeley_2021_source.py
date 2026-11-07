"""Verify the licensed 2021 Mendeley benchmark and its official codebook."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATASET_ID = "dzz48mvjht"
VERSION = 1
CSV_SHA256 = "9376367dde41e79e432d6402ea5d9e44223fc318ff54ed09966d721923947d1e"
CODEBOOK_SHA256 = "ba341780562d4f81b5bd4298d01b067d6af00dbf0192869221c828d6a0b0467a"
CSV_PATH = ROOT / "MendeleyCardiovascular_Disease_Dataset.csv"
CODEBOOK_PATH = (
    ROOT
    / "data"
    / "external"
    / "mendeley_cardiovascular_2021"
    / "Cardiovascular_Disease_Dataset_Description.pdf"
)
MANIFEST_PATH = ROOT / "data" / "manifests" / "mendeley_cardiovascular_2021.json"
REPORT_PATH = ROOT / "results" / "data_provenance_audits" / "mendeley_2021_source.json"
API_ROOT = "https://data.mendeley.com/public-api"
EXPECTED_COLUMNS = [
    "patientid",
    "age",
    "gender",
    "chestpain",
    "restingBP",
    "serumcholestrol",
    "fastingbloodsugar",
    "restingrelectro",
    "maxheartrate",
    "exerciseangia",
    "oldpeak",
    "slope",
    "noofmajorvessels",
    "target",
]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def request_json(url: str, accept: str = "application/json") -> Any:
    request = Request(
        url,
        headers={"Accept": accept, "User-Agent": "CARDIODIAG research provenance audit"},
    )
    with urlopen(request, timeout=45) as response:
        return json.load(response)


def download_and_verify_source() -> dict[str, Any]:
    """Verify current public API hashes and save the one-page codebook."""

    snapshot_url = f"{API_ROOT}/datasets/{DATASET_ID}/snapshot/{VERSION}"
    snapshot = request_json(snapshot_url)
    files_url = (
        f"{API_ROOT}/datasets/{DATASET_ID}/files?folder_id=root&version={VERSION}"
        "&%24start=0&%24limit=1000"
    )
    files = request_json(
        files_url,
        accept="application/vnd.mendeley-public-dataset.1+json",
    )
    expected_files = {
        "Cardiovascular_Disease_Dataset.csv": CSV_SHA256,
        "Cardiovascular_Disease_Dataset_Description.pdf": CODEBOOK_SHA256,
    }
    observed_files = {item.get("filename"): item for item in files}
    for filename, expected_hash in expected_files.items():
        record = observed_files.get(filename)
        if record is None:
            raise ValueError(f"Mendeley source record is missing {filename}")
        observed_hash = record.get("content_details", {}).get("sha256_hash")
        if observed_hash != expected_hash:
            raise ValueError(f"Mendeley API hash changed for {filename}")

    license_name = snapshot.get("licence", {}).get("short_name")
    if license_name != "CC BY 4.0":
        raise ValueError(f"Unexpected Mendeley license: {license_name!r}")

    codebook_record = observed_files["Cardiovascular_Disease_Dataset_Description.pdf"]
    download_url = codebook_record["content_details"]["download_url"]
    request = Request(download_url, headers={"User-Agent": "CARDIODIAG research provenance audit"})
    with urlopen(request, timeout=60) as response:
        codebook_bytes = response.read()
    if sha256_bytes(codebook_bytes) != CODEBOOK_SHA256:
        raise ValueError("Downloaded Mendeley codebook hash differs from the API record")
    CODEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    CODEBOOK_PATH.write_bytes(codebook_bytes)
    return {
        "checked": True,
        "dataset_id": snapshot.get("id"),
        "version": snapshot.get("version"),
        "license": license_name,
        "api_csv_sha256": expected_files["Cardiovascular_Disease_Dataset.csv"],
        "api_codebook_sha256": expected_files[
            "Cardiovascular_Disease_Dataset_Description.pdf"
        ],
    }


def audit_local() -> dict[str, Any]:
    """Check the frozen local CSV/codebook against the source manifest."""

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    csv_hash = sha256_file(CSV_PATH)
    codebook_hash = sha256_file(CODEBOOK_PATH)
    if csv_hash != CSV_SHA256 or csv_hash != manifest["csv_sha256"]:
        raise ValueError("Local Mendeley CSV hash differs from the frozen source hash")
    if codebook_hash != CODEBOOK_SHA256 or codebook_hash != manifest["codebook_sha256"]:
        raise ValueError("Local Mendeley codebook hash differs from the frozen source hash")

    frame = pd.read_csv(CSV_PATH)
    if frame.columns.tolist() != EXPECTED_COLUMNS or frame.shape != (1000, 14):
        raise ValueError(f"Unexpected Mendeley CSV schema: {frame.shape}, {frame.columns.tolist()}")
    if frame["patientid"].duplicated().any() or frame.isna().any().any():
        raise ValueError("Mendeley CSV has duplicate identifiers or missing values")
    target_counts = Counter(frame["target"].astype(int))
    if target_counts != {0: 420, 1: 580}:
        raise ValueError(f"Unexpected Mendeley target counts: {target_counts}")

    return {
        "audit_id": "CD-DATA-003",
        "audited_utc": datetime.now(UTC).isoformat(),
        "source_url": manifest["source_url"],
        "doi": manifest["doi"],
        "license": manifest["license"],
        "csv_path": manifest["csv_path"],
        "csv_sha256": csv_hash,
        "codebook_path": manifest["codebook_path"],
        "codebook_sha256": codebook_hash,
        "rows": int(len(frame)),
        "columns": frame.columns.tolist(),
        "target": "target",
        "target_counts": {str(key): int(value) for key, value in sorted(target_counts.items())},
        "target_codebook": manifest["target_codebook"],
        "reference_standard": manifest["reference_standard"],
        "role": manifest["role"],
        "eligibility_note": manifest["eligibility_note"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--download",
        action="store_true",
        help="refresh the official Mendeley API check and download its codebook",
    )
    args = parser.parse_args()
    online_check = download_and_verify_source() if args.download else {"checked": False}
    report = audit_local()
    report["online_source_check"] = online_check
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: verified {report['rows']} rows and official source codebook")
    print(f"Report: {REPORT_PATH.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
