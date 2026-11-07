# Cross-dataset validation and transport evidence

Three frozen dataset-shift studies have now been run. They establish a
reproducible research workflow and include one source-distinct,
endpoint-aligned external cohort. The empirical evidence remains mixed: model
discrimination transports better than calibration, and the current OOD method
has weak target-site separation. These results do not support clinical use.

## Completed studies

| Study | Training data | Held-out target | Result role | Main caveat |
|---|---|---|---|---|
| `CD-XD-002` | Three of four UCI Heart Disease cohorts per fold | Fourth source cohort, four leave-one-cohort-out folds | Retrospective domain-holdout pilot | All source records are represented in the historical Heart5 composite |
| `CD-XD-003` | Cleveland, Hungary, Switzerland, and VA Long Beach | Z-Alizadeh Sani, 303 records from a separate Tehran hospital | Source-distinct transport stress test | Target uses `>=50%`; source uses `>50%`; person-level overlap cannot be checked |
| `CD-XD-004` | Same four UCI source cohorts | AngioCAD, 377 matched records from a separate Isfahan hospital | Endpoint-aligned external evaluation | 36 of 413 labeled IDs lack feature rows; no cross-dataset person IDs; one target site |

`CD-XD-002` had macro ROC-AUC 0.760, mean Brier 0.202 before and 0.170 after
source-only Platt calibration, and OOD AUROC 0.758. Its held-out alert rate
ranged from 2.4% to 86.8%, showing that the source-calibrated warning rate did
not transport consistently. Full results are in
[`TRANSFER_STUDY_RESULTS_20261105.md`](TRANSFER_STUDY_RESULTS_20261105.md).

`CD-XD-003` used age, sex, and fasting-glucose status to train one logistic
model and evaluated the separate Tehran cohort once. ROC-AUC was 0.720 (95%
class-stratified bootstrap interval 0.651–0.780). The paired Brier, log-loss,
and ECE differences after source-only calibration were inconclusive. OOD
AUROC was 0.604 (95% interval 0.552–0.652). The result is a source-distinct
stress test because the target boundary differs at 50%. Full results are in
[`TRANSFER_STUDY_RESULTS_20261105_ZAS.md`](TRANSFER_STUDY_RESULTS_20261105_ZAS.md).

`CD-XD-004` used the same locked three-feature pipeline to score AngioCAD's
Isfahan cohort, where artery-label bins align with the source `>50%` stenosis
outcome. ROC-AUC was 0.787 (95% interval 0.734–0.838). Source-only Platt
calibration modestly improved Brier and log loss by point estimate, but both
paired intervals included no change; ECE worsened slightly. OOD AUROC was
0.589 (95% interval 0.541–0.635), a weak warning signal. Predictions reproduced
byte-for-byte in a separate run. Full results, hashes, and predictions are in
[`TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md`](TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md).

## Compatibility decision

The four UCI source cohorts are suitable for retrospective within-release
leave-one-cohort-out evaluation, not independent validation, because their
records were represented in Heart5. The Z-Alizadeh Sani cohort is from a
separate hospital, but its CAD cut point includes exactly 50% and is therefore
retained only as a stress test.

AngioCAD is a distinct hospital cohort with artery-severity categories that
separate 50% or less from 51% or greater. This matches the source endpoint and
supports an endpoint-aligned evaluation. Only 377 of 413 labeled IDs had
clinical predictor rows, so the analysis is limited to those matched patients.
The source and target releases lack common person identifiers, preventing
direct patient-level overlap checks. The AngioCAD workbook does not give an
FBS unit; its range is interpreted as mg/dL for threshold harmonization. One
site does not estimate between-hospital variability.

The Kaggle 70K data remain a separate benchmark with a different outcome and
measurement schema. Heart5→Mendeley and Mendeley→Heart5 remain unapproved as
confirmatory external tests because the base study used both development
datasets and endpoint/coding equivalence is not established.

## What the project has achieved

- Fit one predictor on multiple source cohorts and score held-out datasets.
- Freeze preprocessing, source-only calibration, and OOD thresholds before
  using external labels.
- Save provenance, hashes, splits, predictions, probability scores, OOD scores,
  uncertainty intervals, and machine-readable metrics.
- Complete and reproduce one source-distinct external evaluation with an
  endpoint aligned to the training outcome.
- Preserve weak and inconclusive results instead of tuning on the external
  cohort.

The requested workflow is implemented and empirically exercised as a
research prototype. The evidence does **not** show dependable calibration or
OOD rejection: AngioCAD calibration remains poor, and OOD AUROC is only 0.589.
No new prediction algorithm is claimed.

## Next confirmatory gate

Replicate the locked protocol across additional independent hospitals or a
prospective cohort, with sufficient negative cases, patient-level linkage or a
documented overlap procedure, and a stable definition of the endpoint. Improve
calibration and OOD detection using source-only development and validate any
new methods on a still-unseen cohort. Do not use AngioCAD or Z-Alizadeh Sani
labels for further model selection.
