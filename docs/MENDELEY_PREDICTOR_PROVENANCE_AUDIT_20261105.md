# Mendeley Predictor Provenance Audit

**Dataset:** Cardiovascular Disease Dataset, version 1, DOI
`10.17632/dzz48mvjht.1`  
**Local source audit:** `results/data_provenance_audits/mendeley_2021_source.json`  
**Scope:** one-page public codebook, source article, checked CSV, and feature
roles. This is a retrospective benchmark-provenance assessment, not clinical
validation.

## Evidence reviewed

The public record describes 1,000 subjects from one multispecialty hospital in
India and provides a CSV plus a one-page codebook. The codebook gives units or
category meanings for most columns, but only defines `target=0/1` as absence or
presence of heart disease. It does not identify the diagnostic reference
standard, threshold, date, or process used to assign that label. The source
article maps `noofmajorvessels` to major vessels seen by fluoroscopy; neither
the record nor the codebook documents when that procedure occurred relative to
the label or a hypothetical prediction time.

## Field-by-field classification

| Field | Codebook meaning | Provenance class | Main validity concern | Allowed interpretation |
|---|---|---|---|---|
| `patientid` | Patient identification number | Identifier/administrative | Can encode row order or source grouping; not a clinical predictor | Exclude from every model and split feature set |
| `age` | Age in years | Demographic; timing unclear | Collection time and eligibility relative to diagnosis are absent | Retrospective benchmark predictor only |
| `gender` | 0 female, 1 male | Demographic; timing unclear | No timepoint or source-population description beyond one hospital | Retrospective benchmark predictor only |
| `chestpain` | Typical, atypical, non-anginal, asymptomatic | Clinical symptom; timing unclear | May be presenting symptom or recorded after work-up; no timestamp | Do not call a pre-diagnostic feature |
| `restingBP` | Range 94--200 mmHg | Clinical measurement; timing unclear | Measurement setting, timing, and treatment state are absent | Benchmark predictor only |
| `serumcholestrol` | Range 126--564 mg/dL | Laboratory measure; timing unclear | Sample timing, fasting status, treatment, and assay details are absent | Benchmark predictor only |
| `fastingbloodsugar` | Binary: >120 mg/dL | Laboratory-derived binary; timing unclear | Collection time and test protocol are absent | Benchmark predictor only |
| `restingrelectro` | Normal / ST--T abnormality / probable or definite LVH | ECG-derived; timing unclear | An ECG may directly encode diagnostic evidence; timing relative to target is absent | Retrospective benchmark only |
| `maxheartrate` | Maximum heart rate achieved, numeric range 71--202 | Test-derived or measurement context unclear | The codebook does not state protocol, test, or time relative to outcome | Do not assume it is available at early screening |
| `exerciseangia` | Exercise-induced angina, 0 no / 1 yes | Provocation/test-related; timing unclear | May depend on an exercise test; test protocol and timing are absent | Retrospective benchmark only |
| `oldpeak` | ST-related numeric field, range 0--6.2 | ECG/test-derived; exact definition and timing unclear | Potentially direct diagnostic evidence; no timepoint | Retrospective benchmark only |
| `slope` | Peak-exercise ST slope: up / flat / down | Exercise-test-derived; timing unclear | The field refers to a diagnostic test result; prediction-time availability is not established | Retrospective benchmark only |
| `noofmajorvessels` | 0--3; source article describes major vessels seen by fluoroscopy | Possible outcome proxy and potentially post-diagnostic | Angiographic/fluoroscopic evidence may be part of or downstream from diagnosis; temporal order is undocumented | Exclude from early-detection claims; retain only as an explicitly retrospective feature sensitivity |
| `target` | 0 absence / 1 presence of heart disease | Outcome label; reference standard unspecified | No diagnostic procedure, stenosis cutoff, adjudication, or timepoint is stated | Do not equate with UCI/AngioCAD angiographic disease |

“Timing unclear” does not prove that a variable was measured after diagnosis.
It means the public release is insufficient to establish that it was known at
the intended prediction time. Several variables are test-derived and could
make a retrospective classifier appear highly accurate without supporting
early detection.

## Rejection risks and resolution

1. **Undefined outcome construct.** Presence/absence is not an auditable
   reference standard. A high internal AUC cannot repair this missing
   definition. Obtain the protocol and label-generation details from the
   dataset authors or keep the results explicitly benchmark-specific.
2. **Unspecified prediction time.** The dataset provides no index time or
   feature timestamps. Do not describe any Mendeley analysis as prospective,
   early detection, or prediction before diagnostic testing.
3. **Potential outcome-proximal variables.** The fluoroscopy-derived vessel
   count is an especially direct risk. The existing same-split sensitivity
   excluding it changes five nested fold-mean AUCs by only +0.0003 to +0.0007;
   this does not establish that the remaining features are safe or that the
   label is valid.
4. **Single-hospital source.** The record describes one hospital, not a
   multi-hospital external cohort. Do not count Mendeley as an independent
   external test of the CARDIODIAG source data.

## Reproduction and artifacts

- Checked codebook and CSV hashes: `data/manifests/mendeley_cardiovascular_2021.json`.
- Public-record hash confirmation and target definition:
  `results/data_provenance_audits/mendeley_2021_source.json`.
- Feature-exclusion analysis: `docs/VALIDITY_AUDIT_20261105.md` and
  `results/validity_audit_20261105/mendeley_without_major_vessels.json`.
- Original source article: Doppala and Bhattacharyya, DOI
  `10.1155/2022/2585235`.

The dataset itself is licensed CC BY 4.0 according to its public record. That
license does not resolve validity, outcome provenance, or permission for any
separately derived material.
