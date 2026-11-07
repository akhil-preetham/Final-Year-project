# AngioCAD Matching and Feature Harmonization Audit

**Audit ID:** `CD-DATA-004-ANGIOCAD-ID-COMPATIBILITY`  
**Machine-readable evidence:**
`results/data_provenance_audits/angiocad_compatibility/angiocad_compatibility_audit.json`  
**Reproduction manifest:**
`results/data_provenance_audits/angiocad_compatibility/reproduction_manifest.json`

## Patient matching and missing records

The public Zenodo record describes 413 patients and releases separate feature
and artery-label workbooks. Independent inspection finds 377 nonblank unique
feature IDs and 413 nonblank unique label IDs. The workbooks have two blank
rows each. The current loader joins on numeric integer `ID` with a one-to-one
merge assertion; it does not join on row order. The resulting 377 matched
records have unique IDs, with no feature ID missing from the label workbook.
Thirty-six public label IDs have no feature row. A naive positional zip would
match only 27 of the first 377 ID pairs. The released record and workbooks do
not explain the 36 missing features, and the absent patient-level values cannot
be reconstructed from the available release.

The 377 matched rows contain 6 missing ages, 0 missing sex values, and 11
missing FBS values. Existing source-fit imputation is valid for those missing
field values; it cannot recover the 36 absent patient feature records.

## Source-to-canonical mapping

| Source field | Proposed canonical field | Current evidence | Primary mapping decision |
|---|---|---|---|
| UCI `age` / AngioCAD `Age` | `age_years` | UCI source defines years; AngioCAD workbook itself has no units or codebook | Retain numeric age only under an explicit provisional years assumption pending source documentation |
| UCI `sex` / AngioCAD `Sex` | `sex_male_female` | AngioCAD categories are `male`/`female`; UCI convention is 1=male, 0=female | Include after explicit normalization |
| UCI fasting blood sugar `>120 mg/dL` / AngioCAD `FBS` | `fbs_gt_120_mg_dl` | AngioCAD values range 55--514, but neither workbook sheet, comments, file metadata, nor record description states a unit | Exclude from a unit-safe primary mapping; preserve historical `mg/dL` results only as conditional sensitivity analyses |
| AngioCAD `26-50` artery label | Stenosis-category label, not a patient feature | Label bins describe stenosis percentages | Do not interpret as age 26--50; exact 50% cases cannot be separated from this bin |

The FBS unit must not be inferred from its numerical range. The public release
contains only the `Main` feature sheet and `Labels` outcome sheet; no embedded
measurement dictionary or cell comments were present in the inspected
workbooks. The unit can only be resolved with source-author documentation or a
complete data dictionary.

## Endpoint and cohort constraints

The target is positive if any of 15 artery segments is labeled 51--75, 76--90,
91--99, or 100; it is negative if every segment is `NL`, 1--25, or 26--50.
This aligns the *positive cut point* to source `>50%`, but the negative 26--50
bin combines values below and at 50%, preventing exact-boundary sensitivity.
The cohort is single-site, and its site-level distinctness does not prove
person-level separation because common cross-dataset identifiers are absent.

## Consequences for the claim

- Report results as applying to 377 matched patients, not all 413 records.
- Keep the 36 unmatched public IDs visible in the JSON audit; do not impute
  synthetic feature rows.
- Do not use FBS as unit-confirmed evidence. The locked CD-XD-004 historical
  result used an explicit assumption and remains preserved as such.
- The post-hoc age/sex ablation removes FBS, but age-as-years remains a
  provisional AngioCAD mapping assumption. It is not fresh validation or a
  replacement for the locked result.
- Do not describe the 26--50 label bin as an age category.
- Additional target patients, a data dictionary, and a new untouched site
  require external source evidence; code changes cannot supply them.

Run the independent audit with:

```powershell
uv run python experiments/audit_angiocad_compatibility.py
```
