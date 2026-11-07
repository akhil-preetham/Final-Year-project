"""AURA-ML: adaptive unified representation and reliability-aware learning."""

from .calibration import IsotonicCalibrator, SigmoidCalibrator
from .feature_selection import AdaptiveStableSelector
from .fusion import reliability_gated_fusion
from .intelligence import DatasetProfile, profile_dataset
from .pipeline import AURAClassifier, AURAConfig
from .preprocessing import AdaptiveTabularTransformer
from .reliability import reliability_objective
from .representation import MultiViewRepresentation

__all__ = [
    "AdaptiveStableSelector",
    "AdaptiveTabularTransformer",
    "AURAClassifier",
    "AURAConfig",
    "DatasetProfile",
    "IsotonicCalibrator",
    "MultiViewRepresentation",
    "SigmoidCalibrator",
    "profile_dataset",
    "reliability_gated_fusion",
    "reliability_objective",
]
