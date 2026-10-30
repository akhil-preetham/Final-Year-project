"""Faithful, explicitly labelled approximation of the historical notebook flow."""

from __future__ import annotations

from typing import Any

import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    StackingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from .evaluation import evaluate_predictions


def historical_encode_heart5(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Apply the notebook's global encoding and target extraction order."""

    data = frame.dropna().copy()
    if "HeartDisease" not in data:
        raise ValueError("Expected HeartDisease target in historical Five States data")
    data["Sex"] = data["Sex"].map({"M": 1, "F": 0})
    for column in ["ChestPainType", "RestingECG"]:
        encoder = LabelEncoder()
        data[column] = encoder.fit_transform(data[column])
    data["ExerciseAngina"] = data["ExerciseAngina"].map({"Y": 1, "N": 0})
    data["ST_Slope"] = data["ST_Slope"].map({"Up": 1, "Flat": 0, "Down": 0})
    X = data.drop(columns=["HeartDisease"])
    y = data["HeartDisease"].astype(int)
    if X.isna().any().any():
        raise ValueError("Historical encoding produced missing feature values")
    return X, y


def build_historical_ovec(random_state: int = 42) -> VotingClassifier:
    return VotingClassifier(
        estimators=[
            ("knn", KNeighborsClassifier()),
            ("rf", RandomForestClassifier(random_state=random_state)),
            ("lr", LogisticRegression(max_iter=2000, random_state=random_state)),
            ("svc", SVC(probability=True, random_state=random_state)),
        ],
        voting="soft",
        n_jobs=-1,
    )


def build_historical_osec(random_state: int = 42) -> StackingClassifier:
    return StackingClassifier(
        estimators=[
            ("rf", RandomForestClassifier(random_state=random_state)),
            ("tree", DecisionTreeClassifier(random_state=random_state)),
            ("gb", GradientBoostingClassifier(random_state=random_state)),
            ("nb", GaussianNB()),
        ],
        final_estimator=LogisticRegression(max_iter=2000, random_state=random_state),
        cv=5,
        n_jobs=-1,
    )


def run_historical_native(
    frame: pd.DataFrame,
    model_name: str,
    seed: int = 42,
) -> dict[str, Any]:
    """Run the notebook-like 80/20-after-SMOTE protocol.

    This function is intentionally not a recommended clinical evaluation. It
    exists to quantify the effect of the historical ordering and to make the
    deviation from the corrected protocol explicit.
    """

    X, y = historical_encode_heart5(frame)
    X_resampled, y_resampled = SMOTE(random_state=seed).fit_resample(X, y)
    X_train, X_test, y_train, y_test = train_test_split(
        X_resampled,
        y_resampled,
        test_size=0.2,
        random_state=seed,
    )
    models = {
        "ovec": build_historical_ovec(seed),
        "osec": build_historical_osec(seed),
    }
    if model_name not in models:
        raise ValueError(f"Unknown historical model {model_name!r}")
    model = models[model_name]
    model.fit(X_train, y_train)
    probabilities = model.predict_proba(X_test)[:, 1]
    return {
        "protocol": {
            "name": "historical_native",
            "encoding": "global LabelEncoder/manual maps",
            "resampling": "SMOTE before train_test_split",
            "split": "80/20, random_state=42, no stratify",
            "smote_random_state": seed,
            "model": model_name,
        },
        "metrics": evaluate_predictions(y_test.to_numpy(), probabilities),
        "shapes": {
            "original": [int(X.shape[0]), int(X.shape[1])],
            "resampled": [int(X_resampled.shape[0]), int(X_resampled.shape[1])],
            "train": [int(X_train.shape[0]), int(X_train.shape[1])],
            "test": [int(X_test.shape[0]), int(X_test.shape[1])],
        },
    }
