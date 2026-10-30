# CARDIODIAG novelty and gap matrix

**Assessment date:** 2026-10-27  
**Interpretation:** “novelty” here means a contribution distinguishable from
the cited literature, not merely a feature absent from this repository.

| Candidate or existing method | Closest established approach | What CARDIODIAG adds or tests | Contribution class | Evidence needed | Current status |
|---|---|---|---|---|---|
| Historical XAIH-DRC + OVEC/OSEC | XAI-guided feature reduction and standard ensemble learning; the base CARDIODIAG paper | Original application and implementation history | Existing application/method combination | Faithful code-to-paper mapping | Historical approximation only; not new here |
| Corrected fold-local pipeline | Nested validation, leakage-control, and model-selection literature | Re-evaluates the CARDIODIAG workflow with training-only transformations | Methodological correction | Common outer folds, inner selection, leakage tests, historical-vs-corrected separation | Implemented; essential validity control, not algorithmic novelty |
| One-shot correlation/permutation selector | Filter selection and model-based permutation importance | Comparator for a matched stability experiment | Established baseline | Prespecified feature universe and repeated perturbations | Implemented, but relevance estimator needed a held-out training partition |
| Stable XAIH-DRC approximation | Nogueira stability statistic and resampling-based selection | Applies a training-only resampled relevance rule to CARDIODIAG’s feature-reduction question | New combination / empirical extension, not a new theory | Explicit schema, held-out relevance, threshold freeze, ablations, paired stability intervals | Primary candidate; claims deliberately provisional |
| Nogueira chance-corrected stability | Nogueira et al. 2018 | Uses the published statistic for comparison | Established method | Correct feature universe and uncertainty description | Implemented; not novel by itself |
| Calibration-aware model choice | Calibration literature and multi-objective model selection | Could select among CARDIODIAG candidates using a prespecified reliability endpoint | Protocol extension | Inner calibration objective, discrimination guardrail, multiplicity and paired outer evaluation | Candidate B; not selected as primary |
| Split-conformal prediction sets | Angelopoulos and Bates 2023 and clinical conformal work | Adds an abstention/prediction-set layer to internal CARDIODIAG evaluation | Established method applied to this benchmark | Separate fit/calibration/evaluation data and shift stress tests | Complementary reliability layer; not novel by itself |
| Stability–reliability linkage | Literature usually reports feature stability and prediction reliability separately | Tests whether more stable selected sets predict better discrimination, calibration, confidence ranking, or risk coverage on matched splits | Empirical research question / negative or mixed finding | Paired repeated splits, dependence-aware interpretation, replication | Current strongest defensible claim; internal and dataset-conditional |
| Distribution-shift stress tests | External validation and transportability literature | Measures degradation under prespecified perturbations | Empirical robustness study | Frozen perturbation plan, no target-label tuning, external cohort where possible | High-value complementary opportunity; synthetic tests are not external validation |
| Independent external validation | Cardiovascular external-validation literature | Would test transportability of the frozen pipeline | Validation evidence, not algorithmic novelty | Frozen independent compatible cohort, provenance, hash, one-way evaluation | Blocked: no eligible frozen cohort |

## Recommended claim taxonomy

1. **Genuinely new algorithmic contribution:** not established by the present
   evidence. The selector is an operational combination of known relevance and
   stability ideas.
2. **New combination of established methods:** plausible for the matched
   stability–reliability audit, but must be framed as an empirical protocol and
   bounded to these datasets.
3. **Methodological correction:** clearly supported for fold-local preprocessing,
   nested selection, explicit external gating, and separation of historical from
   corrected results.
4. **Useful empirical finding:** supported provisionally by the mixed result
   that selected-set stability did not consistently translate into reliability.
5. **Engineering improvement:** reproducible runners, manifests, tests, and
   generated tables improve traceability but are not scientific novelty.

## Decision rule

The manuscript may use “novel” only for a narrower, literature-supported gap
that survives the completed review. Until then, use “leakage-controlled empirical
audit,” “methodological correction,” “mixed internal evidence,” and
“dataset-conditional finding.”
