# Dataset rights audit and machine-readable registry

**Decision:** redistribution of the full research checkout is **BLOCKED**. The safe default is to omit all source data and record-level derivatives. Public download is not treated as redistribution permission.

Detailed dataset citations, local checksums, provenance and overlap findings remain in `FINAL_DATASET_ATTRIBUTION_REGISTER.md`, `OPEN_DATASET_LICENSE_AUDIT.md`, `FINAL_DATASET_PROVENANCE_AUDIT.md`, and `FINAL_DATA_RELEASE_MANIFEST.md`. The new machine-readable registry is `data/registry/datasets.json`. It records identity, version, access, endpoint, independence and release status for key datasets. Missing rights or patient-independence evidence is represented as unresolved/false, never inferred as permission.

| Dataset | Source/version | Rights/access | Task/independence | Redistribution |
|---|---|---|---|---|
| Heart5 / Five States | Local 918-row composite; upstream version incomplete | Exact source and terms unresolved | UCI lineage overlap; not independent | BLOCKED |
| UCI Heart Disease | ID 45, DOI 10.24432/C52P4X | CC BY 4.0 | Development source lineage | Exclude from proposed data-free bundle |
| Statlog Heart | ID 145, DOI 10.24432/C57303 | CC BY 4.0 | Exact Cleveland match | Exclude; duplicate |
| Z-Alizadeh Sani | ID 412, DOI 10.24432/C5Q31T | CC BY 4.0 | ≥50% vs >50%, prior use, linkage absent | Exclude from public package |
| AngioCAD | Zenodo 15826856, DOI 10.5281/zenodo.15826856 | CC BY 4.0 | Nominal >50%; 377/413 feature match, unit/linkage caveats, prior label review | Exclude from data-free package |
| Duke ACATH | Provider repository | Redistribution terms unclear | ≥75% endpoint; prior use | BLOCKED |
| Mendeley cardiovascular 2021 | v1, DOI 10.17632/dzz48mvjht.1 | CC BY 4.0 | Unspecified reference standard/timing; prior benchmark | Exclude from data-free package |
| Mendeley Heart Disease Clinical 2026 | v1, DOI 10.17632/nt4y898vyh.1 | CC BY 4.0 | 918/918 Heart5 row match | Exclude; duplicate and composite rights unresolved |
| Kaggle Cardiovascular 70K | Kaggle sulianova/cardiovascular-disease-dataset | Listing says Unknown | Separate endpoint; explored | BLOCKED |
| MIMIC-IV | v3.1, DOI 10.13026/kpb9-mt58 | Credentialing, CITI and signed DUA | Not a frozen angiographic endpoint | Restricted; not acquired |
| UCI HF / MI | IDs 519 / 579 | CC BY 4.0 | Different endpoints | Not used for current CAD task |
| PTB-XL / PTB-XL+ / Chapman ECG | versioned PhysioNet records | CC BY 4.0 | ECG modality, not tabular angiographic CAD | Not used for current task |
| MultiD4CAD | Zenodo 15148653 | Controlled access/DUA | CCTA task, not current schema | Restricted; not acquired |

The release checker `experiments/check_dataset_release.py` reads this registry and fails closed for unresolved, restricted, or non-allow-listed dataset IDs. It is a guardrail, not a full package scanner or legal determination. Never publish raw data, local patient identifiers, row-level outputs, dataset-derived model bundles, or restricted archives from this checkout without explicit source terms and review.

Additional record screened: Mendeley `bgf5czvpg2/1`, “extention of Z-Alizadeh sani dataset,” v1, DOI `10.17632/bgf5czvpg2.1`, CC BY 4.0. The publisher describes it as an extension of ZAS with artery-level fields; no row-linkage audit was performed. It is excluded as an independent cohort and from the proposed data-free release. Registry ID: `mendeley_zas_extension`.
