# Final methods and leakage control

## Generic model comparison

The 70,000-row `cardio` task uses three shared stratified outer folds, two
inner folds, seed 42, and ROC-AUC as the prespecified selection metric.
Cleaning, imputation, scaling, one-hot encoding, and model fitting are inside
each estimator pipeline. The outer fold is used only for final prediction.

The tuned artifact evaluates Logistic regression, Random Forest,
HistGradientBoosting, XGBoost, LightGBM, and CatBoost with bounded,
predeclared grids. Results are exploratory because the dataset and protocol
were already used for prior benchmark development.

## OOF ensemble

For each outer fold, each base model is tuned and fitted using only the outer
training rows. Its prediction is written only to that fold's held-out
positions. The reported ensemble is the arithmetic mean of XGBoost,
HistGradientBoosting, and Logistic predictions with fixed one-third weights.
No weights or members were optimized on outer-test labels.

## CARDIODIAG pipeline

Corrected OVEC, OSEC, logistic, and stable-selector pipelines preserve the
original research question. The StableXAIHDRC selector splits original
positional observations before bootstrap sampling, bootstraps only internal fit
positions, fits relevance models on those bootstrap samples, and evaluates
relevance on reserved internal validation observations. Outer test rows remain
outside selector fitting.

## Reliability

Linkage runs use fit, calibration, and evaluation fractions of 0.5625, 0.1875,
and 0.25. Calibration and conformal fitting use the calibration partition; the
evaluation partition is held out until prediction. ECE uses ten uniform bins.
Confidence-error AUC, AURC, selective risk, and conformal coverage are
empirical evaluation quantities, not clinical uncertainty guarantees.

## Statistical scope

Fold and seed summaries are dependent resampling measurements. Bootstrap
intervals in the artifacts are descriptive summaries, not independent-patient
confidence intervals. No multiplicity-adjusted confirmatory claim is made.
