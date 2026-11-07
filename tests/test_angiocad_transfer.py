import numpy as np
import pandas as pd
from run_angiocad_transfer import (
    ARTERY_COLUMNS,
    FEATURES_FILE,
    LABELS_FILE,
    load_angiocad,
)


def test_angiocad_adapter_matches_frozen_cohort_schema() -> None:
    features, target, record_ids, audit = load_angiocad()

    assert list(features.columns) == ["age", "sex", "fbs"]
    assert features.shape == (377, 3)
    assert len(target) == len(record_ids) == 377
    assert len(set(record_ids)) == 377
    assert np.all(np.diff(record_ids) >= 0)
    assert dict(zip(*np.unique(target, return_counts=True), strict=True)) == {
        0: 79,
        1: 298,
    }
    assert features["age"].isna().sum() == 6
    assert features["fbs"].isna().sum() == 11
    assert set(features["sex"].dropna()) == {"female", "male"}
    assert audit["matched_unique_ids"] == 377
    assert audit["label_ids_without_features"] == 36
    assert audit["target_feature_file_ids_without_labels"] == 0


def test_angiocad_target_is_derived_from_matched_artery_labels() -> None:
    _, target, record_ids, _ = load_angiocad()
    labels = pd.read_excel(LABELS_FILE, engine="openpyxl")
    labels = labels.loc[labels["ID"].notna()].set_index("ID")
    matched_labels = labels.loc[record_ids, ARTERY_COLUMNS].astype("string")
    matched_labels = matched_labels.apply(lambda column: column.str.strip())
    positive_bins = {"51-75", "76-90", "91-99", "100"}
    expected = matched_labels.isin(positive_bins).any(axis=1).to_numpy(dtype=np.int8)

    np.testing.assert_array_equal(target, expected)

    feature_ids = pd.read_excel(FEATURES_FILE, engine="openpyxl")["ID"]
    assert feature_ids.notna().sum() == 377
