"""Validate the external-data gate without reading any patient data."""

from __future__ import annotations

import argparse
from pathlib import Path

from cardiodiag.external_gate import validate_external_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    validate_external_manifest(args.manifest)
    print(f"External manifest is frozen and approved: {args.manifest}")


if __name__ == "__main__":
    main()
