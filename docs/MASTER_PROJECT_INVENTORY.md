# CARDIODIAG master project inventory

**Inventory date:** 2026-11-06  
**Git baseline:** `e63b02c8a2aba6344a48025f657696fd99ac3a5f` (`v1.0.0`, `origin/main`).

This inventory distinguishes the committed upstream snapshot from the local research tree. At inventory time, `git ls-tree HEAD` contains the original README, two CSVs, a `Datasets` entry and four RAR archives. The active Python package, experiments, test suite, documentation, datasets, results and paper tree are present in the working directory as untracked files (with `README.md` modified). This matters: the work is on disk, but this checkout does not provide Git history for most of it. Nothing was reset or deleted. Preserve a separate backup and establish intended version control before treating this directory as a reproducible release.

## Component inventory

| Component | Location | Status and scientific role | Evidence and known limits | Acceptance condition / dependencies |
|---|---|---|---|---|
| Upstream snapshot | Git `HEAD`, original archives, `Datasets/` | Historical student repository snapshot at recorded commit | Git tracks the original data/result/code archives, not the current Python research package. Archived notebooks have variants and incomplete method detail. | Preserve original commit and archive hashes; avoid claiming exact reproduction where variants conflict. |
| Corrected pipeline | `src/cardiodiag/` | Training-fold preprocessing, OVEC/OSEC baselines, feature selection, calibration, uncertainty, shift and domain guard | `tests/`, nested result manifests, source-only transfer protocols. UCI/Heart5 cohort independence and external confirmation remain unresolved. | Keep transforms inside training folds; maintain full tests and frozen artifacts. |
| AURA research branch | `src/cardiodiag/aura/`, `docs/AURA_ML_*` | Separate research design/prototypes for adaptive/reliability ideas | Design and ablation reports exist; no evidence here supports a confirmed improvement or clinical use. | Treat exploratory versions separately; require frozen, paired external evaluation for claims. |
| CLIN-ADAPT | `src/clin_adapt/`, `tests/clin_adapt/` | Separate domain adaptation research package | Separate package and task; not part of CARDIODIAG CAD headline results. | Keep package, protocols and results separate. |
| Experiment runners | `experiments/` | Nested validation, transfer, data lineage, table/artifact generation | Results have config/data/code hashes in manifests; some historical/exploratory studies are post hoc. | Use new versioned output directories and retain failed runs. |
| Tests and quality | `tests/`, `pyproject.toml`, `uv.lock` | Schema, leakage, models, transfers, provenance, reliability, application-helper tests | Before this iteration, 122 tests passed; this iteration adds five unit tests for LOF and selective audit helpers. Three OpenPyXL warnings on legacy spreadsheets. | Current full-suite and static-check results are in `REPRODUCIBILITY_REPORT.md`. |
| Data and provenance | root CSVs, `Datasets/`, `data/`, `archive/` | Local source files, manifests, licensing and lineage | Heart5/Five States and Kaggle 70K redistribution unresolved; Duke redistribution unclear; derived overlaps documented. | Do not redistribute raw files, record-level derivatives or legacy archives without rights. |
| Result evidence | `results/` | Frozen internal, OOD, reliability, transfer, overlap and audit artifacts | Internal performance is not independent-site validation; the only endpoint-aligned site is already examined and patient linkage is unverified. | Each claim must cite its run manifest/artifact and preserve its evidence class. |
| Manuscript package | `paper/`, `output/pdf/` | LaTeX draft, references, generated tables/figures, built PDFs | Current consolidated draft is 15 pages and built/visually inspected; it is not submission-ready. | Do not publish until scientific scope and author/institution/venue declarations are confirmed. |
| Demonstration | `demo/` | Existing prediction and domain-guard examples; new local Tk desktop app | Older demos are scripts; new app reads a frozen bundle and aggregate artifacts, rejects invalid schema and preserves abstention. Overview, synthetic input, evidence, and explanation-limit screens were visually verified. It is research-only. | No patient data, clinical workflow or deployment claim. |
| Release artifacts | `dist/`, `FINAL_DATA_RELEASE_MANIFEST.md` | Existing ZIPs audited and excluded | Legacy ZIPs contain raw Mendeley and/or 70K-derived material. Code license/redistribution authority is unconfirmed; no clean release archive is approved. | No publication/push/archive until rights, ownership and file-level scan are complete. |

## Relationship of research assets

1. **Original authors' research:** described in the PeerJ paper and inconsistent local archived notebooks. The available snapshot records commit `e63b02c`; the notebooks do not define one uniquely reproducible executable pipeline.
2. **Student repository:** original CSVs and RAR snapshots at the Git baseline. It is not the same object as the current corrected package.
3. **Corrected implementation:** the local `src/cardiodiag/`, `experiments/`, `tests/`, and `results/` research tree. Most is untracked in the current checkout.
4. **Manuscript:** `paper/manuscript.tex` and generated outputs. It must report the corrected and historical evidence separately.
5. **Experiment artifacts:** `results/` JSON/CSV/model bundles/manifests. These support reproducibility, but several target analyses are exploratory or post hoc.

## Snapshot verification

The upstream commit remains `e63b02c`; this work is on the branch
`codex/research-completion-2026-11-06`. The working tree is **not** clean or
fully tracked: most research files were untracked before this iteration. The
branch preserves the base commit but does not convert existing files into
reviewed history. Do not mistake a passing test suite for version-control or
release completeness.
