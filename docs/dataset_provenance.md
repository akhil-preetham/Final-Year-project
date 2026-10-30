# Dataset provenance and external-validation candidates

## 1. Datasets already used by CARDIODIAG

| Dataset | Provenance | License/access | Role in this project |
|---|---|---|---|
| Five States / `heart5.csv` | Composite of Cleveland, Hungarian, Switzerland, Long Beach VA, and Statlog public heart-disease sources, distributed in the paper through a Kaggle-hosted 1,190-row source with 918 unique rows after exact-duplicate removal. | Upstream component licenses and redistribution terms must be checked individually; the local CSV has no license file. | Historical replication/development benchmark only. Not independent external validation. |
| Mendeley cardiovascular disease dataset | Mendeley Data record `dzz48mvjht`, DOI `10.17632/dzz48mvjht.1`; described as 1,000 subjects from a multispecialty hospital in India. | CC BY 4.0 on the Mendeley record. | Historical replication/development benchmark only because the base paper already used it. |

## 2. Candidate datasets

| Candidate | What it can test | Main limitation | Provisional role |
|---|---|---|---|
| UCI Heart Disease repository | Schema/provenance audit and a reproducibility check against component sources. | It contains sources that overlap the Five States composite; therefore it is not independent. | Overlap audit only; never label as external validation. |
| UCI Heart Failure Clinical Records | Robustness to a different clinical population and a related but different outcome (`death_event`). | 299 records and a different endpoint; feature mapping and target meaning do not match CVD diagnosis. | Optional stress test/sensitivity analysis, not the primary external test. |
| NHANES public-use files | Population-shift and prevalence-shift analysis using survey-weighted covariates and a harmonized self-reported CVD outcome. | Self-reported outcome, changing survey cycles, complex sampling, and incomplete feature alignment. | Possible transportability analysis if the endpoint and covariate subset are prespecified. |
| MIMIC-IV | Independent hospital EHR validation with rich clinical provenance. | PhysioNet credentialed access, required training, difficult phenotype definition, temporal/site confounding, and feature mismatch. | Strongest long-term external-validation candidate if access is obtained before model freeze. |
| eICU-CRD | Multi-center ICU validation and site-shift analysis. | Credentialed access, ICU-only population, and a different case-mix from outpatient/benchmark cohorts. | Secondary external/shift analysis if target phenotype is defensible. |

## 3. External-validation rule

The external dataset must be selected and frozen before final feature-map, threshold, calibration, and model selection decisions. No label-based tuning, recalibration, threshold selection, or repeated model comparison may be performed on that dataset. If the only obtainable source is UCI or another source already embedded in `heart5.csv`, the study must report replication or overlap analysis rather than independent validation.

## 4. Acquisition status

No new dataset has been downloaded in this stage. The next gate is to create a provenance manifest with source URLs/DOIs, version/date, license, cohort definition, target definition, feature mapping, overlap tests, and access status before any external labels are inspected for model development.
