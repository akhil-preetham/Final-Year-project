import audit_angiocad_compatibility as audit
import pandas as pd
import pytest


def test_matching_is_keyed_one_to_one_and_records_unmatched_public_ids():
    features = pd.DataFrame(
        {
            "ID": [1.0, 3.0],
            "Age": [50.0, None],
            "Sex": ["female", "male"],
            "FBS": [100.0, None],
        }
    )
    labels = pd.DataFrame(
        {
            "ID": [3.0, 1.0, 4.0],
            "artery": ["NL", "51-75", "26-50"],
        }
    )

    result = audit.audit_id_frames(features, labels, ["artery"])

    assert "one_to_one" in result["matching_method"]
    assert result["matched_rows"] == 2
    assert result["matched_ids_are_unique"] is True
    assert result["label_ids_without_features"] == [4]
    assert result["feature_ids_without_label"] == []
    assert result["positional_row_id_matches_if_naively_zipped"] == 0
    assert result["age_missing_in_matched_rows"] == 1
    assert result["fbs_missing_in_matched_rows"] == 1


def test_duplicate_patient_ids_are_rejected():
    features = pd.DataFrame(
        {"ID": [1, 1], "Age": [40, 41], "Sex": ["male", "female"], "FBS": [90, 110]}
    )
    labels = pd.DataFrame({"ID": [1], "artery": ["NL"]})

    with pytest.raises(ValueError, match="Duplicate nonblank IDs"):
        audit.audit_id_frames(features, labels, ["artery"])


def test_nonintegral_ids_are_rejected():
    with pytest.raises(ValueError, match="non-integral"):
        audit._integer_ids(pd.Series([1.5]), "ID")
