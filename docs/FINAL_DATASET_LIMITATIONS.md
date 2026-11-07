# Final dataset limitations and implications

## Limitations that affect validity

1. **Heart5 source/rights unresolved.** The 918-row file maps to UCI component data, but its exact upstream 1,190-row Kaggle record, version, preprocessing and standalone license were not recovered. It cannot be represented as an independent dataset from UCI. Because the primary internal results use this file, any use of its scores in a manuscript must disclose the unresolved provenance/rights limitation; do not redistribute its raw rows.
2. **Development-source overlap.** The four UCI cohorts used in the retrospective leave-one-source-out pilot are represented in Heart5. Statlog is an exact 270/270 Cleveland duplicate after label harmonization. These analyses are retrospective source-domain stress tests, not independent external validation.
3. **Mendeley endpoint and predictor timing.** The 1,000-row Mendeley file has no documented diagnostic reference standard, angiographic cutoff or prediction index time. `noofmajorvessels` is angiography-derived and may be outcome-proximal. Its high internal metrics are replication results, not prospective early-detection evidence.
4. **Mendeley 2026 duplicate.** All 918 labelled rows in the 2026 Mendeley file match Heart5 exactly. It adds no independent patient evidence.
5. **Z-Alizadeh Sani threshold and overlap.** It was already examined. It labels CAD at `>=50%`, unlike the source `>50%` threshold; no patient IDs are available to verify cross-dataset de-duplication.
6. **AngioCAD is one previously exposed cohort.** Only 377 of 413 labeled IDs have features, there is one reported hospital, common person IDs are unavailable, and the evaluation was inspected before later reliability/sensitivity analysis. Age/FBS units are not explicitly stated. It supports a source-separated, endpoint-near evaluation only; it does not establish independent-patient multi-site generalization.
7. **Duke endpoint mismatch.** The Duke stress-test endpoint is `>=75%`, not `>50%`; 1,246/3,504 cholesterol measurements are missing. Cross-dataset participant linkage is unavailable. Results are exploratory and not an exact-endpoint validation.
8. **Unknown Kaggle 70K rights and distinct target.** Kaggle's current record states license `Unknown`. It is a different examination-time cardiovascular endpoint/schema and is not an external test of the angiographic CAD model. Keep its raw data and row-level derivatives out of public release until rights are clarified.
9. **No confirmatory untouched external site.** Z-Alizadeh Sani and AngioCAD were already inspected; Duke is endpoint-mismatched; UCI/Statlog overlap development history. No source here demonstrates verified patient-independent, endpoint-identical, untouched external validation.
10. **Candidate tasks are not substitutes.** Heart failure death, MI complications, ECG arrhythmia/diagnostic labels, and ECG/PCG signal-quality tasks have different populations, outcomes, timing and input modalities. They must remain separate studies and cannot increase the sample count of the CAD task.

## Consequences for interpretation

- Internal AUCs do not imply transport, prospective prediction, or clinical utility.
- AngioCAD's source-separated cohort metrics are descriptive one-site results with unresolved identity linkage and feature mapping assumptions. They must not be described as verified independent-patient external validation.
- The registered-site gate abstains on both unregistered evaluation sites; 0% automatic coverage is a fail-closed behavior, not a successful useful operating point.
- Weak feature-based OOD discrimination and low selective coverage remain negative findings, not issues to hide or optimize against exposed test labels.
- CC BY/ODC terms concern copyright/database rights, not whether an endpoint is valid, clinically usable, privacy-safe, or an independent cohort.

## Required future evidence

Recover the exact Five States source and preprocessing/license lineage; obtain written terms for Duke redistribution; determine whether Kaggle 70K use and publication are permitted; secure a new patient-level dataset from a genuinely separate site with prespecified prediction time and an exact angiographic target; obtain valid linkage or transparently report linkage unavailable; freeze harmonized predictors, calibration and thresholds before test labels; and obtain institutional ethics/data-use determinations as required. None can be simulated by downloading another derivative of existing records.
