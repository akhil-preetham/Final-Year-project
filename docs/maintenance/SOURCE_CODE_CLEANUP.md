# Source-code cleanup

## Audited areas

- `src/cardiodiag/` and `src/cardiodiag/aura/`
- `src/clin_adapt/`
- `experiments/`
- `demo/`
- `tests/`

The active tree contains 35 source Python files, 30 experiment scripts, one
demo script, and 21 test files. The source and experiment code totals roughly
7,760 lines before notebooks and generated distributions.

## Findings

- Ruff reports no errors for `src`, `experiments`, `tests`, or `demo`.
- CARDIODIAG, AURA-ML, and CLIN-ADAPT have separate namespaces and should stay
  separate.
- Same-name modules across namespaces are not proven duplicates.
- Experiment scripts are referenced by registries, documentation, or generated
  artifact metadata; none is safe to remove from a filename-only review.
- Dynamic and notebook references make broad dead-code deletion unsafe.

## Action

KEEP all active source and tests pending a narrower call-graph and notebook
reference review. Future cleanup should be limited to demonstrably unused
imports, temporary scripts with no registry or documentation references, and
generated package metadata that is recreated by the build.

