# Updated proposed CARDIODIAG architecture

## Evidence-backed flow

1. **Dataset registry and adapter:** verify dataset identity, schema, labels, units and provenance; reject unknown endpoint mappings.
2. **Training pipeline:** split by patient/site when identifiers permit; fit imputation, encoding, scaling, outlier handling, selection and estimator only within training folds.
3. **Model comparison:** compare corrected logistic, OVEC and OSEC under shared nested partitions. Historical methods remain in a separate forensic branch.
4. **Source calibration:** reserve source-only calibration rows. Platt is the reproduced baseline; beta is similar; temperature is exploratory and not yet externally confirmed; isotonic performed poorly in the current small-source calibration experiment.
5. **Shift assessment:** report feature-wise shift and OOD detector scores as diagnostics. Current KNN/Isolation Forest results do not justify treating a score as a dependable warning.
6. **Uncertainty:** split-conformal prediction sets are valid only under their exchangeability conditions. Do not assert guaranteed coverage under external shift.
7. **Selective output:** a research API may abstain when the domain is unregistered, support is weak, or the set is not singleton. This is fail-closed behavior, not evidence of model correctness.
8. **External validation:** freeze all learned components and thresholds before scoring an untouched endpoint-compatible site; retain target labels for evaluation only.
9. **Provenance:** hash data, protocol, code, environment, predictions and metrics; independently recompute reported values.

## Component evidence labels

| Component | Label |
|---|---|
| Training-only preprocessing and nested internal runner | Implemented and locally tested |
| OVEC/OSEC corrected candidates | Implemented; original hyperparameter protocols not exactly reproduced |
| Source Platt calibration | Implemented and audited |
| Source temperature scaling | Exploratory second-stage candidate; no new-site confirmation |
| Isotonic/beta calibration | Exploratory comparisons; beta similar to Platt, isotonic poor on this target |
| KNN/Isolation Forest feature OOD | Implemented; weak external site-discrimination evidence |
| Conformal sets | Implemented; guarantee conditional on exchangeability |
| Metadata site registry | Implemented as a fail-closed allowlist; not a learned shift detector |
| Useful unseen-site selective policy | Unsupported |
| Clinical prediction or deployment | Out of scope / NO-GO |

The system must not expose a target probability as reliable merely because the preprocessing and software path executes. The current evidence supports a research evaluation pipeline and conservative gating only.
