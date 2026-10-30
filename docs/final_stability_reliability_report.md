# Stability–reliability analysis

The paired linkage artifacts use seeds 42–46 for the post-tuning small-dataset
runs and compare corrected OSEC with stable OSEC on the same fit, calibration,
and evaluation split structure. The existing ten-seed corrected artifacts
remain the primary broader linkage evidence.

The heart5 post-tuning run had cross-seed selected-set Nogueira stability
0.2558. Stable-minus-corrected mean differences were +0.00005 ROC-AUC,
+0.00063 AURC, -0.00087 full-coverage risk, +0.00261 conformal coverage, and
-0.01150 ECE; intervals were descriptive and included zero.

The Mendeley post-tuning run had cross-seed selected-set Nogueira stability
0.2008. Differences were -0.00026 ROC-AUC, +0.00018 AURC, +0.00080
full-coverage risk, -0.00080 conformal coverage, and -0.01240 ECE. The
direction is mixed across metrics and does not support a general
stability–reliability relationship.

The supported conclusion is negative or inconclusive: more stable selected
sets did not consistently produce better predictive reliability.
