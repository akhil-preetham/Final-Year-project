# Final hostile independent review

## Major criticisms

1. **The primary generalization claim is not established.** One endpoint-aligned site is insufficient to estimate between-site heterogeneity; AngioCAD calibration and OOD results are weak.
2. **Calibration candidate comparison is exploratory.** Temperature scaling improved retrospective metrics but was assessed after the site had been previously examined. It requires an untouched site.
3. **OOD result is task-limited.** External OOD AUROC measures dataset discrimination. The synthetic lab covers a few designed shifts, not natural distribution or concept shift, and does not establish individual error detection.
4. **Selective output is impractical as evaluated.** Combined coverage is 5.6%; zero errors in 21 accepted positive-only records does not estimate discrimination or safety.
5. **Exact original reproduction is not possible.** The historical notebooks are inconsistent and lack full run/configuration lineage.
6. **Data semantics remain uncertain.** Person overlap is unavailable across sources; some endpoints, units and predictor timing remain ambiguous.
7. **Paper submission has factual blockers.** Ethics, authorship, funding, conflicts, data rights and venue require author/institution confirmation.
8. **Release provenance is weak.** The local changes are uncommitted in a checkout whose HEAD/remote are the original authors' repository. Do not publish this tree directly.

## Defect resolution status

Corrected nested pipelines and external source-only protocols address direct preprocessing/tuning/calibration leakage in their named experiments. Tests, lint, compilation and selected result audits pass. The remaining criticisms above are not solved by these software checks. External evidence, human declarations, release ownership and original-source lineage remain blocked.

## Verdict

The manuscript can be framed as a transparent exploratory reliability/transport study with negative findings. It is not ready for journal submission under the current metadata and evidence status. A journal reviewer could reasonably reject a claim of robust generalization or a novel validated predictive method. No further local code change can create a second hospital cohort or recover missing original run records.
