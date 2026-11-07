# Limitations and unresolved issues

> Historical status record. The current 2026-11-05 limitation dispositions and
> resolution steps are in `LIMITATION_RESOLUTION_MATRIX.md` and
> `REMAINING_WORK_REGISTER_20261105.md`; the current manuscript build is
> recorded in `QA_REPORT.md`.

- The three datasets have different schemas, targets, provenance, and likely
  collection processes. Their scores are not pooled.
- The Kaggle license metadata remains `Unknown`; redistribution and
  publication clearance are unresolved.
- Existing datasets were used during project development, so new results are
  exploratory/post-hoc rather than untouched confirmation.
- The full custom five-candidate nested Kaggle analysis was not completed.
- CatBoost's advantage over prior XGBoost is approximately 0.00005 pooled
  ROC-AUC and is not evidence of practical superiority.
- The uniform ensemble underperformed XGBoost.
- Fold/seed intervals are descriptive and do not represent independent
  patient uncertainty.
- ECE, AURC, conformal coverage, and confidence-error metrics have
  implementation and assumption limitations.
- AngioCAD supplies one endpoint-aligned source-distinct hospital evaluation
  (`CD-XD-004`) and a post-hoc reliability replay (`CD-XD-006`, AUC 0.790).
  The replay's combined automatic coverage is 5.6%; its weak feature-only OOD
  score and low utility do not establish useful transport. Fresh Duke ACATH
  (`CD-XD-005`) has AUC 0.661 but uses a >=75% rather than >50% endpoint, and
  has a 10.2% observed error rate among the 401 automatically classified
  records. Its results are a transport stress test, not endpoint-identical
  validation.
- All 270 UCI Statlog rows exactly match Cleveland after binary-target
  harmonization and were excluded as duplicate patients. No untouched,
  endpoint-compatible external cohort was verified in the screened public
  data.
- The worktree was dirty, so Git HEAD alone does not capture the full source
  snapshot.
- The tuned JSON artifact was generated before optional booster versions were
  added to the shared provenance helper; its non-destructive provenance
  sidecar records LightGBM 4.7.0 and CatBoost 1.2.10.
- The current manuscript compiles to a visually reviewed 12-page PDF at
  `output/pdf/CARDIODIAG_Domain_Shift_Manuscript_20261105.pdf`.
  Tectonic font fallback, Fontconfig, and underfull-box warnings remain; the
  draft still needs venue-specific proofing and project-team metadata.
