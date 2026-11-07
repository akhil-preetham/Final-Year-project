# UCI Heart Failure Clinical Records (ID 519)

- **Source:** UCI Machine Learning Repository, dataset 519.
- **Dataset DOI:** [10.24432/C5Z89R](https://doi.org/10.24432/C5Z89R).
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0), as stated on the official UCI record.
- **Official record:** <https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records>.
- **Associated article:** Chicco, D. & Jurman, G. (2020). *Machine learning can predict survival of patients with heart failure from serum creatinine and ejection fraction alone*. BMC Medical Informatics and Decision Making, 20, 16. <https://doi.org/10.1186/s12911-020-1023-5>.
- **Study adaptation:** 299 records; binary target `death_event`; the source `time` feature (follow-up duration) is excluded from model predictors. No source rows are included in Git. The derived task is a separate exploratory mortality classification study and is not CARDIODIAG CAD validation.
- **Attribution/change statement:** Dataset metadata and raw data were obtained from the UCI record. The analysis excludes follow-up duration and evaluates a binary death-event label. Reported results are produced by this project and are not results endorsed by UCI or the dataset authors.

When redistributing or adapting source data, retain the UCI attribution and CC BY 4.0 license terms and indicate changes as required by the license. The local public-release package intentionally remains data-free.
