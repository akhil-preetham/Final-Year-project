from cardiodiag.models import build_individual_model, build_osec, build_ovec


def test_core_ensembles_do_not_spawn_nested_joblib_workers() -> None:
    assert build_ovec().n_jobs == 1
    stacking = build_osec()
    assert stacking.n_jobs == 1
    assert stacking.cv == 5


def test_individual_baselines_have_expected_estimators() -> None:
    assert build_individual_model("logistic").class_weight == "balanced"
    assert build_individual_model("knn").n_neighbors == 7
    assert build_individual_model("svm").probability is True
    assert build_individual_model("random_forest").n_estimators == 200
