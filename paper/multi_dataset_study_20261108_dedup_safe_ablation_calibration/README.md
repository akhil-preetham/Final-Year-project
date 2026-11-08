# CARDIODIAG multi-dataset study manuscript

This eight-page version preserves the existing study and adds source-fitted calibration comparisons, a matched OSEC meta-estimator tuning ablation, and the previously reported selector/class-weight ablation. It corresponds to experiment run `20261107T202404Z`, with duplicate-safe Hungary and VA sensitivity analyses. Raw datasets and row-level predictions are not included.

## Build

From this directory, run `tectonic -k --keep-logs -o build main.tex`. The delivered PDF was compiled from this source bundle with Tectonic 0.17.0. A current TeX Live or MiKTeX installation with BibTeX is also suitable.

## Contents

- `main.tex`: manuscript source.
- `references.bib`, `main.bbl`, and `references.bbl`: bibliography sources and resolved entries.
- `tables/`: result tables generated from saved experiment outputs.
- `figures/`: manuscript figures.
- `run_metadata.tex`: experiment run identifier and figure path.
- `BUILD_MANIFEST.json`: compiler version, page count, warnings, verification results, and checksums.

The previous six-page and seven-page bundles remain preserved. The manuscript is a compiled working draft pending author and affiliation confirmation, institutional ethics determination, declarations, data-use wording, and target venue.
