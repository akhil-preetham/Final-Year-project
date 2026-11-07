# Independent-cohort transport protocol

**Protocol ID:** `CD-XD-003`  
**Frozen:** 2026-11-05, before predictive model fitting  
**Status:** one-way source-distinct external-cohort transport stress test  
**Purpose:** test a locked multi-source prediction, source-only probability
calibration, and source-calibrated out-of-distribution (OOD) warning on a
cohort from a separate hospital.

## Scope and claim boundary

The source training data are the Cleveland, Hungary, Switzerland, and VA Long
Beach components of the UCI Heart Disease archive. The target is the UCI
Z-Alizadeh Sani cohort, reported as 303 patients from Shahid Rajaei
Cardiovascular, Medical, and Research Center in Tehran. This cohort was not
found in the project's prior data inventory and is source-distinct from the
four source cohorts. The public file has no patient identifiers, so record-level
duplicate exclusion cannot be verified.

The label cut point is not identical. UCI Heart Disease encodes disease as
greater than 50% diameter narrowing and absence as less than 50%, whereas the
Z-Alizadeh Sani description assigns CAD at greater than or equal to 50%.
Percent-level stenosis measurements are not available to reconcile the
boundary. This study is therefore an independent-site **transport stress
test**, not an endpoint-identical external validation. No clinical-use or
clinical-readiness claim is permitted.

## Frozen cohort and mapping

- External archive: `data/external/uci_z_alizadeh_sani_412/z_alizadeh_sani.zip`.
- The downloaded workbook has 303 rows and 56 columns: 55 predictor columns
  plus `Cath`. UCI's text says 54 features; this discrepancy is recorded and
  the experiment uses only the three fields below.
- Target: `Cath=Normal` maps to 0 and `Cath=Cad` maps to 1. The frozen file has
  87 Normal and 216 Cad records and no missing cells.
- Predictors, chosen only from documented compatible definitions:
  - `age` / `Age`: years, numeric.
  - `sex` / `Sex`: 1=male and 0=female. Source values are numeric; the external
    workbook contains exactly `Male` and `Fmale`. `Male` maps to 1 and the
    apparent spelling error `Fmale` maps to 0, consistent with the published
    binary feature description. This explicit recode is recorded in outputs.
  - `fbs` / `FBS`: binary fasting-glucose indicator at the strict threshold
    `>120 mg/dL`. The source field is already defined this way; the external
    numeric measurement is converted using that same strict threshold.
- Other fields are excluded because equivalent measurement definitions have
  not been established. In particular, `LDL` is not substituted for source
  total cholesterol, and the external `BP` field is not assumed to be the
  source's resting admission pressure.
- The source target maps `num=0` to 0 and `num=1..4` to 1.

## Locked analysis

1. Fit one model using all four source cohorts. Within each source cohort,
   reserve a stratified 20% calibration partition using seed
   `20261105 + 100 + source_index` in the fixed cohort order Cleveland,
   Hungary, Switzerland, VA Long Beach. Use the other 80% for predictor and
   OOD-model fitting. No target rows or labels enter any fit, calibration,
   imputation, scaling, or threshold choice.
2. Fit fixed logistic regression (`C=1`, `liblinear`, no class weighting) on
   the three harmonized predictors. Median-impute and standardize age; most
   frequent-impute and one-hot encode sex and fasting-glucose status. Give
   each source cohort equal total sample weight during fitting.
3. Fit a Platt sigmoid calibrator (`LogisticRegression`, `C=1e6`) on the
   source calibration partition only, with equal total weight per cohort.
   Report raw and calibrated probabilities.
4. Fit a 300-tree Isolation Forest on transformed source-fit rows only. Set
   its alert threshold to the equal-cohort-weighted 95th percentile of
   source-calibration anomaly scores. The threshold targets a nominal 5%
   source false-alert rate. It is not tuned on external rows.
5. Score the full Z-Alizadeh Sani cohort once. Save row-indexed predictions,
   labels, calibrated probabilities, OOD scores, and flags for independent
   recomputation. Do not adapt or refit after inspecting target performance.

No hyperparameter search, feature selection, target recalibration, target
threshold selection, or target-guided model comparison is allowed.

## Outcomes and uncertainty

Report raw and Platt-calibrated ROC-AUC, average precision, Brier score, log
loss, 10-bin fixed-width ECE, calibration intercept and slope, and descriptive
classification measures at a 0.5 probability threshold. Report source versus
target OOD-score AUROC, the source calibration false-alert rate, target alert
rate, and calibration metrics in flagged and accepted target subsets.

Use 1,000 class-stratified bootstrap resamples for descriptive 95% intervals
of predictive metrics and OOD AUROC. Predictive intervals condition on the
observed target class counts; they do not quantify between-hospital
uncertainty. There is one target hospital, so no population-level estimate of
site-to-site variance or significance test is claimed. Source calibration does
not guarantee calibration or nominal OOD coverage under target shift.

## Interpretation rules

- This is an untouched-cohort transfer test from four source datasets to one
  separate hospital, with a three-feature common-denominator representation.
- The endpoint cut-point mismatch and lack of patient IDs limit claims even if
  predictive metrics are strong.
- OOD score is a research warning based on predictors, not a safety alarm.
  Flagging a target record does not establish that its prediction is wrong;
  accepting a record does not establish that it is reliable.
- Calibration or OOD-warning improvements are hypotheses, not assumed
  outcomes. Negative results must be reported as observed.
- The primary contribution, if supported, is evidence about the frozen
  evaluation and reliability behavior; established logistic regression,
  Platt scaling, and Isolation Forest are not claimed as novel methods.

## Provenance

UCI Machine Learning Repository, *Z-Alizadeh Sani*, dataset ID 412, DOI
`10.24432/C5Q31T`, CC BY 4.0. Archive and workbook SHA-256 values are in
`data/manifests/uci_z_alizadeh_sani_external.json` and will be repeated in the
run manifest. Source-cohort provenance is UCI *Heart Disease*, dataset ID 45,
DOI `10.24432/C52P4X`, CC BY 4.0. Attribute both datasets in reuse.
