# Experiment provenance audit

**Assessment date:** 2026-11-05.

## Verified evidence families

| Family | Existing artifact/evidence | Recalculation status | Interpretation |
|---|---|---|---|
| Historical Heart5 native approximation | baseline_reproduction_report.md; generated protocol comparison | Stored metrics recorded; historical ordering intentionally resamples before split | Forensic only; not unbiased reproduction |
| Corrected internal nested evaluation | final_completion_20261105 and master_directive_20261105_serial manifests/predictions | Fresh stage matches prior fold means; maximum absolute metric delta 0; 918 and 1,000 rows have saved predictions/splits | Internal development evidence |
| Seed sensitivity | internal_seed_sensitivity_20261105 | Seeds 43–47 audited; per-row coverage and pooled metrics recomputed; seed 42 excluded because source/lock hashes differ | Exploratory split sensitivity, not independent patient samples |
| UCI leave-one-cohort-out | CD-XD-002 results/protocol | Saved predictions and metrics audited | Retrospective domain stress test; source overlap with Heart5 |
| Z-Alizadeh Sani | CD-XD-003 protocol/results | External prediction and source calibration artifacts independently rescored | Source-distinct stress test; threshold mismatch |
| AngioCAD | CD-XD-004 protocol/results and domain-guard audit | Input/code/output hashes match; saved predictions independently rescore to recorded metrics | One-site endpoint-aligned retrospective evidence |
| Duke ACATH | CD-XD-005 protocol/results and domain-guard audit | Saved predictions independently rescored | Endpoint-mismatched stress test |
| Selective component audit | validity_audit_20261105/selective_policy_components | Frozen predictions parsed and summaries recomputed | Post-hoc diagnostic; low coverage, not policy confirmation |
| Artifacts/manuscript | QA_REPORT.md and publication manifest | Hash, PDF, references, rendering and extraction checks recorded | Integrity checks do not prove scientific validity |

## Provenance limitations

The local authoritative reports state corrected OVEC AUC 0.9295/0.9957 and stable OSEC 0.9253/0.9942 on Heart5/Mendeley; UCI LODO macro AUC 0.760; Z-Alizadeh Sani AUC 0.720; AngioCAD AUC 0.787 on 377 records; Duke AUC 0.661; AngioCAD Isolation Forest OOD AUROC 0.589; and integrated AngioCAD selective coverage 5.6%. These values are supported by local stored outputs and audit reports, not by the values alone. Historical and corrected results use different protocols and must not be compared as a winner/loser benchmark.

The historical paper's exact table-to-run lineage is unavailable. The active local remediation tree is uncommitted. Seed 42 is not included in the later seed-sensitivity aggregate because its source/lock hashes differ. No independent second implementation or fresh external research team reproduced the whole study.

**Status:** Internal and transfer artifact integrity is PASS for the listed audited stages. Exact historical metric reproduction and independent external-team reproduction are BLOCKED by incomplete original lineage and lack of an independent team/cohort.
