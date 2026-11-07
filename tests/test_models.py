from cardiodiag.models import build_osec, build_ovec


def test_core_ensembles_do_not_spawn_nested_joblib_workers() -> None:
    assert build_ovec().n_jobs == 1
    stacking = build_osec()
    assert stacking.n_jobs == 1
    assert stacking.cv == 5
