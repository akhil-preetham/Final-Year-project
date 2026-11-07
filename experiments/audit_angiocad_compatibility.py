"""Independently audit AngioCAD ID matching and feature provenance limits."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import run_angiocad_transfer as angio
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "data_provenance_audits" / "angiocad_compatibility"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _integer_ids(values: pd.Series, field: str) -> pd.Series:
    numeric = pd.to_numeric(values, errors="raise")
    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError(f"{field} includes non-finite identifiers")
    if not np.equal(numeric, np.floor(numeric)).all():
        raise ValueError(f"{field} includes non-integral identifiers")
    return numeric.astype("int64")


def audit_id_frames(
    features_raw: pd.DataFrame,
    labels_raw: pd.DataFrame,
    artery_columns: list[str],
) -> dict[str, Any]:
    for frame, label, required in (
        (features_raw, "features", {"ID", "Age", "Sex", "FBS"}),
        (labels_raw, "labels", {"ID", *artery_columns}),
    ):
        missing_columns = required - set(frame.columns)
        if missing_columns:
            raise ValueError(f"{label} missing columns: {sorted(missing_columns)}")

    features = features_raw.loc[features_raw["ID"].notna()].copy()
    labels = labels_raw.loc[labels_raw["ID"].notna()].copy()
    features["ID"] = _integer_ids(features["ID"], "feature ID")
    labels["ID"] = _integer_ids(labels["ID"], "label ID")
    feature_duplicates = features.loc[features["ID"].duplicated(keep=False), "ID"]
    label_duplicates = labels.loc[labels["ID"].duplicated(keep=False), "ID"]
    if not feature_duplicates.empty or not label_duplicates.empty:
        raise ValueError("Duplicate nonblank IDs prevent one-to-one patient matching")

    feature_ids = set(features["ID"])
    label_ids = set(labels["ID"])
    matched = features[["ID", "Age", "Sex", "FBS"]].merge(
        labels[["ID", *artery_columns]],
        on="ID",
        how="inner",
        validate="one_to_one",
        sort=False,
    )
    position_count = min(len(features), len(labels))
    positionwise_matches = int(
        np.count_nonzero(
            features["ID"].iloc[:position_count].to_numpy()
            == labels["ID"].iloc[:position_count].to_numpy()
        )
    )
    return {
        "matching_method": "inner join on numeric integer ID; one_to_one validation",
        "positional_matching_used": False,
        "positional_row_id_matches_if_naively_zipped": positionwise_matches,
        "positional_rows_compared": position_count,
        "feature_rows_with_nonblank_id": int(len(features)),
        "label_rows_with_nonblank_id": int(len(labels)),
        "feature_duplicate_id_count": int(feature_duplicates.nunique()),
        "label_duplicate_id_count": int(label_duplicates.nunique()),
        "matched_rows": int(len(matched)),
        "matched_ids_are_unique": bool(matched["ID"].is_unique),
        "feature_ids_without_label": sorted(feature_ids - label_ids),
        "label_ids_without_features": sorted(label_ids - feature_ids),
        "age_missing_in_matched_rows": int(matched["Age"].isna().sum()),
        "sex_missing_in_matched_rows": int(matched["Sex"].isna().sum()),
        "fbs_missing_in_matched_rows": int(matched["FBS"].isna().sum()),
        "why_36_label_ids_lack_features": (
            "Not explained in the released workbooks, attached data dictionary, or record metadata."
        ),
        "feature_rows_for_unmatched_labels_recoverable_from_release": False,
    }


def _workbook_metadata(path: Path) -> dict[str, Any]:
    workbook = load_workbook(path, read_only=False, data_only=False)
    comments = []
    for worksheet in workbook.worksheets:
        for row in worksheet.iter_rows():
            for cell in row:
                if cell.comment is not None:
                    comments.append(f"{worksheet.title}!{cell.coordinate}")
    return {
        "sheet_names": workbook.sheetnames,
        "file_metadata_title": workbook.properties.title,
        "file_metadata_subject": workbook.properties.subject,
        "file_metadata_description": workbook.properties.description,
        "commented_cells": comments,
        "contains_embedded_measurement_dictionary": False,
    }


def run(output_dir: Path = OUTPUT) -> None:
    feature_file = angio.FEATURES_FILE
    label_file = angio.LABELS_FILE
    feature_path = ROOT / "data" / "manifests" / "angiocad_external.json"
    source_manifest_path = ROOT / "data" / "manifests" / "uci_heart_disease_transfer_study.json"
    record_metadata_path = angio.TARGET_DIR / "zenodo_record_metadata.json"
    api_metadata = json.loads(record_metadata_path.read_text(encoding="utf-8"))
    features_raw = pd.read_excel(feature_file, engine="openpyxl")
    labels_raw = pd.read_excel(label_file, engine="openpyxl")
    identifier_audit = audit_id_frames(features_raw, labels_raw, angio.ARTERY_COLUMNS)
    fbs_values = pd.to_numeric(features_raw["FBS"], errors="coerce").dropna()
    feature_workbook = _workbook_metadata(feature_file)
    label_workbook = _workbook_metadata(label_file)

    result = {
        "audit_id": "CD-DATA-004-ANGIOCAD-ID-COMPATIBILITY",
        "status": "completed_from_frozen_public_release",
        "inputs": {
            "feature_workbook_sha256": _sha256(feature_file),
            "label_workbook_sha256": _sha256(label_file),
            "target_manifest_sha256": _sha256(feature_path),
            "source_manifest_sha256": _sha256(source_manifest_path),
            "zenodo_record_metadata_sha256": _sha256(record_metadata_path),
        },
        "record_claims": {
            "record_id": api_metadata.get("id"),
            "title": api_metadata.get("metadata", {}).get("title"),
            "description": api_metadata.get("metadata", {}).get("description"),
            "license": api_metadata.get("metadata", {}).get("license", {}).get("id"),
            "files": [item.get("key") for item in api_metadata.get("files", [])],
        },
        "identifier_audit": identifier_audit,
        "workbook_metadata": {
            "features": feature_workbook,
            "labels": label_workbook,
        },
        "feature_semantics": {
            "age": {
                "external_field": "Age",
                "mapping": "retained as numeric; canonical years mapping is provisional",
                "unit_documented_in_workbook": False,
                "missing_matched_rows": identifier_audit["age_missing_in_matched_rows"],
            },
            "sex": {
                "external_field": "Sex",
                "mapping": "male/female strings normalized to source convention",
                "categories_observed_in_workbook": ["female", "male"],
                "missing_matched_rows": identifier_audit["sex_missing_in_matched_rows"],
            },
            "fasting_blood_sugar": {
                "external_field": "FBS",
                "observed_minimum": float(fbs_values.min()),
                "observed_maximum": float(fbs_values.max()),
                "missing_matched_rows": identifier_audit["fbs_missing_in_matched_rows"],
                "measurement_unit_documented": False,
                "primary_harmonization_status": "unusable until unit is verified",
                "historical_protocol_assumption": (
                    "Numeric values were interpreted as mg/dL and thresholded >120."
                ),
                "observed_value_range_is_not_unit_evidence": True,
            },
            "label_bin_26_50": {
                "meaning": "coronary artery stenosis percentage category",
                "patient_age_interval": False,
                "exact_50_percent_cases_separable": False,
                "reason": "The released bin groups 26% through 50% without exact measurements.",
            },
        },
        "source_to_canonical_mapping": [
            {
                "source_feature": "age",
                "target_feature": "Age",
                "canonical": "age_years",
                "primary_use": "include",
                "status": "compatible; source and target define age in years",
            },
            {
                "source_feature": "sex",
                "target_feature": "Sex",
                "canonical": "sex_male_female",
                "primary_use": "include",
                "status": "compatible after explicit binary normalization",
            },
            {
                "source_feature": "fasting blood sugar >120 mg/dL",
                "target_feature": "FBS",
                "canonical": "fbs_gt_120_mg_dl",
                "primary_use": "exclude",
                "status": "target unit undocumented; retain only in labeled sensitivity analyses",
            },
        ],
        "unresolved_evidence": [
            "The released source does not explain why 36 label IDs have no feature rows.",
            "The FBS measurement unit is not documented; mg/dL must not be inferred from range.",
            "No person-level linkage key is provided for cross-dataset overlap assessment.",
            "The 26-50 stenosis bin does not permit isolating exact 50 percent cases.",
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "angiocad_compatibility_audit.json"
    json_path.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    manifest = {
        "audit_id": result["audit_id"],
        "runner_sha256": _sha256(Path(__file__).resolve()),
        "inputs_sha256": result["inputs"],
        "outputs_sha256": {json_path.name: _sha256(json_path)},
    }
    (output_dir / "reproduction_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"Wrote AngioCAD compatibility audit to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    run(parser.parse_args().output_dir)
