# Archive audit

## Inventory

The working tree contains 15 ZIP archives. The four original RAR paths are
tracked deletions in the pre-existing worktree and are not present for content
inspection.

The four historical research directories are now preserved under
`archive/historical_notebooks/`. The two expanded distribution trees are
preserved under `archive/release_snapshots/`; the `dist/` directory now holds
the ZIP distribution artifacts only.

| Archive group | Count | Assessment |
|---|---:|---|
| Kaggle source archive under `data/` | 1 | Dataset provenance artifact; retain locally, licensing unresolved |
| Release ZIPs under `dist/` | 6 | Generated distribution candidates; compare and retain only release versions needed |
| Expanded original distribution's nested LIME ZIPs | 4 | Duplicates of the four top-level LIME ZIPs |
| Top-level LIME ZIPs | 4 | Historical research artifacts; retain until provenance comparison is complete |

## Verified duplicate archives

The following pairs are byte-identical by SHA-256:

- `Paper 1 Code LIME with Diagrams/.../LIME_outputs_20251106_104637.zip`
  and the same path under `dist/CARDIODIAG_Original_Kaggle/`
  (`D599E305933AAE7062D415F8AD64F03C5699280309DECAD72EC9AD576E41A1D5`).
- `NOVEM_CVD_LIME_Report_Latest(3).zip` in both locations
  (`B107DFA203EDEB8DB333B02C0D7465EF1F0DFC8C8B6501212B79120C9652F9B6`).
- `NOVEM_CVD_LIME_Report_Latest(5).zip` in both locations
  (`A6E6B562DEAF27E6C9DDFFAF6C36EA171EEE98F91B9987551052A4C6CBFB5237`).
- `NOVEM_CVD_LIME_Report_Latest(6).zip` in both locations
  (`6745F5008F1F51C40E411925D3B12A9C3EA3FD7D654570D27F6D424DDFA4AC6`).

No archive was deleted. The nested copies are candidates for removal only after
the distribution ZIP is confirmed to be generated from the current tree and
the top-level historical copy is designated canonical.

## Non-identical release ZIPs

The four `CARDIODIAG_Original_Kaggle*.zip` files have different sizes and
SHA-256 values. They must be treated as separate release snapshots until their
manifests and contents are compared. `CARDIODIAG_Kaggle_Minimal.zip` and
`CARDIODIAG_Kaggle_Release.zip` are also different packages.

## Recommendation

Keep the source dataset archive and one canonical copy of each historical LIME
archive. Mark release ZIPs as generated distribution artifacts and document
which one, if any, is the supported release. Do not extract archives
automatically or delete the RAR entries during this maintenance task.
