# Repository audit

## Scope and preservation boundary

This is a read-only audit of the supplied working tree. Existing changes were
recorded before cleanup and are not treated as changes made by this maintenance
task. No files were moved, deleted, or overwritten during the audit.

Initial Git state:

- Branch: `main`, tracking `origin/main`
- Tracked files: 8
- Untracked files (excluding ignored files): 678
- Tracked deletions: four historical `.rar` archive entries
- Tracked modification: `README.md`
- The expanded research implementation and artifacts are currently untracked.

The local tree contains 14,098 files and approximately 1.86 GB, including the
`.venv` directory. Excluding `.venv`, caches, and training logs, the project
content is approximately 0.92 GB.

## Functional areas

| Area | Contents | Action |
|---|---|---|
| `src/cardiodiag/` | CARDIODIAG reusable package and AURA-ML subpackage | Keep active |
| `src/clin_adapt/` | Separate CLIN-ADAPT package | Keep logically separate |
| `experiments/` | Reproducible runners, registries, and report generators | Keep; classify by project |
| `tests/` | Tests for active packages and experiment utilities | Keep |
| `data/` | Manifests and local benchmark data | Keep with provenance controls |
| `results/` | Generated evidence, reports, tables, and registries | Keep; add index |
| `docs/` | Research, methodology, audit, and handoff material | Consolidate navigation only |
| `paper/` | Manuscript, bibliography, tables, figures | Keep; retain backups until reviewed |
| Historical directories | Notebooks, LIME artifacts, and paper-reproduction outputs | Archive logically, do not delete |
| `dist/` | Multiple release trees and ZIP distributions | Treat as generated release material |

## Initial recommendation

The safest first cleanup is documentation and indexing, not destructive
restructuring. The source packages and research artifacts are sufficiently
interconnected that moves should occur only after reference scans and a
reproducibility check. The four deleted RAR entries should not be restored or
removed from history by this task; their expanded directories are present and
must be compared before any archival decision.

