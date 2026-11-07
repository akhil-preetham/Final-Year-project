import hashlib
import json
from pathlib import Path

from cardiodiag.data import (
    drop_feature_columns,
    drop_identifier_columns,
    load_dataset,
    summarize_dataset,
)
from cardiodiag.preprocessing import TrainingOnlyCleaner

ROOT = Path(__file__).resolve().parents[1]


def test_local_dataset_summary_matches_checked_in_data() -> None:
    summary = summarize_dataset(ROOT / "heart5.csv", "HeartDisease")

    assert summary.rows == 918
    assert summary.duplicate_rows == 0
    assert summary.target_counts == {"0": 410, "1": 508}


def test_load_dataset_separates_binary_target() -> None:
    features, target = load_dataset(ROOT / "MendeleyCardiovascular_Disease_Dataset.csv", "target")

    assert "target" not in features.columns
    assert len(features) == len(target) == 1000
    assert set(target.unique()) == {0, 1}


def test_identifier_columns_are_removed_before_modeling() -> None:
    features, _ = load_dataset(ROOT / "MendeleyCardiovascular_Disease_Dataset.csv", "target")
    cleaned, dropped = drop_identifier_columns(features)

    assert dropped == ["patientid"]
    assert "patientid" not in cleaned.columns


def test_declared_feature_exclusion_preserves_schema_and_rejects_unknown_columns() -> None:
    features, _ = load_dataset(ROOT / "MendeleyCardiovascular_Disease_Dataset.csv", "target")
    cleaned = drop_feature_columns(features, ["noofmajorvessels"])

    assert "noofmajorvessels" not in cleaned.columns
    assert "noofmajorvessels" not in cleaned.attrs["categorical_columns"]
    assert cleaned.attrs["numeric_columns"] == features.attrs["numeric_columns"]
    try:
        drop_feature_columns(features, ["not_a_feature"])
    except ValueError as error:
        assert "missing feature columns" in str(error)
    else:
        raise AssertionError("Expected an unknown-feature error")


def test_integer_coded_mendeley_categories_have_explicit_schema() -> None:
    features, _ = load_dataset(ROOT / "MendeleyCardiovascular_Disease_Dataset.csv", "target")

    assert "gender" in features.attrs["categorical_columns"]
    assert "chestpain" in features.attrs["categorical_columns"]
    assert "gender" not in features.attrs["numeric_columns"]
    assert "age" in features.attrs["numeric_columns"]


def test_kaggle_cardiovascular_dataset_schema_and_target_boundary() -> None:
    dataset = ROOT / "data" / "kaggle_cardiovascular_70k" / "cardio_train.csv"
    features, target = load_dataset(dataset, "cardio")

    assert len(features) == len(target) == 70_000
    assert "cardio" not in features.columns
    assert "id" in features.columns
    assert set(target.unique()) == {0, 1}
    assert set(features.attrs["categorical_columns"]) == {
        "gender",
        "cholesterol",
        "gluc",
        "smoke",
        "alco",
        "active",
    }
    assert set(features.attrs["numeric_columns"]) == {
        "age",
        "height",
        "weight",
        "ap_hi",
        "ap_lo",
    }


def test_kaggle_identifier_is_removed_before_modeling() -> None:
    dataset = ROOT / "data" / "kaggle_cardiovascular_70k" / "cardio_train.csv"
    features, _ = load_dataset(dataset, "cardio")
    cleaned, dropped = drop_identifier_columns(features)

    assert dropped == ["id"]
    assert "id" not in cleaned.columns
    assert cleaned.attrs["categorical_columns"] == features.attrs["categorical_columns"]


def test_kaggle_manifest_provenance_and_training_schema() -> None:
    dataset = ROOT / "data" / "kaggle_cardiovascular_70k" / "cardio_train.csv"
    manifest = json.loads((ROOT / "data" / "manifests" / "local_datasets.json").read_text())[-1]

    assert manifest["path"] == "data/kaggle_cardiovascular_70k/cardio_train.csv"
    assert manifest["sha256"] == hashlib.sha256(dataset.read_bytes()).hexdigest()
    assert manifest["target"] == "cardio"
    assert manifest["license"] == (
        "Kaggle metadata reports Unknown; do not redistribute until upstream licensing is verified."
    )

    features, _ = load_dataset(dataset, "cardio")
    cleaned, _ = drop_identifier_columns(features)
    cleaner = TrainingOnlyCleaner(
        lower_quantile=0.0,
        upper_quantile=1.0,
        categorical_columns=cleaned.attrs["categorical_columns"],
    ).fit(cleaned.iloc[:1000])

    assert set(cleaner.categorical_columns_) == set(features.attrs["categorical_columns"])
    assert "id" not in cleaner.feature_names_in_
