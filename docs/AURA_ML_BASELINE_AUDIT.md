# AURA-ML baseline and data audit

## Dataset identity

| Dataset | Rows | Target | SHA-256 | Role |
|---|---:|---|---|---|
| `heart5.csv` | 918 | `HeartDisease` | `e4068802a044e8a1e3ae9fa81deae7025711bf4f13e3057f96e4f1cf3b0180c2` | development/replication |
| `MendeleyCardiovascular_Disease_Dataset.csv` | 1,000 | `target` | `9376367dde41e79e432d6402ea5d9e44223fc318ff54ed09966d721923947d1e` | development/replication |
| `data/kaggle_cardiovascular_70k/cardio_train.csv` | 70,000 | `cardio` | `21a705d23381b0dfd6a6416da701b490744f1fc3b47e9ff3db3968c420ffa10c` | separate benchmark |

The hashes and schemas are recorded in `data/manifests/local_datasets.json`.
The small datasets are not independent external validation; the 70K dataset has
a different endpoint/schema and is not pooled with them.

## Existing fresh evidence

The two small fresh artifacts contain fold metrics but no stored predictions, so
their metrics cannot be recomputed from the JSON alone. The 70K artifact stores
all outer predictions; recomputation gave exact agreement for every listed
model and the ensemble.

| Dataset | Existing best in fresh 2x2 artifact | ROC-AUC | PR-AUC | Accuracy | Brier | ECE |
|---|---|---:|---:|---:|---:|---:|
| heart5 | corrected OVEC | 0.924376 | 0.925052 | 0.876906 | 0.101386 | 0.064511 |
| Mendeley | corrected OVEC | 0.994561 | 0.996026 | 0.966000 | 0.029531 | 0.091993 |
| 70K | CatBoost | 0.800098 | 0.785120 | 0.733671 | 0.180971 | 0.008135 |

The 70K task is substantially harder in discrimination: the balanced target and
noisy blood-pressure measurements produce ROC-AUC near 0.80, while the two
small datasets contain strong public-dataset signals and reach much higher
values. The 70K manifest records implausible blood-pressure and height/weight
values; these are retained rather than silently filtered.

## Weaknesses motivating AURA-ML

1. Existing OVEC/OSEC evidence does not consistently improve all metrics.
2. Stable feature selection has not consistently improved reliability.
3. The fixed 70K ensemble did not beat the best standalone model.
4. The existing small-dataset artifacts do not retain predictions for audit.
5. Data heterogeneity makes a single preprocessing policy difficult to justify.

AURA-ML therefore tests adaptive representation choice, reliability-aware
fusion, and calibration under the same outer splits as a fresh baseline fit.
