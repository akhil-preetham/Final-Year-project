"""Audit release ZIPs for unlicensed raw data and required Mendeley attribution."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
OUTPUT = ROOT / "results" / "data_provenance_audits" / "distribution_data_audit.json"
DATA_MANIFEST = ROOT / "data" / "manifests" / "local_datasets.json"
UNKNOWN_RIGHTS_DATASETS = {"heart5", "kaggle_70k"}
MENDELEY_ATTRIBUTION_TERMS = {
    "mendeley_1k": (
        "https://data.mendeley.com/datasets/dzz48mvjht/1",
        "10.17632/dzz48mvjht.1",
        "CC BY 4.0",
    ),
    "mendeley_2026": (
        "https://data.mendeley.com/datasets/nt4y898vyh/1",
        "10.17632/nt4y898vyh.1",
        "CC BY 4.0",
    ),
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_zip_member(archive: ZipFile, name: str) -> str:
    digest = hashlib.sha256()
    with archive.open(name) as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def run_audit() -> dict:
    manifest = json.loads(DATA_MANIFEST.read_text(encoding="utf-8"))
    heart5_record = next(row for row in manifest if row.get("target") == "HeartDisease")
    kaggle_record = next(row for row in manifest if row.get("target") == "cardio")
    mendeley_record = next(
        row for row in manifest if row.get("target") == "target" and row.get("license")
    )
    mendeley_2026 = json.loads(
        (ROOT / "data" / "manifests" / "mendeley_heart_disease_2026_external.json")
        .read_text(encoding="utf-8")
    )
    dataset_hashes = {
        "heart5": heart5_record["sha256"],
        "kaggle_70k": kaggle_record["sha256"],
        "mendeley_1k": mendeley_record["sha256"],
        "mendeley_2026": mendeley_2026["file_sha256"],
    }
    packages = []
    archives = sorted(DIST_DIR.glob("*.zip"))
    if not archives:
        raise FileNotFoundError("No distribution ZIP files found")

    for path in archives:
        with ZipFile(path) as archive:
            members = archive.namelist()
            dataset_members: dict[str, list[str]] = {
                name: [] for name in dataset_hashes
            }
            derived_70k_named_members: list[str] = []
            for name in members:
                if name.endswith("/"):
                    continue
                member_hash = sha256_zip_member(archive, name)
                for dataset, expected_hash in dataset_hashes.items():
                    if member_hash == expected_hash:
                        dataset_members[dataset].append(name)
                normalized_name = name.lower()
                if "kaggle70k" in normalized_name or "kaggle_70k" in normalized_name:
                    derived_70k_named_members.append(name)

            licensed_mendeley_members = {
                dataset: dataset_members[dataset]
                for dataset in MENDELEY_ATTRIBUTION_TERMS
                if dataset_members[dataset]
            }
            attribution_documents_by_dataset: dict[str, list[str]] = {}
            if licensed_mendeley_members:
                candidate_documents: dict[str, str] = {}
                for name in members:
                    leaf = name.rsplit("/", 1)[-1].lower()
                    if leaf not in {"readme.txt", "readme.md", "license_and_attribution.md"}:
                        continue
                    try:
                        candidate_documents[name] = archive.read(name).decode(
                            "utf-8", "replace"
                        )
                    except KeyError:
                        continue
                for dataset in licensed_mendeley_members:
                    terms = MENDELEY_ATTRIBUTION_TERMS[dataset]
                    attribution_documents_by_dataset[dataset] = [
                        name
                        for name, document in candidate_documents.items()
                        if all(term in document for term in terms)
                    ]
                    if not attribution_documents_by_dataset[dataset]:
                        raise ValueError(
                            f"{path.name} contains {dataset} without complete attribution"
                        )
            packages.append(
                {
                    "archive": path.relative_to(ROOT).as_posix(),
                    "archive_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "member_count": len(members),
                    "dataset_members_by_exact_sha256": dataset_members,
                    "unknown_rights_raw_members": {
                        dataset: dataset_members[dataset]
                        for dataset in UNKNOWN_RIGHTS_DATASETS
                        if dataset_members[dataset]
                    },
                    "derived_70k_named_members": derived_70k_named_members,
                    "mendeley_attribution_documents": attribution_documents_by_dataset,
                }
            )

    if any(item["unknown_rights_raw_members"] for item in packages):
        raise ValueError(
            "A distribution ZIP contains an exact copy of a raw file with unresolved rights"
        )
    result = {
        "audited_utc": datetime.now(UTC).isoformat(),
        "distribution_archives_checked": len(packages),
        "source_dataset_sha256": dataset_hashes,
        "unknown_rights_raw_data_in_any_distribution": False,
        "packages": packages,
        "limitation": (
            "This scan rules out exact byte-for-byte copies of the Heart5 and Kaggle "
            "70K CSVs in the six listed ZIPs and checks source attribution for exact "
            "Mendeley CSV copies. Member-name matches for 70K-derived outputs are "
            "heuristic; the scan does not establish rights to use the source data or "
            "redistribute derived results."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    result = run_audit()
    print(
        "PASS: scanned",
        result["distribution_archives_checked"],
        "release ZIPs; no exact Heart5 or Kaggle 70K raw file included",
    )
    print(f"Report: {OUTPUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
