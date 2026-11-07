"""Prepare the isolated multi-dataset evaluation inputs and provenance manifest.

Raw datasets and prepared row-level data remain in ignored local data folders.
Only source identifiers, hashes, schemas, and aggregate descriptions are copied
to the experiment release directory.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from collections import Counter
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
from prepare_new_public_datasets import prepare_heart_failure, prepare_mi
from run_lodo_transfer import load_cohorts

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "external"
PROCESSED = ROOT / "data" / "processed" / "multi_dataset_evaluation_20261108"
HEART_ARCHIVE = RAW / "uci_heart_disease_45" / "heart_disease.zip"
SPECTF_ARCHIVE = RAW / "uci_spectf_heart_96" / "spectf_heart.zip"
UCI_CATEGORICAL = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
UCI_COHORTS = {
    "uci_cleveland": "cleveland",
    "uci_hungary": "hungary",
    "uci_switzerland": "switzerland",
    "uci_va_long_beach": "va_long_beach",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_rows(frame: pd.DataFrame) -> list[str]:
    normalized = frame.astype("object").where(frame.notna(), None)
    return [
        json.dumps(list(row), ensure_ascii=False, separators=(",", ":"), default=str)
        for row in normalized.itertuples(index=False, name=None)
    ]


def summarize_dataset(
    dataset_id: str,
    frame: pd.DataFrame,
    target: str,
    source: dict[str, Any],
    categorical: list[str] | None = None,
    interpretation: str = "",
) -> dict[str, Any]:
    y = frame[target].astype(int)
    feature_frame = frame.drop(columns=[target])
    signatures = canonical_rows(feature_frame)
    paired = pd.DataFrame({"signature": signatures, "target": y.to_numpy()})
    group_sizes = paired.groupby("signature", dropna=False).size()
    label_counts = paired.groupby("signature", dropna=False)["target"].nunique()
    return {
        "dataset_id": dataset_id,
        "rows": int(len(frame)),
        "predictor_count": int(feature_frame.shape[1]),
        "predictor_names": list(feature_frame.columns),
        "categorical_features": categorical or [],
        "target": target,
        "target_definition": source["target_definition"],
        "class_counts": {str(k): int(v) for k, v in y.value_counts().sort_index().items()},
        "prevalence": float(y.mean()),
        "missing_predictor_cells": int(feature_frame.isna().sum().sum()),
        "missing_predictor_fraction_by_feature": {
            name: float(value) for name, value in feature_frame.isna().mean().items() if value > 0
        },
        "exact_duplicate_predictor_rows": int((group_sizes - 1).clip(lower=0).sum()),
        "duplicate_predictor_groups_with_label_conflict": int((label_counts > 1).sum()),
        "source": source,
        "interpretation": interpretation,
    }


def prepare_uci_cohorts() -> dict[str, dict[str, Any]]:
    if not HEART_ARCHIVE.is_file():
        raise FileNotFoundError(HEART_ARCHIVE)
    if sha256_file(HEART_ARCHIVE) != (
        "b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc"
    ):
        raise ValueError("UCI Heart Disease archive hash differs from the frozen project manifest")
    cohorts, source_manifest = load_cohorts(HEART_ARCHIVE, zero_as_missing=True)
    out: dict[str, dict[str, Any]] = {}
    for dataset_id, cohort_name in UCI_COHORTS.items():
        cohort = cohorts[cohort_name]
        frame = cohort["X"].copy()
        frame["cad_positive"] = cohort["y"].astype(int)
        path = PROCESSED / f"{dataset_id}.csv"
        frame.to_csv(path, index=False)
        source = {
            "name": "UCI Heart Disease",
            "dataset_id": 45,
            "doi": "10.24432/C52P4X",
            "url": "https://archive.ics.uci.edu/dataset/45/heart%2Bdisease",
            "license": "CC BY 4.0; attribution required",
            "archive_path": "data/external/uci_heart_disease_45/heart_disease.zip",
            "archive_sha256": sha256_file(HEART_ARCHIVE),
            **source_manifest[cohort_name],
            "prepared_path": path.relative_to(ROOT).as_posix(),
            "prepared_sha256": sha256_file(path),
            "target_definition": "UCI num=0 vs num=1..4; >50% stenosis as coded by UCI.",
            "cohort_name": cohort_name,
            "preprocessing_note": (
                "Question-mark values treated as missing; zero cholesterol and zero resting "
                "blood pressure recoded as missing per prior project protocol."
            ),
            "lineage_note": (
                "This cohort is represented in the previously used Heart5 composite; this run "
                "is retrospective and is not independent validation."
            ),
        }
        out[dataset_id] = summarize_dataset(
            dataset_id,
            frame,
            "cad_positive",
            source,
            categorical=UCI_CATEGORICAL,
            interpretation="Legacy angiographic CAD cohort; retrospective source stress test.",
        )
    return out


def prepare_spectf() -> dict[str, Any]:
    if not SPECTF_ARCHIVE.is_file():
        raise FileNotFoundError(SPECTF_ARCHIVE)
    names: list[str]
    with zipfile.ZipFile(SPECTF_ARCHIVE) as archive:
        required = {"SPECTF.train", "SPECTF.test", "SPECTF.names"}
        if not required.issubset(set(archive.namelist())):
            raise ValueError("SPECTF source archive is missing expected official files")
        names_text = archive.read("SPECTF.names").decode("utf-8", errors="replace")
        names = ["OVERALL_DIAGNOSIS"] + [
            f"F{index}{suffix}" for index in range(1, 23) for suffix in ("R", "S")
        ]
        partitions: dict[str, pd.DataFrame] = {}
        member_hashes: dict[str, str] = {}
        for split in ("train", "test"):
            member = f"SPECTF.{split}"
            raw = archive.read(member)
            member_hashes[member] = sha256_bytes(raw)
            data = pd.read_csv(BytesIO(raw), sep=",", header=None, skipinitialspace=True)
            expected_rows = 80 if split == "train" else 187
            if data.shape != (expected_rows, 45):
                raise ValueError(f"Unexpected {member} shape: {data.shape}")
            data.columns = names
            data = data.apply(pd.to_numeric, errors="raise").astype(int)
            if not set(data["OVERALL_DIAGNOSIS"].unique()).issubset({0, 1}):
                raise ValueError(f"Unexpected target code in {member}")
            partitions[split] = data

    train, test = partitions["train"], partitions["test"]
    train_path = PROCESSED / "uci_spectf_train.csv"
    test_path = PROCESSED / "uci_spectf_test.csv"
    all_path = PROCESSED / "uci_spectf_all.csv"
    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)
    combined = pd.concat(
        [train.assign(source_split="official_train"), test.assign(source_split="official_test")],
        ignore_index=True,
    )
    combined.to_csv(all_path, index=False)
    signature_sets = [
        set(canonical_rows(train.drop(columns="OVERALL_DIAGNOSIS"))),
        set(canonical_rows(test.drop(columns="OVERALL_DIAGNOSIS"))),
    ]
    source = {
        "name": "UCI SPECTF Heart",
        "dataset_id": 96,
        "doi": "10.24432/C5N015",
        "url": "https://archive.ics.uci.edu/dataset/96/spectf%2Bheart",
        "license": "CC BY 4.0; attribution required",
        "archive_path": "data/external/uci_spectf_heart_96/spectf_heart.zip",
        "archive_sha256": sha256_file(SPECTF_ARCHIVE),
        "member_sha256": member_hashes,
        "source_files": ["SPECTF.train", "SPECTF.test", "SPECTF.names"],
        "target_definition": "UCI OVERALL_DIAGNOSIS: 0/1 normal/abnormal SPECT classification.",
        "official_split": {
            "train_rows": int(len(train)),
            "train_class_counts": {
                str(k): int(v)
                for k, v in train["OVERALL_DIAGNOSIS"].value_counts().sort_index().items()
            },
            "test_rows": int(len(test)),
            "test_class_counts": {
                str(k): int(v)
                for k, v in test["OVERALL_DIAGNOSIS"].value_counts().sort_index().items()
            },
            "train_test_exact_feature_overlap": len(signature_sets[0] & signature_sets[1]),
        },
        "prepared_paths": {
            "train": train_path.relative_to(ROOT).as_posix(),
            "test": test_path.relative_to(ROOT).as_posix(),
            "all": all_path.relative_to(ROOT).as_posix(),
        },
        "prepared_sha256": {
            "train": sha256_file(train_path),
            "test": sha256_file(test_path),
            "all": sha256_file(all_path),
        },
        "compatibility_note": (
            "A separate SPECT imaging classification task; not the angiographic CAD endpoint "
            "and not cross-compatible with the clinical UCI cohorts."
        ),
        "source_document_excerpt": names_text[:500],
    }
    frame = combined.drop(columns="source_split")
    summary = summarize_dataset(
        "uci_spectf_heart",
        frame,
        "OVERALL_DIAGNOSIS",
        source,
        interpretation="Separate SPECT normal/abnormal task; official 80/187 split is retained.",
    )
    summary["official_split"] = source["official_split"]
    return summary


def uci_cohort_overlap_audit(dataset_summaries: dict[str, Any]) -> dict[str, Any]:
    frames = {
        dataset_id: pd.read_csv(PROCESSED / f"{dataset_id}.csv") for dataset_id in UCI_COHORTS
    }
    features = [column for column in frames["uci_cleveland"] if column != "cad_positive"]
    signatures: dict[str, tuple[Counter[str], Counter[str]]] = {}
    for dataset_id, frame in frames.items():
        feature_keys = Counter(canonical_rows(frame[features]))
        labeled = frame[features].copy()
        labeled["cad_positive"] = frame["cad_positive"].astype(int)
        labeled_keys = Counter(canonical_rows(labeled))
        signatures[dataset_id] = (feature_keys, labeled_keys)
    pairwise: dict[str, Any] = {}
    ids = list(frames)
    for left_index, left in enumerate(ids):
        for right in ids[left_index + 1 :]:
            feature_overlap = sum((signatures[left][0] & signatures[right][0]).values())
            labeled_overlap = sum((signatures[left][1] & signatures[right][1]).values())
            pairwise[f"{left}__{right}"] = {
                "exact_feature_row_overlap_count": int(feature_overlap),
                "exact_feature_and_label_row_overlap_count": int(labeled_overlap),
                "patient_level_independence_verified": False,
                "interpretation": (
                    "Exact row matching is a screening check only; UCI files have no persistent "
                    "participant linkage key."
                ),
            }
    return {
        "feature_schema": features,
        "pairwise": pairwise,
        "known_heart5_lineage_overlap": {dataset_id: True for dataset_id in dataset_summaries},
        "interpretation": (
            "All four component cohorts were represented in the previously used Heart5 composite; "
            "no cohort is a new independent external validation set."
        ),
    }


def prepare_all() -> dict[str, Any]:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    dataset_manifest: dict[str, Any] = {"datasets": {}}
    dataset_manifest["datasets"].update(prepare_uci_cohorts())
    hf = prepare_heart_failure(PROCESSED)
    mi = prepare_mi(PROCESSED)
    hf_path = ROOT / hf["prepared_path"]
    mi_path = ROOT / mi["prepared_path"]
    for dataset_id, path, summary, target, note in (
        (
            "uci_heart_failure_519",
            hf_path,
            hf,
            "death_event",
            "Separate death-event task; varying follow-up horizons; not CAD validation.",
        ),
        (
            "uci_mi_complications_579",
            mi_path,
            mi,
            "any_lethal_outcome",
            "Separate MI lethal-outcome task; admission variables only; not CAD validation.",
        ),
    ):
        frame = pd.read_csv(path)
        source = {
            "name": "UCI Heart Failure Clinical Records"
            if dataset_id == "uci_heart_failure_519"
            else "UCI Myocardial Infarction Complications",
            "dataset_id": 519 if dataset_id == "uci_heart_failure_519" else 579,
            "doi": "10.24432/C5Z89R"
            if dataset_id == "uci_heart_failure_519"
            else "10.24432/C53P5M",
            "url": (
                "https://archive.ics.uci.edu/dataset/519/heart%2Bfailure%2Bclinical%2Brecords"
                if dataset_id == "uci_heart_failure_519"
                else "https://archive.ics.uci.edu/dataset/579/myocardial%2Binfarction%2Bcomplications"
            ),
            "license": "CC BY 4.0; attribution required",
            "source_path": summary["source_path"],
            "source_sha256": summary["source_sha256"],
            "source_archive_sha256": sha256_file(
                ROOT
                / "data"
                / "external"
                / (
                    "uci_heart_failure_519"
                    if dataset_id == "uci_heart_failure_519"
                    else "uci_mi_complications_579"
                )
                / "source.zip"
            ),
            "prepared_path": path.relative_to(ROOT).as_posix(),
            "prepared_sha256": sha256_file(path),
            "target_definition": note,
            "preprocessing_note": summary.get("interpretation", ""),
            "lineage_note": "Patient-level overlap with other datasets was not established.",
        }
        dataset_manifest["datasets"][dataset_id] = summarize_dataset(
            dataset_id,
            frame,
            target,
            source,
            interpretation=note,
        )
    dataset_manifest["datasets"]["uci_spectf_heart"] = prepare_spectf()
    dataset_manifest["uci_cohort_overlap_audit"] = uci_cohort_overlap_audit(
        {key: value for key, value in dataset_manifest["datasets"].items() if key in UCI_COHORTS}
    )
    return {
        "manifest_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "preparation_script": "experiments/prepare_multi_dataset_evaluation.py",
        "data_handling": (
            "Raw source files and prepared rows remain in gitignored local data folders; "
            "only aggregate source manifests and metrics are for public release."
        ),
        **dataset_manifest,
    }


def main() -> None:
    manifest = prepare_all()
    out = ROOT / "results" / "multi_dataset_evaluation_20261108" / "datasets"
    out.mkdir(parents=True, exist_ok=True)
    destination = out / "dataset_manifest.json"
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote dataset manifest: {destination}")
    for name, data in manifest["datasets"].items():
        print(
            f"{name}: n={data['rows']}, predictors={data['predictor_count']}, "
            f"classes={data['class_counts']}, missing={data['missing_predictor_cells']}"
        )


if __name__ == "__main__":
    main()
