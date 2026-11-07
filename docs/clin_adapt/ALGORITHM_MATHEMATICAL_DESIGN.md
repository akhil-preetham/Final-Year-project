# Provisional CASL mathematical design

CASL means **Clinical Adaptive Strategy Learning**. The v0.1 implementation is
a transparent validation policy, not yet a new learning theory or established
novel algorithm.

## Candidate utility

For candidate `k`, let `p_k` be inner out-of-fold probabilities and `y` the
inner labels. The current utility is:

```text
U_k = AUROC(y, p_k) - lambda * Brier(y, p_k)
```

with `lambda = 0.25`. Candidates are rejected if AUROC is below 0.5 or Brier is
above 0.35. These are safety gates, not tuned test-set thresholds.

## Coordination

The top at most `M=3` usable candidates receive validation weights:

```text
w_k = exp(U_k / tau) / sum_j exp(U_j / tau),   tau = 0.05
```

Their prediction matrix `P` produces `p_f = P w`. A diversity statistic is the
mean of `1 - |corr(p_i, p_j)|` over candidate pairs. Fusion is retained only if:

```text
U_f >= max_k(U_k) + delta
and diversity(P) > 0
```

where `delta = 0.002`. Otherwise the best single candidate is retained.

## Calibration

When enabled, sigmoid and isotonic calibrators are cross-fitted on the inner
predictions. A calibration method is retained only if its Brier score improves
the uncalibrated score by at least `1e-4`. No outer-test labels are used.

## Failure policy

Execution failures are recorded independently. The coordinator diagnoses common
failure classes—convergence, memory, categorical encoding and unknown failures—
and emits a controlled recommendation. It does not mutate the search repeatedly
or change random seeds opportunistically.

## Novelty boundary

The equations are closely related to dynamic ensemble selection, reliability-
weighted ensembles and AutoML portfolio selection. The implementation therefore
claims **provisional CASL infrastructure**, not algorithmic novelty. A novelty
claim would require a dataset-level held-out evaluation demonstrating a distinct
capability, such as safer semantic refusal or reliable cross-cohort calibration,
against existing methods under equal information budgets.
