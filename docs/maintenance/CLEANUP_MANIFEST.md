# Cleanup manifest

This is the controlled action manifest. `UNCERTAIN` means retain the item until
additional provenance or reference evidence is available.

| Path or class | Action | Reason | Risk |
|---|---|---|---|
| `src/cardiodiag/` | KEEP | Active reusable CARDIODIAG and AURA-ML implementation | Low |
| `src/clin_adapt/` | KEEP | Separate active research package | Low |
| `experiments/` | KEEP | Referenced experiment runners and registries | Low |
| `tests/` | KEEP | Verification surface | Low |
| `data/manifests/` and local benchmark data | KEEP | Provenance and reproducibility inputs | Medium |
| `results/` | KEEP | Frozen, exploratory, and failed evidence | Medium |
| Historical notebook directories | ARCHIVE | Historical research evidence, not active modules; moved under `archive/historical_notebooks/` | High |
| `dist/` expanded trees | ARCHIVE | Generated release snapshots; moved under `archive/release_snapshots/` | Medium |
| Top-level and nested LIME ZIP pairs | MERGE candidate | Byte-identical archive pairs | Medium |
| Four deleted RAR entries | UNCERTAIN | Pre-existing user deletion; original binary absent | High |
| `catboost_info/` | DELETE candidate | Training log output, reproducible and generated | Low |
| `.pytest_cache/`, `.ruff_cache/`, `.venv/` | IGNORE/DELETE candidate | Local generated environment and caches | Low |
| `paper/manuscript.backup_*.tex` | KEEP pending review | Historical manuscript snapshots may support provenance | Medium |
| `src/*.egg-info/` | REGENERATE candidate | Build-generated package metadata | Low |

No MOVE, MERGE, ARCHIVE, or DELETE action should be executed until the
corresponding references and baseline checks are recorded.
