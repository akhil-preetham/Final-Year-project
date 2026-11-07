# UCI Myocardial Infarction Complications (ID 579)

- **Source:** Golovenkin, S., Shulman, V., Rossiev, D., Shesternya, P., Nikulina, S., Orlova, Y. & Voino-Yasenetsky, V. (2020). *Myocardial infarction complications* [dataset]. UCI Machine Learning Repository.
- **Dataset DOI:** [10.24432/C53P5M](https://doi.org/10.24432/C53P5M).
- **Detailed data DOI:** [10.25392/leicester.data.12045261.v3](https://doi.org/10.25392/leicester.data.12045261.v3).
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0), as stated on the official UCI record.
- **Official record:** <https://archive.ics.uci.edu/dataset/579/myocardial+infarction+complications>.
- **Study adaptation:** 1,700 records; the primary task recodes `LET_IS > 0` as `any_lethal_outcome`. Admission-time inputs follow the UCI allowed-column list; later-observed fields, identifier `ID`, all 12 source outcome fields, and contemporaneous pulmonary-edema/cardiogenic-shock proxy fields are excluded from predictors. Categorical-coded features are handled as categorical variables. No source rows are included in Git.
- **Attribution/change statement:** The project uses the UCI `MI.data` release and official variable metadata. It derives a binary any-lethal-outcome label and applies the predictor exclusions documented in the experiment report. Reported results are produced by this project and are not results endorsed by UCI, the dataset authors, or the associated institutions.

When redistributing or adapting source data, retain the UCI attribution and CC BY 4.0 license terms and indicate changes as required by the license. The local public-release package intentionally remains data-free.
