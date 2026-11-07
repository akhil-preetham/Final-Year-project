"""Fail-closed domain and uncertainty gate for research predictions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from cardiodiag.uncertainty import conformal_prediction_sets


class DomainAwareSelectivePredictor:
    """Return scores only for registered domains and singleton in-support cases.

    The domain identifier is assumed to come from trusted data provenance or
    deployment metadata. Unknown or missing domains fail closed before a risk
    score is exposed. This is a research guard, not a clinical authorization
    system or guarantee of generalization.
    """

    def __init__(self, bundle: dict[str, Any]) -> None:
        required = {
            "preprocessor",
            "predictor",
            "calibrator",
            "neighbors",
            "source_domains",
            "conformal_thresholds_by_domain",
            "ood_thresholds_by_domain",
            "features",
        }
        missing = required - bundle.keys()
        if missing:
            raise ValueError(f"Model bundle is missing required keys: {sorted(missing)}")
        self.bundle = bundle
        self.source_domains = frozenset(str(name) for name in bundle["source_domains"])
        self.features = tuple(bundle["features"])
        self.numeric_features = tuple(bundle.get("numeric_features", ("age", "chol")))
        self.categorical_features = tuple(
            bundle.get(
                "categorical_features",
                (name for name in self.features if name not in self.numeric_features),
            )
        )
        self.allowed_categories = bundle.get("allowed_categories", {"sex": ["female", "male"]})

    @classmethod
    def load(cls, path: str | Path) -> DomainAwareSelectivePredictor:
        """Load a locally generated, trusted project bundle."""

        bundle = joblib.load(path)
        if not isinstance(bundle, dict):
            raise ValueError("Model bundle must contain a dictionary")
        return cls(bundle)

    def _abstain(self, n_rows: int, reason: str) -> list[dict[str, Any]]:
        return [
            {
                "action": "abstain",
                "reason": reason,
                "probability": None,
                "prediction_set": [],
                "prediction": None,
                "ood_score": None,
            }
            for _ in range(n_rows)
        ]

    def predict(self, features: pd.DataFrame, domain_id: str | None) -> list[dict[str, Any]]:
        """Score registered-domain rows; abstain on unknown domains or weak support."""

        if not isinstance(features, pd.DataFrame):
            raise TypeError("features must be a pandas DataFrame")
        if len(features) == 0:
            return []
        if domain_id is None or str(domain_id) not in self.source_domains:
            return self._abstain(len(features), "domain_not_in_source_registry")
        if not set(self.features).issubset(features.columns):
            return self._abstain(len(features), "required_feature_schema_missing")

        frame = features.loc[:, self.features].copy()
        for column in self.numeric_features:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        for column in self.categorical_features:
            allowed = self.allowed_categories.get(column, [])
            observed = frame[column].dropna()
            if allowed and not observed.isin(allowed).all():
                return self._abstain(len(features), f"unsupported_category_encoding:{column}")

        matrix = self.bundle["preprocessor"].transform(frame)
        raw_probability = self.bundle["predictor"].predict_proba(matrix)[:, 1]
        logits = np.log(
            np.clip(raw_probability, 1e-7, 1 - 1e-7) / np.clip(1 - raw_probability, 1e-7, 1.0)
        )
        probability = self.bundle["calibrator"].predict_proba(logits.reshape(-1, 1))[:, 1]
        distances = self.bundle["neighbors"].kneighbors(matrix, return_distance=True)[0]
        ood_scores = distances.mean(axis=1)
        domain = str(domain_id)
        conformal_threshold = float(self.bundle["conformal_thresholds_by_domain"][domain])
        ood_threshold = float(self.bundle["ood_thresholds_by_domain"][domain])
        sets = conformal_prediction_sets(
            np.column_stack([1.0 - probability, probability]), conformal_threshold
        )

        results: list[dict[str, Any]] = []
        for index in range(len(features)):
            labels = np.flatnonzero(sets[index]).astype(int).tolist()
            reasons: list[str] = []
            if len(labels) != 1:
                reasons.append("non_singleton_conformal_set")
            outside_support = ood_scores[index] > ood_threshold
            if outside_support:
                reasons.append("outside_source_feature_support")
            action = "classify" if not reasons else "abstain"
            results.append(
                {
                    "action": action,
                    "reason": ";".join(reasons) if reasons else None,
                    "probability": float(probability[index]) if action == "classify" else None,
                    "prediction_set": [] if outside_support else labels,
                    "prediction": labels[0] if action == "classify" else None,
                    "ood_score": float(ood_scores[index]),
                }
            )
        return results
