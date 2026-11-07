# Repository forensic audit

**Assessment:** 2026-11-05. This audit inventories and interprets the current local project. It preserves historical material and does not treat passing tests as scientific validity.

## Repository identity and state

| Item | Finding | Classification |
|---|---|---|
| Checked-out Git HEAD | e63b02c8a2aba6344a48025f657696fd99ac3a5f, original authors' snapshot | Provenance fact |
| Checked-out branch | main | Provenance fact |
| Tracked working-tree change | README.md modified; project also contains extensive untracked research work | Reproducibility/engineering issue |
| Configured repository purpose | Original authors' upstream, not a publication destination | Publication risk |
| Student public repository | Separate Git history, public HEAD ae30f91adc71675e00619bb5f12235841d71a4fa | Version-boundary fact |
| Local current state | New modules, studies, reports, and manuscript exceed the public snapshot and are not committed | Reproducibility risk |

No commit or push is part of this audit. Do not stage or publish the full current tree without reviewing its untracked files, data rights, and intended remote.

## Structure and evidence

The project contains the Python package in src/cardiodiag, experiment runners in experiments, 34 test files, 132 documents, 57 experiment scripts, manifests, result artifacts, archived historical notebooks/releases, and a paper source/build tree. This is an existing equivalent to a flat version of the requested directory layout; restructuring into duplicated package trees would add risk without scientific benefit.

Core audit trail:

- Original provenance and paper/source boundary: SOURCE_PROVENANCE.md, PROTOCOL_AUDIT.md.
- Original algorithm and fidelity: ORIGINAL_ALGORITHM_WALKTHROUGH.md, ORIGINAL_REPRODUCTION_MATRIX_20261105.md, PAPER_TO_CODE_MAP.md.
- Data identity/overlap: DATA_PROVENANCE.md, DATASET_COMPATIBILITY.md, dataset-provenance audits.
- Experiments and outcomes: MASTER_DIRECTIVE_COMPLETION_MATRIX.md, AUTHORITATIVE_METRIC_REGISTRY.md, CD-XD transfer protocols/results.
- Quality checks: QA_REPORT.md.
- Scientific limitations and remaining inputs: LIMITATION_RESOLUTION_MATRIX.md, REMAINING_WORK_REGISTER_20261105.md.

## Finding classification

| Finding | Type | Disposition |
|---|---|---|
| No single canonical original notebook protocol | Critical scientific issue for exact reproduction | Irreducible with archived evidence; report reconstruction as approximate |
| Leakage-prone pre-split resampling/global transforms in historical variants | Major methodological issue | Corrected runs separate; historical path retained and labelled |
| Current local work is uncommitted and Git HEAD is original upstream | Reproducibility/engineering issue | Must be resolved before release; no publication commit made here |
| Several datasets overlap, and some endpoint/feature semantics differ | Critical scientific issue for external claims | Audited; exclude duplicates or downgrade to stress tests |
| External calibration and OOD performance weak; selective coverage low | Statistical/scientific issue | Negative finding retained; reliable generalization not established |
| Current manuscript facts and data rights are not fully confirmed | Documentation/external dependency | Pending owner/coauthor/institution confirmation |
| Local tests and artifact QA are extensive | Engineering evidence | Supports software integrity only, not validity |

## Audit boundary

This report indexes the current checked-in and local evidence. It does not claim source-independent replication by a second team, a fresh-environment installation by an independent researcher, or prospective clinical validation. The detailed acceptance statuses are in FINAL_ACCEPTANCE_MATRIX_20261105.md.
