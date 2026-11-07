from experiments.audit_mendeley_2021_source import audit_local


def test_mendeley_source_csv_and_official_codebook_hashes_match() -> None:
    report = audit_local()

    assert report["rows"] == 1000
    assert report["csv_sha256"] == (
        "9376367dde41e79e432d6402ea5d9e44223fc318ff54ed09966d721923947d1e"
    )
    assert report["codebook_sha256"] == (
        "ba341780562d4f81b5bd4298d01b067d6af00dbf0192869221c828d6a0b0467a"
    )
    assert report["target_counts"] == {"0": 420, "1": 580}


def test_mendeley_binary_label_has_no_documented_angiographic_reference_standard() -> None:
    report = audit_local()

    assert "absence" in report["target_codebook"]
    assert "presence" in report["target_codebook"]
    assert "do not specify" in report["reference_standard"]
    assert "Do not pool" in report["eligibility_note"]
