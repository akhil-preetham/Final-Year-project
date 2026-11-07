# Generalization-aware cardiovascular prediction under dataset shift

**Study:** `CD-XD-002`  
**Status:** exploratory retrospective leave-one-source-out pilot completed  
**Clinical status:** research prototype; not clinically validated  
**Protocol:** [TRANSFER_STUDY_PROTOCOL_20261105.md](TRANSFER_STUDY_PROTOCOL_20261105.md)

## Did the experiment match the proposed design?

**At the run level, yes:** each outer fold trained on three source cohorts and
held out the fourth complete cohort. Probability calibration and the OOD alert
threshold were fit using source data only. The target cohort did not contribute
to preprocessing, predictor fitting, calibration, or threshold selection.

**As independent external validation, no:** the four UCI cohorts are already
represented in the project's historical `heart5.csv` composite, which was used
in earlier project experiments. The held-out cohorts were unseen to their
corresponding model fits, but not to the project as a whole. UCI describes this
release as four databases (Cleveland, Hungary, Switzerland, and VA Long Beach)
and defines the `num` endpoint as angiographic heart-disease presence/absence.
[UCI Heart Disease dataset and documentation](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease)

The result is useful feasibility evidence for the pipeline, not a claim of
generalization to a new health system or population.

## Main results

The model was fixed logistic regression. The primary data policy treats zero
cholesterol and zero resting blood pressure as missing; the sensitivity run
keeps those zero values. All values below are per held-out cohort, not pooled.
Intervals are class-stratified bootstrap 95% intervals with 1,000 resamples.

![Per-cohort transfer, calibration, and OOD results](../results/transfer_20261105_lodo_final/transfer_summary.png)

| Held-out cohort | N (negative / positive) | ROC-AUC (95% CI) | Brier: raw → calibrated | Calibrated ECE | OOD AUROC (95% CI) | OOD flagged / coverage |
|---|---:|---:|---:|---:|---:|---:|
| Cleveland | 303 (164 / 139) | 0.855 (0.813–0.894) | 0.212 → 0.157 | 0.061 | 0.980 (0.968–0.991) | 86.8% / 13.2% |
| Hungary | 294 (188 / 106) | 0.854 (0.806–0.895) | 0.245 → 0.203 | 0.231 | 0.515 (0.454–0.577) | 2.4% / 97.6% |
| Switzerland | 123 (8 / 115) | 0.720 (0.552–0.879) | 0.167 → 0.122 | 0.183 | 0.852 (0.809–0.892) | 37.4% / 62.6% |
| VA Long Beach | 200 (51 / 149) | 0.613 (0.513–0.707) | 0.184 → 0.198 | 0.133 | 0.685 (0.628–0.737) | 15.5% / 84.5% |

### Descriptive macro-average across the four cohorts

- ROC-AUC: **0.760** (site range 0.613–0.855); average precision: **0.857**.
- Mean Brier score improved from **0.202** before calibration to **0.170**
  after source-only Platt calibration. It improved in three cohorts and worsened
  in VA Long Beach. ROC-AUC did not change, as expected for a monotone
  calibrator.
- Calibrated expected calibration error averaged **0.152** and ranged from
  **0.061 to 0.231**. The held-out probabilities therefore remain unevenly
  calibrated despite the average Brier improvement.
- OOD-score AUROC averaged **0.758**, but ranged from **0.515 to 0.980**.
  At the source-calibrated nominal 5% alert threshold, the target alert rate
  ranged from **2.4% to 86.8%**. The detector does not yet provide a reliable,
  consistent “outside validated conditions” gate across these cohorts.
- The observed weighted false-alert rate on source calibration rows was
  **4.9%–5.6%** across outer folds, close to the locked 5% target.
- OOD flags did not consistently isolate poorly performing predictions. The
  calibrated Brier score among flagged versus accepted cases was 0.160 vs
  0.136 in Cleveland, 0.198 vs 0.203 in Hungary (only 7 cases were flagged),
  0.148 vs 0.107 in Switzerland, and 0.226 vs 0.192 in VA Long Beach. Ranking
  and calibration behavior also differed by site. These post-hoc subsets do
  not establish a stable selective-risk benefit.

The Switzerland cohort has only eight negative examples. Its metrics and
confidence interval are consequently imprecise. The bootstrap intervals
condition on the observed class counts and do not estimate uncertainty across
health systems.

## Zero-value sensitivity

