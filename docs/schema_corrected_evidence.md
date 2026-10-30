# Schema-corrected bounded evidence

**Run date:** 2026-10-27  
**Artifact prefix:** `results/generated/schema_corrected_*`  
**Status:** verified sensitivity evidence, not a replacement for the earlier
3-fold/10-repeat artifacts.

## Protocol

The code was corrected before these runs to use explicit local feature schemas
and validation-only permutation relevance within each selector resample. The
following bounded runs were completed without using external data or labels:

- 2 outer folds and 2 inner folds for all five nested candidates on each local
  dataset;
- 5 stratified folds × 3 repeats with six relevance resamples for stability;
- four repeated 56.25% fit / 18.75% calibration / 25% evaluation splits for
  selective reliability;
- four paired splits for stability–reliability linkage.

The 10-minute two-dataset default internal-stage run did not finish before the
execution limit and wrote no artifacts. It is therefore not claimed as passed.

## Feature schema verification

| Dataset | Numeric predictors | Explicit categorical predictors |
|---|---|---|
| `heart5.csv` | Age, RestingBP, Cholesterol, MaxHR, Oldpeak | Sex, ChestPainType, FastingBS, RestingECG, ExerciseAngina, ST_Slope |
| Mendeley | age, restingBP, serumcholestrol, maxheartrate, oldpeak | gender, chestpain, fastingbloodsugar, restingrelectro, exerciseangia, slope, noofmajorvessels |

The Mendeley integer-coded categories are now one-hot encoded and are not
treated as continuous measurements by the cleaner or preprocessor.

## Bounded nested results

The generated table is `results/tables/schema_corrected_nested_2x2.md` and the
machine-readable source is `results/generated/schema_corrected_*nested_2x2.json`.

| Dataset | Candidate with highest bounded ROC-AUC mean | ROC-AUC mean | Stable-vs-corrected interpretation |
|---|---|---:|---|
| `heart5.csv` | corrected OVEC | 0.9276 | Stable logistic was similar; stable OSEC was similar in discrimination but worse in ECE. |
| Mendeley | corrected OVEC | 0.9946 | Stable OSEC was slightly below OVEC and had higher ECE than corrected OVEC. |

The fold count is deliberately small and these values are sensitivity evidence,
not final confirmatory estimates. The generated CSV/Markdown/LaTeX files are
derived directly from the JSON artifacts.

## Stability evidence

| Dataset | Stable mean Nogueira | One-shot mean Nogueira | Paired difference | 95% bootstrap interval | Interpretation |
|---|---:|---:|---:|---:|---|
| `heart5.csv` | 0.204 | 0.014 | 0.189 | [0.027, 0.425] | Positive comparative stability evidence in this bounded rerun. |
| Mendeley | 0.484 | 0.215 | 0.269 | [0.039, 0.574] | Positive comparative stability evidence in this bounded rerun. |

The intervals are bootstrap intervals over three repeat-level estimates and are
not independent-patient confidence intervals. They support a narrower claim
about the selector under this perturbation design, not generalizability.

## Selective reliability and linkage

Four-seed repeated uncertainty summaries show that confidence-error AUC is above
0.5 for both candidates and both datasets. The stable selector did not give a
uniform benefit:

- On `heart5.csv`, stable OSEC had slightly lower confidence-error AUC (0.739
  vs 0.740), lower AURC (0.052 vs 0.052), and lower ECE (0.091 vs 0.104), with
  overlapping repeated-seed intervals.
- On Mendeley, stable OSEC had slightly higher confidence-error AUC (0.931 vs
  0.924) but also slightly higher AURC (0.0039 vs 0.0037), ECE (0.234 vs
  0.232), and full-coverage risk (0.037 vs 0.034). Conformal coverage was
  essentially the same (0.902 vs 0.903).

The four-seed linkage artifacts report cross-seed selected-set stability of
0.162 on `heart5.csv` and 0.149 on Mendeley after the schema correction. Paired
ROC-AUC differences were +0.0009 [0.0002, 0.0019] and -0.0004 [-0.0013,
0.0004], respectively. These bounded results still do not show a consistent
stability-to-reliability improvement.

## Evaluation-only robustness stress test

The runner `experiments/run_robustness.py` fits each candidate once on a clean
development split and perturbs evaluation rows only. It is explicitly not
external validation. At seed 42, the measured ROC-AUC values were:

| Dataset | Candidate | Clean | 10% evaluation missingness | 5% of training-SD numeric noise |
|---|---|---:|---:|---:|
| `heart5.csv` | corrected OSEC | 0.935 | 0.922 | 0.931 |
| `heart5.csv` | stable OSEC | 0.935 | 0.922 | 0.931 |
| Mendeley | corrected OSEC | 0.998 | 0.993 | 0.810 |
| Mendeley | stable OSEC | 0.998 | 0.993 | 0.815 |

The Mendeley numeric-noise stress test shows substantial degradation and the
Five States missingness stress test shows a smaller degradation. These are
single-split sensitivity results, not population-shift estimates. The raw
artifacts are `schema_corrected_heart5_robustness.json` and
`schema_corrected_mendeley_robustness.json`.

## Evidence decision

The schema correction changes the feature universe and the bounded numerical
results, so previous artifacts remain historical pre-correction evidence. The
current evidence supports:

1. explicit feature typing and held-out training-only relevance materially
   improve the auditability of the implementation;
2. comparative feature-set stability can be positive under the chosen bounded
   perturbation design; and
3. stability remains an unreliable surrogate for discrimination, calibration,
   confidence ranking, or selective risk.

It does not support a universal performance improvement, external validation,
clinical utility, or a new algorithmic novelty claim.
