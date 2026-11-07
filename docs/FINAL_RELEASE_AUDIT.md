# Final code and data release audit

**Decision: public code release BLOCKED; raw-data release NO-GO.** This repository-only audit does not replace legal advice or institutional ownership confirmation.

## Current boundary

- The Git baseline has no root software `LICENSE`; the inspected original repository history/audit likewise did not establish an upstream software license. Do not create one with guessed terms.
- Most of the current research tree is untracked at the upstream baseline. This is a source-control/history gap, not proof that the code is unowned or releasable.
- The data-free allow-list is in `FINAL_DATA_RELEASE_MANIFEST.md`. It is policy, not a built/verified archive.
- Existing `dist/*.zip` archives are excluded. Prior ZIP audits found Mendeley raw data and/or large 70K-derived result artifacts.
- Heart5/Five States exact upstream terms and Kaggle 70K terms remain unresolved. Duke provider-use terms do not explicitly establish redistribution. Do not redistribute raw datasets, row-level predictions/derivatives, record-linked splits, model bundles derived from restricted data, credentials, or untraced archives.
- Preserve CC BY 4.0 notices/attribution and modification statements; preserve ODC-By requirements for EPHNOGRAM if it is ever used. No candidate dataset is added by this directive.
- The local research desktop app reads existing model/evaluation artifacts but stores no input rows and exposes no network server. Its artifacts are not thereby authorized for public release.

## Release readiness checklist

| Gate | Result | Evidence / action |
|---|---|---|
| Source ownership and permission | BLOCKED | Obtain written owner/team authority and establish applicable license. |
| Third-party code/license review | INCOMPLETE | Inventory source/notebook/archive provenance and dependency licenses before bundling. |
| Dataset license/attribution | PASS for documented attribution policy; unresolved sources excluded | See attribution register and per-dataset notices. |
| Data-free allow-list | PASS as policy | `FINAL_DATA_RELEASE_MANIFEST.md`; not proof a package was built. |
| Clean archive and file-level scan | NOT DONE | Only after rights are confirmed, create a new archive with explicit allow-list and scan every member for data, identifiers, credentials, models and prohibited files. |
| Public upload/push | NOT AUTHORIZED | No upload performed; explicit publication approval is still required. |

## Decision

The repository may be used locally for research/engineering. Do not publish or distribute a source archive until ownership/license authority, third-party code status, data exclusions, package scan and explicit publication authorization are resolved. Do not treat “publicly downloadable” as “redistributable.”
