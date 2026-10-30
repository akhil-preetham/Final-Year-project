"""Leakage-controlled CARDIODIAG research implementation."""

from .data import DatasetSummary, drop_identifier_columns, load_dataset, summarize_dataset
from .evaluation import evaluate_predictions
from .feature_selection import StableXAIHDRC, one_shot_selection_mask
from .historical import run_historical_native
from .nested_validation import run_nested_validation
from .preprocessing import TrainingOnlyCleaner, make_tabular_preprocessor
from .reliability import (
    bootstrap_mean_ci,
    calibration_summary,
    nogueira_stability,
    selective_risk_curve,
    selector_stability_summary,
    uncertainty_evidence,
)
from .uncertainty import SplitConformalClassifier

__all__ = [
    "DatasetSummary",
    "StableXAIHDRC",
    "one_shot_selection_mask",
    "TrainingOnlyCleaner",
    "SplitConformalClassifier",
    "drop_identifier_columns",
    "calibration_summary",
    "uncertainty_evidence",
    "nogueira_stability",
    "bootstrap_mean_ci",
    "selective_risk_curve",
    "selector_stability_summary",
    "run_historical_native",
    "run_nested_validation",
    "evaluate_predictions",
    "load_dataset",
    "make_tabular_preprocessor",
    "summarize_dataset",
]
