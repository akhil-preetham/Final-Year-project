# Model benchmark claim-to-evidence audit

| Claim | Evidence required | Current status |
|---|---|---|
| A candidate is feasible on the 70k task | Completed screening artifact with timing and finite metrics | Supported for all 11 available candidates by `kaggle70k_model_screening.json` |
| XGBoost has the highest mean ROC-AUC in the generic 70k benchmark | Completed primary generic artifact with held-out outer folds | Supported descriptively: XGBoost mean ROC-AUC 0.80038; not a claim of universal superiority |
| XGBoost has the best mean Brier/ECE among these candidates | Held-out outer-fold Brier/ECE summaries | Supported descriptively: Brier 0.18092 and ECE 0.01089 in the primary generic artifact |
| Stable selection improves prediction or reliability | Matched corrected and stable pipelines under the same protocol | Prior linkage evidence does not establish this; no new generic-model claim |
| Optional model family is suitable | Verified dependency, official source, license, API, and completed reproducible run | Deferred for unavailable packages |
| The 70k dataset is external validation | Compatible target/features and one-way frozen external protocol | Unsupported; this is a separate `cardio` benchmark |
| Full CARDIODIAG benchmark completed | All requested workflows have verified artifacts | Unsupported: generic model benchmark completed, but custom nested validation remains incomplete |

The generic benchmark outputs are structurally compatible with the runner's
3x2 protocol and have truthful provenance. They do not replace the corrected
stability, linkage, or custom nested-validation artifacts, and they should not
be pooled with incompatible targets or protocols.
