# AURA-ML V2 specification and confirmatory protocol

## V2 decision rule

V1 ablations showed that feature selection did not consistently improve
performance, intelligence switches were often inactive, and fusion was useful
only on some heart5 folds. V2 therefore removes feature selection from the
frozen default policy while retaining adaptive representation, inner-only model
choice, optional reliability-gated fusion, and training-side calibration.

V2 candidates are original logistic regression, adaptive logistic regression,
adaptive HistGradientBoosting, adaptive CatBoost, and adaptive XGBoost. The
inner objective remains:

\[
U_j=0.60A_j+0.20\frac{P_j-\pi}{1-\pi}+0.10(1-B_j)+0.05(1-E_j)
      -0.10\,\mathrm{SD}(A_{j,\ell})-10^{-5}\log(1+t_j).
\]

Here \(A_j\), \(P_j\), \(B_j\), and \(E_j\) are inner out-of-fold ROC-AUC,
PR-AUC, Brier score, and ECE; \(\pi\) is training prevalence; and \(t_j\) is
training time. Fusion is retained only when its utility exceeds the strongest
single candidate by 0.002. These quantities are never computed from outer-test
labels.

## Calibration and threshold policy

V2 compares no calibration, sigmoid calibration, and isotonic calibration using
three-way cross-fitted inner predictions. A method is retained only when its
inner Brier score improves by at least \(10^{-4}\) over the uncalibrated
prediction. Calibration intercept and slope are reported on outer predictions
as diagnostics, not selection targets.

The default decision threshold is 0.5. V2 also selects a threshold from a
0.05--0.95 grid using inner cross-fitted balanced accuracy. Both the default
and validation-optimized outer metrics are reported. Outer labels are never
used to choose a threshold.

## Confirmatory protocol

V2 uses three outer folds, three inner folds, and seeds 42, 43, and 44 on the
two small development benchmarks. Baselines use identical outer splits within
each seed and include corrected OVEC, corrected OSEC, logistic regression,
random forest, HistGradientBoosting, XGBoost, CatBoost, and a prespecified
ensemble. The 70K 3x3 run was attempted with the same policy but exceeded the
35-minute execution budget without producing an artifact; V1's 2x2 result is
not relabeled as V2 confirmation.

## Solver investigation

The AURA selector's fixed transformed 70K representation has 19 features. A
four-resample solver diagnostic found no warnings for liblinear, lbfgs, or saga;
liblinear required 8--12 iterations per resample, lbfgs 18--20, and saga
113--138. The previous three full-workflow liblinear warnings were not
reproduced by the isolated selector diagnostic and were not persisted with
stack traces, so the exact emitting call cannot be proven retrospectively.
The V2 70K attempt remains blocked by runtime, not silently accepted as
converged evidence.
