"""Hash the audited manuscript inputs and final PDF into a publication manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "paper" / "build" / "research_draft_20261105"
BUILT_PDF = BUILD / "manuscript.pdf"
OUTPUT_PDF = ROOT / "output" / "pdf" / "CARDIODIAG_Research_Draft_20261105.pdf"
MANIFEST = BUILD / "publication_manifest.json"
CONTACT_SHEET = BUILD / "contact_sheet.png"
SOURCES = [
    "paper/manuscript.tex",
    "paper/references.bib",
    "paper/tables/validity_sensitivity_mendeley.tex",
    "paper/tables/validity_sensitivity_angiocad.tex",
    "paper/tables/nested_summary.tex",
    "paper/tables/domain_guard_transfer.tex",
    "paper/figures/master_directive_20261105_final/figure_manifest.json",
    "data/manifests/uci_heart_disease_transfer_study.json",
    "data/manifests/angiocad_external.json",
    "data/manifests/mendeley_cardiovascular_2021.json",
    "data/manifests/local_datasets.json",
    "LICENSE_AND_ATTRIBUTION.md",
    "docs/DATA_PROVENANCE.md",
    "docs/TRANSFER_STUDY_PROTOCOL_20261105_ANGIOCAD.md",
    "docs/VALIDITY_AUDIT_20261105.md",
    "docs/REMAINING_WORK_REGISTER_20261105.md",
    "docs/EXTERNAL_DATA_ACCESS_PATHWAYS.md",
    "docs/LIMITATION_RESOLUTION_MATRIX.md",
    "results/master_directive_20261105_serial/mendeley_nested_validation.json",
    "results/validity_audit_20261105/mendeley_without_major_vessels.json",
    "results/transfer_20261105_angiocad_external/run_manifest.json",
    "results/transfer_20261105_angiocad_external/external_predictions.csv",
    "results/validity_audit_20261105/angiocad_without_fbs_final/run_manifest.json",
    "results/validity_audit_20261105/angiocad_without_fbs_final/target_predictions.csv",
    "results/validity_audit_20261105/validity_sensitivity_audit.json",
    "experiments/run_nested_validation.py",
    "experiments/run_angiocad_fbs_sensitivity.py",
    "experiments/audit_validity_sensitivities.py",
    "experiments/build_validity_audit_publication_manifest.py",
    "src/cardiodiag/nested_validation.py",
    "src/cardiodiag/data.py",
]
TECTONIC_ARCHIVE_SHA256 = (
    "f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not BUILT_PDF.is_file() or not OUTPUT_PDF.is_file():
        raise FileNotFoundError("Build PDF or final output PDF is missing")
    if not CONTACT_SHEET.is_file():
        raise FileNotFoundError("Rendered-page contact sheet is missing")
    if sha256(BUILT_PDF) != sha256(OUTPUT_PDF):
        raise ValueError("Built PDF and delivered output PDF differ")
    missing = [relative for relative in SOURCES if not (ROOT / relative).is_file()]
    if missing:
        raise FileNotFoundError(f"Publication inputs are missing: {missing}")

    manifest = {
        "status": "compiled_and_visually_inspected",
        "assessment_date": "2026-11-05",
        "compiler": {
            "name": "Tectonic",
            "version": "0.17.0",
            "archive_sha256": TECTONIC_ARCHIVE_SHA256,
        },
        "build_command": (
            "tectonic -k --keep-logs -o build/research_draft_20261105 manuscript.tex"
        ),
        "rendering": (
            "Poppler pdftoppm at 110 dpi; all 13 pages reviewed in the contact "
            "sheet; pages 1, 12, and 13 inspected full-page."
        ),
        "visual_review": {
            "pages_in_contact_sheet": 13,
            "full_pages_inspected": [1, 12, 13],
            "contact_sheet": CONTACT_SHEET.relative_to(ROOT).as_posix(),
            "contact_sheet_sha256": sha256(CONTACT_SHEET),
        },
        "sources": [
            {"path": relative, "sha256": sha256(ROOT / relative)} for relative in SOURCES
        ],
        "build_pdf": {
            "path": BUILT_PDF.relative_to(ROOT).as_posix(),
            "sha256": sha256(BUILT_PDF),
        },
        "output_pdf": {
            "path": OUTPUT_PDF.relative_to(ROOT).as_posix(),
            "sha256": sha256(OUTPUT_PDF),
        },
        "page_count": 13,
        "latex_log_warnings": [
            "Fontconfig reports no default configuration in this desktop runtime.",
            "Tectonic reports font fallback and underfull boxes; "
            "no unresolved citation/reference or overfull-box warnings were found.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote publication manifest: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
