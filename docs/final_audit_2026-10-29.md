# Final evidence audit — 2026-10-29

## Repository state

- HEAD: `e63b02c8a2aba6344a48025f657696fd99ac3a5f`
- Worktree: dirty before this audit; pre-existing deleted archives,
  `README.md` changes, untracked research package files, datasets, reports,
  results, and `catboost_info/` were preserved.
- No historical result was overwritten, staged, committed, pushed, or deleted.

## Current evidence classes

1. **Historical/native and schema-corrected artifacts:** retained for
   comparison only.
2. **Post-boundary-corrected CARDIODIAG artifacts:** corrected selector,
   stability, nested, and linkage evidence on the original two benchmarks.
3. **Kaggle 70k generic benchmark:** prior 11-model 3x2 benchmark.
4. **Post-tuning exploratory benchmark:** bounded six-model inner-CV tuning
   plus a fixed uniform OOF ensemble on shared outer folds.
5. **Custom validation:** original five-candidate nested runs on heart5 and
   Mendeley; reduced corrected-logistic versus stable-logistic Kaggle run.

## Protocol audit

All new model comparisons use fold-local `TrainingOnlyCleaner`,
`ColumnTransformer`, inner ROC-AUC selection, and identical stratified outer
folds. The ensemble uses fixed one-third weights and outer predictions
generated independently for each model; no outer labels select weights.

The custom selector remains distinct from the generic benchmark. The full
five-candidate Kaggle nested protocol was not completed because the earlier
reduced run exceeded six minutes without output. The reduced Kaggle pair is
explicitly labeled and is not substituted for the full protocol.

## Evidence conclusion

CatBoost's marginal pooled ROC-AUC difference over the prior XGBoost result is
descriptive and not a demonstrated practical or statistical improvement. The
uniform ensemble is worse than XGBoost. Stable selection does not show a
consistent predictive or reliability advantage. No external-validation or
clinical-utility claim is supported.
