# Independent cohort search and qualification

**Search cut-off:** 2026-11-06. Search was limited to authoritative dataset records, publisher/institutional descriptions, and existing provenance audits. No dataset was downloaded in this pass.

## Qualification rule

A confirmatory external cohort must have a documented independent population, patient-level non-overlap basis, the same prespecified CAD target definition (>50% diameter stenosis in a major coronary artery), measured prediction-time predictors with compatible units, lawful access, and no prior label use in CARDIODIAG development or policy selection. Missing evidence fails closed. Availability alone does not qualify a cohort.

## Candidate review

| Candidate | Official identity / source | Cohort, endpoint, features and independence | Access / status | Decision |
|---|---|---|---|---|
| UCI Heart Disease | [UCI ID 45, DOI 10.24432/C52P4X](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease) | Four historical cohorts; `num` uses 0 for <50% and 1–4 for >50%. It is already the CARDIODIAG development lineage. Individual names were removed and replaced with dummy values. | CC BY 4.0; already acquired and used. | Reject: source overlap and prior use. |
| UCI Statlog Heart | [UCI ID 145](https://archive.ics.uci.edu/dataset/145/statlog%2Bheart) | Local audit matched all 270 records to Cleveland after target harmonization. | CC BY 4.0; already screened. | Reject: duplicate. |
| Z-Alizadeh Sani | [UCI ID 412, DOI 10.24432/C5Q31T](https://archive.ics.uci.edu/dataset/412/z%2Balizadeh%2Bsani) | 303 patients from a Tehran center; target is ≥50% stenosis, versus source >50%; only age, sex and fasting glucose map cleanly; person IDs unavailable. Evaluated as CD-XD-003. | CC BY 4.0; prior label use. | Reject as confirmatory; retain as transport stress test. |
| AngioCAD | [Zenodo record 15826856](https://zenodo.org/records/15826856), DOI 10.5281/zenodo.15826856 | Isfahan site; endpoint bins start at 51%, nominally aligning to >50%. 413 label IDs, 377 feature matches; FBS units undocumented; cross-source patient linkage unavailable. Evaluated in CD-XD-004 and subsequent post-hoc work. | CC BY 4.0; public. | Reject as confirmatory due prior label exposure and unresolved overlap/features. |
| Duke ACATH | [Vanderbilt Biostatistics repository](https://hbiostat.org/data/repo/acath) | 3,504 records; target threshold ≥75%, not >50%; already evaluated. Participant linkage to CARDIODIAG source not established. | Repository use terms do not clearly settle redistribution. | Reject: endpoint mismatch, prior use, rights uncertainty. |
| Mendeley Heart Disease Clinical 2026 | [Mendeley v1, DOI 10.17632/nt4y898vyh.1](https://data.mendeley.com/datasets/nt4y898vyh/1) | Local multiset comparison found an exact 918/918 match to Heart5; same patient rows, not a new cohort. | CC BY 4.0; screened. | Reject: duplicate. |
| Mendeley cardiovascular 2021 | [Mendeley v1, DOI 10.17632/dzz48mvjht.1](https://data.mendeley.com/datasets/dzz48mvjht/1) | 1,000-row benchmark; endpoint reference standard and predictor timing insufficiently specified; already used. | CC BY 4.0; acquired. | Reject: endpoint/timing incompatibility and prior use. |
| Kaggle Cardiovascular 70K | [Kaggle dataset](https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset) | Different dataset lineage and target; not angiographic CAD endpoint; used in separate exploratory work. | Listing reports license Unknown. | Reject: incompatible task, prior exploration, unresolved rights. |
| UCI Heart Failure Clinical Records | [UCI ID 519](https://archive.ics.uci.edu/dataset/519/heart%2Bfailure%2Bclinical%2Brecords) | 299 heart-failure patients; death during follow-up is the outcome. | CC BY 4.0. | Reject: different clinical prediction task. |
| UCI MI Complications | [UCI ID 579](https://archive.ics.uci.edu/dataset/579/myocardial%2Binfarction%2Bcomplications) | 1,700 cases; time-indexed complications after MI with prediction-time partitions. | CC BY 4.0. | Reject: different endpoint/task. |
| PTB-XL / PTB-XL+ | [PhysioNet PTB-XL 1.0.3](https://physionet.org/content/ptb-xl/1.0.3/), [PTB-XL+ 1.0.1](https://physionet.org/content/ptb-xl-plus/1.0.1/) | ECG waveforms and derived ECG features, with diagnostic labels; not the current tabular angiography input task. PTB-XL+ derives from PTB-XL. | CC BY 4.0; public. | Reject: modality/task mismatch; derivative is not an independent cohort. |
| Chapman-Shaoxing-Ningbo ECG | [PhysioNet 1.0.0](https://physionet.org/content/ecg-arrhythmia/1.0.0/) | ECG records with rhythm/diagnostic labels; no compatible angiographic clinical feature schema. | CC BY 4.0; public. | Reject: modality/task mismatch. |
| MIMIC-IV | [PhysioNet v3.1](https://physionet.org/content/mimiciv/3.1/) | Hospital/ICU EHR; no ready-made frozen >50% angiographic endpoint or CARDIODIAG feature-time definition. ICD extraction would define a different retrospective task. | Credentialed access, CITI training and signed DUA required; derived datasets/models retain sensitivity and sharing limits. | Not a current cohort. Future separately approved study only. |
| MultiD4CAD | [Zenodo record 15148653](https://zenodo.org/records/15148653) | CCTA population (118 patients); image/imaging-derived task, not the current invasive-angiography tabular predictor set. | Controlled access / DUA pathway; not acquired. | Not a drop-in cohort; possible separate protocol after approval. |

## Conclusion and prospective protocol

No qualifying untouched cohort is available in the audited repository and source records. External generalization remains **NOT DEMONSTRATED**. Existing AngioCAD results are the closest endpoint-aligned site evaluation, but labels have already been examined and patient independence cannot be established. No repeated scoring, threshold selection, or relabeling of an already examined cohort can restore confirmatory status.

For a prospective independent-site study: (1) secure institutional and data-provider permission; (2) identify cohort, recruitment dates, site and patient de-duplication basis; (3) define the >50% angiographic outcome and predictor timing/units; (4) complete overlap and schema/unit checks before labels are exposed; (5) hash and freeze model, preprocessing, calibration, thresholds, endpoints, exclusions, and statistical code; (6) open labels once for frozen inference; (7) report bootstrap uncertainty, calibration, shift, subgroup completeness, coverage and selective risk; (8) preserve record-level data only in the authorized environment.

A ready-to-fill access request is in `INSTITUTIONAL_DATA_ACCESS_REQUEST.md`. The existing fail-closed manifest validator is `experiments/check_external_manifest.py`; external scoring is `experiments/run_external_evaluation.py`. They require a frozen manifest and do not authorize access or establish cohort truth.


## Additional repository and literature screen (2026-11-06)

A targeted search of Mendeley Data, Figshare, Harvard Dataverse and published CAD studies identified no additional open patient-level cohort that met the frozen qualification rule. Search is not exhaustive. The [2017 Mendeley extension of Z-Alizadeh Sani](https://data.mendeley.com/datasets/bgf5czvpg2/1) explicitly describes itself as an extension adding LAD/LCX/RCA fields; it is therefore treated as part of the already examined ZAS cohort family, not independent evidence. Its precise row linkage and endpoint boundary have not been audited, which is an additional reason not to qualify it.

The [APPROACH and institutional cross-site validation protocol](https://bmjopen.bmj.com/content/16/4/e108799) and a [recent three-hospital Alberta prognosis study](https://www.sciencedirect.com/science/article/pii/S0828282X25015892) describe access-controlled patient data. The latter predicts mortality/MACE among patients with obstructive CAD, not the current diagnostic endpoint; neither provides an authorized downloadable patient-level cohort for this project. Published multi-site results are useful literature context, not CARDIODIAG validation data. A targeted Mendeley search also found CADICA metadata and an angiography image dataset; both are imaging tasks and do not provide the current compatible tabular cohort.

No Figshare or Harvard Dataverse search result was accepted as a qualifying cohort. Absence from this targeted screen is not proof that no such dataset exists.

## Gate hardening

The external manifest gate now requires cohort population/recruitment, endpoint compatibility evidence, a per-feature schema/unit/prediction-time mapping, authorized evaluation access, documented patient-independence evidence, unseen labels, and explicit positive qualification flags. It rejects prior label exposure and incomplete feature mappings. These flags must be supported by documents; a manifest does not independently verify the truth of a submitter's assertions. Current candidates remain unqualified.
