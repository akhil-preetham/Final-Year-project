# CARDIODIAG: final consolidated manuscript draft

**Status:** research manuscript draft; not submission-ready. This Markdown companion is a readable synopsis of `paper/manuscript.tex`. Tables and exact analyses in the LaTeX source remain the authoritative manuscript content.

## Title

**A Reproducibility and Transportability Audit of Cardiovascular Prediction Under Dataset Shift**

## Abstract

### Background

Cardiovascular prediction models can appear reliable on development data while failing under changes in cohort, endpoint, measurement, and data source. This engineering study audits a CARDIODIAG pipeline for leakage control, calibration, uncertainty estimation, distribution-shift detection, and abstention. The goal is to test whether available evidence supports dependable prediction on data outside the development sources, not to establish a clinical diagnostic device.

### Methods

The repository's historical Five States composite and a 1,000-row Mendeley benchmark were retained for replication, with nested three-fold outer/inner evaluation at seed 42. Four UCI Heart Disease cohorts were used in retrospective leave-one-source-out stress tests. Separate one-way transport evaluations used Z-Alizadeh Sani, AngioCAD, and Duke ACATH, with endpoint and provenance caveats reported per cohort. All preprocessing, imputation, calibration, feature selection, and threshold operations were fit using training/source data only in the corresponding frozen protocols. We audited dataset lineage, licenses, row overlap, prediction timing, and the saved prediction artifacts. No ECG, heart-failure mortality, or MI-complication endpoint was merged with tabular CAD classification.

### Results

In internal nested evaluation, corrected OVEC had mean ROC-AUC 0.930 (fold SD 0.007) on Heart5 and 0.996 (0.001) on Mendeley. The Mendeley reference standard, prediction timing, and stenosis threshold are undocumented, and Heart5 overlaps the UCI component cohorts. Statlog's 270 records exactly match Cleveland after target harmonization. Z-Alizadeh Sani had ROC-AUC 0.720 (bootstrap 95% CI 0.651–0.780), but its target boundary is >=50% versus source >50%, it had already been examined, and person-level overlap cannot be assessed. AngioCAD had ROC-AUC 0.787 (0.734–0.838) on 377 matched records; only 377 of 413 labeled IDs had features, age/FBS units are incompletely documented, common patient linkage is absent, and the outcomes had been examined before later reliability analyses. A post-hoc combined abstention policy covered 5.6% of AngioCAD records. Duke had ROC-AUC 0.661 (0.642–0.680), but its >=75% endpoint differs from the source >50% endpoint; its combined selective coverage was 11.4%, with 41 errors among 401 accepted records. Feature-only OOD separation was weak, and a trusted registry gate withheld scores for all unregistered target sites.

### Conclusion

The repository supports a reproducible engineering prototype and a documented negative result for the stated generalization objective. It does not establish verified patient-independent, untouched, endpoint-identical external validation or useful operation under shift. The research claim is therefore **NO-GO** pending a suitable new cohort and a frozen prospective validation protocol. Clinical use is outside scope.

## Methods and data provenance

The exact dataset identities, source records, DOI/version, access and license terms, attribution requirements, overlap findings, and release disposition are in [`FINAL_DATASET_ATTRIBUTION_REGISTER.md`](FINAL_DATASET_ATTRIBUTION_REGISTER.md). The compatibility and overlap reports are [`DATASET_COMPATIBILITY_MATRIX.md`](DATASET_COMPATIBILITY_MATRIX.md) and [`DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md`](DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md). Summary:

