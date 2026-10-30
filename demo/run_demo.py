"""Non-clinical demonstration of prediction, uncertainty, and abstention."""

from __future__ import annotations

import argparse
from pathlib import Path

from sklearn.model_selection import train_test_split

from cardiodiag.data import load_dataset
from cardiodiag.experiments import build_corrected_pipeline
from cardiodiag.uncertainty import SplitConformalClassifier


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("heart5.csv"))
    args = parser.parse_args()
    X, y = load_dataset(args.dataset, "HeartDisease")
    X_fit, X_eval, y_fit, y_eval = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )
    X_train, X_cal, y_train, y_cal = train_test_split(
        X_fit, y_fit, test_size=0.25, stratify=y_fit, random_state=42
    )
    pipeline = build_corrected_pipeline(X_train, variant="osec", seed=42)
    model = SplitConformalClassifier(pipeline, alpha=0.1)
    model.fit(X_train, y_train, X_cal, y_cal)
    probabilities = model.predict_proba(X_eval.iloc[[0]])[0]
    prediction_set = model.predict_sets(X_eval.iloc[[0]])[0]
    prediction = model.predict(X_eval.iloc[[0]])[0]
    print("CARDIODIAG research prototype demonstration")
    print("WARNING: not clinically validated; do not use for patient care.")
    print(f"Observed evaluation label (demo only): {int(y_eval.iloc[0])}")
    print(f"Predicted class: {prediction if prediction >= 0 else 'ABSTAIN'}")
    print(f"Probability of class 1: {probabilities[1]:.4f}")
    print(f"Conformal prediction set: {prediction_set.astype(int).tolist()}")


if __name__ == "__main__":
    main()
