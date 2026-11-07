# CD-XD-003: independent-cohort transport stress test

**Run date:** 2026-11-05  
**Protocol:** [`TRANSFER_STUDY_PROTOCOL_20261105_ZAS.md`](TRANSFER_STUDY_PROTOCOL_20261105_ZAS.md)  
**Status:** completed source-distinct external-cohort transport stress test; not
endpoint-identical validation  
**Use boundary:** research only; not a clinical diagnostic system

## Question and result in brief

The project now has a locked experiment that trains on four source datasets,
calibrates probabilities and sets an OOD threshold using source-only data, then
scores a cohort from a separate hospital once. This completes the intended
workflow for **multi-source training, one-way cohort transfer, source-only
calibration, and an OOD warning**.

The test cohort is the UCI Z-Alizadeh Sani dataset, reported as 303 patients
from Shahid Rajaei Cardiovascular, Medical, and Research Center in Tehran. The
four training cohorts are Cleveland, Hungary, Switzerland, and VA Long Beach.
The source and target are geographically and institutionally distinct, but
the diagnosis thresholds differ at exactly 50% stenosis: the source defines
positive as `>50%`, while the target defines CAD as `>=50%`. There are no
stenosis percentages in the public file to harmonize this boundary. The result
must therefore be described as an **external-cohort transport stress test**,
not endpoint-identical external validation. [UCI Z-Alizadeh Sani](https://archive.ics.uci.edu/dataset/412/z%2Balizadeh%2Bsani),
[original cohort paper](https://www.sciencedirect.com/science/article/abs/pii/S0169260713000801),
[UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease).

On this cohort, ROC-AUC was **0.720** (class-stratified bootstrap 95% CI
0.651–0.780). Source-only Platt calibration moved Brier score from 0.200 to
0.193 and ECE from 0.136 to 0.110, but the paired bootstrap intervals for
these changes included no difference. The OOD detector separated source
calibration rows from target rows weakly (AUROC 0.604, 95% CI 0.552–0.652).
It flagged 14.9% of the target cohort at a 5.3% source false-alert rate.
Flagged target rows had worse Brier score than accepted rows (0.238 vs 0.185),
but only five of the 45 flagged rows were negative, so the subgroup estimate
is imprecise. These results support continued study of reliability under
shift, but **do not establish dependable calibration or a safe reject rule**.

## Frozen data and feature map

The target archive is `data/external/uci_z_alizadeh_sani_412/z_alizadeh_sani.zip`
(SHA-256 `48210a6623fa6112423d9bc357f72fe3fca12ae77866e63e08632e15d95b724e`).
The workbook SHA-256 is
`90fefd4ecdb6263b3f2a260bb2b5d3b9fa92ba35d626dd56ad8c6db5fbbad163`. The UCI
record says the dataset has 54 features, but the frozen workbook contains 55
predictor columns plus `Cath` (56 columns total); the discrepancy is recorded
and no undocumented fields are used.

The protocol uses only three harmonized predictors:

| Source field | Z-Alizadeh Sani field | Frozen mapping |
|---|---|---|
| `age` | `Age` | Years, numeric |
| `sex` | `Sex` | `1=male`, `0=female`; raw `Male` maps to 1 and the workbook's `Fmale` spelling maps to 0 |
| `fbs` | `FBS` | Binary fasting glucose `>120 mg/dL`; same strict cutoff in both datasets |

The target has 216 CAD and 87 Normal rows and no missing cells. Other predictors
were omitted because their measurement definitions were not established as
equivalent. The source cohorts sum to 920 records; 735 were used for model/OOD
fitting and 185 for source-only calibration and the OOD threshold.

## Locked method

- One equal-domain-weighted logistic regression (`C=1`, `liblinear`) trained
  on all four source cohorts; no class weighting or tuning.
- Separate stratified 80/20 fit/calibration split within each source cohort,
  with recorded fixed seeds.
- Source-fit-only median imputation and standardization for age; most-frequent
  imputation and one-hot encoding for sex and FBS status.
- Source-only Platt scaling (`C=1e6`) using source calibration rows.
- Isolation Forest fitted only to transformed source-fit rows; threshold set
  to the equal-domain-weighted 95th percentile of source calibration anomaly
  scores.
- Target labels were first used for the final evaluation metrics. No target
  label influenced feature mapping, imputation, fitting, calibration, or OOD
  threshold selection.
- 1,000 class-stratified bootstrap samples provide descriptive intervals that
  condition on the observed target class counts.

The post-run paired bootstrap on saved target predictions is supplemental and
was not used to choose a model. Negative differences favor calibrated
probabilities.

## Predictive and calibration results

| Metric | Raw probability | Source-Platt probability |
|---|---:|---:|
| ROC-AUC (95% CI) | 0.720 (0.651–0.780) | 0.720 (0.651–0.780) |
| Average precision (95% CI) | 0.853 (0.807–0.894) | 0.853 (0.807–0.894) |
| Brier score (95% CI) | 0.200 (0.192–0.208) | 0.193 (0.174–0.213) |
| Log loss (95% CI) | 0.590 (0.573–0.607) | 0.569 (0.526–0.616) |
| ECE, 10 fixed bins (95% CI) | 0.136 (0.115–0.172) | 0.110 (0.097–0.154) |
| Accuracy at fixed 0.5 | 0.739 | 0.700 |
| Balanced accuracy at fixed 0.5 | 0.601 | 0.631 |
| Sensitivity at fixed 0.5 | 0.926 | 0.792 |
| Specificity at fixed 0.5 | 0.276 | 0.471 |

The calibration transform is monotonic, so ranking measures did not change.
The supplemental paired bootstrap gave calibrated-minus-raw Brier difference
`-0.0071` (95% CI `-0.0185 to 0.0038`), log-loss difference `-0.0206`
(`-0.0486 to 0.0098`), and ECE difference `-0.0262` (`-0.0613 to 0.0220`).
All three intervals include zero. This is a modest point-estimate improvement,
not evidence of a conclusive calibration gain.

The frozen runner was executed a second time into a separate output directory.
Both the 303-row external prediction CSV and 185-row source-calibration CSV
were byte-identical, with maximum numeric difference zero. The hashes and
comparison are saved in
`results/transfer_20261105_zas_external/reproducibility_check.json`.

At the fixed 0.5 cutoff, calibration lowered sensitivity and accuracy while
raising specificity and balanced accuracy. The cutoff was not optimized, and
no decision-utility or clinical-threshold claim is made. On the target labels,
the raw and calibrated calibration slopes were 2.50 and 0.87, respectively;
the calibrated intercept was 0.60. The source-fitted Platt intercept and slope
were -0.61 and 2.89.

## Dataset shift and OOD results

| Cohort | Positive rate | Mean age | Male share | FBS >120 mg/dL share |
|---|---:|---:|---:|---:|
| Cleveland | 45.9% | 54.4 | 68.0% | 14.9% |
| Hungary | 36.1% | 47.8 | 72.4% | 6.8% |
| Switzerland | 93.5% | 55.3 | 91.9% | 4.1% |
| VA Long Beach | 74.5% | 59.4 | 97.0% | 34.0% |
| Z-Alizadeh Sani target | 71.3% | 58.9 | 58.1% | 29.0% |

The target differs especially in sex distribution and glucose prevalence from
most sources; it also has a higher positive rate than the pooled source sample
(55.3%). This provides an observed covariate/prevalence-shift setting for the
three-feature model.

| OOD result | Estimate |
|---|---:|
| Source calibration false-alert rate at frozen threshold | 5.3% |
| Target alert rate | 14.9% (45/303) |
| Target coverage after OOD flags | 85.1% (258/303) |
| Source-vs-target OOD AUROC (95% CI) | 0.604 (0.552–0.652) |
| Calibrated Brier, accepted target rows | 0.185 (n=258) |
| Calibrated Brier, flagged target rows | 0.238 (n=45; 5 negative, 40 positive) |

The detector provides weak evidence that this cohort differs from the source
calibration mixture. The higher error among flagged records is compatible with
the intended warning behavior in this one cohort, but flagging does not
identify all errors and the subgroup is small. OOD AUROC and alert rate do not
measure clinical safety.

## Reproducible artifacts

- Frozen protocol: `docs/TRANSFER_STUDY_PROTOCOL_20261105_ZAS.md`
- Dataset manifest: `data/manifests/uci_z_alizadeh_sani_external.json`
- Runner: `experiments/run_external_transfer.py`
- Supplemental paired analysis: `experiments/analyze_external_transfer.py`
- Figure generator: `experiments/plot_external_transfer.py`
- Run manifest, exact split indices, hashes, software versions, and metrics:
  `results/transfer_20261105_zas_external/run_manifest.json`
- Per-row held-out predictions and OOD decisions:
  `results/transfer_20261105_zas_external/external_predictions.csv`
- Source-calibration predictions:
  `results/transfer_20261105_zas_external/source_calibration_predictions.csv`
- Paired calibration differences:
  `results/transfer_20261105_zas_external/paired_calibration_differences.json`
- Exact repeat-run comparison:
  `results/transfer_20261105_zas_external/reproducibility_check.json`
- Figure:
  `results/transfer_20261105_zas_external/external_transfer_summary.png`

Re-run the locked fit with:

```powershell
.\.venv\Scripts\python.exe experiments\run_external_transfer.py
.\.venv\Scripts\python.exe experiments\analyze_external_transfer.py
.\.venv\Scripts\python.exe experiments\plot_external_transfer.py
```

## Interpretation and remaining evidence

The specified workflow is implemented and has been run on a genuinely
source-distinct hospital cohort. The results do **not** justify a claim of
strong generalization, reliably calibrated risk, or dependable OOD rejection.
The most supportable project contribution is currently an auditable
multi-source transfer and reliability evaluation, with mixed and limited
empirical results. Logistic regression, Platt scaling, and Isolation Forest
are established components; no algorithmic novelty is claimed.

This study itself has an endpoint boundary mismatch. A separate endpoint-
aligned follow-up on AngioCAD was completed as `CD-XD-004` and is reported in
`TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md`. That evaluation provides one
additional hospital site but still has limitations: only 377 of 413 labeled
IDs have feature rows, cross-dataset patient-level linkage is unavailable,
calibration remains poor, and OOD separation is weak. Multiple external
hospitals or a prospective cohort are still needed to estimate site-to-site
and temporal variation. All results are research evidence, not clinical
validation.
