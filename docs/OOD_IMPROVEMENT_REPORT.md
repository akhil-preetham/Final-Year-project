# CARDIODIAG OOD improvement report

**Updated:** 2026-11-06  
**Decision:** no detector supports a reliable unseen-site OOD claim. Local implementation improvements are diagnostic only.

## Baseline carried forward

The primary AngioCAD source-versus-target Isolation Forest AUROC is 0.589 (conditional 95% interval 0.541–0.635). The later, post-hoc AngioCAD study reports 0.5787 for domain-robust Isolation Forest and 0.5801 for kNN distance. Z-Alizadeh Sani's 0.604 result is a separate cohort with a different endpoint boundary. These are retrospective domain-discrimination results, not proof of individual prediction error detection. All were already examined; no new detector or threshold was selected from those labels.

## New comparison: source-only synthetic covariate shifts

The existing controlled shift laboratory was extended with **Local Outlier Factor in novelty mode**. The detector is fitted only to the training portion of `heart5.csv` after source-fit median imputation and standardization. `novelty=True` permits scoring the held-out source and transformed copies without refitting neighborhoods on the evaluation rows. Larger scores mean less source-like. Two tests check score direction on a known large synthetic displacement and reject invalid feature shapes.

Runner: `experiments/controlled_shift_lab.py`; the exact repeat in run5 reproduces all 35 metrics rows from the earlier run4 output.  
Artifact: `results/controlled_shift_lab_20261106_run5/controlled_shift_metrics.json` and `controlled_shift_metrics.csv`  
Study ID: `SYNTHETIC-COVARIATE-SHIFT-001`; seed 20261106; 60/40 stratified source split; 368 held-out source rows and 368 transformed copies for each diagnostic. Every shift preserves copied labels; labels are not used by detector fitting or shift AUROC.

| Synthetic change | LOF AUROC | LOF AUPRC | TPR at FPR ≤5% | Context among tested methods |
|---|---:|---:|---:|---|
| Age mean +1 SD | 0.591 | 0.574 | 0.098 | Ledoit–Wolf Mahalanobis was 0.605; no method was useful at low FPR. |
| Cholesterol variance ×1.75 | 0.629 | 0.627 | 0.128 | Highest AUROC in this one scenario; KNN was 0.615. No interval or independent replication was estimated. |
| Cholesterol–MaxHR correlation disruption | 0.524 | 0.521 | 0.046 | Near chance; the detectors do not reliably see this dependency shift. |
| Resting blood pressure ×10 | 1.000 | 1.000 | 1.000 | Implausibly extreme unit-error simulation; several methods also scored 1.000. |
| 50% cholesterol missingness | 0.684 | 0.661 | 0.109 | Below Ledoit–Wolf Mahalanobis 0.752 and PCA reconstruction 0.759. |

Across these constructed cases, LOF does not dominate. Its apparent variance-shift advantage is one scenario-specific diagnostic without uncertainty intervals and cannot justify an OOD deployment rule. It remains in the synthetic comparison runner, not in the frozen prediction bundle or application policy. Mahalanobis, KNN, Isolation Forest, PCA reconstruction, a domain classifier, and missingness monitoring remain separate comparison methods; no universal detector winner is claimed.

## Scope and safeguards

- This is a synthetic covariate-shift experiment on a small, composite development source, not a clinical external cohort.
- It does not test concept shift, prediction-error detection, or whether abstention improves patient outcomes.
- AngioCAD/Duke were excluded from this new selection exercise because their labels had already been examined.
- No target labels selected thresholds, transformations, or methods. This lab reports ranking metrics only; it does not register a deployment cutoff.
- The generated unit shift is an extreme software diagnostic and must not be used as evidence of natural hospital-shift sensitivity.

## Remaining work and gate

No real-world OOD method passes the research acceptance gate. Any future method comparison must be frozen on source-held-out domains, then evaluated once on a newly obtained, rights-cleared, untouched cohort with documented independence and endpoint compatibility. Report AUROC, prevalence-aware AUPRC, TPR at a prespecified low FPR, source false-alert rate, target alert rate, error-detection association, and calibration separately. Repeated review of AngioCAD or Duke cannot restore confirmatory status.

**OOD reliability: NO-GO.** The code now includes a tested LOF novelty diagnostic; the scientific OOD claim remains unproven.
