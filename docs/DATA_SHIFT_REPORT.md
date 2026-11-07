# Data-shift report

Artifact: `results/generated/dataset_shift.json`. Labels were excluded from
all shift calculations.

| Pair | Domain-classifier AUC | Interpretation |
|---|---:|---|
| Heart5 → Mendeley | 1.0000 | Strong covariate/schema shift |
| Heart5 → 70K | 1.0000 | Narrow mapping and coding shift; not transfer-ready |
| Mendeley → 70K | 0.7887 | Detectable shift under age/gender mapping |

Selected numeric shifts:

| Pair/feature | SMD | KS statistic | PSI |
|---|---:|---:|---:|
| Heart5/Mendeley Age | -0.299 | 0.261 | 1.307 |
| Heart5/Mendeley RestingBP | 0.777 | 0.346 | 1.234 |
| Heart5/Mendeley Cholesterol | 0.927 | 0.441 | 1.383 |
| Heart5/Mendeley Oldpeak | 1.272 | 0.482 | 1.986 |
| Mendeley/70K age | 0.301 | 0.348 | 1.106 |

Categorical PSI values are inflated where category coding differs, so they are
evidence of coding/schema incompatibility as well as possible population
shift. Missingness is zero in all supplied datasets. These results establish
covariate shift, not label shift or concept shift; the latter require
comparable endpoints and feature-target relationship analysis.

