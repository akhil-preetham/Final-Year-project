# Reviewer-readiness audit

**Review date:** 2026-10-27  
**Reviewer stance:** skeptical journal reviewer; claims are checked against
source code and saved artifacts rather than project summaries.

| Issue | Severity | Evidence | Required correction | Resolution |
|---|---|---|---|---|
| Independent validation is absent | Critical | No frozen external manifest; Mendeley was used by the base study and Five States is a composite | State internal-only scope and do not claim transportability | Resolved in wording; external gate remains closed |
| Coded Mendeley categories were previously treated as numeric | High | Original pipeline inferred types from pandas dtype | Declare schema, one-hot encode categories, rerun sensitivity evidence | Addressed in `data.py`, preprocessing, manifests, and schema-corrected artifacts |
| Stable selector used in-sample permutation importance | High | Original `_combined_relevance` fit and evaluated on the same resample | Use an inner validation partition within each training resample | Addressed; full default rerun remains compute-limited |
| Historical reproduction is not exact | High | Colab paths, inconsistent notebook blocks, missing environment metadata | Label native historical run as an approximation and preserve it separately | Resolved in audit and baseline report |
| Primary endpoint was not calibration-aware | Moderate | Nested `GridSearchCV` selects ROC-AUC; calibration is reported afterward | Call it a discrimination-selected protocol; use a separate calibration-aware study only if prespecified | Resolved by narrowing claim; Candidate B deferred |
| Repeated-fold/seed intervals may understate dependence | High | Bootstrap functions resample fold/seed summaries as if independent | Describe as descriptive paired resampling intervals and avoid confirmatory p-value language | Partially resolved in documentation; a hierarchical analysis is still open |
| Multiple candidates/endpoints create multiplicity | Moderate | Five candidates and many metrics are reported | Prespecify primary ROC-AUC and label other metrics secondary/exploratory | Resolved in `docs/research_decision.md`; manuscript should retain this language |
| Calibration metric is bin-sensitive | Moderate | ECE uses ten uniform bins and can be unstable in small bins | Report binning rule, calibration curve, intercept/slope, Brier, and limitations | Implemented/documented; no universal calibration claim |
| Conformal coverage is assumed only under exchangeability | High | Split conformal is calibrated internally; no shift cohort exists | State exchangeability assumption and measure coverage under shift rather than assume it | Resolved for internal claims; external test unavailable |
| Confidence is not semantic uncertainty | Moderate | Confidence-error AUC and AURC are empirical rankings | Avoid “understands uncertainty,” clinical safety, or calibrated correctness language | Resolved in manuscript/docs |
| Feature selection may be unstable across feature encodings | Moderate | One-hot feature universe changes with schema and fold category availability | Record union feature universe and absent categories; report counts and selection frequencies | Addressed by runner; bounded post-correction stability is low-to-moderate |
| Existing result artifacts predate the correction | High | Old JSON files remain under original names | Do not silently replace them; identify schema-corrected prefix and regenerate final tables from it | Addressed; old and new artifacts are separate |
| Manuscript metadata and venue are incomplete | Moderate | Author fields are placeholders; target journal not selected | Obtain author, affiliation, funding, ethics/data-use statements, and journal instructions | Open human-input item |
| PDF compilation is unverified | Low | `pdflatex` is not available per handoff; no successful compile recorded | Run LaTeX in a compatible environment and retain log | Open environment item |
| Data licenses and source overlap constrain redistribution | High | Local Five States license is not supplied; Mendeley is CC BY 4.0 | Preserve attribution, verify component terms, and avoid claiming independent cohorts | Documented; licensing verification remains open |

## Overall verdict

The package is **methodologically improved and internally reproducible through
bounded sensitivity experiments**, but it is not ready for a clinical or
external-validation claim. The strongest publishable framing is a transparent
methodological correction plus a cautious, dataset-conditional empirical finding:
feature-set stability can improve under a training-only procedure without
reliably improving predictive or selective reliability.

## Remaining publication gates

1. Complete the full post-correction repeated/nested analysis if compute is
   available, without changing thresholds after seeing evaluation outcomes.
2. Expand the completed single-split perturbation stress test to repeated splits
   or provide a frozen independent compatible cohort.
3. Complete author, ethics/data-use, funding, and target-journal metadata.
4. Compile and visually inspect the IEEE manuscript.
5. Perform a final source-complete literature search before submission.
