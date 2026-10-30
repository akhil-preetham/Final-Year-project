# CARDIODIAG final project completion report

## Completion status

**Partially completed, with verified evidence and explicit blockers.**

The existing corrected selector, provenance system, Kaggle 70k integration,
stability/linkage analyses, generic 3x2 benchmark, bounded priority-model
tuning, and a prespecified OOF ensemble are preserved and audited. The full
five-candidate custom CARDIODIAG nested workflow on 70k remains infeasible
within the attempted runtime; a reduced corrected-logistic versus
stable-logistic comparison was completed instead. No unsupported completion is
claimed.

A compact candidate-pool experiment was subsequently completed on all three
datasets. It evaluated the requested linear, local, bagging, boosting,
probabilistic, and ensemble families with RBF SVM/KNN restricted to the two
small datasets for computational feasibility.

## Baseline and primary benchmark

The verified artifact is
`results/generated/kaggle70k_model_benchmark.json`. It contains 11 completed
models, 33 outer-fold evaluations, finite metrics, selected inner parameters,
timings, and truthful provenance. XGBoost leads the descriptive ranking with
mean ROC-AUC 0.80038, mean PR-AUC 0.78561, mean Brier 0.18092, and mean ECE
0.01089.

The benchmark uses seed 42, three outer folds, two inner folds, ROC-AUC
selection, and training-only preprocessing. Existing custom CARDIODIAG
artifacts remain separate evidence.

The new tuned artifact is
`results/generated/kaggle70k_tuned_priority_oof_ensemble.json`. CatBoost has
pooled outer ROC-AUC 0.80043 versus 0.80022 for XGBoost in the same run and
0.80038 for the prior baseline. The uniform XGBoost +
HistGradientBoosting + logistic OOF ensemble scored 0.79897 and therefore did
not improve XGBoost.

## Research and implementation decisions

The current environment provides XGBoost, scikit-learn, LightGBM 4.7.0, and
CatBoost 1.2.10. EBM, TabM, TabPFN, and TabICL remain unavailable. The fixed
OOF ensemble was evaluated with shared outer folds and did not improve the
best standalone model.

The compact-pool artifacts are
`kaggle70k_compact_candidate_pool.json`,
`heart5_compact_candidate_pool.json`, and
`mendeley_compact_candidate_pool.json`. On 70k, stacking scored 0.80028
pooled ROC-AUC, XGBoost 0.80008, CatBoost 0.79998, and fixed soft voting
0.79943 in this protocol. These are exploratory and are not pooled with the
earlier tuned artifact.

Custom nested validation completed for heart5 and Mendeley using the original
five candidates. A reduced Kaggle 70k pair completed for corrected logistic
versus stable logistic. Stability-reliability linkage completed on all three
datasets, with separate artifacts and no pooled target estimate.

## Quality assurance

Executed:

```text
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check src tests experiments
git diff --check
```

Results: the final full suite passed with 43 tests in 51.60 seconds; focused
tuned-runner tests passed; Ruff, `uv lock --check`, and diff checks passed.
Independent JSON validation confirmed the tuned models and all custom artifacts
contain provenance and finite reported metrics.

The reproducibility manifest now declares LightGBM and CatBoost, and `uv.lock`
was updated to resolve LightGBM 4.7.0 and CatBoost 1.2.10. LaTeX compilation
was checked but `pdflatex` is unavailable on this host.

## Remaining work

1. If desired, run a larger untouched tuning stage to assess whether the
   marginal CatBoost/XGBoost difference persists.
2. Profile and complete the full five-candidate custom 70k nested workflow,
   or retain the reduced pair as the explicit feasibility boundary.
3. Compile and reconcile the manuscript only after these results are reviewed.
   LaTeX compilation was not attempted in this step.

No source was staged, committed, pushed, published, or destructively removed.
