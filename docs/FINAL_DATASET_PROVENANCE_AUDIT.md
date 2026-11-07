# Final dataset provenance audit

The controlling source/license/attribution records are [`FINAL_DATASET_ATTRIBUTION_REGISTER.md`](FINAL_DATASET_ATTRIBUTION_REGISTER.md), [`OPEN_DATASET_LICENSE_AUDIT.md`](OPEN_DATASET_LICENSE_AUDIT.md), [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md), and [`SOURCE_PROVENANCE.md`](SOURCE_PROVENANCE.md). This file points to the audited source of truth and records release implications; it does not replace those item-level records.

## Reconciled high-risk identities

- **UCI Heart Disease:** official UCI DOI `10.24432/C52P4X`; 303-row Cleveland subset and the four-cohort 920-record collection are different scopes. Heart5/UCI matches are not independent validation.
- **Statlog Heart:** UCI DOI `10.24432/C57303`; local 270/270 exact match to Cleveland after harmonizing its class label.
- **Z-Alizadeh Sani:** official UCI record is ID 412, DOI `10.24432/C5Q31T`; do not use the UCI ID 451 link supplied in an earlier candidate list. Endpoint is >=50% stenosis and not identical to source >50%.
- **Heart5/Five States:** named 1,190-row composite; exact upstream artifact/version/terms are unresolved. Treat as unresolved for redistribution, not as cleared because individual rows resemble open UCI records.
- **Kaggle Cardiovascular 70K:** local data use is represented in experiments; the audited listing reports `Unknown` license and exact upstream lineage is not established. Exclude raw and row-level derivatives from public release pending authoritative terms.
- **Duke ACATH:** provider-use terms in the audit do not explicitly establish redistribution permission; >=75% endpoint differs from UCI source >50%.
- **Mendeley cardiovascular data, 2021 (1,000 rows):** local file `MendeleyCardiovascular_Disease_Dataset.csv`, DOI `10.17632/dzz48mvjht.1`; this is the dataset used in the internal 1,000-row benchmark and earlier paper lineage. The public target reference standard and predictor timing are unspecified, so no prospective/early diagnosis or external-validation claim follows.
- **Mendeley Heart Disease Clinical, 2026 (918 rows):** separate record, DOI `10.17632/nt4y898vyh.1`; exact 918/918 row multiset match to Heart5. It was screened for provenance, not used for the 1,000-row internal metrics, and is not an independent cohort.
- **Open candidate tasks:** UCI HF, MI complications, PTB-XL, PTB-XL+, Chapman-Shaoxing-Ningbo and EPHNOGRAM are not merged into the current CAD task. Follow each official record's license/attribution and version notes before future use.

## Release boundary

`FINAL_DATA_RELEASE_MANIFEST.md` is the controlling allow-list policy. No raw data, record-level predictions, record-linked splits, trained model bundles, legacy ZIPs, or unresolved derivatives are approved for release. CC BY attribution/change notices and EPHNOGRAM ODC-By conditions must remain with any future authorized redistribution. The current policy is data-free but does not itself certify a clean archive or code rights.
