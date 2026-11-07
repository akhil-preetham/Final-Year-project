# Dataset provenance and external-validation candidates

## 1. Datasets already used by CARDIODIAG

| Dataset | Provenance | License/access | Role in this project |
|---|---|---|---|
| Five States / `heart5.csv` | Composite of Cleveland, Hungarian, Switzerland, Long Beach VA, and Statlog public heart-disease sources, distributed in the paper through a Kaggle-hosted 1,190-row source with 918 unique rows after exact-duplicate removal. | Upstream component licenses and redistribution terms must be checked individually; the local CSV has no license file. | Historical replication/development benchmark only. Not independent external validation. |
| Mendeley cardiovascular disease dataset | Mendeley Data record `dzz48mvjht`, DOI `10.17632/dzz48mvjht.1`; described as 1,000 subjects from a multispecialty hospital in India. | CC BY 4.0; CSV and official codebook hashes are recorded in `data/manifests/mendeley_cardiovascular_2021.json`. | Historical replication/development benchmark only because the base paper already used it. The codebook defines presence/absence but not a diagnostic reference standard or angiographic threshold, so it is not pooled with angiographic cohorts. |

## 2. Candidate datasets

| Candidate | What it can test | Main limitation | Provisional role |
|---|---|---|---|
| UCI Heart Disease repository | Four archived cohorts: Cleveland, Hungary, Switzerland, and VA Long Beach; one is held out per `CD-XD-002` outer fold. | CC BY 4.0; archive hash, cohort counts, target, feature map, and source details are in `data/manifests/uci_heart_disease_transfer_study.json`. | Exploratory retrospective leave-one-source-out pilot only. The cohorts overlap the Five States composite and are not independent external validation. |
| UCI Z-Alizadeh Sani (ID 412) | 303 records from Shahid Rajaei Cardiovascular, Medical, and Research Center, Tehran; original dataset paper reports this as a separate site. | CC BY 4.0; source archive/workbook hashes, target counts, mapping, and compatibility caveat are in `data/manifests/uci_z_alizadeh_sani_external.json`. | Source-distinct one-way transport stress test (`CD-XD-003`); target uses `>=50%` stenosis, source uses `>50%`, so not endpoint-identical validation. |
| AngioCAD (Zenodo record 15826856) | 377 matched clinical/artery-label records from Shahid Chamran Heart Center, Isfahan, Iran; article reports 413 patients. | CC BY 4.0; feature/label workbook checksums, target construction, and mismatch audit are in `data/manifests/angiocad_external.json`. | Endpoint-aligned source-distinct external evaluation (`CD-XD-004`); 36 label IDs have no clinical-feature row, and person-level overlap with source files cannot be checked. |
| UCI Heart Failure Clinical Records | Robustness to a different clinical population and a related but different outcome (`death_event`). | 299 records and a different endpoint; feature mapping and target meaning do not match CVD diagnosis. | Optional stress test/sensitivity analysis, not the primary external test. |
| NHANES public-use files | Population-shift and prevalence-shift analysis using survey-weighted covariates and a harmonized self-reported CVD outcome. | Self-reported outcome, changing survey cycles, complex sampling, and incomplete feature alignment. | Possible transportability analysis if the endpoint and covariate subset are prespecified. |
| MIMIC-IV | Independent hospital EHR validation with rich clinical provenance. | PhysioNet credentialed access, required training, difficult phenotype definition, temporal/site confounding, and feature mismatch. | Strongest long-term external-validation candidate if access is obtained before model freeze. |
| eICU-CRD | Multi-center ICU validation and site-shift analysis. | Credentialed access, ICU-only population, and a different case-mix from outpatient/benchmark cohorts. | Secondary external/shift analysis if target phenotype is defensible. |

## 3. External-validation rule

An external dataset must be selected and frozen before final feature-map,
threshold, calibration, and model-selection decisions. No label-based tuning,
recalibration, threshold selection, or repeated model comparison may be
performed on that dataset. `CD-XD-003` uses a fixed three-feature map but its
outcome boundary differs from the source. `CD-XD-004` adds an endpoint-aligned
AngioCAD cohort and a locked one-way evaluation. It is site-distinct, though
public data do not permit patient-level linkage and 36 of the 413 labeled IDs
are missing clinical features. Additional sites and prospective evaluation
are still needed to estimate between-site performance.

## 4. Acquisition status

The UCI Heart Disease archive was downloaded on 2026-11-05 for the exploratory
`CD-XD-002` pilot. The Z-Alizadeh Sani archive was downloaded for `CD-XD-003`
and AngioCAD's public structured workbooks were acquired for `CD-XD-004`.
Both source-distinct site results are frozen and documented; AngioCAD has the
aligned `>50%` outcome boundary. The next gate is external replication across
additional hospitals or a prospective cohort, with source, license, target,
feature mapping, and overlap procedures frozen before any model decisions.
# Current controlling record

This ledger preserves earlier experiment descriptions. Use
[`FINAL_DATASET_ATTRIBUTION_REGISTER.md`](FINAL_DATASET_ATTRIBUTION_REGISTER.md)
for canonical names, source versions, DOI/license, attribution and release
eligibility. Historical terms such as “source-distinct” describe reported
site/source separation only; without common patient identifiers they do not
establish patient independence. No verified patient-independent,
untouched, endpoint-identical external validation has been demonstrated.

