"""Tests for the fixed-default OSEC ablation configuration."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SCRIPT = ROOT / "experiments" / "run_osec_optimization_ablation.py"
SPEC = importlib.util.spec_from_file_location("cardiodiag_osec_optimization_ablation", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
ablation = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ablation
SPEC.loader.exec_module(ablation)


def test_fixed_osec_keeps_stacking_architecture_and_default_c() -> None:
    rng = np.random.default_rng(89)
    X = pd.DataFrame(rng.normal(size=(40, 4)), columns=["a", "b", "c", "d"])

    estimator = ablation.make_fixed_osec(X, seed=89)

    assert estimator.get_params()["model__final_estimator__C"] == 1.0
    assert estimator.get_params()["model__cv"] == 5
