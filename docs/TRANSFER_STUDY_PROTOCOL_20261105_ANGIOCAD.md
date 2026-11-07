# Locked external validation protocol: AngioCAD

**Protocol ID:** `CD-XD-004`  
**Protocol frozen:** 2026-11-05, after provenance and schema eligibility audit and before fitting or scoring this target cohort  
**Status:** one-way, source-distinct, endpoint-aligned external-cohort evaluation

## Objective and claim boundary

Evaluate the already locked multi-source cardiovascular prediction, source-only
probability calibration, and source-calibrated out-of-distribution (OOD)
warning on an independent hospital cohort with a matching angiographic
stenosis threshold. This is a research prototype. It is not clinically
validated and does not support diagnostic or treatment decisions.

The training sources are Cleveland, Hungary, Switzerland, and VA Long Beach
from the UCI Heart Disease archive. The external site is Shahid Chamran Heart
Center, Isfahan, Iran, as identified in the AngioCAD dataset article. The
public files contain no cross-dataset person identifiers, so record-level
deduplication against the source files cannot be verified. Site and cohort
provenance are distinct; this limitation is retained in every interpretation.

## Cohort and target

The external dataset is AngioCAD, Zenodo record `15826856`, CC BY 4.0. The
Zenodo record describes 413 patients and contains separate clinical-feature
and artery-label workbooks. A schema audit found 413 unique nonblank IDs in the
label workbook but only 377 unique nonblank IDs in the feature workbook. All
377 feature IDs match a label ID; 36 labeled IDs have no clinical-feature row.
Both workbooks also contain two blank rows. The analysis therefore uses the
377 uniquely matched patients; the missing 36 cases are excluded because
their predictors are unavailable. Among matched rows, age is missing for 6
patients and FBS for 11; these are imputed using source-fit values only.

Derive the binary target from the 15 artery-segment label columns. Label a
patient positive (`1`) when any segment is recorded in `51-75`, `76-90`,
`91-99`, or `100`. Label a patient negative (`0`) when every segment is
recorded as `NL`, `1-25`, or `26-50`. The matched cohort contains 298 positive
and 79 negative cases. Positive bins start at 51% and the negative `26-50` bin
falls at or below the source UCI Heart Disease positive cut point of `>50%`.
The AngioCAD workbook does not preserve exact stenosis percentages within the
`26-50` bin, so cases at exactly 50% cannot be separated from lower values for
a boundary-specific sensitivity analysis. Unlike the prior Z-Alizadeh Sani
stress-test cohort, AngioCAD does not classify the 50% threshold as positive.

## Harmonized predictors

Use the same three predictors already frozen for `CD-XD-003`:

- `age`: years, numeric.
- `sex`: male/female, normalized to source values `male` and `female`.
- `fbs`: binary fasting blood sugar indicator `>120 mg/dL`. The source UCI
  feature is already defined at this strict threshold; convert AngioCAD's
  numeric FBS measurement with the same rule. The AngioCAD workbook does not
  state the unit; its observed values (55--514) are interpreted as mg/dL. This
  unit mapping is an explicit assumption rather than a unit recorded in the
  workbook.

Exclude all other fields. In particular, exclude the AngioCAD `Diagnosis`,
medication, laboratory, and artery-label columns to avoid introducing features
with uncertain source equivalence or direct target information.

## Locked fit, calibration, and OOD procedure

Reuse the exact `CD-XD-003` source-only pipeline and fixed seed. Within each
source cohort, reserve a stratified 20% calibration partition using seed
`20261105 + 100 + source_index`, in the fixed order Cleveland, Hungary,
Switzerland, VA Long Beach. Fit preprocessing and one logistic regression
(`C=1`, `liblinear`, no class weighting) on the remaining 80% of each source
cohort, assigning equal total weight to each domain. Median-impute and scale
age; most-frequent-impute and one-hot encode sex and FBS status. Fit Platt
calibration (`LogisticRegression`, `C=1e6`) on the source calibration rows
only, with equal total weight per cohort. Fit a 300-tree Isolation Forest on
source-fit rows only; set the alert threshold to the equal-domain-weighted
95th percentile of source-calibration anomaly scores.

Do not use any AngioCAD rows or labels for model fitting, calibration,
imputation, scaling, feature selection, OOD fitting, or threshold selection.
After all source-only components are frozen, score the 377 matched external
rows once. Do not adjust the model after observing external performance.

## Outcomes and uncertainty

Report raw and Platt-calibrated ROC-AUC, average precision, Brier score, log
loss, fixed-width 10-bin ECE, calibration intercept and slope, and descriptive
classification measures at probability 0.5. Report source-calibration false
alert rate, AngioCAD alert rate and coverage, source-vs-AngioCAD OOD AUROC,
and calibrated metrics in accepted and flagged subsets.

Use 1,000 class-stratified bootstrap resamples for descriptive 95% intervals
of predictive metrics and OOD AUROC. These predictive intervals condition on
the observed matched-cohort class counts; they do not estimate between-site
uncertainty. One external hospital cannot identify population-level site
variance. The OOD alert is a research warning, not a safety alarm.

## Interpretation rules

- This study tests transfer to one separate hospital using a common-denominator
  three-feature representation and an endpoint derived from stenosis bins.
- The target is an angiography-referred clinical cohort with a high positive
  fraction; results do not establish performance in population screening or
  other care settings.
- The source-calibrated probabilities may remain miscalibrated under shift.
  Calibration and OOD warning performance are empirical outcomes, not assumed
  benefits.
- Report negative or inconclusive findings without retuning. Logistic
  regression, Platt scaling, and Isolation Forest are established methods and
  are not claimed as algorithmic novelty.
- Attribute the dataset and article; retain the feature/label workbook
  discrepancy and inability to verify person-level overlap as limitations.

## Provenance

**Protocol clarification:** after an initial execution, the description of the
target's `26-50` negative bin was clarified to state that it includes the 50%
boundary but does not preserve exact percentages. The FBS unit assumption was
also stated explicitly because the workbook does not encode a unit. The
operational label rule, feature set, source splits, model, calibration, OOD
threshold, and outcomes were unchanged. The final run and reproduction use
the hash of this clarified protocol.

Hosseini, M. S., Naghsh-Nilchi, A. R., Safayani, M., et al. *AngioCAD: A
public X-ray angiography dataset and an adaptive fusion framework for
stenosis detection*. Computer Methods and Programs in Biomedicine, 282 (2026),
109368. https://doi.org/10.1016/j.cmpb.2026.109368. Dataset record:
https://doi.org/10.5281/zenodo.15826856. Public record metadata, file checksums,
and access details are saved in
`data/external/angiocad_zenodo_15826856/` and
`data/manifests/angiocad_external.json`.
