"""Reproducible corrected-baseline and proposed-method experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .data import drop_identifier_columns, load_dataset, summarize_dataset
from .evaluation import evaluate_predictions
from .feature_selection import StableXAIHDRC
from .models import build_osec, build_ovec
from .preprocessing import TrainingOnlyCleaner, make_tabular_preprocessor


@dataclass(frozen=True)
class ExperimentConfig:
    dataset: str
    target: str
    variant: str
    seed: int
    test_size: float
    outlier_strategy: str
    use_stable_selector: bool


def build_corrected_pipeline(
    X_train: Any,
    variant: str,
    seed: int = 42,
    use_stable_selector: bool = False,
    outlier_strategy: str = "median",
) -> Pipeline:
    """Construct a pipeline whose every fitted transformation is training-only."""

    if not hasattr(X_train, "select_dtypes"):
        raise TypeError("X_train must be a pandas DataFrame")
    configured_categorical = set(X_train.attrs.get("categorical_columns", []))
    categorical = [
        column
        for column in X_train.columns
        if column in configured_categorical
        or column not in X_train.select_dtypes(include=["number"]).columns
    ]
    numeric = [column for column in X_train.columns if column not in categorical]
    models = {
        "logistic": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=seed,
        ),
        "ovec": build_ovec(random_state=seed),
        "osec": build_osec(random_state=seed),
    }
    if variant not in models:
        raise ValueError(f"Unknown variant {variant!r}; choose from {sorted(models)}")
    steps: list[tuple[str, Any]] = [
        (
            "cleaner",
            TrainingOnlyCleaner(
                outlier_strategy=outlier_strategy,
                categorical_columns=tuple(categorical),
            ),
        ),
        ("preprocessor", make_tabular_preprocessor(numeric, categorical)),
    ]
    if use_stable_selector:
        steps.append(
            (
                "stable_xaih_drc",
                StableXAIHDRC(
                    n_resamples=6,
                    fallback_top_k=min(8, max(2, len(numeric))),
                    random_state=seed,
                ),
            )
        )
    steps.append(("model", clone(models[variant])))
    return Pipeline(steps=steps)


def run_single_experiment(
    dataset_path: str | Path,
    target: str,
    variant: str,
    seed: int = 42,
    test_size: float = 0.25,
    use_stable_selector: bool = False,
    outlier_strategy: str = "median",
) -> dict[str, Any]:
    """Fit one frozen internal split and return machine-readable metrics."""

    X, y = load_dataset(dataset_path, target)
    X, dropped_identifiers = drop_identifier_columns(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
        random_state=seed,
    )
    pipeline = build_corrected_pipeline(
        X_train,
        variant=variant,
        seed=seed,
        use_stable_selector=use_stable_selector,
        outlier_strategy=outlier_strategy,
    )
    pipeline.fit(X_train, y_train)
    probabilities = pipeline.predict_proba(X_test)[:, 1]
    metrics = evaluate_predictions(y_test.to_numpy(), probabilities)
    config = ExperimentConfig(
        dataset=str(dataset_path),
        target=target,
        variant=variant,
        seed=seed,
        test_size=test_size,
        outlier_strategy=outlier_strategy,
        use_stable_selector=use_stable_selector,
    )
    return {
        "config": asdict(config),
        "dataset_summary": summarize_dataset(dataset_path, target).to_dict(),
        "dropped_identifier_columns": dropped_identifiers,
        "metrics": metrics,
    }


def run_repeated_experiments(
    dataset_path: str | Path,
    target: str,
    variants: list[tuple[str, bool]],
    seeds: list[int],
) -> list[dict[str, Any]]:
    """Run a prespecified set of variants and seeds without test-set tuning."""

    results = []
    for variant, stable_selector in variants:
        for seed in seeds:
            results.append(
                run_single_experiment(
                    dataset_path,
                    target,
                    variant=variant,
                    seed=seed,
                    use_stable_selector=stable_selector,
                )
            )
    return results
