"""Compare feature-selection stability under repeated training perturbations."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.model_selection import RepeatedStratifiedKFold

from cardiodiag.data import drop_identifier_columns, load_dataset
from cardiodiag.experiments import build_corrected_pipeline
from cardiodiag.feature_selection import StableXAIHDRC, one_shot_selection_mask
from cardiodiag.provenance import collect_provenance
from cardiodiag.reliability import bootstrap_mean_ci, nogueira_stability


def _provenance_metadata(
    dataset: Path,
    target: str,
    n_splits: int,
    n_repeats: int,
    n_resamples: int,
    stability_threshold: float,
    relevance_threshold: float,
    seed: int,
) -> dict[str, Any]:
    """Collect stability provenance without changing the computation."""

    return collect_provenance(
        dataset=dataset,
        target=target,
        experiment_type="stability_evidence",
        configuration={
            "n_splits": n_splits,
            "n_repeats": n_repeats,
            "n_resamples": n_resamples,
            "stability_threshold": stability_threshold,
            "relevance_threshold": relevance_threshold,
            "seed": seed,
        },
    )


def _training_matrix(X_train: Any, y_train: Any, seed: int) -> tuple[np.ndarray, list[str]]:
    """Fit the cleaner and encoder on one training perturbation only."""

    pipeline = build_corrected_pipeline(
        X_train,
        variant="logistic",
        seed=seed,
        use_stable_selector=False,
    )
    cleaner = pipeline.named_steps["cleaner"]
    preprocessor = pipeline.named_steps["preprocessor"]
    cleaned = cleaner.fit_transform(X_train, y_train)
    transformed = preprocessor.fit_transform(cleaned, y_train)
    names = preprocessor.get_feature_names_out().tolist()
    return np.asarray(transformed, dtype=float), names


def _selection_matrix(selection_sets: list[set[str]], universe: list[str]) -> np.ndarray:
    index = {name: position for position, name in enumerate(universe)}
    matrix = np.zeros((len(selection_sets), len(universe)), dtype=float)
    for row, selected in enumerate(selection_sets):
        for name in selected:
            matrix[row, index[name]] = 1.0
    return matrix


def _method_summary(
    selection_sets: list[set[str]],
    universe: list[str],
    repeat_sets: dict[int, list[set[str]]],
) -> dict[str, Any]:
    repeat_stability = {
        str(repeat): nogueira_stability(_selection_matrix(sets, universe))
        for repeat, sets in sorted(repeat_sets.items())
    }
    repeat_values = np.asarray(list(repeat_stability.values()), dtype=float)
    mean, low, high = bootstrap_mean_ci(repeat_values)
    matrix = _selection_matrix(selection_sets, universe)
    frequencies = matrix.mean(axis=0)
    return {
        "n_training_perturbations": int(len(selection_sets)),
        "feature_universe_size": int(len(universe)),
        "mean_selected_features": float(matrix.sum(axis=1).mean()),
        "overall_nogueira_stability": nogueira_stability(matrix),
        "repeat_nogueira_stability": repeat_stability,
        "mean_repeat_nogueira_stability": mean,
        "mean_repeat_nogueira_stability_ci": {"low": low, "high": high},
        "selection_frequency": [
            {"feature": name, "frequency": float(frequencies[index])}
            for index, name in enumerate(universe)
            if frequencies[index] > 0
        ],
    }


def run_dataset(
    dataset: Path,
    target: str,
    n_splits: int,
    n_repeats: int,
    n_resamples: int,
    stability_threshold: float,
    relevance_threshold: float,
    seed: int,
) -> dict[str, Any]:
    """Run a prespecified stability comparison without using outer test labels."""

    X, y = load_dataset(dataset, target)
    X, dropped_identifiers = drop_identifier_columns(X)
    numeric_count = len(X.select_dtypes(include=["number"]).columns)
    fallback_top_k = min(8, max(2, numeric_count))
    splitter = RepeatedStratifiedKFold(
        n_splits=n_splits,
        n_repeats=n_repeats,
        random_state=seed,
    )

    all_names: set[str] = set()
    all_sets: dict[str, list[set[str]]] = {"stable_xaih_drc": [], "one_shot_xaih_drc": []}
    grouped_sets: dict[str, dict[int, list[set[str]]]] = {
        "stable_xaih_drc": defaultdict(list),
        "one_shot_xaih_drc": defaultdict(list),
    }
    records: list[dict[str, Any]] = []

    for split_id, (train_index, _) in enumerate(splitter.split(X, y)):
        repeat_id = split_id // n_splits
        fold_id = split_id % n_splits
        X_train = X.iloc[train_index]
        y_train = y.iloc[train_index]
        transformed, names = _training_matrix(X_train, y_train, seed + split_id)
        stable = StableXAIHDRC(
            n_resamples=n_resamples,
            stability_threshold=stability_threshold,
            relevance_threshold=relevance_threshold,
            fallback_top_k=fallback_top_k,
            random_state=seed + split_id,
        ).fit(transformed, y_train.to_numpy())
        one_shot = one_shot_selection_mask(
            transformed,
            y_train.to_numpy(),
            relevance_threshold=relevance_threshold,
            fallback_top_k=fallback_top_k,
            random_state=seed + split_id,
        )
        stable_selected = {names[index] for index in stable.get_support(indices=True)}
        one_shot_selected = {names[index] for index in np.flatnonzero(one_shot)}
        all_names.update(names)
        for method, selected in (
            ("stable_xaih_drc", stable_selected),
            ("one_shot_xaih_drc", one_shot_selected),
        ):
            all_sets[method].append(selected)
            grouped_sets[method][repeat_id].append(selected)
        records.append(
            {
                "repeat": repeat_id,
                "fold": fold_id,
                "transformed_feature_count": len(names),
                "stable_selected_count": len(stable_selected),
                "one_shot_selected_count": len(one_shot_selected),
                "stable_selected_features": sorted(stable_selected),
                "one_shot_selected_features": sorted(one_shot_selected),
            }
        )

    universe = sorted(all_names)
    summaries = {
        method: _method_summary(all_sets[method], universe, grouped_sets[method])
        for method in all_sets
    }
    stable_repeat = summaries["stable_xaih_drc"]["repeat_nogueira_stability"]
    one_shot_repeat = summaries["one_shot_xaih_drc"]["repeat_nogueira_stability"]
    differences = np.asarray(
        [stable_repeat[key] - one_shot_repeat[key] for key in sorted(stable_repeat)],
        dtype=float,
    )
    difference, low, high = bootstrap_mean_ci(differences)

    return {
        "dataset": str(dataset),
        "target": target,
        "dropped_identifier_columns": dropped_identifiers,
        "provenance": _provenance_metadata(
            dataset=dataset,
            target=target,
            n_splits=n_splits,
            n_repeats=n_repeats,
            n_resamples=n_resamples,
            stability_threshold=stability_threshold,
            relevance_threshold=relevance_threshold,
            seed=seed,
        ),
        "protocol": {
            "n_splits": n_splits,
            "n_repeats": n_repeats,
            "n_resamples": n_resamples,
            "stability_threshold": stability_threshold,
            "relevance_threshold": relevance_threshold,
            "selection_baseline": "single-pass correlation/permutation selector",
            "feature_universe": (
                "union of training-fold transformed feature names; absent fold-local "
                "categories are recorded as not selected"
            ),
            "test_labels_used": False,
        },
        "methods": summaries,
        "paired_stability_difference": {
            "stable_minus_one_shot_mean": difference,
            "bootstrap_ci": {"low": low, "high": high},
            "positive_stability_evidence": bool(low > 0),
            "interpretation": (
                "positive evidence requires the paired 95% interval to exclude zero; "
                "this is comparative evidence, not a universal proof"
            ),
        },
        "perturbation_records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--n-repeats", type=int, default=3)
    parser.add_argument("--n-resamples", type=int, default=8)
    parser.add_argument("--stability-threshold", type=float, default=0.75)
    parser.add_argument("--relevance-threshold", type=float, default=0.02)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run_dataset(
        dataset=args.dataset,
        target=args.target,
        n_splits=args.n_splits,
        n_repeats=args.n_repeats,
        n_resamples=args.n_resamples,
        stability_threshold=args.stability_threshold,
        relevance_threshold=args.relevance_threshold,
        seed=args.seed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote stability evidence to {args.output}")


if __name__ == "__main__":
    main()
