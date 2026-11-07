# CD-XD-004: endpoint-aligned AngioCAD external evaluation

**Study:** `CD-XD-004`  
**Protocol:** `docs/TRANSFER_STUDY_PROTOCOL_20261105_ANGIOCAD.md`  
**Status:** completed and reproduced  
**Claim boundary:** a research evaluation on one independent hospital cohort; not a clinically validated diagnostic system

## Result in brief

The locked four-source logistic model had moderate-to-good ranking performance
on the external AngioCAD cohort (ROC-AUC 0.787, 95% bootstrap interval
0.734–0.838). Source-only Platt calibration made small, uncertain improvements
to Brier score and log loss, while expected calibration error worsened slightly.
Predicted risks remained miscalibrated. The Isolation Forest gave weak
source-vs-target separation (AUROC 0.589, 95% interval 0.541–0.635), so this
prototype does **not** reliably recognize the target cohort as outside its
source operating conditions. The study supports the evaluation workflow; it
does not establish robust transport, dependable uncertainty, or clinical use.

## Cohort and endpoint

AngioCAD is reported as a 413-patient dataset from Shahid Chamran Heart Center
in Isfahan, Iran. The public release has separate clinical-feature and
artery-label workbooks. The label workbook contains 413 unique nonblank IDs,
while the feature workbook contains 377; all 377 feature IDs match a label ID,
leaving 36 labeled patients without clinical predictors. Each workbook also
contains two empty rows. We used the 377 matched cases and excluded the 36
cases with no feature row. Six matched patients lack age and 11 lack FBS;
missing values were imputed from source-fit data only. The matched cohort has
298 positives (79.0%) and 79 negatives.

The patient label was derived from 15 artery-segment annotations. A case was
positive if any segment was labeled `51-75`, `76-90`, `91-99`, or `100`; it was
negative if all segments were `NL`, `1-25`, or `26-50`. Positive bins start at
51%, matching the source `>50%` positive cut point. The negative `26-50` bin
includes the 50% boundary but does not preserve exact percentages within that
interval, so exact-50 cases cannot be isolated for a boundary sensitivity
analysis. The external site is distinct from the four source sites, although
public data do not permit person-level duplicate checks across datasets.

Only three common predictors were used: age in years, sex, and the binary
fasting-blood-sugar indicator `>120 mg/dL`. All other AngioCAD columns were
excluded, including its diagnosis, medication, other laboratory, and artery
fields. The AngioCAD workbook does not give an FBS unit; its numeric values
(55--514) are interpreted as mg/dL. This feature harmonization is an explicit
assumption. The UCI source cohorts are Cleveland, Hungary, Switzerland, and VA
Long Beach. Of 920 source records, 735 were used for fitting and 185 for
source-only calibration, with equal total weight per source cohort.

## Locked pipeline

The frozen model is logistic regression (`C=1`, `liblinear`) with age median
imputation and scaling, plus most-frequent imputation and one-hot encoding for
sex and FBS status. Platt scaling (`C=1e6`) was fitted only on the reserved
source calibration rows. A 300-tree Isolation Forest was fitted on source-fit
rows; its alert threshold was the weighted 95th percentile of source
calibration anomaly scores. No AngioCAD row or label entered any fitted
component or threshold. We used 1,000 class-stratified bootstrap resamples for
descriptive intervals; these intervals condition on this cohort's observed
class counts and do not estimate between-hospital variance.

## Predictive performance

| Metric | Raw model | Source Platt calibrated |
|---|---:|---:|
| ROC-AUC (95% interval) | 0.787 (0.734–0.838) | 0.787 (0.734–0.838) |
| Average precision (95% interval) | 0.932 (0.913–0.952) | 0.932 (0.913–0.952) |
| Brier score (95% interval) | 0.190 (0.184–0.196) | 0.185 (0.171–0.200) |
| Log loss (95% interval) | 0.569 (0.556–0.581) | 0.548 (0.516–0.580) |
| 10-bin ECE (95% interval) | 0.211 (0.203–0.232) | 0.216 (0.198–0.234) |
| Balanced accuracy at 0.5 | 0.630 | 0.719 |
| Sensitivity at 0.5 | 0.906 | 0.728 |
| Specificity at 0.5 | 0.354 | 0.709 |

