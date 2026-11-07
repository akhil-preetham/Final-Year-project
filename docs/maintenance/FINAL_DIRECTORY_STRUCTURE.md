# Proposed final directory structure

```text
src/
  cardiodiag/
  clin_adapt/
experiments/
  cardiodiag/
  clin_adapt/
configs/                         # only if non-empty configuration files exist
data/
  manifests/
  kaggle_cardiovascular_70k/
results/
  cardiodiag/
  aura/
  clin_adapt/
docs/
  architecture/
  methodology/
  research/
  reports/
  maintenance/
paper/
demo/
tests/
  cardiodiag/
  clin_adapt/
archive/
  historical_notebooks/
  historical_results/
  release_snapshots/
```

The implemented tree uses `archive/historical_notebooks/` and
`archive/release_snapshots/`. `results/` retains its existing protocol-specific
subdirectories and now has `results/RESULT_INDEX.md`; no empty
`historical_results/` directory was created.

Existing result paths used by the manuscript and experiment registries remain
unchanged.
