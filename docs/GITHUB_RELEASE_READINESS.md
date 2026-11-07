# CARDIODIAG GitHub release readiness

**Decision:** local engineering work is ready for review; public repository publication is **BLOCKED**.

## Checklist

| Area | Result | Evidence / resolution |
|---|---|---|
| Existing project preserved | PASS | No rebuild from scratch; work is on `codex/research-completion-2026-11-06` based on upstream commit `e63b02c8a2aba6344a48025f657696fd99ac3a5f`. No prior archive, experiment, or manuscript artifact was overwritten. |
| Source-controlled snapshot | BLOCKED | Most research source, tests, docs, results, paper and data are untracked relative to the base commit. The branch anchor preserves the original commit but is not a complete versioned snapshot. Owner intent and file-by-file tracking review are needed. |
| Project code license | BLOCKED | No root software `LICENSE` is authorized. `LICENSE_AND_ATTRIBUTION.md` is a data/source notice, not a project software license. The original repository's root license was not established in the existing audit. Do not choose a license without the code owner's authority. |
| Dataset rights | BLOCKED for a data-bearing release | The data-free allow-list remains controlling. Heart5 and Kaggle 70K rights are unresolved; Duke redistribution is unclear. Do not include raw data or row-level derivatives. |
| Legacy release archives | EXCLUDE | Six existing `dist/*.zip` files are historical snapshots, not approved release packages. The prior ZIP audit checked exact raw CSV copies and attribution but was not a complete content/rights review. Preserve locally; do not upload. |
| Candidate package contents | NOT BUILT | Building a public archive before rights are established would create an unsafe release candidate. `FINAL_DATA_RELEASE_MANIFEST.md` remains a policy allow-list, not an archive attestation. |
| Secrets scan | LIMITED LOCAL SCAN | A scoped text-pattern scan is recorded below; no credentials should be inferred absent solely from regex results. No dedicated `gitleaks` executable was available at audit time. A full file/zip and provider-side secret scan remains a release gate. |
| Personal paths | FIXED IN ACTIVE DOCS | Two active docs contained local Windows paths and were made portable. Historical archived snapshots include old paths and must be excluded from a public package. |
| Stray root error artifact | PASS — removed | Exact contents were verified as a failed-command error message; file was untracked and unreferenced. Removed using a Windows extended-length path on 2026-11-06. |
| Dependencies | PARTIAL | Clean lock resolves 54 packages; `pip-licenses` reports metadata for 45 third-party packages (`DEPENDENCY_LICENSE_AUDIT.md`). The local project itself is `UNKNOWN`. A full source/notebook/bundled-code license and vulnerability audit remains incomplete. |
| README / install / dataset / evaluation / limits | PARTIAL READY | README, lock-based install guidance, provenance, protocol, evaluation, limitations and ethical scope exist. README was not audited as a final public landing page after every historical claim. |
| `CITATION.cff` | BLOCKED | Author list/order/affiliations are provisional. Do not invent metadata; create citation metadata only after author confirmation. |
| Public push/upload | NOT DONE | No public repository update or upload has been performed. |

## Source scan

The project uses a local keyword scan for likely credential patterns and a scoped path scan. These checks are screening tools, not proof that all secrets or personal information are absent. The active documentation path scan identified the inventory checkout path and a hard-coded local `uv` executable; both were removed from active docs. The scoped credential-pattern scan returned no matches in the scanned active text files. Older archived snapshots remain unchanged and are excluded. A non-text/binary, archive-member, dependency, model, and output-file review is still required before publication.

## Concrete next release gate

1. Confirm code ownership and written redistribution permission from the responsible authors/institution.
2. Confirm author names/order/affiliations for citation metadata.
3. Approve an explicit file allow-list and exclude `data/`, `archive/`, `dist/`, legacy `.rar`, row-level `results/`, model bundles, local environments and non-cleared PDF/source files.
4. Generate an SBOM and dependency-license report; inspect bundled third-party code and notebooks.
5. Build a new archive from the allow-list, scan every member for secrets, data, IDs, local paths and model artifacts, then clean-install and test that exact archive.
6. Obtain explicit project-owner approval before pushing to a public remote.

**Public GitHub release: BLOCKED.** Tests passing do not grant software or dataset redistribution rights.

## Follow-up cleanup

The accidental root `nul` error artifact referenced in the historical audit was content-checked and removed on 2026-11-06 using a Windows extended-length path. It was untracked and no active script referenced it. This resolves that local cleanup item only; it does not change the public-release BLOCKED decision. See `PUBLIC_RELEASE_MANIFEST.md` and `CODE_OWNERSHIP_AUDIT.md`.

