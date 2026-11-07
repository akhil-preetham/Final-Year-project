# Final CARDIODIAG dataset compatibility matrix

**Updated:** 2026-11-07. This is a landing page for the reconciled compatibility findings. The detailed record is [`DATASET_COMPATIBILITY_MATRIX.md`](DATASET_COMPATIBILITY_MATRIX.md), with licensing in [`OPEN_DATASET_LICENSE_AUDIT.md`](OPEN_DATASET_LICENSE_AUDIT.md), lineage in [`FINAL_DATASET_ATTRIBUTION_REGISTER.md`](FINAL_DATASET_ATTRIBUTION_REGISTER.md), overlap in [`DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md`](DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md), and acquisition recommendations in [`RECOMMENDED_DATASET_ACQUISITION_PLAN.md`](RECOMMENDED_DATASET_ACQUISITION_PLAN.md).

| Dataset | Endpoint and input | Relation to current work | CARDIODIAG tabular CAD role |
|---|---|---|---|
| UCI Heart Disease (Cleveland, Hungary, Switzerland, VA Long Beach) | Stenosis-based heart disease (`num=1..4` vs 0; source definition >50%); mixed clinical predictors | Current development/source lineage; Heart5 contains represented UCI records | Compatible for internal/source-domain stress tests; not independent of Heart5. |
| Statlog Heart | Binary heart disease, Cleveland-like 13 features | 270/270 exact record matches to Cleveland after target harmonization | Duplicate/alias check only; not independent validation. |
| Z-Alizadeh Sani | CAD vs normal by cath, >=50% stenosis; wider mixed feature set | Previously used; no patient IDs for linkage | Endpoint differs at the 50% boundary; transport stress test only. |
| UCI Heart Failure Clinical Records | Death by end of available follow-up in an HF cohort | Acquired 2026-11-07; no cross-source linkage | Separate exploratory binary event task; horizon unspecified; not compatible CAD validation. |
| UCI Myocardial Infarction Complications | Any recorded lethal outcome using admission-time predictors | Acquired 2026-11-07; participant IDs unavailable | Separate exploratory task with later fields excluded; not compatible CAD validation. |
| PTB-XL / PTB-XL+ | Multi-label 12-lead ECG and derived ECG features | No local acquisition; PTB-XL+ derives from PTB-XL | ECG-specific task only; PTB-XL+ is not an independent cohort. |
| Chapman-Shaoxing-Ningbo ECG | ECG rhythm/diagnostic labels and signals | No local acquisition | ECG-specific task only; not tabular angiographic CAD. |
| EPHNOGRAM | ECG/phonocardiogram signals and associated labels | No local acquisition | Signal task only; ODC-By obligations; not tabular CAD. |
| Heart5 / Five States composite | Binary heart/vascular outcome; 1,190-row named composite | Exact upstream Kaggle record and terms unresolved; mapped UCI records present | Existing internal development evidence; not independently releasable or external to its UCI components. |
| Mendeley cardiovascular (2021; 1,000 rows) | Tabular binary target; one-hospital public benchmark | Current local 1,000-row internal benchmark; reference standard and feature timing unspecified | Internal benchmark only; not prospective or external validation. |
| Mendeley Heart Disease Clinical (2026; 918 rows) | Tabular binary heart-disease target | Separate provenance-screened release; exact 918/918 multiset match to Heart5 | Not used for the 1,000-row metrics; duplicate/overlapping data, not independent validation. |
| Cardiovascular 70K | Binary target with separate feature schema | Kaggle license listed Unknown in audit; exact source/version not resolved | Separate benchmark/exploratory task; no pooling with CAD claims and no raw release. |
| AngioCAD | Cath stenosis at nominal >50%; 377 matched features of 413 labels; age/sex/FBS-compatible subset | Different named site; person linkage is unavailable and target was previously examined | Endpoint-aligned stress test only; one-site, post hoc, units partly undocumented. |
| Duke ACATH | At least 75% stenosis; 3,504 target records | Different source, but threshold differs and redistribution terms unclear | Endpoint-mismatched stress test only. |

Open access, an open license, and permission to redistribute are distinct. This matrix does not grant data rights. Raw data and row-level derivatives with unresolved/restrictive terms remain excluded from release.
