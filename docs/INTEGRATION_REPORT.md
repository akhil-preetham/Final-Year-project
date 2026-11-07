# Integration report

## Retained components

| Component | Correctness | Usefulness | Computational status | Result |
|---|---|---|---|---|
| Training-only preprocessing | Supported by leakage audit and tests | High | Feasible | Authoritative |
| Nested validation | Inner selection and outer scoring are separated | High | Feasible | Authoritative |
| Stable XAIH-DRC approximation | Fold-local and testable, not original LIME | Conditional | Feasible | Ablation only |
| Calibration/reliability | Metrics expose probability quality separately from ranking | High | Feasible | Retained |
| Conformal/selective prediction | Empirical coverage/risk can be measured | Conditional | Feasible | Retained as internal evidence |
| Robustness perturbations | Evaluation-only stress testing | Useful | Feasible | Retained |
| Fairness | Available only for supported demographic columns | Limited | Feasible | Conditional |
| AURA-ML | Dataset-conditional improvements and inactive switches | Mixed | Expensive but feasible | Exploratory only |

## Rejected or deferred

- LoRAS was not integrated into the authoritative pipeline because its
  historical package, parameters, and fold-local behavior are not reproducibly
  frozen.
- LIME-based selection was not integrated into final metrics because no
  reusable fold-local transformer was available.
- Cross-dataset prediction was not run because endpoint and feature semantics
  are not approved equivalent.
- No new algorithm or CLIN-ADAPT V2 was introduced.

## Overall result

The integration improves auditability and leakage control, not universal
predictive performance. Existing evidence supports retaining reliability and
stability analysis as separate measurements rather than presenting stability as
an automatic reliability improvement.

