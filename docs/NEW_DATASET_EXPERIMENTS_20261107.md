# New public clinical dataset experiments

**Run date:** 2026-11-07

**Status:** exploratory nested internal validation; not clinical validation and not CARDIODIAG CAD external validation.

## Data sources and task definitions

Both datasets were downloaded from their official UCI repository records, which state CC BY 4.0 and permit reuse/adaptation with attribution. Source files remain local under ignored `data/external/`; the data-free project release contains neither raw rows nor prepared person-level CSVs. Exact source hashes, DOI/version and credits are recorded in [`data/manifests/`](../data/manifests/). The source license does not replace any institutional or journal ethics determination that may apply.

| Source | Records and predictors | Target used here | Predictor-time and data handling |
|---|---:|---|---|
| [UCI Heart Failure Clinical Records, ID 519](https://archive.ics.uci.edu/dataset/519/heart%2Bfailure%2Bclinical%2Brecords), DOI `10.24432/C5Z89R` | 299 records; 11 predictors after excluding `time` | `death_event`: death recorded by the end of the available follow-up (96 positive, 203 negative) | Follow-up duration ranges from 4 to 285 days and is not used as an input. The source does not define one common prediction horizon, so this is binary event classification rather than a time-to-event model. |
| [UCI Myocardial Infarction Complications, ID 579](https://archive.ics.uci.edu/dataset/579/myocardial%2Binfarction%2Bcomplications), DOI `10.24432/C53P5M` | 1,700 records; 100 admission-time predictors | `any_lethal_outcome = (LET_IS > 0)` (271 positive, 1,429 negative) | Follows UCI's hospital-admission input list and removes later-observed columns 93–95 and 100–105, record ID, all 12 source outcome fields, and contemporaneous cardiogenic-shock/pulmonary-edema proxy fields. Categorical-coded features are encoded as categorical inputs. Prepared predictors contain 15,200 missing cells; fold-trained imputation is used. |

The myocardial-infarction target is any of seven recorded lethal causes. The UCI record does not define a single outcome horizon and notes that its record ID cannot be linked to a participant. Cross-validation therefore splits records, not verified patients; duplicate persons cannot be ruled out and could make estimates optimistic. The predictors are not treated as a CAD endpoint or as validation for CARDIODIAG.

## Evaluation protocol

Each task was analyzed independently. The candidate set was corrected logistic regression, the CARDIODIAG OVEC voting ensemble and the OSEC stacking ensemble. Model selection optimized ROC-AUC in three shuffled stratified inner folds. Performance was estimated with one five-fold shuffled stratified outer cross-validation at seed 42. Imputation, categorical encoding, outlier processing and model fitting were contained in the training pipeline. Hyperparameter tuning stayed within outer training folds.

All candidate families are reported; no model is selected as a winner from these results. Tables show mean and standard deviation across the five outer folds. The standard deviations describe fold variation and are not confidence intervals. Metrics are ROC-AUC, average precision (PR-AUC), Brier score and ten-bin uniform expected calibration error (ECE). Row-level labels, predictions and split indices were removed before saving the aggregate JSON outputs.

## Results

### Heart failure death event

| Model | ROC-AUC | Average precision | Brier | ECE |
|---|---:|---:|---:|---:|
| Corrected logistic regression | 0.718 ± 0.051 | 0.586 ± 0.133 | 0.213 ± 0.016 | 0.211 ± 0.034 |
| Corrected OVEC | 0.728 ± 0.059 | 0.568 ± 0.121 | 0.188 ± 0.021 | 0.182 ± 0.044 |
| Corrected OSEC | 0.711 ± 0.048 | 0.578 ± 0.061 | 0.220 ± 0.015 | 0.190 ± 0.043 |

Discrimination was modest across the three candidates. ECE values indicate material calibration error under this coarse diagnostic; these outputs should not be read as reliable individual risk probabilities.

### Myocardial-infarction lethal outcome

| Model | ROC-AUC | Average precision | Brier | ECE |
|---|---:|---:|---:|---:|
| Corrected logistic regression | 0.867 ± 0.017 | 0.584 ± 0.078 | 0.140 ± 0.008 | 0.251 ± 0.022 |
| Corrected OVEC | 0.884 ± 0.013 | 0.628 ± 0.052 | 0.092 ± 0.005 | 0.112 ± 0.020 |
| Corrected OSEC | 0.872 ± 0.023 | 0.626 ± 0.076 | 0.145 ± 0.015 | 0.236 ± 0.021 |

OVEC had the highest fold-mean discrimination and lowest fold-mean Brier/ECE in this run. This is descriptive, not evidence that it is statistically superior or clinically useful. Event prevalence is about 16%, and the other models' ECE values are high; calibration and clinical utility remain unestablished.

## Figures and reproducibility files

- ROC-AUC: [`new_dataset_roc_auc.pdf`](../results/new_datasets_20261107/figures/new_dataset_roc_auc.pdf) and PNG counterpart.
- Average precision: [`new_dataset_average_precision.pdf`](../results/new_datasets_20261107/figures/new_dataset_average_precision.pdf) and PNG counterpart.
- Aggregate metrics and provenance: `results/new_datasets_20261107/*_nested_metrics.json`.
- Preparation: [`experiments/prepare_new_public_datasets.py`](../experiments/prepare_new_public_datasets.py).
- Nested evaluation: [`experiments/run_new_public_dataset_nested.py`](../experiments/run_new_public_dataset_nested.py).
- Plot generation: [`experiments/plot_new_public_dataset_metrics.py`](../experiments/plot_new_public_dataset_metrics.py).
- Source notices: [`UCI_HEART_FAILURE_519.md`](../data/attribution/UCI_HEART_FAILURE_519.md) and [`UCI_MI_COMPLICATIONS_579.md`](../data/attribution/UCI_MI_COMPLICATIONS_579.md).

The separate six-page CARDIODIAG manuscript remains focused on its angiographic CAD task. These two datasets must not be added to its CAD validation sample or used to strengthen an external-generalization claim. Before any standalone publication, authors should verify the source citations, obtain the relevant institutional/journal ethics determination, and describe the no-common-horizon and calibration limitations.