When zero cholesterol and blood-pressure values are retained, macro ROC-AUC is
**0.745**, calibrated Brier score **0.186**, calibrated ECE **0.178**, OOD AUROC
**0.747**, and the mean target alert rate **34.2%**. The primary values are
0.760, 0.170, 0.152, 0.758, and 35.5%, respectively. The qualitative result is
unchanged: transfer varies substantially by site, and OOD detection is not
consistent enough to be used as a dependable abstention policy.

## Interpretation and novelty

This experiment demonstrates a working multi-source, dataset-level holdout
pipeline with source-only probability calibration and an explicit source-only
OOD threshold. The empirical finding is **heterogeneous transfer**: the
predictor ranks Cleveland and Hungary reasonably well, drops on VA Long Beach,
and has wide uncertainty on Switzerland. Calibration helps average Brier score
but does not resolve site-level reliability. The OOD detector distinguishes
some held-out domains well and is near chance on Hungary.

The current implementation combines established components—logistic
regression, Platt calibration, and Isolation Forest. It does **not** establish
algorithmic novelty. A defensible future contribution could be a rigorously
evaluated reliability policy that reports when prediction should be withheld,
but this pilot does not yet show a stable policy or a novel method. A broader
literature review and a new independent cohort are required before making a
novelty or generalization claim. A targeted search already found close prior
work: a 2026 uncertainty-aware heart-disease ensemble reports leave-one-center-
out evaluation across four clinical sites, and the 2026 CardioMeta preprint
studies calibrated multi-source CVD status prediction across NHANES and
MIMIC-IV. Those studies make the broad “uncertainty + multi-site CVD shift”
combination insufficient as a novelty claim. The remaining candidate is a
specific, transparent evaluation of source-only calibration and prespecified
OOD refusal behavior on independent compatible cohorts; the present cohort
reuse and inconsistent OOD results do not establish that contribution.

Sources: [UAFE heart-disease ensemble](https://pmc.ncbi.nlm.nih.gov/articles/PMC13106842/),
[CardioMeta preprint](https://arxiv.org/abs/2607.15721), and the [AHA scientific
statement on CVD prediction-model validation](https://pmc.ncbi.nlm.nih.gov/articles/PMC13067998/).
An earlier health-data reject-option study also explicitly combines OOD
detection and abstention under dataset shift
([ODROP](https://arxiv.org/abs/2405.19864)).

## Limitations and next required evidence

1. **Prior project exposure:** all four domains are represented in the earlier
   Heart5 composite. This study is retrospective and exploratory.
2. **Small number of domains:** four legacy cohorts are not enough to estimate
   variation across the wider range of hospitals and contemporary populations.
3. **Case-mix and sampling:** the Switzerland cohort has only 8 negative cases;
   its observed prevalence does not support a population calibration claim.
4. **OOD alert inconsistency:** the same source-calibrated policy alerted on
   2.4% to 86.8% of target cases. This is unsuitable as a clinical refusal rule.
5. **Endpoint and measurement age:** the task uses an angiographic diagnosis
   from a legacy dataset release, not prospective general-population CVD risk.
6. **Needed next:** freeze a compatible dataset from patients and a site not
   previously used in this project, verify the label and feature definitions,
   then perform a one-way evaluation. Credentialed BioLINCC or institutional
   data may be candidates, but availability and approvals must be established
   before analysis.

## Reproducibility artifacts

- Frozen protocol: `docs/TRANSFER_STUDY_PROTOCOL_20261105.md`.
- Runner: `experiments/run_lodo_transfer.py`.
- Plot generator: `experiments/plot_lodo_transfer.py`.
- Final run manifest, fold-level results, and row predictions:
  `results/transfer_20261105_lodo_final/run_manifest.json` and
  `results/transfer_20261105_lodo_final/outer_predictions.csv`.
- Figure: `results/transfer_20261105_lodo_final/transfer_summary.png`.
- UCI source archive: `data/external/uci_heart_disease_45/heart_disease.zip`.
- Archive SHA-256:
  `b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc`.
- Run manifest records the frozen protocol hash, runner hash, source-member
  hashes, split indices, dependency versions, and run timestamp.

UCI dataset attribution: Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano,
R. (1989). *Heart Disease*. UCI Machine Learning Repository, DOI
[`10.24432/C52P4X`](https://doi.org/10.24432/C52P4X), licensed CC BY 4.0.

## Run commands

```powershell
.\.venv\Scripts\python.exe experiments\run_lodo_transfer.py
.\.venv\Scripts\python.exe experiments\plot_lodo_transfer.py
```
