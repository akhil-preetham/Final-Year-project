# CARDIODIAG final project audit

**Audit date:** 2026-11-02
**Scope:** repository state, implementation, data, experiments, evidence,
manuscript, tests, provenance, and release hygiene.

> Historical audit. The 2026-11-05 closeout supersedes its PDF, prediction
> persistence, test-count, and source-archive status. See
> `FINAL_RESEARCH_REPORT.md`, `QA_REPORT.md`, and
> `MASTER_DIRECTIVE_COMPLETION_MATRIX.md` for current evidence.
>
> External-validation update: a threshold-aligned AngioCAD evaluation
> (`CD-XD-004`) was completed on 2026-11-05 after this audit. The critical
> finding below describes the earlier audit state; current results are in
> `TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md`.
>
> Manuscript-metadata update: provisional author names and a common affiliation
> were later supplied. Current confirmation gaps and the updated draft are in
> `REMAINING_WORK_REGISTER_20261105.md` and `paper/manuscript.tex`.

## Executive assessment

CARDIODIAG contains a substantial research extension around an archived
notebook-based implementation. The corrected package is runnable locally and
its current tests and lint checks pass. The evidence supports an internal
leakage-controlled comparison and a mixed stability/reliability finding. It
does not support independent transport validation, clinical utility, fairness,
deployment readiness, or a universally superior new algorithm.

## Findings

| Severity | Finding | Evidence | Affected area | Action/status |
|---|---|---|---|---|
| Critical | No endpoint-identical external cohort is frozen | `CD-XD-003` freezes a distinct Tehran cohort but target cut point is `>=50%` vs source `>50%`; no patient IDs for overlap checks | Generalization | A one-way transport stress test is complete; confirmatory endpoint-aligned validation remains blocked |
| High | Historical notebooks contain underspecified or leakage-prone paths | `docs/baseline_reproduction_report.md`, archived notebooks | Historical results | Preserved as historical evidence and separated from corrected results |
| High | Full five-candidate custom 70K CARDIODIAG nested run did not finish | `docs/final_project_completion_report.md`; no complete artifact exists | Large-dataset experiment | Reduced logistic pair and generic benchmark are reported separately |
| High | Manuscript submission metadata was unavailable at this audit date | `paper/manuscript.tex` placeholder at the time; no venue selected | Publication | Later updated with provisional author names/affiliation; factual declarations and venue remain pending |
| High | Dataset redistribution terms are incomplete for local composite/Kaggle data | `data/manifests/local_datasets.json`, `LICENSE_AND_ATTRIBUTION.md` | Licensing | Keep raw-data redistribution conditional; verify upstream terms |
| Moderate | Fold/seed summaries are descriptive resampling intervals, not independent-patient CIs | result artifacts and methods documentation | Statistics | Wording is constrained in manuscript and reports |
| Moderate | Primary nested artifacts do not retain all outer-fold prediction vectors | `results/generated/post_boundary_corrected_nested_*.json` | Recomputability | Treat stored fold/pooled metrics as authoritative; add prediction persistence in a future rerun |
| Moderate | Feature stability and predictive reliability are not interchangeable | post-boundary stability and linkage artifacts | Scientific claim | Use the decoupling audit framing; do not claim stability improves reliability |
| Low | LaTeX PDF compilation is unavailable on this host | no `pdflatex`, `xelatex`, or `tectonic` executable found | Release QA | Source/table/citation checks can pass, but PDF build remains unverified |
| Low | Working tree includes generated release files and expanded archives | `git status --short` | Git hygiene | Preserve user work; stage only an intentional allow-list later |

## Completed components

- Explicit local feature schemas and identifier removal.
- Training-only cleaning, imputation, encoding, scaling, feature selection, and
  inner model selection in corrected pipelines.
- OVEC/OSEC and stable-selector implementation with tests.
- Nested internal validation on the two CARDIODIAG development benchmarks.
- Repeated stability, reliability, calibration, conformal, linkage, and
  evaluation-only robustness analyses.
- Separate 70K model benchmark, tuned models, and compact candidate pool.
- Hash/provenance manifests, fail-closed external gate, registry generation,
  manuscript tables, and non-clinical demo.

## Unsupported claims explicitly prohibited

- Endpoint-identical external validation, prospective utility, or clinical
  transportability.
- Clinical benefit, safety, diagnostic use, or deployment readiness.
- Fairness across attributes not measured in the data.
- Causal interpretation of selected features or XAI explanations.
- Universal superiority of OVEC, OSEC, the stable selector, or any ensemble.

## Acceptance decision

The project is **TECHNICALLY COMPLETE for the checked-in internal research
package**, subject to the stated reproducibility and artifact limitations. It is
not **RESEARCH COMPLETE**, **PUBLICATION PACKAGE COMPLETE**, or **SUBMISSION
READY** because independent validation, publication metadata, licensing review,
and PDF compilation remain unresolved.
