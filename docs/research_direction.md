# CARDIODIAG research-gap and contribution assessment

**Status:** literature-informed working assessment; novelty remains unverified until the final systematic search and experiments are complete.

## 1. Strongest gaps supported by the audit and literature

| Gap | Evidence currently available | Consequence for CARDIODIAG |
|---|---|---|
| Leakage-resistant development is not demonstrated | Local notebooks perform global outlier treatment, class-specific imputation, LoRAS, and PCA before splitting; the paper describes a leakage-controlled order but does not provide executable evidence for it. | Rebuild every data-dependent operation as a fold-local transformer and compare against the historical implementation. |
| External validation is not independent | The Five States file is a composite of public component datasets; Mendeley is the second dataset used in the original paper. | Treat both as development/replication evidence, not new external validation. Freeze an independent source before final model selection. |
| XAIH-DRC stability and interpretation are unresolved | The paper uses Pearson/LIME/Spearman thresholds and conditional PCA, but threshold estimation, fold-local fitting, PCA variance, and stability are underspecified. | A stability-aware, training-only XAI feature map is the most direct algorithmic target. |
| Calibration and uncertainty are under-validated | Calibration is reported, but the protocol and separation from evaluation data are unclear; at least one reported calibration slope indicates distortion. | Add prespecified calibration metrics and an uncertainty/abstention analysis without calling ensemble disagreement a probability of correctness. |
| Fairness evidence is incomplete | Subgroup performance is reported, but demographic coverage and fairness criteria are limited. | Report only supported subgroups, include calibration/error-rate breakdowns where sample sizes permit, and avoid broad fairness claims. |
| Generalization claims are stronger than the design | The paper uses two retrospective benchmarks and calls the result generalizable, while recent prediction-model guidance emphasizes transportability and independent validation. | Reframe the study around robustness/transportability, not clinical readiness. |

## 2. Recent and methodologically relevant sources to track

The following are verified starting points, not an exhaustive systematic review.

- Khan, Raza, and Nadeem (2026), the base CardioDiag paper, PeerJ Computer Science, DOI `10.7717/peerj-cs.4059`.
- Collins et al., TRIPOD+AI reporting guidance for prediction-model studies, official statement: `https://www.tripod-statement.org/`.
- Li et al. (2023), *Evaluating and mitigating bias in machine learning models for cardiovascular disease prediction*, Journal of Biomedical Informatics, DOI `10.1016/j.jbi.2023.104294`.
- Ueda et al. (2024), *Fairness of artificial intelligence in healthcare: review and recommendations*, Japanese Journal of Radiology, DOI `10.1007/s11604-023-01474-3`.
- Wenger et al. (2025), *External validation of an artificial intelligence model for predicting type 2 myocardial infarction*, European Heart Journal, DOI `10.1093/eurheartj/ehaf717`.
- Cao et al. (2025), *Interpretable conformal predictor for sepsis risk prediction*, Computer Methods and Programs in Biomedicine, DOI `10.1016/j.cmpb.2025.108587`.
- 2026 methodology papers on source-only transportability, external validation under temporal shift, and deployment-time calibration should be included in the final review; their conclusions are relevant to protocol design but do not by themselves establish a CARDIODIAG-specific gap.

## 3. Candidate contributions

### Candidate A — Leakage-controlled nested CARDIODIAG reproduction

**Definition:** Reimplement the original baseline using patient/group-aware splits, training-only preprocessing, fold-local imputation/outlier rules/feature selection/LoRAS/PCA, nested model selection, and a final untouched holdout.

**Strengths:** essential scientific control; directly tests whether reported gains survive proper evaluation; straightforward to justify.

**Weaknesses:** primarily a methodological correction, not by itself a new algorithm; requires careful historical-vs-corrected comparisons.

### Candidate B — Stability-aware, training-only XAIH-DRC

**Definition:** Replace one-shot global Pearson/LIME/Spearman decisions with a transformer fitted inside each training fold. Across inner resamples, estimate feature relevance and selection frequency; retain features only when relevance and direction are sufficiently stable. Apply a learned redundancy/PCA branch only from training data, with the retained-variance rule specified in advance.

**Strengths:** directly targets the paper's most distinctive but least reproducible component; improves resistance to sampling instability and feature-selection leakage; preserves an interpretable original-feature branch; supports stability figures and ablations.

**Weaknesses:** stability thresholds add tuning choices; LIME is computationally expensive; nominal categorical variables still require a principled representation; novelty must be checked against recent stability-selection and XAI-feature-selection literature.

