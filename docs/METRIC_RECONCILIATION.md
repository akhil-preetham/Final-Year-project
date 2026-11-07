# Metric reconciliation

Metrics below are not pooled. Each row belongs to a separately named protocol.

## Historical native protocol

Artifact: `results/generated/heart5_protocol_comparison.json`; SMOTE before an
80:20 non-stratified split.

| Dataset/model | Accuracy | ROC-AUC | PR-AUC | Brier | ECE |
|---|---:|---:|---:|---:|---:|
| Historical OVEC | 0.862745 | 0.916340 | 0.925548 | 0.123612 | 0.109354 |
| Historical OSEC | 0.887255 | 0.951607 | 0.963591 | 0.088987 | 0.102237 |

## New reconstructed 2x2 nested protocol

Artifact: `results/generated/reconstruction_2x2/`; 2 outer folds, 2 inner
folds, seed 42, training-only preprocessing and inner model selection.

| Dataset/model | Accuracy | Balanced accuracy | ROC-AUC | PR-AUC | Brier | ECE |
|---|---:|---:|---:|---:|---:|---:|
| Heart5 corrected OVEC | 0.876906 | 0.872782 | 0.924376 | 0.925052 | 0.101386 | 0.064511 |
| Heart5 stable OVEC* | 0.876906 | 0.872782 | 0.924376 | 0.925052 | 0.101386 | 0.064511 |
| Mendeley corrected OVEC | 0.966000 | 0.964450 | 0.994561 | 0.996026 | 0.029531 | 0.091993 |
| Mendeley stable OSEC | 0.967000 | 0.965969 | 0.992516 | 0.994170 | 0.028423 | 0.170655 |

`stable OVEC*` is the corrected OVEC row; the active candidate list has no
stable-OVEC variant. Stable OSEC is shown because it is the closest available
stability comparison.

## Original paper metrics

The paper citation and claims are recorded in the provenance documents, but a
publisher PDF/supplementary extraction was not available during this run.
Paper-only metrics are therefore **not independently reconciled** and are not
substituted with notebook output.

## AURA-ML evidence

The existing 2x2 AURA report records pooled ROC-AUC of 0.924990 on Heart5,
0.995854 on Mendeley, and 0.801851 on 70K. Its paired intervals include zero
on the two small datasets; the V2 3x3 report improves Mendeley but is worse on
Heart5. These are exploratory or feasibility results, not external validation.

