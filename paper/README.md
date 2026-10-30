# Manuscript package

This directory contains an editable IEEE journal-style manuscript prepared from
the verified internal evidence. It is not claimed to be clinically validated or
ready for submission until the final literature/venue review is completed. The
manuscript explicitly reports that independent external validation was not
available and treats that as a limitation.

## Build status

- `manuscript.tex`: editable manuscript with evidence-based internal results
  and an explicit no-external-validation limitation.
- `references.bib`: verified starting references.
- `tables/nested_summary.tex`: generated from stored nested-validation output.
- `tables/stability_evidence.tex`: repeated feature-selection stability summary.
- `tables/uncertainty_evidence.tex`: repeated selective-reliability summary.
- `tables/stability_reliability_linkage.tex`: paired stability/reliability
  linkage summary.

Run the result generators after any experiment changes, then compile with a
current official IEEE journal template and the target journal's author
instructions. Do not add claims of clinical benefit, fairness, novelty, or
external validation without new verified evidence.

The current manuscript claim is intentionally narrow: the corrected stability
comparison does not establish a positive advantage on either benchmark,
feature-set stability is not a dependable proxy for reliability, confidence is
empirically informative on both internal benchmarks, and no independent
generalization evidence is available.
