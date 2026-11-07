# External cohort access pathways

**Checked:** 2026-11-05. This is a screening log, not a claim that the search
covered every dataset.

## Candidate decisions

| Candidate | Fit to current study | Access | Current decision |
|---|---|---|---|
| UCI Statlog Heart | Same variables/outcome as Cleveland after harmonization | Public | Excluded: local exact row-level audit found 270/270 records match Cleveland |
| Heart Disease Clinical Dataset for AI Research (Mendeley, 2026) | 918 rows, same 11 predictors and binary target as Heart5 | Public Mendeley Data record, CC BY 4.0 | Excluded: downloaded file matches all 918 Heart5 labeled rows exactly; it is a duplicate release, not an unseen cohort |
| UCI Z-Alizadeh Sani | Source-distinct Tehran cohort, 303 patients; age, sex, and fasting glucose can be mapped | Public UCI release, CC BY 4.0; already acquired and evaluated as CD-XD-003 | Keep as a source-distinct transport stress test, not endpoint-identical validation: target is `>=50%` versus source `>50%`; no patient IDs for person-level overlap audit |
| Duke ACATH | Independent cath-lab cohort; its significant-CAD threshold is stricter than the source threshold | Public source data already acquired | Keep as an endpoint-mismatched stress test, not endpoint-compatible validation |
| AngioCAD | Independent hospital and stenosis-based target; 377 records had matching features | Public source data already acquired | CD-XD-004 is an external cohort result; CD-XD-006 is post-hoc because AngioCAD was already examined |
| MultiD4CAD | Independent Palermo CCTA cohort with clinical risk factors and CAD labels; 118 patients (78 CAD, 40 no CAD) | Restricted Zenodo record; signed DUA, public Zenodo identity, and a request to the dataset team are required | Candidate for a separate CCTA-domain stress test after access and label audit; not a drop-in substitute for the source invasive-angiography endpoint |
| APPROACH registry | Large Alberta cath/ACS cohort with clinical and procedural information | Contact study team; no direct public download listed | Stronger potential scale, but access, endpoint mapping, and collaboration are unresolved |
| ACC NCDR | Large clinical registry with relevant cath data | Hospital/practice data are not public and require written permission | Not directly obtainable from this workspace |
| Angiographic dataset for stenosis detection (Mendeley) | 100 patients with confirmed one-vessel disease; angiographic images and stenosis boxes, with stenosis defined by QCA/physiology criteria | Public, CC BY 4.0 | Exclude from this tabular patient-level model: image-only labels and a positive-only cohort do not match the source feature map or binary endpoint |
| ARCADE | Public X-ray angiography frames annotated for artery and stenosis-detection tasks | Public Zenodo download | Exclude: image/frame annotations do not provide a compatible patient-level clinical feature map and endpoint |
| AngioLens | Angiography images from one hospital, including normal and stenosis categories | Zenodo record is public but files are restricted | Exclude for this project: access is restricted and the image task does not match the current tabular input/endpoint |
| VISION-CAD | Longitudinal cohort of 300 people with residual coronary plaque after clinically indicated angiography | Research-data catalog lists an access pathway; patient data are not an open download | Exclude as a current external test: selected residual-plaque population and longitudinal plaque-progression outcomes differ from the source binary stenosis endpoint |

## Additional public-source screen (2026-11-05)

A targeted search of official dataset records and data descriptors found the
additional candidates above, but no new independent, endpoint-compatible
patient-level tabular cohort. The 2026 Mendeley clinical heart dataset is public
under CC BY 4.0 and has the same 918-row schema and class counts as Heart5. The
downloaded file SHA-256 matches Mendeley's API hash, and a 12-column
row-multiset comparison found exact labeled matches for 918/918 rows. It adds
no independent patients. See `CD-DATA-001` in
`results/external_candidate_screen_20261105/mendeley_heart_disease_2026_overlap.json`.

The Mendeley angiography
collection contains images from 100 patients already confirmed to have
one-vessel disease, with stenosis labels tied to QCA or physiologic criteria;
it is not a negative/positive clinical prediction cohort. ARCADE and AngioLens
are image-centered datasets, and AngioLens files are restricted. VISION-CAD is
a selected longitudinal plaque cohort, not an untreated test cohort for the
current endpoint. These candidates were screened and not downloaded or added
to model evaluation.

## Follow-up access review (2026-11-05)

A second source-level check was made because the project still lacks an untouched
endpoint-compatible cohort:

