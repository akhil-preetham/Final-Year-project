"""Command-line entry points for audit and smoke experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sklearn.model_selection import train_test_split

from .data import load_dataset, summarize_dataset
from .evaluation import evaluate_predictions
from .feature_selection import StableXAIHDRC
from .models import build_osec
from .preprocessing import TrainingOnlyCleaner, make_tabular_preprocessor


def _dataset_paths(root: Path) -> list[tuple[Path, str]]:
    return [
        (root / "heart5.csv", "HeartDisease"),
        (root / "MendeleyCardiovascular_Disease_Dataset.csv", "target"),
    ]


def run_audit(root: Path) -> None:
    for path, target in _dataset_paths(root):
        print(json.dumps(summarize_dataset(path, target).to_dict(), indent=2))


def run_smoke(root: Path) -> dict[str, float | int | list[float]]:
    X, y = load_dataset(root / "heart5.csv", "HeartDisease")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )
    numeric = list(X_train.select_dtypes(include=["number"]).columns)
    categorical = [column for column in X_train.columns if column not in numeric]
    preprocess = make_tabular_preprocessor(numeric, categorical)
    selector = StableXAIHDRC(n_resamples=4, fallback_top_k=4, random_state=42)
    model = build_osec(random_state=42)
    cleaner = TrainingOnlyCleaner().fit(X_train)
    preprocess.fit(cleaner.transform(X_train), y_train)
    X_train_encoded = preprocess.transform(cleaner.transform(X_train))
    X_test_encoded = preprocess.transform(cleaner.transform(X_test))
    selector.fit(X_train_encoded, y_train)
    model.fit(selector.transform(X_train_encoded), y_train)
    probabilities = model.predict_proba(selector.transform(X_test_encoded))[:, 1]
    return evaluate_predictions(y_test.to_numpy(), probabilities)


def main() -> None:
    parser = argparse.ArgumentParser(prog="cardiodiag")
    parser.add_argument("command", choices=["audit", "smoke"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    if args.command == "audit":
        run_audit(args.root)
    else:
        print(json.dumps(run_smoke(args.root), indent=2))
