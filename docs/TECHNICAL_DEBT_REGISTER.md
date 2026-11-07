# Technical debt and unresolved evidence register

**Assessment date:** 2026-11-05. No item is marked resolved by assertion alone.

| ID | Finding | Class | Status | Resolution/evidence |
|---|---|---|---|---|
| TD-01 | Active local remediation state is uncommitted and checked out on original authors' commit | Engineering/reproducibility | FAIL for clean release handoff | Create a reviewed project-owned snapshot/commit before release; do not push to upstream original repository |
| TD-02 | Exact original LoRAS/XAIH-DRC/LIME/PCA protocol and table lineage unavailable | Scientific/reproducibility | BLOCKED | Requires canonical original supplement, settings, environment, split indices and run-to-table mapping |
| TD-03 | No untouched second endpoint-compatible external cohort | Scientific/external dependency | BLOCKED | Requires legitimate compatible cohort, frozen protocol, overlap audit, and units/codebook |
| TD-04 | One-site AngioCAD performance has poor calibration and weak feature OOD | Statistical/methodological | PARTIAL; claim remains NO-GO | Requires additional independent sites and predeclared calibration/shift evaluation |
| TD-05 | Integrated selective AngioCAD coverage 5.6%; unknown-site gate rejects all sites | Methodological/utility | PARTIAL | Current policy is fail-closed; useful risk-coverage operation not demonstrated |
| TD-06 | Patient-level linkage unavailable across source datasets | Scientific/data | BLOCKED | Requires lawful common linkage keys or source-provided overlap analysis |
| TD-07 | Mendeley diagnostic reference standard/timing unclear; AngioCAD FBS unit absent | Data/documentation | BLOCKED | Requires authoritative codebooks/source confirmation; do not infer semantics |
| TD-08 | Full matched factorial across all selectors, learners, calibration, OOD and selective policies absent | Statistical/compute | PARTIAL | Original A–L key unavailable; existing A–L matrix is a workstream crosswalk, not completed factorial |
| TD-09 | Manuscript author order/individual affiliations, ethics determination, funding, coauthor contributions, conflicts, venue, and all-author approval pending | External dependency/documentation | BLOCKED | Requires factual project-team/institution input |
| TD-10 | Redistribution rights for some derived/release outputs, especially 70K-derived results, unsettled | Legal/data governance | BLOCKED | Requires dataset-specific license review; do not redistribute uncertain files |
| TD-11 | Local QA records 106 collected tests passing, but pytest console wrapper has a uv trampoline issue | Engineering | PARTIAL | Python-module invocation passes; wrapper/environment issue documented in QA_REPORT.md |
| TD-12 | Fresh-environment installation/reproduction by an independent researcher not evidenced | Reproducibility | PARTIAL | Requires clean external environment and independent operator |

There are no known remediable critical or major defects identified in the corrected split/preprocessing path by the recorded audits. The table retains material defects, blocked evidence, and the release-state issue; therefore the broad research objective and publication submission are not PASS.
