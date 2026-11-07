# CLIN-ADAPT ablation report

The ablations are bounded 2×2 development runs with seed 42. They are not
confirmatory evidence and do not modify the frozen CARDIODIAG baseline.

## Heart5

| Configuration | ROC-AUC | PR-AUC | Brier | Runtime |
|---|---:|---:|---:|---:|
| Single CatBoost | 0.926239 | 0.926438 | 0.100399 | 4.20 s |
| Full portfolio, no fusion | 0.927876 | 0.926586 | 0.099716 | 17.24 s |
| Full portfolio, CASL | **0.928495** | **0.929006** | **0.098414** | 20.16 s |

CASL selected validation-justified three-model ensembles in both outer folds of
this bounded run. This is promising development evidence, but the comparison is
not a repeated-seed or dataset-level generalization test.

## Mendeley

| Configuration | ROC-AUC | PR-AUC | Brier | Runtime |
|---|---:|---:|---:|---:|
| Single CatBoost | **0.996622** | **0.997452** | **0.019245** | 6.02 s |
| Full portfolio, no fusion | 0.992812 | 0.994309 | 0.026538 | 23.17 s |
| Full portfolio, CASL | 0.992812 | 0.994309 | 0.026538 | 25.56 s |

CASL did not add a fusion gain in this run; it retained the selected single
candidate in both folds. This negative result is important: the coordinator
does not force an ensemble and does not improve every dataset.

## Interpretation

The Heart5 difference is compatible with a useful adaptive coordination policy,
but the Mendeley ablation shows no improvement over its no-fusion control. The
results therefore do not establish universal superiority or novelty. The next
valid test is repeated-seed, paired nested evidence on compatible tasks and,
for the proposed research gap, dataset-level cross-cohort evaluation.
