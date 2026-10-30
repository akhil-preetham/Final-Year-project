# Limitations and unresolved issues

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
- No independent external validation, prospective validation, clinical utility,
  fairness, or deployment-readiness claim is supported.
- The worktree was dirty, so Git HEAD alone does not capture the full source
  snapshot.
- The tuned JSON artifact was generated before optional booster versions were
  added to the shared provenance helper; its non-destructive provenance
  sidecar records LightGBM 4.7.0 and CatBoost 1.2.10.
- LaTeX compilation was not available or performed in this phase.
