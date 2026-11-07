# Cohort independence audit

**Decision:** no verified patient-independent, untouched, endpoint-identical external cohort is established by the current project evidence.

| Pair / candidate | Evidence | Independence conclusion | Use permitted in current claims |
|---|---|---|---|
| Heart5 and UCI Heart Disease | Row mapping identifies UCI component records inside the composite | Overlap demonstrated | Development/lineage stress tests only; never count represented records as external validation. |
| Statlog and Cleveland | 270/270 exact row matches after target harmonization | Same records demonstrated | Duplicate-data check only. |
| Mendeley 2026 and Heart5 | 918/918 multiset matches reported; 914 unique rows and four ambiguous multiplicities | Substantial overlap demonstrated | Internal/source comparison only. |
| Z-Alizadeh Sani and UCI | Different stated site, but no patient identifiers for linkage; endpoint >=50% vs >50% | Person-level independence unverified; label mismatch | Exploratory endpoint-shift/transport stress test only. |
| AngioCAD and UCI source | Different stated institution; public records provide no common-person linkage; 377 target features match 413 label IDs; labels were inspected previously | Site-distinct is reported; patient independence and fresh holdout status are not proven | Exploratory, already examined site stress test; not confirmatory validation. |
| Duke ACATH and UCI source | Different provider; no shared patient linkage; source >50%, Duke >=75%; target examined | Patient independence unverified and endpoint differs | Endpoint-mismatched stress test only. |
| PTB-XL and PTB-XL+ | Official derived-dataset relationship | Not independent by design | Separate ECG feature study only. |

## Required conditions to reopen the gate

Acquire or obtain documented access to an endpoint-compatible cohort that has not been used in fitting, calibration, feature/model selection, threshold design or prior outcome inspection. Record official source/version, data rights, patient/cohort independence basis, target definition, measurement units and feature mapping. Freeze model and protocol before target outcomes are analyzed. If linkage cannot be established, narrow claims to “source-distinct site-level stress test; patient independence unverified.”

Existing detailed mappings and sensitivity outputs are in [`DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md`](DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md), `results/data_provenance_audits/heart5_uci_row_map.csv`, `data/external/uci_statlog_heart/overlap_audit.json`, `results/external_candidate_screen_20261105/mendeley_heart_disease_2026_overlap.json`, and the named CD-XD transfer-study artifacts. A new cohort, not more splits of these rows, is required for confirmation.
