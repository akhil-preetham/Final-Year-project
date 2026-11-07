"""Build a conservative path-level ownership inventory without opening files."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".venv-clean-check",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    ".uv-cache",
}
GENERATED_PREFIXES = ("results/", "output/", "paper/build/", "dist/", "catboost_info/")
THIRD_PARTY_PREFIXES = ("data/raw/", "data/external/", "data/processed/")
THIRD_PARTY_SUFFIXES = {".rar", ".zip", ".xlsx"}


def classify_path(relative_path: str, tracked: bool) -> tuple[str, str, str]:
    """Return conservative ownership class, evidence, and release decision."""
    path = relative_path.replace("\\", "/")
    if path.startswith(GENERATED_PREFIXES):
        return (
            "generated_artifact",
            "Path is within a generated output/build family",
            "exclude_by_default",
        )
    if path.startswith(THIRD_PARTY_PREFIXES) or Path(path).suffix.lower() in THIRD_PARTY_SUFFIXES:
        return (
            "third_party_code_or_data",
            "Dataset/archive path or extension; inspect source-specific rights",
            "exclude_pending_rights_review",
        )
    if tracked:
        return (
            "original_upstream_snapshot",
            "Present in base Git tree; establishes history, not copyright ownership",
            "exclude_pending_owner_and_license_review",
        )
    return (
        "unknown_ownership",
        "Untracked file; authorship and third-party content are unconfirmed",
        "exclude_pending_contributor_confirmation",
    )


def build_rows(root: Path = ROOT) -> list[dict[str, str]]:
    """Inventory files and classify each without reading its contents."""
    tracked_result = subprocess.run(
        ["git", "ls-files"], cwd=root, check=True, capture_output=True, text=True
    )
    tracked = {line.replace("\\", "/") for line in tracked_result.stdout.splitlines()}
    rows: list[dict[str, str]] = []
    for folder, dirnames, filenames in os.walk(root):
        current = Path(folder)
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        for filename in filenames:
            path = current / filename
            relative = path.relative_to(root).as_posix()
            ownership, evidence, release = classify_path(relative, relative in tracked)
            rows.append({
                "path": relative,
                "classification": ownership,
                "git_status": "tracked_in_base" if relative in tracked else "untracked_or_ignored",
                "evidence": evidence,
                "release_disposition": release,
            })
    return sorted(rows, key=lambda row: row["path"].casefold())


def write_matrix(output_path: Path) -> int:
    rows = build_rows()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else ["path"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs" / "CODE_OWNERSHIP_FILE_MATRIX.csv",
    )
    args = parser.parse_args()
    count = write_matrix(args.output)
    print(f"Wrote {count} conservative file ownership rows to {args.output}")


if __name__ == "__main__":
    main()
