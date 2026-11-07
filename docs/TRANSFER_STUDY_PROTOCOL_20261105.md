# Multi-source transfer study protocol

**Protocol ID:** `CD-XD-002`  
**Frozen:** 2026-11-05 (after a label-count and data-quality audit, before model fitting)  
**Status:** exploratory retrospective leave-one-source-out pilot  
**Purpose:** evaluate source-only prediction, probability calibration, and an
out-of-distribution (OOD) warning on complete held-out cohorts.

## Scope and claim boundary

The current local benchmarks cannot support independent external validation.
This pilot uses the four named source cohorts in the UCI Heart Disease release:
Cleveland, Hungary, Switzerland, and VA Long Beach. Each cohort is held out as
a complete test domain in turn. The downloaded UCI archive is frozen by SHA-256
in the result artifact.

This is a **retrospective domain-holdout experiment**, not a new external
validation study. The project's historical `heart5.csv` composite contains
records from these component sources, and the local study has already used that
composite. Consequently, each target domain is unseen by the fit/calibration
steps of its corresponding run, but its records were not unseen to the project
as a whole. The four source cohorts also come from one legacy dataset release;
they do not establish transport to a contemporary health system or clinical
population. No clinical-use claim is permitted.

## Eligibility and estimand

- **Target:** binary presence of coronary heart disease, with UCI `num=0`
  mapped to absence and `num=1,2,3,4` mapped to presence.
- **Label meaning:** the UCI documentation defines the underlying angiographic
  criterion as less than 50% versus greater than 50% diameter narrowing in a
  major vessel.
- **Cohorts:** the four processed, named files in the archived UCI release:
  `processed.cleveland.data`, `processed.hungarian.data`,
  `processed.switzerland.data`, and `processed.va.data`.
- **Predictors:** the 13 shared UCI attributes: `age`, `sex`, `cp`, `trestbps`,
  `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, and
  `thal`. Patient identifiers and all other fields are excluded.
- **Missing values:** `?` is treated as missing. Missing numeric predictors
  are median-imputed and missing categorical predictors are most-frequent
  imputed, with each imputer fitted on source-training rows only.
- **Impossible measurement codes:** in the primary run, `chol=0` and
  `trestbps=0` are treated as missing because the documented units are
  mg/dL and mm Hg, respectively. A fixed sensitivity run retains these zero
  values. No other value is removed or winsorized.
- **Data status:** UCI identifies four databases and documents the 14-field
  representation. The ZIP contains processed representations for the four
  domains, which this script parses and audits before fitting.

The pre-model audit found 303 Cleveland, 294 Hungary, 123 Switzerland, and 200
VA records. After collapsing `num`, negative/positive counts are 164/139,
188/106, 8/115, and 51/149, respectively. It also found 123 zero cholesterol
values in Switzerland, 49 in VA, and one zero resting blood pressure in VA.
The 8 negative Switzerland records make threshold, calibration, and
class-conditional estimates particularly imprecise; this cohort is retained
because it is part of the frozen multi-source design, not because of any model
result.

The binary angiographic endpoint is more specific than broad cardiovascular
risk or mortality. These results must be described as heart-disease presence
classification on this legacy benchmark only.

## Locked evaluation

1. Run four outer folds. In each fold, one complete cohort is the target; its
   rows and labels do not enter preprocessing, fitting, probability calibration,
   OOD fitting, or threshold selection.
2. From each of the other three cohorts, make one stratified 80/20 source
   training/calibration split using the frozen seed schedule in the runner.
   No target rows enter either split.
3. Fit a fixed logistic-regression predictor (`C=1`, `liblinear`, no class
   reweighting) after a training-only transformation: median-imputed and
   standardized numeric fields; most-frequent-imputed and one-hot-encoded
   categorical fields. Preserve missingness indicators learned from source
   training rows. Give each source cohort equal total weight during model
   fitting so the largest cohort does not dominate solely by row count.
4. Fit a sigmoid/Platt probability calibrator using only source-calibration
   rows and their source-trained model scores, using logistic regression with
   `C=1e6`. Weight calibration rows equally by source cohort. No calibration or
   threshold adjustment uses target labels.
5. Fit an Isolation Forest on transformed source-training predictors only.
   Weight its fit equally by source cohort. Set the OOD alert threshold to the
   equal-cohort-weighted 95th percentile of anomaly scores on source-calibration
   rows, corresponding to a nominal 5% source false-alert rate. Do not optimize
   this threshold against target data.
6. Score each complete target cohort once after the pipeline is frozen. Save
   per-row raw and calibrated probabilities, OOD scores, flags, and labels so
   results can be independently recomputed.
7. Repeat the exact pipeline once with the predeclared zero-value sensitivity
   policy. Do not select between the two policies based on target performance.

No hyperparameter search or target adaptation is performed. The fixed logistic
baseline is intended to test the evaluation and reliability design, not to
claim a new classifier.

## Outcomes

Report per target cohort:

- ROC-AUC and average precision;
- Brier score, log loss, expected calibration error (10 fixed-width bins),
  calibration intercept, and calibration slope, before and after Platt
  calibration;
- OOD-score AUROC separating source-calibration rows from target rows,
  target alert rate at the source-calibrated 5% threshold, and performance and
  coverage among unflagged target rows;
- target class counts, source split counts, missingness, and the exact
  predictor/target hashes and software versions.

Use 1,000 class-stratified bootstrap resamples for per-cohort descriptive 95%
intervals of predictive metrics. These intervals condition on the observed
class counts and do not quantify between-hospital uncertainty. Report the
macro-average across the four target cohorts as descriptive only; do not pool
all rows into a single headline result. Retain all unsuccessful, undefined, or
ill-conditioned metrics with an explicit reason.

## Interpretation rules

- Dataset-level holdout is the primary split; random row-level validation is
  not a substitute.
- OOD detection here means identifying a held-out source domain using
  predictors alone. It is not proof that a flagged patient is unsafe, and it
  is not a clinical alarm.
- Better calibration on the held-out cohort is not expected to be guaranteed by
  source-only calibration. Report degradation and negative results unchanged.
- Because the component records occur in the historical composite and the
  cohorts are legacy data, positive results are pilot evidence only. A
  confirmatory claim requires a prospectively frozen, independent, compatible
  cohort not previously used in this project.

## Provenance

Source: UCI Machine Learning Repository, *Heart Disease*, DOI
`10.24432/C52P4X`, dataset ID 45, CC BY 4.0. The archive is stored at
`data/external/uci_heart_disease_45/heart_disease.zip`; its SHA-256 is recorded
in the run manifest. Cite the dataset and attribute the UCI repository and
listed dataset contributors in any reuse.
