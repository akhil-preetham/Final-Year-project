# Public release manifest (proposed; not an authorization)

**State:** NOT APPROVED. This file is a conservative policy checklist, not an assembled release or copyright license.

## Candidate allow-list after permissions

- `README.md`, `pyproject.toml`, `uv.lock`
- `src/`, `experiments/`, `tests/`, `demo/` after file-level authorship and third-party review
- Dataset provenance and acquisition instructions, excluding sensitive access agreements
- Aggregate results only after record-level and redistribution review

## Exclude

- All raw or derived dataset files from `data/`, root CSVs and archives
- `archive/`, `dist/`, all `.rar` files, legacy ZIPs
- Row-level predictions, labels, subject IDs, indices or record-linked outputs under `results/`
- Model bundles trained on data whose redistribution rights are unresolved
- Credentials, local environments, caches, logs and build artifacts
- Manuscript material until author approval and rights review

## Approval gates

| Gate | Status |
|---|---|
| Code ownership and upstream permission | BLOCKED |
| Contributor declarations and attribution | PENDING |
| Dataset-derived output clearance | BLOCKED |
| Dependency and bundled-code license audit | PARTIAL |
| Full file/archive secret and personal-data scan | NOT RUN |
| Clean allow-listed archive and exact-archive checks | NOT BUILT |
| Project owner public-upload approval | PENDING |

No software license is granted by this manifest. Do not push or upload until every gate is resolved and approved.
