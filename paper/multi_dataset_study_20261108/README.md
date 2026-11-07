# CARDIODIAG multi-dataset study manuscript

This source bundle contains the six-page manuscript and the figures and generated tables used in the delivered PDF. It corresponds to experiment run `20261107T202404Z`. Raw clinical datasets and row-level predictions are not included.

## Build

From this directory, run `tectonic -k --keep-logs -o build main.tex`. The delivered PDF was rebuilt from this source bundle with Tectonic 0.17.0. A current TeX Live or MiKTeX installation with BibTeX is also suitable.

## Contents

- `main.tex`: manuscript source.
- `references.bib` and `main.bbl`: citations and resolved bibliography.
- `tables/`: result tables generated from saved aggregate experiment outputs.
- `figures/`: manuscript figures.
- `run_metadata.tex`: experiment run identifier and figure path.
- `BUILD_MANIFEST.json`: build version, page count, warnings, and checksums.
