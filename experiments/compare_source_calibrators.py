"""Compare source-fitted probability maps on the frozen AngioCAD predictions.

External labels are used only for descriptive scoring and bootstrap intervals.
No calibrator or setting is selected using those labels.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize, minimize_scalar
from scipy.special import expit, logit
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results/transfer_20261105_angiocad_external"
OUTPUT = ROOT / "results/second_stage_calibration_20261106_stratified"
SEED = 20261105
EPS = 1e-7


def ece(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    ids = np.minimum(np.digitize(p, edges[1:-1]), bins - 1)
    return float(
        sum(
            np.mean(ids == b) * abs(np.mean(y[ids == b]) - np.mean(p[ids == b]))
            for b in range(bins)
            if np.any(ids == b)
        )
    )


def score(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    lp = logit(np.clip(p, EPS, 1 - EPS))
    slope_fit = LogisticRegression(C=1e6, solver="lbfgs", max_iter=2000)
    slope_fit.fit(lp.reshape(-1, 1), y)
    return {
        "n": int(len(y)),
        "prevalence": float(y.mean()),
        "mean_predicted_risk": float(np.mean(p)),
        "roc_auc": float(roc_auc_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "ece_10_equal_width": ece(y, p),
        "calibration_intercept": float(slope_fit.intercept_[0]),
        "calibration_slope": float(slope_fit.coef_[0, 0]),
    }


def beta_fit(p: np.ndarray, y: np.ndarray, sample_weight: np.ndarray):
    x = np.column_stack([np.log(np.clip(p, EPS, 1)), -np.log(np.clip(1 - p, EPS, 1))])

    def objective(theta):
        q = expit(theta[0] * x[:, 0] + theta[1] * x[:, 1] + theta[2])
        q = np.clip(q, EPS, 1 - EPS)
        point_loss = -(y * np.log(q) + (1 - y) * np.log(1 - q))
        return float(np.average(point_loss, weights=sample_weight))

    fit = minimize(
        objective, [1.0, 1.0, 0.0], method="L-BFGS-B", bounds=[(0, None), (0, None), (None, None)]
    )
    if not fit.success:
        raise RuntimeError(f"Beta calibration optimization failed: {fit.message}")
    return lambda z: expit(
        fit.x[0] * np.log(np.clip(z, EPS, 1))
        + fit.x[1] * -np.log(np.clip(1 - z, EPS, 1))
        + fit.x[2]
    ), fit.x


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=False)
    source = pd.read_csv(INPUT / "source_calibration_predictions.csv")
    target = pd.read_csv(INPUT / "external_predictions.csv")
    sy = source.y_binary.to_numpy(dtype=int)
    sp = source.raw_probability.to_numpy(dtype=float)
    domain_counts = source.source_cohort.value_counts()
    sw = source.source_cohort.map(
        {name: len(source) / (len(domain_counts) * count) for name, count in domain_counts.items()}
    ).to_numpy(dtype=float)
    ty = target.y_binary.to_numpy(dtype=int)
    tp = target.raw_probability.to_numpy(dtype=float)
    saved_platt = target.platt_probability.to_numpy(dtype=float)
    methods: dict[str, np.ndarray] = {
        "uncalibrated": tp,
        "frozen_original_source_platt": saved_platt,
    }

    platt = LogisticRegression(C=1e6, solver="lbfgs", max_iter=2000)
    platt.fit(logit(np.clip(sp, EPS, 1 - EPS)).reshape(-1, 1), sy, sample_weight=sw)
    methods["source_refit_platt"] = platt.predict_proba(
        logit(np.clip(tp, EPS, 1 - EPS)).reshape(-1, 1)
    )[:, 1]

    iso = IsotonicRegression(out_of_bounds="clip").fit(sp, sy, sample_weight=sw)
    methods["source_isotonic"] = iso.predict(tp)

    beta, beta_params = beta_fit(sp, sy, sw)
    methods["source_beta"] = beta(tp)

    def temp_loss(log_t):
        q = expit(logit(np.clip(sp, EPS, 1 - EPS)) / np.exp(log_t))
        return float(
            np.average(
                -(
                    sy * np.log(np.clip(q, EPS, 1 - EPS))
                    + (1 - sy) * np.log(np.clip(1 - q, EPS, 1 - EPS))
                ),
                weights=sw,
            )
        )

    temp = minimize_scalar(temp_loss, bounds=(-3, 3), method="bounded")
    temperature = float(np.exp(temp.x))
    methods["source_temperature"] = expit(logit(np.clip(tp, EPS, 1 - EPS)) / temperature)

    # Target labels enter only the fixed-metric evaluation and paired bootstrap.
    rng = np.random.default_rng(SEED)
    class_indices = [np.flatnonzero(ty == label) for label in (0, 1)]
    rows = []
    curves = {}
    for name, probs in methods.items():
        base = score(ty, probs)
        samples = {k: [] for k in ("brier", "log_loss", "ece_10_equal_width", "roc_auc")}
        for _ in range(2000):
            idx = np.concatenate(
                [rng.choice(group, len(group), replace=True) for group in class_indices]
            )
            if np.unique(ty[idx]).size < 2:
                continue
            yy, pp = ty[idx], probs[idx]
            pp_clip = np.clip(pp, EPS, 1 - EPS)
            samples["brier"].append(float(np.mean((yy - pp) ** 2)))
            samples["log_loss"].append(
                float(-np.mean(yy * np.log(pp_clip) + (1 - yy) * np.log(1 - pp_clip)))
            )
            samples["ece_10_equal_width"].append(ece(yy, pp))
            samples["roc_auc"].append(float(roc_auc_score(yy, pp)))
        base["bootstrap_95_ci"] = {
            key: [float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))]
            for key, vals in samples.items()
        }
        rows.append({"method": name, **base})
        observed, predicted = calibration_curve(ty, probs, n_bins=10, strategy="uniform")
        curves[name] = {"observed": observed.tolist(), "predicted": predicted.tolist()}

    result = {
        "study_id": "CD-XD-004-POSTHOC-CALIBRATION-COMPARISON",
        "status": "exploratory_secondary_analysis_not_confirmatory",
        "input_target_predictions_sha256": hashlib
        .sha256((INPUT / "external_predictions.csv").read_bytes())
        .hexdigest(),
        "input_source_calibration_sha256": hashlib
        .sha256((INPUT / "source_calibration_predictions.csv").read_bytes())
        .hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "target_labels_used_for": (
            "fixed descriptive metrics and bootstrap intervals only; "
            "never fit or tune calibrators"
        ),
        "source_calibration_n": int(len(sy)),
        "external_n": int(len(ty)),
        "external_event_count": int(ty.sum()),
        "external_prevalence": float(ty.mean()),
        "temperature": temperature,
        "beta_parameters": beta_params.tolist(),
        "bootstrap_replicates": 2000,
        "seed": SEED,
        "methods": rows,
        "calibration_curves": curves,
        "excluded_methods": {
            "prevalence_shift": (
                "not fitted: external prevalence cannot be used as an unlabeled "
                "prior-shift estimate; requires P(X|Y) stability and a separate "
                "unlabeled target protocol"
            ),
            "target_labeled_calibration": (
                "not confirmatory: the full cohort has already been examined; "
                "a new split is only post-hoc adaptation feasibility"
            ),
            "domain_specific_platt": (
                "not transported: no defensible mapping from an unseen target "
                "to one of the four source-site calibrators"
            ),
        },
    }
    (OUTPUT / "calibration_comparison.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    pd.DataFrame(rows).drop(columns=["bootstrap_95_ci"]).to_csv(
        OUTPUT / "calibration_metrics.csv", index=False
    )
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], "--", color="black", label="ideal")
    for name, c in curves.items():
        ax.plot(c["predicted"], c["observed"], marker="o", label=name)
    ax.set(
        xlim=(0, 1),
        ylim=(0, 1),
        xlabel="Mean predicted probability",
        ylabel="Observed event fraction",
        title="Source-fitted calibration on AngioCAD (post-hoc)",
    )
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUTPUT / "calibration_curves.png", dpi=180)
    plt.close(fig)
    print(f"Wrote {OUTPUT}; target labels used only for fixed evaluation.")


if __name__ == "__main__":
    main()