### Candidate C — Calibrated selective CARDIODIAG under shift

**Definition:** Keep the corrected CARDIODIAG predictor fixed, then add a separately fitted calibration/uncertainty layer and an explicit abstention rule. Evaluate risk-versus-coverage, calibration, and external degradation under prevalence and covariate shift.

**Strengths:** directly addresses reliability and clinical decision relevance; can provide a useful “do not auto-classify” behavior; aligns with recent conformal/uncertainty work.

**Weaknesses:** conformal guarantees depend on exchangeability assumptions that may fail under external shift; calibration requires a dedicated calibration split; it is more of a prediction-policy contribution than an improvement to the CARDIODIAG representation itself.

### Candidate D — Domain adaptation or distribution-shift correction

**Definition:** Learn a source-to-target correction or reweighting strategy using an unlabeled or labelled target sample.

**Strengths:** directly targets transportability.

**Weaknesses:** high risk of tuning to the external set; needs a clearly independent target design and adequate sample size; can turn the external test into development data; not recommended as the first contribution.

## 4. Recommendation

**Primary direction:** Candidate B, implemented on top of Candidate A's leakage-controlled pipeline.

The recommended contribution is a **stability-aware, leakage-controlled XAIH-DRC extension**. The contribution should be defined mathematically before naming it. A provisional internal label is `LC-Stable-XAIH-DRC`; it is not a novelty claim.

The central hypothesis is:

> If XAI-guided feature reduction is estimated only from training data and retained only when its relevance is stable across resamples, then the resulting model will show smaller train-to-validation gaps, more stable explanations, and less performance/calibration degradation on independent data than the historical CARDIODIAG pipeline.

**Complementary direction, only if data and compute permit:** Candidate C, using a dedicated calibration split and a prespecified uncertainty/abstention analysis. It should be reported as a reliability layer, not as proof that uncertainty equals correctness.

## 5. Provisional mathematical definition

For a training fold \(D_{tr}\), generate \(B\) inner resamples. For feature \(j\), let \(r_{j,b}\) be the signed relevance score from the specified XAI/statistical procedure in resample \(b\), and let \(s_{j,b}\in\{0,1\}\) indicate whether it passes the training-only relevance rule. Define:

\[
\pi_j = \frac{1}{B}\sum_{b=1}^{B}s_{j,b},\qquad
\bar r_j = \frac{1}{B}\sum_{b=1}^{B}r_{j,b},\qquad
v_j = \operatorname{Var}(r_{j,1},\ldots,r_{j,B}).
\]

Retain original feature \(j\) when \(\pi_j\ge\pi_{min}\), \(|\bar r_j|\ge r_{min}\), and \(v_j\le v_{max}\). Estimate redundancy and any PCA mapping only on the selected training representation. The final pipeline is:

\[
X \xrightarrow{T_{tr}} X' \xrightarrow{S_{tr}} X_s \xrightarrow{R_{tr}} Z \xrightarrow{f_{tr}} \hat p(Y=1\mid X),
\]

where all operators are fitted on the relevant training data and then frozen for validation, holdout, and external inference.

This definition is intentionally provisional. The thresholds, score normalization, categorical handling, and whether the PCA branch is necessary must be selected by nested validation and documented before looking at the final external labels.

## 6. Evidence update: October 26, 2026

The contribution is now evaluated as a **stability--reliability decoupling
audit**, rather than as an assumed accuracy improvement. Repeated feature-set
comparisons use a one-shot relevance selector as a comparator and a
chance-corrected stability statistic. Paired linkage runs use the same
fit/calibration/evaluation splits to test whether selector stability predicts
ROC-AUC, calibration, confidence-error ranking, risk-coverage, or conformal
coverage.

The evidence is mixed: feature-set stability is positive on the Mendeley
benchmark but inconclusive on `heart5.csv`; confidence is empirically
informative on both internal benchmarks, but the stable selector is not
consistently better calibrated or better at selective ranking. Paired ROC-AUC
differences are approximately zero on both datasets. A literature review is
still required before describing the audit as a novel algorithm.
That caution is important because the October 25, 2026 search already found
recent cardiovascular work combining uncertainty-aware ensembles with
leave-one-center-out validation and recent clinical conformal selective-
prediction work under distribution shift. The defensible near-term claim is
therefore an auditable, dataset-specific evidence package unless a broader
review identifies a narrower unclaimed methodological gap.
