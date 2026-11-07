"""Controlled synthetic covariate-shift diagnostics on Heart5.

This is a software/method diagnostic only. Transformed rows are synthetic,
retain labels, and are never described as external clinical validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.neighbors import LocalOutlierFactor, NearestNeighbors

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "heart5.csv"
OUT = ROOT / "results/controlled_shift_lab_20261106_run4"
SEED = 20261106
FEATURES = ["Age", "RestingBP", "Cholesterol", "MaxHR", "Oldpeak"]


def local_outlier_factor_scores(
    train: np.ndarray, source_eval: np.ndarray, shifted_eval: np.ndarray
) -> np.ndarray:
    """Return source-fit LOF novelty scores, with larger values more anomalous."""
    train = np.asarray(train, dtype=float)
    source_eval = np.asarray(source_eval, dtype=float)
    shifted_eval = np.asarray(shifted_eval, dtype=float)
    if train.ndim != 2 or len(train) < 3:
        raise ValueError("LOF requires at least three two-dimensional training rows")
    if source_eval.ndim != 2 or shifted_eval.ndim != 2:
        raise ValueError("LOF evaluation inputs must be two-dimensional")
    if source_eval.shape[1] != train.shape[1] or shifted_eval.shape[1] != train.shape[1]:
        raise ValueError("LOF training and evaluation feature counts must match")
    detector = LocalOutlierFactor(n_neighbors=min(20, len(train) - 1), novelty=True)
    detector.fit(train)
    return np.r_[-detector.score_samples(source_eval), -detector.score_samples(shifted_eval)]


def transforms(frame: pd.DataFrame, rng: np.random.Generator) -> dict[str, pd.DataFrame]:
    shifted = {}
    x = frame.copy()
    x["Age"] += x["Age"].std(ddof=0)
    shifted["mean_shift_age"] = x
    x = frame.copy()
    x["Cholesterol"] = x["Cholesterol"].mean() + 1.75 * (x["Cholesterol"] - x["Cholesterol"].mean())
    shifted["variance_shift_chol"] = x
    x = frame.copy()
    x["Cholesterol"] = rng.permutation(x["Cholesterol"].to_numpy())
    shifted["correlation_shift_chol_thalach"] = x
    x = frame.copy()
    x["RestingBP"] *= 10
    shifted["unit_shift_trestbps_x10"] = x
    x = frame.copy()
    x.loc[rng.random(len(x)) < 0.5, "Cholesterol"] = np.nan
    shifted["missingness_shift_chol_50pct"] = x
    return shifted


def main(output_dir: Path = OUT) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    frame = pd.read_csv(DATA)
    y = frame["HeartDisease"].astype(int).to_numpy()
    X = frame[FEATURES].apply(pd.to_numeric, errors="coerce")
    train_i, test_i = train_test_split(
        np.arange(len(X)), test_size=0.4, random_state=SEED, stratify=y
    )
    train, test = X.iloc[train_i].copy(), X.iloc[test_i].copy()
    med = train.median()
    train_imp = train.fillna(med)
    mean, scale = train_imp.mean(), train_imp.std(ddof=0).replace(0, 1)

    def embed(z: pd.DataFrame) -> np.ndarray:
        missing = z.isna().to_numpy(dtype=float)
        value = z.fillna(med)
        return np.column_stack([((value - mean) / scale).to_numpy(), missing])

    a, b = embed(train), embed(test)
    knn = NearestNeighbors(n_neighbors=10).fit(a)
    # Novelty mode is required because scoring the held-out samples with the
    # default LOF transductive API would contaminate the reference neighborhood.
    lw = LedoitWolf().fit(a)
    pca = PCA(n_components=0.95, random_state=SEED).fit(a)
    iso = IsolationForest(n_estimators=300, random_state=SEED, contamination="auto").fit(a)

    records = []
    for j, (name, shifted_train) in enumerate(
        transforms(train, np.random.default_rng(SEED + 1)).items()
    ):
        shifted_test = transforms(test, np.random.default_rng(SEED + 100 + j))[name]
        sb, sa = embed(shifted_train), embed(shifted_test)
        # Domain classifier is trained on synthetic source-vs-shift training pairs
        # and evaluated on held-out source-vs-shift pairs.
        dc_x = np.vstack([a, sb])
        dc_y = np.r_[np.zeros(len(a)), np.ones(len(sb))]
        dc = LogisticRegression(max_iter=2000, class_weight="balanced").fit(dc_x, dc_y)
        eval_x = np.vstack([b, sa])
        eval_y = np.r_[np.zeros(len(b)), np.ones(len(sa))]
        pca_b = np.mean((b - pca.inverse_transform(pca.transform(b))) ** 2, axis=1)
        pca_sa = np.mean((sa - pca.inverse_transform(pca.transform(sa))) ** 2, axis=1)
        scores = {
            "knn_distance": np.r_[
                knn.kneighbors(b)[0].mean(axis=1), knn.kneighbors(sa)[0].mean(axis=1)
            ],
            "local_outlier_factor": local_outlier_factor_scores(a, b, sa),
            "mahalanobis": np.r_[lw.mahalanobis(b), lw.mahalanobis(sa)],
            "isolation_forest": np.r_[-iso.score_samples(b), -iso.score_samples(sa)],
            "pca_reconstruction": np.r_[pca_b, pca_sa],
            "domain_classifier": dc.predict_proba(eval_x)[:, 1],
            "missingness_fraction": np.r_[
                np.mean(test.isna().to_numpy(), axis=1),
                np.mean(shifted_test.isna().to_numpy(), axis=1),
            ],
        }
        for method, score in scores.items():
            fpr, tpr, _ = roc_curve(eval_y, score)
            records.append(
                {
                    "shift": name,
                    "detector": method,
                    "n_source_test": len(b),
                    "n_shifted_test": len(sa),
                    "auroc": float(roc_auc_score(eval_y, score)),
                    "auprc": float(average_precision_score(eval_y, score)),
                    "tpr_at_fpr_le_5pct": float(tpr[fpr <= 0.05].max())
                    if np.any(fpr <= 0.05)
                    else 0.0,
                    "fpr_at_tpr_ge_80pct": float(fpr[np.flatnonzero(tpr >= 0.8)[0]])
                    if np.any(tpr >= 0.8)
                    else 1.0,
                }
            )

    result = {
        "study_id": "SYNTHETIC-COVARIATE-SHIFT-001",
        "status": "controlled_synthetic_diagnostic_not_external_validation",
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "feature_columns": FEATURES,
        "split": {"seed": SEED, "test_fraction": 0.4, "stratified_by_target": True},
        "shifts": [
            "age mean + 1 SD",
            "cholesterol variance x 1.75",
            "cholesterol permutation (correlation disruption)",
            "resting blood pressure x 10 (synthetic unit shift)",
            "50% cholesterol missingness",
        ],
        "methods": list(scores),
        "metrics": records,
        "limits": [
            "Transformed records are synthetic copies of held-out source rows.",
            "Domain discrimination is not individual error detection or concept-shift detection.",
            "The detector threshold was not selected for deployment; this is a ranking diagnostic.",
            (
                "Local Outlier Factor uses novelty=True and is fitted only on source-train "
                "rows; it is scored on held-out source and transformed copies."
            ),
            (
                "Target labels were not used to fit detectors; labels remain unchanged "
                "and are not used in shift AUC."
            ),
            "No result here is real-world external validation.",
        ],
    }
    (output_dir / "controlled_shift_metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    pd.DataFrame(records).to_csv(output_dir / "controlled_shift_metrics.csv", index=False)
    print(f"Wrote synthetic-shift diagnostic to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT)
    main(parser.parse_args().output_dir)