| Candidate | Source evidence and fit | Decision |
|---|---|---|
| CARDIIGAN, Innsbruck | The published study reports 4,888 elective angiography patients and obstructive CAD defined as at least 50% stenosis in a main coronary artery. Its data-sharing statement says no additional data are available. It is one center, and `>=50%` is not exactly the source `>50%` boundary. | Strong methodological candidate, but not currently obtainable or an exact endpoint match. Contacting the authors would be required; do not count it as external validation without the patient-level data and a frozen mapping. |
| APPROACH/Ottawa/UHN multi-institutional study protocol | The 2026 protocol describes data from five institutions and an expected sample around 6,000; patient-level data are to remain in secure institutional environments and are not publicly released. | Best future multi-site access lead, but this is a protocol/access pathway rather than an available cohort. Requires a qualified institutional investigator, ethics/data-use approvals, and collaboration. |
| MHI QCA/CathAI cohort | Published work describes image/video-level stenosis data from 709 patients/858 exams, with QCA labels at artery/lesion level and a selected trial population that excluded obstructive CAD at baseline. | Not a drop-in target for CARDIODIAG's tabular patient-level prediction features and endpoint. Could support a separate image-domain study, which is outside this prototype. |

The official AngioCAD Zenodo record was also checked directly. It exposes the
large image archive plus `AngioCAD_Features.xlsx` and `AngioCAD_Labels.xlsx`;
the workbook has an `FBS` field but no unit dictionary. The 36 IDs without
matched feature rows are therefore not recoverable from the released
workbooks. The paired age/sex-only sensitivity is the available local response;
the unit and omitted rows require source-author clarification.

This review found no newly accessible public, patient-level tabular dataset
that simultaneously provides pre-outcome clinical predictors, an endpoint
compatible with the source angiographic definition, and sufficient independent
sites. The project remains a one-site external evaluation, not multi-site
generalization evidence.

## MultiD4CAD request preparation

The public Zenodo record describes a controlled-access dataset of 118 CCTA
patients and points to a DUA. The associated data paper instructs applicants
to sign the DUA, email it to the dataset team, identify their public Zenodo
username/email, request Zenodo Reader access, and then download the files. The
agreement makes the named investigator responsible for data-controller
obligations and prohibits redistribution. The unsigned source DUA was saved at
`data/access_requests/multid4cad/DUA.pdf`; provenance and SHA-256 are recorded
in `data/access_requests/multid4cad/source.json`.

The dataset is **not treated as acquired or authorized**. Its 118 rows are not
assumed to meet the workflow's external precision targets. No identity was
created or exposed, no DUA was signed, and no request was sent. The reported
label is CAD/no CAD from a single CCTA site; it is not documented as the same
angiographic `>50%` stenosis target used by this project's source dataset. Its
118 patients are insufficient to claim broad external validation without a
precision analysis. If access is obtained by an authorized investigator, first
audit label definition, clinical-feature availability, time ordering, and the
DUA before deciding whether it can support a secondary stress test.

## Sources

- [MultiD4CAD Zenodo record](https://zenodo.org/records/15148653)
- [MultiD4CAD data paper and access instructions](https://pmc.ncbi.nlm.nih.gov/articles/PMC12475242/)
- [UCI Z-Alizadeh Sani dataset record](https://archive.ics.uci.edu/dataset/412/z%2Balizadeh%2Bsani)
- [Mendeley 2026 Heart Disease Clinical dataset](https://data.mendeley.com/datasets/nt4y898vyh/1)
- [Mendeley 2026 overlap audit runner](../experiments/audit_mendeley_heart_2026_overlap.py) and [machine-readable result](../results/external_candidate_screen_20261105/mendeley_heart_disease_2026_overlap.json)
- [Heart5-to-UCI source-lineage audit](../results/data_provenance_audits/heart5_uci_lineage.json)
- [CD-XD-003 protocol](TRANSFER_STUDY_PROTOCOL_20261105_ZAS.md) and [results](TRANSFER_STUDY_RESULTS_20261105_ZAS.md)
- [APPROACH data profile and access status](https://atlaslongitudinaldatasets.ac.uk/datasets/approach)
- [APPROACH registry information](https://libin.ucalgary.ca/research/approach/about)
- [ACC NCDR data availability FAQ](https://cvquality.acc.org/NCDR-Home/about-ncdr/faqs)
- [Mendeley angiographic dataset record indexed by the US National Library of Medicine](https://datasetcatalog.nlm.nih.gov/dataset?q=0002934893)
- [ARCADE official Zenodo record](https://zenodo.org/records/10390295)
- [AngioLens official Zenodo record](https://zenodo.org/records/20813162)
- [VISION-CAD research data catalog entry](https://researchdata.edu.au/health/view/3485148)
- [UCI Statlog record-level overlap audit](../data/external/uci_statlog_heart/overlap_audit.json)
- [Current dataset compatibility decisions](DATASET_COMPATIBILITY.md)
- [CARDIIGAN 4,888-patient study and data-sharing statement](https://pmc.ncbi.nlm.nih.gov/articles/PMC5558815/)
- [2026 five-institution APPROACH/Ottawa/UHN study protocol](https://bmjopen.bmj.com/content/16/4/e108799)
- [CathAI QCA stenosis cohort methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC10421915/)
- [AngioCAD Zenodo record and released workbooks](https://zenodo.org/records/15826856)
