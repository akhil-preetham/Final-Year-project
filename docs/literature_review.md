# CARDIODIAG literature review

**Review date:** 2026-10-27  
**Purpose:** source-verifiable methodological review used to choose the next
implementation and constrain novelty language.  
**Scope note:** this is a focused review of the methods that determine whether
the present CARDIODIAG evidence is valid. It is not a registered systematic
review or a claim of exhaustive database coverage.

## Source-backed conclusions

| Topic | Source | Relevant conclusion for CARDIODIAG |
|---|---|---|
| Feature-selection stability | Nogueira, Sechidis, Brown, *JMLR* 2018, 18:174, stable article/PDF: https://www.jmlr.org/papers/v18/17-514.html | Stability is a distinct property of a selector and should be quantified with a chance-corrected statistic; stability alone is not predictive validity. The current project is right to compare selected sets rather than report only one fitted ranking. |
| Stability selection | Meinshausen and Bühlmann, *Annals of Statistics* 2010, DOI: https://doi.org/10.1214/09-AOS687 | Resampling-based selection has formal error-control assumptions and tuning consequences. The CARDIODIAG selector does not reproduce their procedure or guarantees and must not use “stability selection” as if it did. |
| Selection bias and nested validation | Varma and Simon, *BMC Bioinformatics* 2006, DOI: https://doi.org/10.1186/1471-2105-7-91; Cawley and Talbot, *Neural Computation* 2010, DOI: https://doi.org/10.1162/NECO_a_00022 | Model-selection information must be isolated from performance estimation. The nested outer/inner design is necessary, but the current implementation must state which endpoint is selected and avoid using outer results to choose the contribution. |
| XAI/local explanations | Ribeiro, Singh, Guestrin, KDD 2016, DOI: https://doi.org/10.1145/2939672.2939778 | LIME explains a local surrogate under a perturbation distribution; it is not automatically a stable global feature selector. LIME settings, perturbations, and stability must be specified, and the current correlation/permutation approximation must be called an approximation. |
| Calibration | Van Calster et al., *BMC Medicine* 2019, DOI: https://doi.org/10.1186/s12916-019-1466-7; scikit-learn calibration documentation: https://scikit-learn.org/stable/modules/calibration.html | Discrimination and calibration measure different properties. Brier/ECE alone do not establish well-calibrated probabilities; calibration intercept and slope, curves, sample size, and a calibration protocol are required. The current calibration metrics are descriptive held-out metrics, not a calibration-aware selection result. |
| Prediction-model reporting | Collins et al., TRIPOD+AI, *BMJ* 2024, DOI: https://doi.org/10.1136/bmj-2023-078378; checklist: https://www.tripod-statement.org/ | Reporting should identify the target population, outcome, predictors, model development/evaluation boundary, missing-data handling, subgroup information, open-science materials, and limitations. The manuscript should be checked against the 27-item guidance. |
| Risk of bias and applicability | Moons et al., PROBAST+AI, *BMJ* 2025, DOI: https://doi.org/10.1136/bmj-2024-082505 | Model development quality and evaluation risk of bias are separate assessments. Data source, predictor measurement, outcome definition, and analysis must each be appraised. Public benchmark accuracy does not establish applicability. |
| Conformal prediction | Angelopoulos and Bates, *Foundations and Trends in Machine Learning* 2023, DOI: https://doi.org/10.1561/2200000101 | Split conformal prediction gives marginal finite-sample coverage under exchangeability with a correctly separated calibration sample. Coverage is not guaranteed under dataset shift and should be measured rather than assumed in an external cohort. |
| External validation | Wessler et al., *Circulation: Cardiovascular Quality and Outcomes* 2021, DOI: https://doi.org/10.1161/CIRCOUTCOMES.121.007858 | Cardiovascular models often lose performance outside development settings. A second public file is not automatically independent; source overlap, endpoint, setting, and measurement must be reviewed. |
| Discrimination comparison | DeLong, DeLong, Clarke-Pearson, *Biometrics* 1988, DOI: https://doi.org/10.2307/2531595 | Paired ROC-AUC comparisons require paired predictions on the same observations. The current results use common folds and bootstrap summaries; a confirmatory comparison should make the paired unit and multiplicity explicit. |
| Precision-recall interpretation | Saito and Rehmsmeier, *PLOS ONE* 2015, DOI: https://doi.org/10.1371/journal.pone.0118432 | PR-AUC is prevalence-dependent and should accompany, not replace, ROC-AUC. The project should report prevalence and avoid comparing PR-AUC across cohorts without context. |

## Implications for the four candidate directions

### A — Stability-aware XAIH-DRC

The gap is not “resampling plus feature selection”; that is established. The
credible CARDIODIAG-specific question is whether its distinctive XAI-guided
reduction remains reproducible after feature typing, fold-local preprocessing,
and held-out training-only relevance estimation, and whether selector stability
translates into held-out predictive reliability. This is a falsifiable empirical
question. It is not a new stability-selection theorem or a clinical explanation
guarantee.

Required controls:

- explicit nominal/ordinal/continuous feature schema;
- inner validation or out-of-bag relevance rather than in-sample permutation;
- matched transformed feature universe and identical perturbations for the
  stable and one-shot comparators;
- no outer-test labels for thresholds, selection, or contribution choice;
- feature-count and stability reporting alongside discrimination and calibration;
- a negative/inconclusive conclusion if stability does not improve reliability.

### B — Calibration-aware model selection

The literature clearly treats calibration as separate from discrimination, so a
prespecified multi-objective selection rule could be useful. However, selecting
weights for ROC-AUC, Brier score, and calibration slope introduces another
researcher degree of freedom and requires a dedicated calibration objective,
inner validation, and multiplicity control. With only two small benchmark files,
the likely contribution would be a protocol comparison rather than a robust new
method. It is a complementary ablation, not the primary direction.

### C — Uncertainty-aware selective prediction

Conformal sets and risk-coverage curves are established methods. The useful
CARDIODIAG result is a transparent reliability analysis under a separate
calibration split, with explicit exchangeability assumptions and stress tests.
It should be described as a prediction policy/evaluation layer. Confidence-error
AUC, ensemble disagreement, or internal conformal coverage must not be called
semantic uncertainty or deployment safety.

### D — Robustness under distribution shift

This is the most important unanswered practical question, but an honest
external-shift study requires a frozen compatible cohort with matched endpoint
and predictor definitions. Synthetic missingness/noise and covariate-shift
stress tests can be run now, but they are not external validation. Domain
adaptation would risk using target data for tuning and is not justified before an
independent cohort and an analysis plan are frozen.

## Novelty assessment

The literature supports the following restrained wording:

> This project performs a leakage-controlled, CARDIODIAG-specific empirical
> audit of whether feature-set stability is associated with predictive and
> selective reliability under matched internal perturbations.

The review does **not** support calling the current selector a novel algorithm,
calling conformal prediction novel, or calling the combination of XAI,
stability, and abstention novel without a broader systematic search. A mixed or
negative result is scientifically informative only as an empirical finding that
requires replication and careful scope.

## Search and evidence limitations

- The review used primary articles, journal/official pages, DOI records, and
  official software documentation available at the audit date.
- No claim of exhaustive PubMed, Scopus, Web of Science, or IEEE Xplore
  screening is made.
- Current cardiovascular applications should be searched again immediately
  before submission, especially work combining feature stability, uncertainty,
  calibration, and multi-site validation.
- The base CARDIODIAG article and its two local benchmark datasets are part of
  the project evidence, not independent confirmation of a new method.