The target event rate was 79.0%, while mean predicted risk was 58.3% raw and
57.4% after source-only calibration. Calibration intercept/slope were
0.339/4.146 raw and 1.219/1.436 calibrated, consistent with substantial
miscalibration after transfer. The unchanged AUC and average precision are
expected because a monotonic Platt transform preserves ranking. Average
precision is high in this positive-heavy cohort and should not be read without
the 79.0% prevalence.

A paired, class-stratified bootstrap compared calibrated with raw
probabilities. The Brier-score difference was −0.0047 (95% interval
−0.0133 to 0.0049), the log-loss difference was −0.0209 (−0.0415 to 0.0006),
and the ECE difference was +0.0051 (−0.0213 to 0.0164); negative favors the
calibrated value for each metric. All intervals include no change. The modest
point improvements in Brier score and log loss are therefore inconclusive,
and calibration error did not improve at the point estimate.

## OOD warning

| Quantity | Result |
|---|---:|
| Source calibration false-alert rate | 5.3% |
| AngioCAD alert rate | 11.7% (44/377) |
| AngioCAD accepted coverage | 88.3% (333/377) |
| Source-vs-AngioCAD OOD AUROC (95% interval) | 0.589 (0.541–0.635) |
| Accepted cases: calibrated Brier, n=333 | 0.179 |
| Flagged cases: calibrated Brier, n=44 | 0.233 |

The score distributions overlap substantially, and the OOD AUROC is too low
for a dependable shift warning. The flagged subset had a worse calibrated
Brier score in this cohort, but it is small and this descriptive difference
does not establish that the detector identifies unreliable individual
predictions. An unflagged case is not thereby shown to be reliable.

## Reproducibility and artifacts

The final run and a separate repeat produced byte-identical external and
source-calibration prediction CSVs. Independent recalculation of AUC, average
precision, Brier score, log loss, and ECE matched the run manifest to a maximum
absolute difference of `2.8e-17`. File hashes are saved in
`results/transfer_20261105_angiocad_external/reproducibility_check.json`.
After an initial execution, we clarified in the protocol that exact 50% values
cannot be isolated inside the target's `26-50` bin and that the FBS unit was
assumed from its value range. No labels, feature transformations, model
settings, thresholds, or outcomes changed; both final runs use the clarified
protocol and final data-manifest hashes.

Key artifacts:

- Frozen protocol: `docs/TRANSFER_STUDY_PROTOCOL_20261105_ANGIOCAD.md`
- Dataset manifest and checksums: `data/manifests/angiocad_external.json`
- Runner: `experiments/run_angiocad_transfer.py`
- Analysis and plotting: `experiments/analyze_angiocad_transfer.py`, `experiments/plot_angiocad_transfer.py`
- Predictions, run manifest, paired calibration analysis, and figure: `results/transfer_20261105_angiocad_external/`
- Repeat run: `results/transfer_20261105_angiocad_external_reproduction/`

Reproduce the primary run and supplementary summaries from the repository root:

```powershell
.\.venv\Scripts\python.exe experiments\run_angiocad_transfer.py
.\.venv\Scripts\python.exe experiments\analyze_angiocad_transfer.py
.\.venv\Scripts\python.exe experiments\plot_angiocad_transfer.py
.\.venv\Scripts\python.exe experiments\run_angiocad_transfer.py --output-dir results\transfer_20261105_angiocad_external_reproduction
```

Dataset files are attributed to the AngioCAD authors under the record's CC BY
4.0 license. See `LICENSE_AND_ATTRIBUTION.md` for the formal citation.

## Interpretation

This exact-endpoint external evaluation closes the dataset-eligibility gap for
the proposed research prototype. It does not show that the current model is
well calibrated or that the OOD mechanism reliably recognizes dataset shift.
The defensible project contribution is an auditable, reproducible evaluation
of multi-source transfer, source-only uncertainty calibration, and OOD
warning under dataset shift, together with clear evidence that these
reliability components remain inadequate on an unseen site. No new prediction
algorithm is claimed.

The result is limited to a single angiography-referred Iranian cohort, 377
matched records, three harmonized predictors, a high target prevalence, and
bootstrap intervals conditional on the observed labels. Prospective,
multi-hospital, person-level linkage-safe validation and improved shift
warning methods remain future work.
