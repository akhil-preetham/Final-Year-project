"""End-to-end AURA-ML estimator.

The estimator performs all data-dependent choices on the data supplied to
``fit``.  In an outer experiment that data is the outer-training fold, so the
outer test fold is never consulted by representation, selection, fusion, or
calibration decisions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, clone
from sklearn.model_selection import StratifiedKFold

from cardiodiag.evaluation import evaluate_predictions

from .calibration import IsotonicCalibrator, SigmoidCalibrator
from .feature_selection import AdaptiveStableSelector
from .fusion import reliability_gated_fusion
from .intelligence import profile_dataset
from .model_selection import available_models
from .reliability import reliability_objective
from .representation import MultiViewRepresentation


@dataclass(frozen=True)
class AURAConfig:
    inner_splits: int = 2
    seed: int = 42
    use_intelligence: bool = True
    use_multiview: bool = True
    use_feature_selection: bool = True
    use_fusion: bool = True
    use_reliability: bool = True
    use_calibration: bool = True
    minimum_fusion_improvement: float = 0.002
    disagreement_penalty: float = 2.0
    max_features: int = 32
    calibration_methods: tuple[str, ...] = ("sigmoid",)
    calibration_min_brier_improvement: float = 1e-4
    threshold_mode: str = "default"


class AURAClassifier(BaseEstimator):
    """Adaptive representation, model, fusion, and calibration classifier."""

    def __init__(self, config: AURAConfig | None = None) -> None:
        self.config = config or AURAConfig()

    def fit(self, X: pd.DataFrame, y: pd.Series | np.ndarray) -> AURAClassifier:
        if not isinstance(X, pd.DataFrame):
            raise TypeError("AURAClassifier expects a pandas DataFrame")
        y_array = np.asarray(y, dtype=int)
        if len(X) != len(y_array) or np.unique(y_array).size != 2:
            raise ValueError("AURAClassifier requires a binary target aligned with X")
        if self.config.inner_splits < 2:
            raise ValueError("inner_splits must be at least two")
        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        self.profile_ = profile_dataset(X, y_array).to_dict()
        self.candidate_specs_ = self._candidate_specs()
        models = available_models(self.config.seed)
        self.inner_results_: dict[str, Any] = {}
        oof_predictions: dict[str, np.ndarray] = {}
        inner = StratifiedKFold(
            n_splits=self.config.inner_splits,
            shuffle=True,
            random_state=self.config.seed,
        )
        for candidate_name, model_name, view, use_selector in self.candidate_specs_:
            if model_name not in models:
                continue
            predictions = np.full(len(X), np.nan, dtype=float)
            fold_auc: list[float] = []
            fold_records: list[dict[str, Any]] = []
            started = perf_counter()
            for fold, (train, validation) in enumerate(inner.split(X, y_array)):
                representation = self._new_representation(view)
                X_train = X.iloc[train]
                X_validation = X.iloc[validation]
                representation.fit(X_train, y_array[train])
                transformed_train = representation.transform(X_train)
                transformed_validation = representation.transform(X_validation)
                selector = self._new_selector() if use_selector else None
                if selector is not None:
                    transformed_train = selector.fit_transform(transformed_train, y_array[train])
                    transformed_validation = selector.transform(transformed_validation)
                model = clone(models[model_name])
                model.fit(transformed_train, y_array[train])
                probabilities = model.predict_proba(transformed_validation)[:, 1]
                predictions[validation] = probabilities
                metrics = evaluate_predictions(y_array[validation], probabilities)
                fold_auc.append(float(metrics["roc_auc"]))
                fold_records.append(
                    {
                        "fold": fold,
                        "train_n": int(len(train)),
                        "validation_n": int(len(validation)),
                        "metrics": metrics,
                        "selected_features": int(
                            len(selector.selected_indices_)
                            if selector is not None
                            else transformed_train.shape[1]
                        ),
                        "preprocessing_policy": representation.profile_,
                    }
                )
            if np.isnan(predictions).any():
                raise RuntimeError(
                    f"Candidate {candidate_name} did not produce complete OOF predictions"
                )
            objective = reliability_objective(
                y_array,
                predictions,
                fold_auc,
                perf_counter() - started,
                self.profile_["class_prevalence"],
            )
            oof_predictions[candidate_name] = predictions
            self.inner_results_[candidate_name] = {
                "candidate": {
                    "model": model_name,
                    "view": view,
                    "feature_selection": use_selector,
                },
                "folds": fold_records,
                "metrics": evaluate_predictions(y_array, predictions),
                "objective": objective,
            }

        if not oof_predictions:
            raise RuntimeError("No AURA-ML candidate could be fitted")
        names = list(oof_predictions)
        utilities = np.asarray(
            [self.inner_results_[name]["objective"]["utility"] for name in names]
        )
        best_index = int(np.argmax(utilities))
        best_name = names[best_index]
        self.fusion_weights_ = _softmax(utilities, temperature=0.05)
        prediction_matrix = np.column_stack([oof_predictions[name] for name in names])
        if self.config.use_reliability:
            fused_oof = reliability_gated_fusion(
                prediction_matrix,
                self.fusion_weights_,
                self.config.disagreement_penalty,
            )
        else:
            fused_oof = prediction_matrix @ self.fusion_weights_
        fused_fold_auc = [
            float(evaluate_predictions(y_array[validation], fused_oof[validation])["roc_auc"])
            for _, validation in inner.split(X, y_array)
        ]
        fused_objective = reliability_objective(
            y_array,
            fused_oof,
            fused_fold_auc,
            prevalence=self.profile_["class_prevalence"],
        )
        best_objective = self.inner_results_[best_name]["objective"]
        self.use_fusion_ = bool(
            self.config.use_fusion
            and len(names) > 1
            and fused_objective["utility"]
            >= best_objective["utility"] + self.config.minimum_fusion_improvement
        )
        self.selected_names_ = names if self.use_fusion_ else [best_name]
        self.raw_oof_predictions_ = fused_oof if self.use_fusion_ else oof_predictions[best_name]
        self.selected_inner_objective_ = fused_objective if self.use_fusion_ else best_objective
        self.fusion_evidence_ = {
            "candidate_names": names,
            "candidate_utilities": {
                name: float(utilities[index]) for index, name in enumerate(names)
            },
            "weights": self.fusion_weights_.tolist(),
            "fusion_objective": fused_objective,
            "best_single_candidate": best_name,
            "selected_output": (
                "reliability_gated_fusion" if self.use_fusion_ else "single_candidate"
            ),
        }
        self.calibration_method_ = "none"
        self.calibrator_ = None
        raw_oof = self.raw_oof_predictions_
        calibration_predictions = {"none": raw_oof}
        if self.config.use_calibration:
            calibration_predictions.update(
                _cross_fitted_calibrators(
                    raw_oof,
                    y_array,
                    self.config.seed,
                    self.config.calibration_methods,
                )
            )
        calibration_evidence = {
            method: evaluate_predictions(y_array, probabilities)
            for method, probabilities in calibration_predictions.items()
        }
        best_calibration = min(
            calibration_predictions,
            key=lambda method: (
                calibration_evidence[method]["brier"],
                calibration_evidence[method]["ece_uniform"],
            ),
        )
        raw_brier = calibration_evidence["none"]["brier"]
        if (
            best_calibration != "none"
            and calibration_evidence[best_calibration]["brier"]
            + self.config.calibration_min_brier_improvement
            < raw_brier
        ):
            self.calibration_method_ = best_calibration
            self.calibrator_ = _build_calibrator(best_calibration).fit(raw_oof, y_array)
        selected_oof = calibration_predictions.get(self.calibration_method_, raw_oof)
        self.calibration_evidence_ = calibration_evidence
        self.threshold_evidence_ = _threshold_evidence(y_array, selected_oof)
        self.decision_threshold_ = _select_threshold(
            y_array, selected_oof, self.config.threshold_mode
        )
        self.calibrated_oof_predictions_ = selected_oof
        self._fit_selected_models(X, y_array, models)
        self.fit_summary_ = {
            "config": asdict(self.config),
            "profile": self.profile_,
            "candidate_count": len(names),
            "selected_names": self.selected_names_,
            "fusion": self.fusion_evidence_,
            "calibration_method": self.calibration_method_,
            "calibration_evidence": self.calibration_evidence_,
            "decision_threshold": self.decision_threshold_,
            "threshold_evidence": self.threshold_evidence_,
            "inner_results": self.inner_results_,
        }
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not hasattr(self, "fitted_candidates_"):
            raise RuntimeError("AURAClassifier must be fitted before prediction")
        raw = self._predict_raw(X)
        if self.use_fusion_:
            probabilities = reliability_gated_fusion(
                raw, self.fusion_weights_, self.config.disagreement_penalty
            ) if self.config.use_reliability else raw @ self.fusion_weights_
        else:
            probabilities = raw[:, 0]
        if self.calibrator_ is not None:
            probabilities = self.calibrator_.predict(probabilities)
        probabilities = np.clip(probabilities, 1e-6, 1 - 1e-6)
        return np.column_stack([1.0 - probabilities, probabilities])

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return (self.predict_proba(X)[:, 1] >= self.decision_threshold_).astype(int)

    def _candidate_specs(self) -> list[tuple[str, str, str, bool]]:
        view = "multi" if self.config.use_multiview else "original"
        selector = self.config.use_feature_selection
        return [
            ("logistic_original", "logistic", "original", False),
            ("logistic_adaptive", "logistic", view, selector),
            ("hist_adaptive", "hist_gradient_boosting", view, False),
            ("catboost_adaptive", "catboost", view, False),
            ("xgboost_adaptive", "xgboost", view, False),
        ]

    def _new_representation(self, view: str) -> MultiViewRepresentation:
        return MultiViewRepresentation(view=view, adaptive=self.config.use_intelligence)

    def _new_selector(self) -> AdaptiveStableSelector:
        return AdaptiveStableSelector(
            n_resamples=4,
            stability_threshold=0.5,
            max_features=self.config.max_features,
            random_state=self.config.seed,
        )

    def _fit_selected_models(self, X: pd.DataFrame, y: np.ndarray, models: dict[str, Any]) -> None:
        self.fitted_candidates_: dict[str, tuple[Any, Any, Any]] = {}
        for name in self.selected_names_:
            spec = next(item for item in self.candidate_specs_ if item[0] == name)
            _, model_name, view, use_selector = spec
            representation = self._new_representation(view)
            representation.fit(X, y)
            transformed = representation.transform(X)
            selector = self._new_selector() if use_selector else None
            if selector is not None:
                transformed = selector.fit_transform(transformed, y)
            model = clone(models[model_name])
            model.fit(transformed, y)
            self.fitted_candidates_[name] = (representation, selector, model)

    def _predict_raw(self, X: pd.DataFrame) -> np.ndarray:
        values = []
        for name in self.selected_names_:
            representation, selector, model = self.fitted_candidates_[name]
            transformed = representation.transform(X)
            if selector is not None:
                transformed = selector.transform(transformed)
            values.append(model.predict_proba(transformed)[:, 1])
        return np.column_stack(values)


def _softmax(values: np.ndarray, temperature: float) -> np.ndarray:
    scaled = (values - values.max()) / max(temperature, 1e-6)
    weights = np.exp(scaled)
    return weights / weights.sum()


def _cross_fitted_calibrators(
    probabilities: np.ndarray,
    y: np.ndarray,
    seed: int,
    methods: tuple[str, ...],
) -> dict[str, np.ndarray]:
    outputs = {method: np.empty_like(probabilities, dtype=float) for method in methods}
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    for train, validation in cv.split(probabilities, y):
        for method in methods:
            calibrator = _build_calibrator(method).fit(probabilities[train], y[train])
            outputs[method][validation] = calibrator.predict(probabilities[validation])
    return outputs


def _build_calibrator(method: str) -> Any:
    if method == "sigmoid":
        return SigmoidCalibrator()
    if method == "isotonic":
        return IsotonicCalibrator()
    raise ValueError(f"Unsupported calibration method: {method}")


def _threshold_evidence(y: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    default = evaluate_predictions(y, probabilities, threshold=0.5)
    optimized = _select_threshold(y, probabilities, "validation_balanced_accuracy")
    optimized_metrics = evaluate_predictions(y, probabilities, threshold=optimized)
    return {
        "default_threshold": 0.5,
        "default_metrics": default,
        "optimized_threshold": optimized,
        "optimized_metrics": optimized_metrics,
    }


def _select_threshold(y: np.ndarray, probabilities: np.ndarray, mode: str) -> float:
    if mode == "default":
        return 0.5
    if mode != "validation_balanced_accuracy":
        raise ValueError("threshold_mode must be 'default' or 'validation_balanced_accuracy'")
    candidates = np.linspace(0.05, 0.95, 91)
    scores = [
        evaluate_predictions(y, probabilities, threshold=float(threshold))["balanced_accuracy"]
        for threshold in candidates
    ]
    best = max(range(len(candidates)), key=lambda index: (scores[index], -candidates[index]))
    return float(candidates[best])
