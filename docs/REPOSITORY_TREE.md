# Repository tree and responsibilities

```text
src/
  cardiodiag/             corrected CARDIODIAG pipeline and AURA-ML modules
  clin_adapt/             separate CLIN-ADAPT research package
experiments/               reproducible runners and artifact generators
data/
  manifests/               dataset identity, schema, hash, and gate metadata
results/                   generated evidence grouped by protocol/component
docs/                      audits, methodology, evidence, and handoffs
paper/                     manuscript, bibliography, tables, and figures
demo/                      non-clinical demonstration
tests/                     package and experiment tests
archive/
  historical_notebooks/    original notebook workflows and LIME artifacts
  release_snapshots/       expanded distribution snapshots
dist/                      ZIP distribution artifacts
```

The active implementation is intentionally separate from the historical
notebooks. `cardiodiag.aura` is a CARDIODIAG research subpackage; CLIN-ADAPT
remains a separate package and is not merged into CARDIODIAG.

