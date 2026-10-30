# Calibration and selective-prediction report

The tuned generic benchmark reports Brier score and ten-bin uniform ECE. The
best ECE in that run was LightGBM (0.00948), while CatBoost had the best Brier
score (0.18082). XGBoost had ECE 0.01075 and Brier 0.18098. These differences
are descriptive and do not establish a universally best calibration method.

The CARDIODIAG linkage artifacts additionally report confidence-error AUC,
AURC, full-coverage risk, conformal coverage, and ECE for corrected OSEC
versus stable OSEC. On heart5, the stable-minus-corrected differences were
ROC-AUC +0.00005, AURC +0.00063, full-coverage risk -0.00087, and ECE
-0.01150; all corresponding descriptive intervals included zero. On Mendeley,
ROC-AUC was -0.00026, AURC +0.00018, full-coverage risk +0.00080, and ECE
-0.01240; these mixed results do not support a consistent advantage.

The existing linkage implementation uses a valid calibration split and
evaluation split. Conformal coverage is conditional on its exchangeability
assumption and is not a guarantee under dataset shift. ECE is binning
sensitive. No clinical threshold, safety, or deployment claim is made.
