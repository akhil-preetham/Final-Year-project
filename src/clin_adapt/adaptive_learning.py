"""Provisional CASL validation coordinator.

CASL here means *Clinical Adaptive Strategy Learning*.  This implementation is
deliberately a transparent policy for testing, not a novelty claim: it combines
validation utility, failure rejection, prediction diversity and a fixed
improvement margin.  A future paper may claim novelty only if a cross-dataset
study demonstrates a capability beyond established dynamic selection and
mixture-of-experts methods.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .evaluation import evaluate_binary_predictions, utility


@dataclass(frozen=True)
class CASLConfig:
    minimum_fusion_improvement: float = 0.002
    calibration_weight: float = 0.25
    max_ensemble_size: int = 3
    minimum_auc: float = 0.5
    maximum_brier: float = 0.35
    diversity_weight: float = 0.05


@dataclass(frozen=True)
class CoordinationDecision:
    output_type: str
    selected_names: tuple[str, ...]
    weights: tuple[float, ...]
    candidate_utilities: dict[str, float]
    candidate_metrics: dict[str, dict[str, float | int]]
    rejected_candidates: dict[str, str]
    fusion_metrics: dict[str, float | int] | None
    best_single_name: str
    rationale: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CASLCoordinator:
    """Coordinate candidates using validation-only evidence."""

    def __init__(self, config: CASLConfig | None = None) -> None:
        self.config = config or CASLConfig()

    def decide(
        self,
        y_true: np.ndarray,
        predictions: dict[str, np.ndarray],
    ) -> CoordinationDecision:
        """Select one candidate or a justified validation-only ensemble."""

        metrics: dict[str, dict[str, float | int]] = {}
        utilities: dict[str, float] = {}
        rejected: dict[str, str] = {}
        usable: list[str] = []
        for name, values in predictions.items():
            try:
                candidate_metrics = evaluate_binary_predictions(y_true, values)
            except Exception as exc:
                rejected[name] = f"metric_failure:{type(exc).__name__}:{exc}"
                continue
            metrics[name] = candidate_metrics
            if candidate_metrics["roc_auc"] < self.config.minimum_auc:
                rejected[name] = "roc_auc_below_minimum"
            elif candidate_metrics["brier"] > self.config.maximum_brier:
                rejected[name] = "brier_above_maximum"
            else:
                usable.append(name)
                utilities[name] = utility(candidate_metrics, self.config.calibration_weight)
        if not usable:
            raise RuntimeError("CASL found no usable candidate")
        usable.sort(key=lambda name: (-utilities[name], name))
        best_name = usable[0]
        top = usable[: self.config.max_ensemble_size]
        weights = _softmax(np.asarray([utilities[name] for name in top]), temperature=0.05)
        matrix = np.column_stack([predictions[name] for name in top])
        fused = matrix @ weights
        fused_metrics = evaluate_binary_predictions(y_true, fused)
        fused_utility = utility(fused_metrics, self.config.calibration_weight)
        best_utility = utilities[best_name]
        diverse = _prediction_diversity(matrix)
        rationale = [f"best_single={best_name}", f"candidate_count={len(usable)}"]
        if len(top) > 1:
            rationale.append(f"top_candidate_diversity={diverse:.6f}")
        if (
            len(top) > 1
            and fused_utility >= best_utility + self.config.minimum_fusion_improvement
            and diverse > 0.0
        ):
            rationale.append("fusion passed fixed inner-validation improvement and diversity gates")
            return CoordinationDecision(
                output_type="validation_justified_fusion",
                selected_names=tuple(top),
                weights=tuple(float(weight) for weight in weights),
                candidate_utilities=utilities,
                candidate_metrics=metrics,
                rejected_candidates=rejected,
                fusion_metrics=fused_metrics,
                best_single_name=best_name,
                rationale=tuple(rationale),
            )
        rationale.append("single candidate retained; fusion gate not met")
        return CoordinationDecision(
            output_type="single_candidate",
            selected_names=(best_name,),
            weights=(1.0,),
            candidate_utilities=utilities,
            candidate_metrics=metrics,
            rejected_candidates=rejected,
            fusion_metrics=fused_metrics,
            best_single_name=best_name,
            rationale=tuple(rationale),
        )

    def diagnose_failures(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert execution failures into controlled, non-automatic alternatives."""

        diagnoses: list[dict[str, Any]] = []
        for record in records:
            if record.get("status") == "completed":
                continue
            error = str(record.get("error_message") or record.get("error_type") or "unknown")
            if "converg" in error.lower() or "iteration" in error.lower():
                recommendation = "increase_iterations_or_regularize"
            elif "memory" in error.lower() or "allocat" in error.lower():
                recommendation = "reduce_parallelism_or_model_size"
            elif "categor" in error.lower() or "string" in error.lower():
                recommendation = "verify_training_only_encoding"
            else:
                recommendation = "inspect_candidate_specific_failure"
            diagnoses.append(
                {"candidate": record.get("name"), "error": error, "alternative": recommendation}
            )
        return diagnoses


def _softmax(values: np.ndarray, temperature: float) -> np.ndarray:
    scaled = (values - values.max()) / max(temperature, 1e-8)
    weights = np.exp(scaled)
    return weights / weights.sum()


def _prediction_diversity(matrix: np.ndarray) -> float:
    if matrix.shape[1] < 2:
        return 0.0
    centered = matrix - matrix.mean(axis=0, keepdims=True)
    scales = np.sqrt(np.sum(centered * centered, axis=0))
    if np.any(scales == 0):
        return 0.0
    correlation = (centered.T @ centered) / np.outer(scales, scales)
    upper = correlation[np.triu_indices(matrix.shape[1], k=1)]
    if upper.size == 0:
        return 0.0
    return float(np.mean(1.0 - np.abs(upper)))
