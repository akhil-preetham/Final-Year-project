# Controlled covariate-shift laboratory

**Run:** 2026-11-06. **Status:** synthetic diagnostics, not clinical external validation.

The runner creates a stratified held-out split of the local Heart5 rows. For each controlled transformation, it compares held-out unmodified rows with transformed copies using KNN distance, Ledoit-Wolf Mahalanobis distance, Isolation Forest, PCA reconstruction error, a domain classifier, and missingness fraction. Metrics include AUROC, AUPRC, TPR at no more than 5% FPR, and FPR at the first point reaching 80% TPR. All transformations preserve row labels; labels are not used by the detectors or domain-discrimination metric.

## Main results (selected)

| Synthetic shift | Best detector AUROC | Interpretation |
|---|---:|---|
| Age mean +1 SD | Domain classifier 0.780 | Detectable moderate one-feature location shift |
| Cholesterol variance ×1.75 | KNN 0.615 | Weak detection despite a designed spread change |
| Cholesterol permutation, disrupting correlation | KNN 0.527 | Marginally above chance; correlation disruption is poorly detected |
| Resting blood pressure ×10 | Domain classifier/KNN/Mahalanobis/PCA 1.000 | Extreme unit shift is easy to detect; this does not establish subtle-shift performance |
| 50% cholesterol missingness | PCA 0.759; missingness fraction 0.753; domain classifier 0.756 | Missingness is detectable when its rate changes substantially |

The domain classifier scored 0.5 on the symmetric cholesterol variance and permutation shifts, despite training on synthetic versions. A linear domain classifier can miss symmetric changes; a detector can also be highly sensitive to an implausibly large unit error. These results demonstrate detector- and shift-specific behavior, not a universal OOD solution.

The artifact and complete detector-by-shift table are in results/controlled_shift_lab_20261106_run2/. The first two run directories contain incomplete attempts and are not analysis outputs; the run2 manifest names the complete result. The script hashes the source CSV and runner.

## Important scope limits

This laboratory evaluates **synthetic source-versus-transformed-domain discrimination** only. It does not measure prediction-error detection, individual anomaly detection under natural patient variation, or real concept shift. No labels were changed, no detector threshold was chosen for use, and no synthetic record is represented as a real patient. The source dataset is small, composite, and not an independent hospital sample. Real AngioCAD OOD AUROC remains 0.589 in its separate locked report.

Next work should compare prediction-error association using source held-out labels and separately simulate a known concept change where P(Y|X) is altered. Such synthetic results can show a detector's theoretical blind spot, but cannot substitute for an additional labelled hospital cohort.
