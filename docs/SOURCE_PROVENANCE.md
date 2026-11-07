# Original-source provenance

## Audited source

| Field | Value |
|---|---|
| Repository | `https://github.com/jaffarkulachi/Cardio-Diag-Approach-Code` |
| Audited branch | `main` |
| Audited commit | `e63b02c8a2aba6344a48025f657696fd99ac3a5f` |
| Tags | `1.0.0`, `v1.0.0` |
| Local clone | Temporary read-only clone outside this repository |
| Source license | No license file was present in the audited root checkout |
| Repository contents | README, two CSV datasets, one dataset marker, and four RAR archives |

The original checkout was cloned without editing, and its working tree was
clean. The expanded historical material in this repository is preserved under
`archive/historical_notebooks/` and is not treated as an authoritative,
portable build of the original project.

## Root-file hashes

The local source checkout contains the same dataset hashes recorded in
`data/manifests/local_datasets.json`:

- `heart5.csv`: `e4068802a044e8a1e3ae9fa81deae7025711bf4f13e3057f96e4f1cf3b0180c2`
- `MendeleyCardiovascular_Disease_Dataset.csv`:
  `9376367dde41e79e432d6402ea5d9e44223fc318ff54ed09966d721923947d1e`

The four original RAR files are retained as pre-existing deleted Git paths in
the working tree. Their expanded counterparts remain available in the archive
area; no historical evidence was removed by the reconstruction work.

## Paper provenance

The supplied file `../peerj-cs-4059-BASE_PAPER.pdf` is the 61-page published
article by Khan, Raza, and Nadeem, “CardioDiag: a machine learning approach for
cardiovascular disease diagnosis using XAI-guided hybrid dimensionality
reduction and optimized-based ensemble classifiers,” *PeerJ Computer Science*,
volume 12 (2026), DOI `10.7717/peerj-cs.4059`, published 2026-08-25. The article
PDF and the original source commit are audited separately because the commit
dated 2026-01-31 predates publication. Protocol claims from the paper are cited
by article page in `docs/PROTOCOL_AUDIT.md`; code behavior is evidenced by the
archived notebooks. The two evidence sources must not be conflated.

## Provenance boundary

The modern implementation under `src/` is a separately labelled research
reconstruction. It must not be presented as the original authors'
implementation. Historical notebook outputs remain evidence of what was
executed, not proof that the published protocol was leakage-free or portable.

