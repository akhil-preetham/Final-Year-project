# Final research contribution and novelty assessment

## Primary research question

When cardiovascular prediction models are trained on heterogeneous public source cohorts, how well do discrimination, calibration, shift warnings, and abstention behavior carry to source-distinct cohorts with endpoint-compatible features?

## Supporting questions

1. Does nested, training-only preprocessing change the interpretation of original CARDIODIAG ensemble results?
2. Can source-only calibration transfer to a distinct hospital?
3. Do feature-space shift scores distinguish cohort membership and identify unreliable individual predictions?
4. Does conformal/support-based abstention retain useful coverage under dataset shift?

## Hypotheses and falsification

| Hypothesis | Test | Falsifying evidence/current result |
|---|---|---|
| Source calibration improves external probability quality | Fit only on source calibration data; compare fixed target scores and paired intervals | AngioCAD improvements under Platt were small/inconclusive; temperature improved this post-hoc target but lacks new-site confirmation |
| Feature-only detectors detect a shifted cohort | Source-only thresholds; report domain AUROC/AUPRC and alert rates | AngioCAD AUROC 0.589 for Isolation Forest; synthetic correlation/variance changes often near chance |
| Selective prediction offers a useful risk-coverage tradeoff | Freeze source policy; report accepted events, risk and coverage | AngioCAD combined coverage 5.6%, with one observed outcome class among accepted cases |
| Corrected ensembles generalize across sources | Matched nested internal and leave-cohort/site-out studies | Internal metrics are high on development data; external evidence is mixed and not enough for dependable transport |

## Contribution supported today

The defensible contribution is a reproducible methodological reassessment and integrated reliability evaluation of a CARDIODIAG-style cardiovascular tabular pipeline: it separates historically leakage-prone workflows from corrected evaluation, tests source-only calibration/shift/abstention components, and reports where they fail to transfer. The negative findings are part of the result.

OVEC/OSEC, Platt/isotonic/beta/temperature scaling, KNN/Isolation Forest, conformal prediction and abstention are established components. Their assembly in this repository is engineering integration, not by itself a novel algorithm. StableXAIHDRC is an approximation, not the original XAIH-DRC. No universal superiority, clinically validated method, or reliable unseen-site behavior is established.

## Scope and limits

Evidence comprises one endpoint-aligned external site, two endpoint-mismatched stress tests, UCI cohorts overlapping the Heart5 composite, small development datasets, and synthetic covariate-shift diagnostics. The current contribution is suitable for a transparent exploratory research report. A stronger confirmatory contribution requires another untouched compatible hospital cohort and preregistered method comparisons.

See RESEARCH_GAP_AND_NOVELTY.md and CROSS_DATASET_GENERALIZATION_REVIEW.md for the broader literature review. Do not describe the present work as prospective validation or a novel universally generalizable algorithm.
