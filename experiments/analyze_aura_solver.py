"""Compare AURA selector solvers on one fixed 70K training representation."""

from __future__ import annotations

import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from cardiodiag.aura.preprocessing import AdaptiveTabularTransformer
from cardiodiag.data import drop_identifier_columns, load_dataset


def run(dataset: Path, target: str, output: Path, seed: int = 42) -> dict:
    X, y = load_dataset(dataset, target)
    X, _ = drop_identifier_columns(X)
    transformer = AdaptiveTabularTransformer().fit(X, y)
    transformed = transformer.transform(X)
    labels = y.to_numpy(dtype=int)
    rng = np.random.default_rng(seed)
    records = {}
    for solver in ("liblinear", "lbfgs", "saga"):
        warnings_seen: list[str] = []
        fits = []
        started = time.perf_counter()
        for repeat in range(4):
            indices = rng.integers(0, len(labels), size=len(labels))
            model = LogisticRegression(
                penalty="l1" if solver != "lbfgs" else "l2",
                solver=solver,
                C=0.2,
                max_iter=3000,
                tol=1e-3,
                class_weight="balanced",
                random_state=seed + repeat,
            )
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                model.fit(transformed[indices], labels[indices])
            warnings_seen.extend(str(item.message) for item in caught)
            fits.append(
                {
                    "repeat": repeat,
                    "n_iter": np.asarray(model.n_iter_).astype(int).tolist(),
                    "train_auc": float(
                        roc_auc_score(
                            labels[indices],
                            model.predict_proba(transformed[indices])[:, 1],
                        )
                    ),
                    "coefficient_norm": float(np.linalg.norm(model.coef_)),
                }
            )
        records[solver] = {
            "fits": fits,
            "warning_count": len(warnings_seen),
            "warnings": sorted(set(warnings_seen)),
            "runtime_seconds": time.perf_counter() - started,
        }
    result = {
        "status": "completed",
        "dataset": str(dataset),
        "target": target,
        "rows": len(labels),
        "transformed_features": transformed.shape[1],
        "seed": seed,
        "records": records,
        "interpretation": (
            "This is a solver diagnostic on the fixed training representation, "
            "not an outer predictive comparison."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run(args.dataset, args.target, args.output, args.seed)
    print(f"Wrote solver diagnostic to {args.output}; rows={result['rows']}")


if __name__ == "__main__":
    main()
