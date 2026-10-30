# Candidate contribution and evidence plan

## Candidate contribution

The strongest defensible candidate is a **leakage-controlled
stability--reliability decoupling audit for CARDIODIAG**. The contribution is
not currently claimed as a new algorithm. It is a falsifiable research package
that joins two decisions that are usually reported separately:

1. select features only inside the training data and quantify whether the
   selected set survives repeated training perturbations; and
2. expose an abstention/prediction-set decision when the fitted model's
   confidence is not empirically reliable.

The working name is `LC-Stability-Reliability-Audit`. It should be renamed only
after a complete literature review confirms that the exact evaluation question
is not already reported.

## Hypotheses and acceptance rules

### H1 — Feature selection is more stable than a single-pass comparator

For each repeated stratified training perturbation, fit:

- `stable_xaih_drc`: the resampled selector with a prespecified inclusion
  threshold; and
- `one_shot_xaih_drc`: the same relevance score computed once on the training
  fold.

Compare the selected sets on the same transformed feature universe using:

- Nogueira chance-corrected stability;
- mean selected-feature count;
- per-feature selection frequency; and
- a paired bootstrap interval over repeat-level stability differences.

The positive claim is allowed only when the paired 95% interval for
`stable_xaih_drc - one_shot_xaih_drc` is above zero and the feature-count
difference is reported. A high internal `selection_frequency_` by itself is not
enough because it describes resamples inside one fit and does not compare
methods or training folds.

Run:

```text
uv run python experiments/run_stability_evidence.py \
  --dataset heart5.csv \
  --target HeartDisease \
  --output results/generated/heart5_stability_evidence.json
```

The script does not use outer test labels. Fold-local one-hot feature names are
aligned by their union; a category unavailable in a training fold is recorded
as not selected for that perturbation.

### H2 — Confidence is useful for selective decisions

The model cannot be shown to "understand" uncertainty in a human or semantic
sense. The measurable claim is narrower: confidence should rank correct
predictions above errors, and refusing low-confidence cases should reduce risk.

The current reliability output reports:

- `confidence_error_auc` — discrimination of correct versus incorrect cases by
  confidence;
- area under the risk-coverage curve (`aurc`);
- risk at prespecified coverage values;
- monotonicity violations in the finite-sample risk-coverage curve;
- split-conformal coverage and abstention on a labelled evaluation split.

Positive evidence requires all of the following to be considered together:

- confidence-error AUC above 0.5 with an uncertainty interval or repeated-fold
  evidence;
- lower risk at lower coverage than at full coverage;
- conformal coverage close to its nominal target on data that were not used for
  fitting or calibration; and
- explicit reporting of failures under shift.

Conformal coverage is not assumed on an external or shifted cohort. It must be
measured there, and any violation must remain part of the result.

### H3 — Results generalize beyond development data

This cannot be established with the two supplied datasets. `heart5.csv` and the
Mendeley dataset are development/replication evidence for this project; the
Mendeley source was used by the base paper, and the Five States file is a
composite of public component datasets.

The evidence hierarchy is:

1. repeated nested internal validation: estimates development-set robustness;
2. prespecified synthetic or temporal/site stress tests: estimates sensitivity
   to known perturbations but are not external validation; and
3. one-way evaluation on a frozen, genuinely independent compatible cohort:
   required for an external generalization claim.

No external generalization claim is permitted until the manifest gate passes and
the frozen pipeline is evaluated without external-label fitting, calibration,
threshold tuning, or model selection.

The one-way runner is implemented in
`experiments/run_external_evaluation.py`. It first validates the frozen
manifest, then fits and calibrates only on the development data, and finally
applies the resulting pipeline to the external rows for metrics. Running it
with `data/manifests/external_dataset.template.json` fails closed before reading
either dataset, as intended.

## Current interpretation

- The project can test H1 directly with the new stability-evidence runner.
- The project can test H2 empirically, but not prove that the model "knows" its
  uncertainty.
- The project cannot yet test H3 with a valid independent cohort.
- A negative H1 or H2 result is still a useful contribution: it would show that
  the proposed stability/reliability layer does not justify stronger claims on
  these benchmarks.
- The combined linkage analysis tests the stronger and more useful question:
  whether feature-set stability is a valid proxy for predictive or selective
  reliability. Current evidence says it is not a dependable proxy.

## Evidence obtained so far

The bounded runs completed on October 25, 2026 used 5-fold, 10-repeat training
perturbations for H1 and 10 repeated fit/calibration/evaluation splits for H2.
These are internal benchmark results, not external validation.

### H1 results

| Dataset | Stable mean Nogueira | One-shot mean Nogueira | Paired difference (95% bootstrap CI) | Interpretation |
|---|---:|---:|---:|---|
| `heart5.csv` | 0.646 | 0.549 | 0.098 [-0.111, 0.254] | Inconclusive; no positive stability claim |
| Mendeley | 0.708 | 0.630 | 0.078 [0.035, 0.119] | Positive comparative evidence on this benchmark |

The result is mixed. It supports a dataset-conditional stability improvement on
Mendeley, but not a universal claim across both development datasets.

### H2 results

Repeated internal reliability results for corrected OSEC versus stable OSEC:

- `heart5.csv`: confidence-error AUC `0.762 [0.734, 0.789]` versus
  `0.755 [0.720, 0.785]`; conformal coverage `0.913 [0.903, 0.921]` versus
  `0.913 [0.903, 0.922]`.
- Mendeley: confidence-error AUC `0.917 [0.895, 0.935]` versus
  `0.925 [0.905, 0.943]`; conformal coverage `0.914 [0.896, 0.933]` versus
  `0.917 [0.898, 0.936]`.

Confidence ranks correctness substantially above chance in these internal
repeats, and the conformal coverage is near the nominal 90% target. However,
the ECE remains non-trivial and the results do not show that the stability-aware
variant is consistently more reliable. The safe claim is **empirical selective
reliability on these development benchmarks**, not that the model understands
uncertainty or will retain coverage under shift.

Generated evidence files:

- `results/generated/heart5_stability_evidence.json`
- `results/generated/mendeley_stability_evidence.json`
- `results/generated/heart5_uncertainty_evidence.json`
- `results/generated/mendeley_uncertainty_evidence.json`
- `results/generated/heart5_stability_reliability_linkage.json`
- `results/generated/mendeley_stability_reliability_linkage.json`

### Stability--reliability linkage

The paired linkage runner used the same ten seeds for fitting, calibration, and
evaluation. Cross-seed selected-set stability was `0.368` on Five States and
`0.579` on Mendeley. Despite this, stable-minus-corrected ROC-AUC differences
were approximately zero on both datasets, and the main confidence-error,
conformal-coverage, and calibration differences had intervals crossing zero.
Five States showed a small adverse AURC difference of `+0.0025`
(`[0.0002, 0.0055]`). This supports the narrower contribution that feature
stability and predictive/selective reliability must be evaluated separately.
