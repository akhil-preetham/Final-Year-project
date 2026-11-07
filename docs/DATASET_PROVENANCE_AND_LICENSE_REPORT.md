# CARDIODIAG dataset provenance and license report

**Audit date:** 2026-11-06  
**Controlling detailed records:** `OPEN_DATASET_LICENSE_AUDIT.md`, `FINAL_DATASET_ATTRIBUTION_REGISTER.md`, `FINAL_DATASET_PROVENANCE_AUDIT.md`, `DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md`, and `FINAL_DATA_RELEASE_MANIFEST.md`.

## Current local dataset roles and release status

| Dataset / local role | Source and terms evidenced in this checkout | Lineage / endpoint constraint | Release decision |
|---|---|---|---|
| UCI Heart Disease; source/development | UCI ID 45, DOI `10.24432/C52P4X`, CC BY 4.0 | Cleveland and other source cohorts are part of CARDIODIAG's lineage; it cannot validate itself. | Redistribution is permitted under CC BY 4.0 with attribution and change notice; excluded from proposed data-free package. |
| Statlog Heart; overlap audit | UCI ID 145, DOI `10.24432/C57303`, CC BY 4.0 | Exact 270/270 Cleveland row match after target harmonization. | Not independent validation; do not count as a new cohort. |
| Z-Alizadeh Sani; exploratory transfer | UCI ID 412, DOI `10.24432/C5Q31T`, CC BY 4.0 | ≥50% stenosis vs source >50%; previously examined. | Cite and preserve CC BY attribution; not confirmatory. |
| Mendeley cardiovascular 2021; internal 1,000-row benchmark | DOI `10.17632/dzz48mvjht.1`, v1, recorded CC BY 4.0 | Target reference standard and predictor timing are unspecified; not external validation. | Attribution notice exists; omit from data-free package. |
| Mendeley Heart Disease Clinical 2026; provenance screen only | DOI `10.17632/nt4y898vyh.1`, v1, recorded CC BY 4.0 | 918/918 row multiset match to Heart5; not the 1,000-row benchmark. | Attribution notice exists; not independent. |
| Heart5/Five States composite | Exact upstream source/version/terms unresolved | Mapped UCI records do not recover full composite source, transformations or imputation history. | Raw file and row-level derivatives excluded. |
| Kaggle Cardiovascular 70K | Kaggle listing reports license `Unknown`; exact upstream lineage/version unresolved. | Different feature/endpoint task; not compatible external CAD validation. | Raw data and row-level derivatives excluded pending authoritative rights. |
| AngioCAD structured cohort | Zenodo DOI `10.5281/zenodo.15826856`, CC BY 4.0 | 377 matched feature/label rows of 413 labels; age/FBS units and patient linkage uncertain; outcomes already examined. | Attribute per record; no confirmatory status. |
| Duke ACATH | Vanderbilt repository permits attributed use, but does not clearly grant redistribution. | ≥75% stenosis vs source >50%; previously examined. | Obtain written redistribution terms; exclude raw and row-level artifacts. |
| MultiD4CAD | Controlled access and DUA; not acquired. | No current external-validation role. | Do not download absent required approval; DUA restricts redistribution. |

## Candidates considered for the current tabular CAD task

| Candidate | Official record / access / license | Endpoint and compatibility decision |
|---|---|---|
| UCI Heart Disease | [UCI ID 45](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease), DOI `10.24432/C52P4X`, CC BY 4.0; public download with no credentialing listed. | The source dataset; historical overlap with development data prevents external validation. |
| Statlog Heart | [UCI ID 145](https://archive.ics.uci.edu/dataset/145/statlog%2Bheart), DOI `10.24432/C57303`, CC BY 4.0; public download. | Exact Cleveland duplicate in the local overlap test. |
| Z-Alizadeh Sani | [UCI ID 412](https://archive.ics.uci.edu/dataset/412/z%2Balizadeh%2Bsani), DOI `10.24432/C5Q31T`, CC BY 4.0; public download. | Similar CAD concept, but ≥50% vs >50% endpoint and prior examination; stress test only. |
| Heart Failure Clinical Records | [UCI ID 519](https://archive.ics.uci.edu/dataset/519/heart%2Bfailure%2Bclinical%2Brecords), DOI `10.24432/C5Z89R`, CC BY 4.0; public download. | 299 HF patients; 12 clinical features, no missing values on the UCI record; outcome is death during follow-up. Separate prognosis task. |
| Myocardial Infarction Complications | [UCI ID 579](https://archive.ics.uci.edu/dataset/579/myocardial%2Binfarction%2Bcomplications), DOI `10.24432/C53P5M`, CC BY 4.0; public download. | 1,700 cases and 111 features; predicts MI complications at explicit admission/day-1/day-2/day-3 prediction times. Not the CAD diagnosis endpoint. |
| PTB-XL v1.0.3 | [PhysioNet record](https://physionet.org/content/ptb-xl/1.0.3/), version DOI `10.13026/kfzx-aw45`, CC BY 4.0; open file access under license. | 12-lead ECG waveforms and diagnostic labels; ECG signal task, not compatible tabular angiography. |
| PTB-XL+ v1.0.1 | [PhysioNet record](https://physionet.org/content/ptb-xl-plus/1.0.1/), DOI `10.13026/g6h6-7g88`, CC BY 4.0; open file access under license. | Derived ECG features from PTB-XL, so not a new independent cohort; ECG-specific pipeline. |
| Chapman–Shaoxing–Ningbo ECG v1.0.0 | [PhysioNet record](https://physionet.org/content/ecg-arrhythmia/1.0.0/), DOI `10.13026/wgex-er52`, CC BY 4.0; open file access under license. | 45,152 12-lead ECG records with diagnostic labels; ECG-specific prediction, no merge with CAD tabular task. |
| EPHNOGRAM v1.0.0 | [PhysioNet record](https://physionet.org/content/ephnogram/1.0.0/), ODC-By 1.0 per existing official-record audit; public access subject to license. | ECG and phonocardiogram signals, separate modality/task; ODC-By attribution conditions differ from CC BY. |
| MIMIC-IV v3.1 | [PhysioNet record](https://physionet.org/content/mimiciv/3.1/), DOI `10.13026/07hj-2a80`; credentialed access, CITI training, and signed DUA required. | Broad hospital/ICU EHR data are not a frozen, endpoint-equivalent >50% angiographic CAD cohort. Access and endpoint engineering would be a separate approved task. |

## Decision and preservation rules

No candidate verified in this audit supplies a **new, untouched, patient-independent cohort with the same prediction-time feature schema and endpoint** for confirmatory validation. UCI datasets are accessible and clearly licensed but overlap/are already represented. Z-Alizadeh Sani is close but differs at the endpoint boundary and was used. HF, MI and ECG records have incompatible outcome or modality. MIMIC-IV is credentialed and does not by its existence create an endpoint-compatible angiography cohort. No candidate was downloaded in this iteration.

For CC BY 4.0 sources, preserve creator/source attribution, a license link and indication of changes; do not imply endorsement. For EPHNOGRAM, retain the ODC-By notice and database attribution requirements. Dataset permission does not resolve ethics, privacy, code ownership, third-party content or derivative-work issues. The release allow-list remains data-free; no raw dataset or row-level result is cleared by this summary.
