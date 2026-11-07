# License and attribution notes

This repository is a research extension of the supplied CARDIODIAG source
checkout. The historical notebooks, archived files, and datasets retain their
original attribution and licensing obligations.

## Base publication

M. J. Khan, B. Raza, and A. Nadeem, “CardioDiag: a machine learning approach
for cardiovascular disease diagnosis using XAI-guided hybrid dimensionality
reduction and optimized-based ensemble classifiers,” *PeerJ Computer Science*,
vol. 12, e4059, 2026. DOI: `10.7717/peerj-cs.4059`.

## Original repository

`https://github.com/jaffarkulachi/Cardio-Diag-Approach-Code`

The original repository is preserved as the source of the historical notebooks.
The code under `src/cardiodiag/` is a separately labelled research extension;
it is not presented as the original authors’ implementation.

## Mendeley dataset

`https://data.mendeley.com/datasets/dzz48mvjht/1`  
DOI: `10.17632/dzz48mvjht.1`  
The Mendeley record identifies the dataset as CC BY 4.0. Any redistribution
must preserve the dataset attribution and the upstream terms.
The official one-page codebook is retained at
`data/external/mendeley_cardiovascular_2021/Cardiovascular_Disease_Dataset_Description.pdf`
and hash-checked against the Mendeley API. It defines the binary target as
absence/presence of heart disease but does not state the diagnostic reference
standard or angiographic threshold. See
`data/manifests/mendeley_cardiovascular_2021.json`.

## UCI Heart Disease dataset

Janosi, A., Steinbrunn, W., Pfisterer, M., and Detrano, R. (1989). *Heart
Disease*. UCI Machine Learning Repository, dataset 45, DOI
[`10.24432/C52P4X`](https://doi.org/10.24432/C52P4X). The UCI record identifies
the dataset as CC BY 4.0. The downloaded archive and component files are
attributed in `data/manifests/uci_heart_disease_transfer_study.json`. The
Heart5 provenance audit maps all 918 table rows to observed UCI component rows
(914 uniquely, four ambiguously due to source missing fields); it does not
recover the Heart5 imputation history. See
`results/data_provenance_audits/heart5_uci_lineage.json`.

The row-level match supports attribution to the CC BY 4.0 UCI source. The local
composite has no separate license notice or complete transformation/imputation
record, so do not describe the composite's standalone redistribution status as
fully cleared until its owner or source authors confirm the derived-file terms.

The exact upstream Kaggle-hosted 1,190-row source artifact, owner, version and
license have not been recovered. Treat the local `heart5.csv` and its
row-level derivatives as rights-unresolved and exclude them from public data
releases. See `docs/FINAL_DATASET_ATTRIBUTION_REGISTER.md`.

## Mendeley 2026 Heart Disease dataset

Saha, A., Arifen, R., and Azad, A. (2026). *Heart Disease Clinical Dataset for
Artificial Intelligence and Healthcare Research*. Mendeley Data, version 1,
DOI [`10.17632/nt4y898vyh.1`](https://doi.org/10.17632/nt4y898vyh.1). The record
declares CC BY 4.0. The downloaded `heart.csv` was used only for provenance
screening and exactly duplicates the 918-row Heart5 table; it is not counted
as independent validation. Preserve the attribution if reusing that copy.

## Cardiovascular Disease 70K dataset

The local file is attributed to the Kaggle dataset by Svetlana Ulianova at
`https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset`.
The retrieved Kaggle metadata reports its license as `Unknown`; do not
redistribute the raw file unless the upstream rights are confirmed. A
byte-level scan of the six current ZIP packages found no exact copy of the
70K CSV. Derived 70K tables remain in some historical packages, and this scan
does not establish rights for those results. See
`results/data_provenance_audits/distribution_data_audit.json`.
The official Kaggle dataset page still displays `Unknown` for the license;
therefore the 70K raw dataset and row-level derivatives are excluded from any
new public data bundle until the exact upstream artifact and reuse terms are
verified. Prior 70K experiment artifacts remain preserved locally and retain
their exploratory status. See `docs/FINAL_DATA_RELEASE_MANIFEST.md`.

## UCI Z-Alizadeh Sani dataset

Alizadehsani, R., Roshanzamir, M., and Sani, Z. (2013). *Z-Alizadeh Sani*.
UCI Machine Learning Repository, dataset 412, DOI
[`10.24432/C5Q31T`](https://doi.org/10.24432/C5Q31T). The UCI record identifies
the dataset as CC BY 4.0. Attribute the downloaded archive and workbook in
`data/manifests/uci_z_alizadeh_sani_external.json`. The study report documents
the different endpoint boundary and does not present the data as an
endpoint-identical external validation cohort.

## AngioCAD dataset

Hosseini, M. S., Naghsh-Nilchi, A. R., Safayani, M., et al. (2026). *AngioCAD:
A public X-ray angiography dataset and an adaptive fusion framework for
stenosis detection*. Computer Methods and Programs in Biomedicine, 282, 109368.
Article DOI [`10.1016/j.cmpb.2026.109368`](https://doi.org/10.1016/j.cmpb.2026.109368).
Dataset DOI [`10.5281/zenodo.15826856`](https://doi.org/10.5281/zenodo.15826856).
The Zenodo record identifies the files as CC BY 4.0. The clinical-feature and
artery-label workbooks used in `CD-XD-004` are listed with SHA-256 hashes in
`data/manifests/angiocad_external.json`. The report documents that 36 of the
413 labeled IDs lack a matching clinical-feature row in the public workbooks.
The raw workbooks are CC BY 4.0 and may be shared with source attribution,
license link and change notice. The lack of cross-dataset identifiers means
the separately reported site does not establish patient-level independence.
Use the detailed notice at `data/attribution/ANGIOCAD.md`.

## Duke ACATH

The Duke Cardiac Catheterization dataset is supplied by Vanderbilt Biostatistics
from the Duke University Cardiovascular Disease Databank. The provider says
anyone may use it with requested attribution, but provides no dataset DOI or
standardized license and does not clearly state raw-file redistribution rights.
The project therefore does not redistribute the raw workbook or row-level
derivatives. See `data/manifests/duke_acath_external.json`.

## Proposed code-only release

The final release plan excludes all raw data. The old `dist/*.zip` files are
legacy archives and are not approved for public upload because they contain
dataset copies and/or derived 70K artifacts whose rights were not fully
reviewed. Individual CC BY attribution notices are under `data/attribution/`;
see `docs/FINAL_DATA_RELEASE_MANIFEST.md` for the allow-list and exclusions.

## Research-use warning

The implementation is for reproducible research and education. It has not been
prospectively or clinically validated and must not be used to diagnose or treat
patients.
