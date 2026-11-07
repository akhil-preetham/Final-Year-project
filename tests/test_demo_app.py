import json
from pathlib import Path

import pytest

from cardiodiag.demo_app import (
    build_input_frame,
    load_verified_predictor,
    run_research_demo_prediction,
)
from cardiodiag.domain_guard import DomainAwareSelectivePredictor

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "results" / "transfer_20261105_duke_acath_final" / "model_bundle.joblib"


@pytest.fixture(scope="module")
def predictor() -> DomainAwareSelectivePredictor:
    return DomainAwareSelectivePredictor.load(BUNDLE)


def test_demo_input_rejects_missing_or_unexpected_features(predictor) -> None:
    with pytest.raises(ValueError, match="schema mismatch"):
        build_input_frame(predictor, {"age": 35, "sex": "female"})
    with pytest.raises(ValueError, match="schema mismatch"):
        build_input_frame(predictor, {"age": 35, "sex": "female", "chol": 180, "site": "cleveland"})


@pytest.mark.parametrize("age", [0, 121, float("nan"), float("inf"), "bad"])
def test_demo_input_rejects_invalid_age(age, predictor) -> None:
    with pytest.raises(ValueError):
        build_input_frame(predictor, {"age": age, "sex": "female", "chol": 180})


@pytest.mark.parametrize("chol", [0, 1001, float("nan"), float("inf"), "bad"])
def test_demo_input_rejects_invalid_cholesterol(chol, predictor) -> None:
    with pytest.raises(ValueError):
        build_input_frame(predictor, {"age": 35, "sex": "female", "chol": chol})


def test_demo_input_preserves_declared_model_feature_order(predictor) -> None:
    frame = build_input_frame(predictor, {"chol": 180, "sex": "female", "age": 35})
    assert tuple(frame.columns) == tuple(predictor.features)
    assert frame.loc[0, "age"] == 35


def test_demo_fails_closed_for_unknown_domain(predictor) -> None:
    result = run_research_demo_prediction(
        predictor, {"age": 35, "sex": "female", "chol": 180}, None
    )
    assert result["action"] == "abstain"
    assert result["reason"] == "domain_not_in_source_registry"
    assert result["probability"] is None


def test_demo_loads_only_a_hash_verified_bundle() -> None:
    loaded = load_verified_predictor(BUNDLE)
    assert tuple(loaded.features) == ("age", "sex", "chol")


def test_demo_rejects_bundle_with_mismatched_integrity_manifest(tmp_path: Path) -> None:
    bundle = tmp_path / "model_bundle.joblib"
    bundle.write_bytes(b"untrusted changed artifact")
    manifest = tmp_path / "domain_guard_demo_manifest.json"
    manifest.write_text(json.dumps({"model_bundle_sha256": "0" * 64}), encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256"):
        load_verified_predictor(bundle)


def test_demo_runs_frozen_policy_for_registered_domain(predictor) -> None:
    result = run_research_demo_prediction(
        predictor,
        {"age": 35, "sex": "female", "chol": 180},
        "cleveland",
    )
    assert result["action"] in {"classify", "abstain"}
    if result["action"] == "abstain":
        assert result["probability"] is None
        assert result["reason"]
    else:
        assert 0 <= result["probability"] <= 1
        assert len(result["prediction_set"]) == 1
