# Manuscript Submission Readiness Report

## Recommendation

**Do not submit the current manuscript to a journal yet.** It can serve as an
internal engineering-research draft after the revisions in this audit, but the
current evidence and unresolved metadata leave clear rejection paths.

## Reasons a reviewer could reject it

1. **The headline goal is not achieved.** AngioCAD feature-only OOD AUROC is
   0.580 for kNN and 0.579 for Isolation Forest in the frozen reliability
   replay; age/sex-only sensitivity is 0.544. These scores are weak domain
   separation and do not identify when a prediction is unreliable.
2. **Useful automatic coverage is not demonstrated.** The registered
   conformal+kNN policy covers 21/377 AngioCAD records (5.6%); all 21 are
   positive. The metadata registry gate emits no score for any unseen site.
3. **Calibration does not transport reliably.** The primary AngioCAD source
   calibrated ECE is 0.216; Duke Platt calibration worsened Brier from 0.216 to
   0.241 and ECE from 0.119 to 0.198.
4. **External evidence is insufficient.** Only one endpoint-aligned
   source-distinct cohort is available; Z-Alizadeh Sani and Duke use different
   threshold semantics. None is an untouched confirmatory target after the
   subsequent AngioCAD analyses.
5. **The evaluated AngioCAD cohort is selected by missingness.** Thirty-six of
   413 public label IDs have no feature row and the source does not explain
   why. Results apply to the 377 matchable records.
6. **Feature definitions remain incomplete.** AngioCAD FBS and age units are
   not stated in the feature workbook, and exact 50% stenosis cannot be
   isolated from the 26--50 bin.
7. **Mendeley's label and prediction time are unclear.** The public codebook
   does not define the diagnostic reference standard or field timing; some
   variables are test-derived or potentially outcome-proximal.
8. **Exact original-method reproduction is unavailable.** Conflicting
   notebooks, missing LoRAS settings, changing LIME/PCA logic, and unknown
   table lineage prevent a faithful numerical reproduction.
9. **The full factorial is not complete.** Separate experiments are not a
   shared-split A--L factorial, and no original A--L condition key was found.
10. **Submission declarations and venue are unresolved.** Author order,
    two coauthor contributions, institutional ethics determination, funding,
    competing interests, data-use terms, author approval, and journal selection
    remain pending.

## What is ready

- A source-only, leakage-controlled research prototype and reproducible
  execution artifacts.
- An honest negative transportability result and a tested fail-closed gate.
- A revised interpretation that does not claim clinical readiness, dependable
  unseen-site prediction, or a new prediction algorithm.
- A revised 14-page IEEE-style internal draft with the provenance, ablation,
  selective-policy evidence, explicit research `NO-GO`, extractable text on
  all pages, full-page inspection of dense sections, and a hash manifest. It
  is not venue-proofed or ready to submit.

## Minimum conditions before submission

- Freeze the claim as a reproducibility and transportability audit with
  negative reliability findings.
- Resolve author metadata and institutional ethics/data-use status; obtain
  funding and competing-interest declarations from all authors.
- Confirm distribution rights for every dataset-derived result to be shared.
- Select a journal and complete venue-specific formatting, reporting, and
  author-approval checks.
- If the paper claims external generalization beyond the examined cohorts,
  obtain a new untouched, endpoint-compatible, independently sourced cohort
  and run the frozen protocol once.

No amount of re-analysis of the same AngioCAD labels can make them a fresh
confirmation set. A journal may still consider a methods/reproducibility
audit, but acceptance cannot be guaranteed and the present submission verdict
is `NO-GO`.
