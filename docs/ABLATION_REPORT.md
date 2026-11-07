# Ablation report

## Comparable corrected candidates

The bounded reconstructed 2x2 run used identical folds and seed for all
candidates. Pooled ROC-AUC / Brier / ECE:

| Dataset | Logistic | OVEC | OSEC | Stable logistic | Stable OSEC |
|---|---|---|---|---|---|
| Heart5 | 0.922575 / 0.108764 / 0.042428 | 0.924376 / 0.101386 / 0.064511 | 0.912056 / 0.112506 / 0.077005 | 0.922715 / 0.108699 / 0.042472 | 0.911677 / 0.112456 / 0.082004 |
| Mendeley | 0.987705 / 0.032236 / 0.098549 | 0.994561 / 0.029531 / 0.091993 | 0.985657 / 0.031626 / 0.097200 | 0.989635 / 0.031629 / 0.074198 | 0.992516 / 0.028423 / 0.170655 |

## AURA ablations

Existing AURA 2x2 ablations show dataset-conditional effects. On Heart5,
removing multiview slightly improved ROC-AUC to 0.925855 and Brier to 0.101326;
removing dynamic fusion reduced ROC-AUC to 0.922556. On Mendeley, full AURA
ROC-AUC was 0.995854 and Brier 0.019551, but many switches were inactive
because a single tree model was repeatedly selected.

## Interpretation

No component is a universal winner. The strongest reproducible conclusion is
that corrected OVEC is a strong small-dataset baseline, stable selection has
small dataset-specific effects, and AURA-ML should remain exploratory until
larger repeated protocols and compatible external data are available.