- **Heart5 / Five States:** 918-row derived composite. Every row maps to UCI component records (914 unique matches, four ambiguous); exact 1,190-row upstream Kaggle source, version, transformation history, and standalone license remain unresolved. Not independent of the UCI components.
- **Mendeley cardiovascular v1:** DOI `10.17632/dzz48mvjht.1`, CC BY 4.0; 1,000 rows. Historical replication only; the outcome reference standard and predictor timing are unclear.
- **UCI Heart Disease:** DOI `10.24432/C52P4X`, CC BY 4.0; 920 observations across Cleveland, Hungary, Switzerland, and VA Long Beach. These components overlap Heart5.
- **Statlog Heart:** DOI `10.24432/C57303`, CC BY 4.0; exact 270/270 Cleveland match after class harmonization. Not a new cohort.
- **Z-Alizadeh Sani:** DOI `10.24432/C5Q31T`, CC BY 4.0; 303 records, used previously; target >=50% differs from source >50%; identifiers do not support patient-level overlap checks.
- **AngioCAD:** Zenodo DOI `10.5281/zenodo.15826856`, CC BY 4.0; 377 matched of 413 labeled IDs. Site is reported separately, but no common-person linkage is available, and target outcomes were previously inspected.
- **Duke ACATH:** 3,504 rows, provider grants use with attribution but redistribution terms are not explicit; target >=75% differs from source >50%.
- **Mendeley Heart Disease Clinical v1:** DOI `10.17632/nt4y898vyh.1`, CC BY 4.0; exact 918/918 labeled-row multiset match to Heart5; provenance screen only.
- **Kaggle Cardiovascular 70K:** license is listed as `Unknown`; distinct target/schema. Not CAD validation and excluded from public raw-data and row-level derivative release.

Candidate HF, MI-complication, and ECG datasets were audited but not downloaded. Their outcomes/modalities require distinct prediction tasks; PTB-XL+ shares PTB-XL lineage. EPHNOGRAM is ODC-By, not CC BY.

## Results and interpretation

All nested summary table entries are generated from saved JSON in `results/master_directive_20261105_serial/` by `experiments/summarize_nested.py`; the source stage manifest records data/result hashes and explicitly marks `external_validation: false`. Transfer and domain-guard tables derive from saved study metrics, not manually keyed values. Full tables, confidence intervals, calibration, feature-selection, and abstention analyses are in `paper/manuscript.tex` and the linked result directories.

Internal discrimination does not resolve endpoint validity, leakage from source lineage, prediction-time ambiguity, or transport. AngioCAD and Duke are descriptive site-level stress tests and are not claimed to establish patient-independent external validation. The registry gate achieves zero target coverage because neither target site is registered; the combined rule's small target coverage is not evidence of a useful deployment operating point.

## Limitations

The key limitations are unresolved Heart5 source/rights, target/reference-standard ambiguity in Mendeley, known source overlap, missing cross-source identifiers, endpoint mismatch in Z-Alizadeh Sani and Duke, post-hoc target exposure for AngioCAD, incomplete AngioCAD records and undocumented units, weak feature-only OOD detection, low selective coverage, and no prospective or clinical validation. The complete itemized account is [`FINAL_DATASET_LIMITATIONS.md`](FINAL_DATASET_LIMITATIONS.md).

## Reproducibility and availability

The code, environment lock, protocols, and aggregate result-generation scripts are in the repository. No public package has been generated or authorized, and no root project code license is present; redistribution authority must be resolved first. The proposed package is data-free. Existing `dist/*.zip` files are legacy snapshots and are not approved for upload. Raw Heart5, Kaggle 70K, and Duke data plus row-level derivatives are excluded pending rights clarification; other openly licensed data are also omitted under the data-free release policy. See [`FINAL_DATA_RELEASE_MANIFEST.md`](FINAL_DATA_RELEASE_MANIFEST.md).

## Declarations

Authors and shared affiliation are provisional as recorded in the LaTeX source. Ethics determination, funding, competing interests, individual affiliations/order, final contributions for two coauthors, and journal selection are pending. No approval, exemption, funding status, or coauthor contribution is invented here.

## Publication status

This is a technically reproducible research draft, not a submission-ready paper. The generalization claim is a research **NO-GO** on current evidence. The engineering prototype can be described as a reproducible evaluation and fail-closed demonstration, with the negative findings and dataset caveats stated prominently.
