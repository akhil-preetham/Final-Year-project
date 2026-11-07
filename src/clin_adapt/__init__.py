"""CLIN-ADAPT: controlled adaptive learning for structured clinical data.

This package is intentionally separate from the historical CARDIODIAG/AURA
implementation.  The first release provides a model registry, safe dataset
profiling, failure-isolated parallel execution, and a provisional CASL
validation coordinator.  It does not claim a new classifier or established
algorithmic novelty.
"""

from .adaptive_learning import CASLConfig, CASLCoordinator, CoordinationDecision
from .evaluation import evaluate_binary_predictions
from .parallel_engine import ExecutionRecord, ParallelExecutionEngine
from .profiling import ClinicalDatasetProfile, profile_clinical_dataset
from .registry import ModelSpec, discover_model_registry
from .resources import detect_runtime_resources

__all__ = [
    "CASLConfig",
    "CASLCoordinator",
    "ClinicalDatasetProfile",
    "CoordinationDecision",
    "ExecutionRecord",
    "ModelSpec",
    "ParallelExecutionEngine",
    "discover_model_registry",
    "detect_runtime_resources",
    "evaluate_binary_predictions",
    "profile_clinical_dataset",
]
