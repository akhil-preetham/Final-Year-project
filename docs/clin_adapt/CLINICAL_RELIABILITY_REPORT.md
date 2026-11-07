# CLIN-ADAPT clinical reliability report

## Metrics available

The result artifacts store Brier score and log loss in addition to ROC-AUC,
PR-AUC, threshold metrics and confusion counts. Calibration selection is
inner-only and can choose none, sigmoid or isotonic calibration. The current
release does not claim that ECE, Brier or threshold metrics are transportable
outside the development cohort.

## Observed development results

| Dataset | CLIN-ADAPT ROC-AUC | Brier | Log loss | Interpretation |
|---|---:|---:|---:|---|
| Heart5 | 0.926700 | 0.100377 | 0.334433 | below frozen compact-pool ROC-AUC by an unpaired 0.002333 |
| Mendeley | 0.997701 | 0.015325 | 0.056860 | competitive development result; not external reliability |
| 70K priority | 0.802481 | 0.179835 | 0.539488 | descriptive 2×2 priority run; not full registry coverage |

## Clinical limitations

- No calibration slope/intercept or decision-curve analysis is claimed in this
  first release.
- No independent prevalence-shift or temporal-shift cohort is available.
- No subgroup analysis is reported because site, demographic and protected-group
  governance has not been approved for these files.
- High within-dataset performance on Mendeley does not establish clinical
  transportability.
- The 70K data contain documented implausible blood-pressure values; no rows
  were silently removed or repaired.

## Reliability objective

Future CLIN-ADAPT evaluation should treat probability quality, abstention,
coverage and mapping failure as first-class outcomes. An adaptive policy that
improves ROC-AUC but produces unsafe confidence under shift is not a clinical
success.
