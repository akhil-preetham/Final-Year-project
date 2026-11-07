# Current CARDIODIAG intended-use boundary

**Recorded:** 2026-11-05  
**Status:** Research-only scope; no clinical intended use approved

## Current scope

The project owner described CARDIODIAG as a research-based final-year project
that may have clinical use in the future. For the current work, this is
interpreted as an offline research prototype for retrospective analysis of the
documented datasets and synthetic demonstrations. This interpretation records
the present scope; it is not clinical approval or authorization for patient
use.

- **Users:** project researchers and software developers.
- **Setting:** offline research and development environment.
- **Inputs:** documented historical cohort files and synthetic examples.
- **Research task:** study binary CAD-label prediction and model behavior
  under dataset shift. Dataset-specific target and feature definitions remain
  explicit in each protocol.
- **Outputs:** research probabilities, abstention behavior, metrics, plots,
  and reproducibility artifacts for analysis.
- **Clinical action:** none. Outputs must not guide screening, diagnosis,
  triage, treatment, referral, or other patient-care decisions.
- **Intended clinical population, prediction time, comparator, clinical
  threshold, jurisdiction, and deployment site:** not specified.

The prototype is not clinically validated. Its synthetic demo is not a clinical
test. The trusted-site guard abstains on an unregistered site; this is a
software behavior, not proof that registered-site outputs are safe.

## Conditions for any future clinical work

Before modeling for a clinical function, the project needs a named clinical
partner and a reviewed intended-use specification covering the patient
population, care setting, intended user, point in workflow, reference outcome,
prediction horizon, action supported, exclusions, comparator, decision
thresholds, jurisdiction, and manufacturer. The project would then need
authorized compatible data, ethics and institutional review, prospective
silent-mode evaluation, safety/usability/security evidence, and jurisdiction-
specific regulatory review. None of those approvals is implied by the present
research scope.

## Gate interpretation

The current research-only boundary is documented, so the project can be
described accurately as a research prototype. Gate G1 remains **partial** for
real-world readiness because no clinical intended use or clinical owner has
been specified or approved. The overall deployment decision remains `NO_GO`.
