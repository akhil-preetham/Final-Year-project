# Leakage and validation audit

## Corrected pipeline controls

The corrected implementation places data-dependent operations inside the
training portion of each relevant split:

- numeric outlier bounds and imputation statistics;
- categorical imputation and one-hot category discovery;
- scaling;
- selector relevance, resampling, and fallback ranking;
- hyperparameter selection in inner folds;
- calibration and conformal fitting on a separate calibration partition;
- threshold/abstention evaluation after fitting and calibration.

`src/cardiodiag/experiments.py` builds the pipeline, while
`src/cardiodiag/nested_validation.py` evaluates candidates in outer folds. The
outer test rows are not passed to fitting or model selection.

## Historical defects retained as historical evidence

The archived notebook workflows include paths where SMOTE, preprocessing, or
dimensionality reduction precede the final evaluation split. Their reported
metrics are preserved for auditability but are never pooled with corrected
results and are not presented as unbiased generalization estimates.

## Boundary review

| Operation | Corrected location | Audit result |
|---|---|---|
| Identifier removal | Before modeling, with schema attrs preserved | Pass |
| Feature typing | Explicit target/schema mapping in `data.py` | Pass for three local schemas |
| Outlier handling | `TrainingOnlyCleaner.fit` on training rows | Pass |
| Imputation/scaling/encoding | sklearn pipeline fitted per training fold | Pass |
| Stable selector relevance | Internal fit/validation split within outer training data | Pass; not outer leakage |
| Hyperparameter search | `GridSearchCV` on outer-training rows only | Pass |
| Calibration/conformal | Separate fit/calibration/evaluation runner partitions | Pass for stored linkage runs |
| Threshold policy | Fixed empirical evaluation policy; not clinical tuning | Pass with limitation |
| Patient grouping | No patient-level grouping metadata available for heart5/70K; Mendeley identifier is unique and removed | Limitation |
| External evaluation | Fail-closed manifest gate and one-way runner | Blocked until a valid manifest exists |

## Validation protocols

The authoritative registry separates:

1. primary corrected nested internal validation (3 outer x 3 inner, seed 42);
2. schema-corrected bounded sensitivity (2 x 2 or repeated bounded runs);
3. exploratory 70K model benchmarks (3 outer x 2 inner);
4. historical single-split/notebook evidence; and
5. evaluation-only stress tests.

Fold means and pooled out-of-fold metrics are both reported where available and
are not treated as interchangeable. Bootstrap intervals are descriptive
resampling summaries, not independent-patient uncertainty guarantees.

## Remaining risks

- Stored nested artifacts do not contain all raw outer-fold prediction vectors,
  limiting independent metric recomputation.
- No patient identifiers or source linkage allow a definitive overlap audit.
- No temporal ordering is available, so temporal leakage cannot be assessed.
- The datasets are retrospective public benchmarks and do not establish clinical
  utility, prospective performance, or transportability.
