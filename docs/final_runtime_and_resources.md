# Runtime and resource report

The tuned six-model 70k run completed in the existing Windows virtual
environment with serial model fitting (`n_jobs=1`) and three outer/two inner
folds. Recorded model runtimes were approximately: Logistic 5.6 s, Random
Forest 227.3 s, HistGradientBoosting 51.3 s, XGBoost 33.4 s, LightGBM 16.5 s,
and CatBoost 48.2 s. Peak memory was not instrumented.

The full custom five-candidate Kaggle nested workflow remains infeasible under
the attempted budget; a reduced logistic pair was completed and labeled as
such. The small-dataset five-candidate nested runs and post-tuning linkage
runs completed.

Optional packages installed for the substantive run were LightGBM 4.7.0 and
CatBoost 1.2.10. EBM, TabM, TabPFN, and TabICL remain unavailable.
