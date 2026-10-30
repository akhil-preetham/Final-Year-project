# Final results and limitations

## Verified result

The primary generic benchmark is
`results/generated/kaggle70k_model_benchmark.json`, with tabular exports
`kaggle70k_model_summary.csv`, `kaggle70k_model_fold_metrics.csv`, and
`kaggle70k_model_timing.csv` under `results/generated/`.

XGBoost is the highest-ranked available standalone candidate by mean ROC-AUC:
0.80038. Its mean PR-AUC is 0.78561, Brier score is 0.18092, and ten-bin
uniform ECE is 0.01089. Its fold ROC-AUC values are 0.798112, 0.804051, and
0.798971. The corresponding sample standard deviation is approximately
0.00337; this describes the three shared folds and is not patient-level
uncertainty.

## CARDIODIAG findings

The corrected stability and linkage artifacts do not show a stable-selector
predictive or reliability advantage on the 70k benchmark. The custom nested
validation artifact was not completed because the reduced smoke run exceeded
six minutes without output. The generic model benchmark must not be used as a
replacement for corrected OVEC, OSEC, or StableXAIHDRC evidence.

## Calibration and uncertainty

The generic benchmark reports Brier score and ten-bin ECE. It does not contain
training-side Platt or isotonic calibration, conformal prediction,
risk-coverage curves, AURC, or error-detection analyses. No unsupported
calibration or selective-prediction figures are generated.

## Model availability

XGBoost and all scikit-learn candidates listed in the benchmark completed.
CatBoost, LightGBM, EBM, TabM, TabPFN, and TabICL were deferred because the
required packages or runtime support were unavailable. Their absence is a
coverage limitation, not negative evidence against those methods.

## Dataset and reproducibility limitations

The Kaggle license metadata remains `Unknown`. The worktree was dirty when the
benchmark ran, so Git HEAD does not identify the complete source snapshot.
The `cardio` target and schema differ from the existing datasets; this is not
valid external clinical validation. The three-fold comparison is a bounded
generic benchmark, not a complete final nested CARDIODIAG evaluation.

No manuscript claim is changed by this report.
