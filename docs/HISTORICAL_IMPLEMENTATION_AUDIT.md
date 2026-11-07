# Historical implementation audit

## Conclusion

The original implementation is preserved and understandable as an archived
set of Colab/notebook workflows, but it is not a single portable executable
implementation. The active package is a leakage-controlled reconstruction and
does not claim byte-for-byte equivalence.

## Component audit

| Component | Historical evidence | Active status | Decision |
|---|---|---|---|
| Percentile method | 1st/99th percentile notebook cells | `TrainingOnlyCleaner` fits quantiles on training rows | Retained with corrected fitting boundary |
| LoRAS | Notebook calls `loras.fit_resample`; package/version/parameters are not frozen | No verified reusable LoRAS implementation | Rejected from authoritative pipeline; historical evidence retained |
| XAIH-DRC | Correlation, LIME, agreement, and PCA notebook analyses | `StableXAIHDRC` is an explicit approximation | Retained as stability research component, not faithful claim |
| LIME selection | `LimeTabularExplainer` in reviewer notebook | No fold-local reusable LIME transformer | Not integrated into authoritative metrics |
| OVEC | Soft `VotingClassifier` workflows | `build_ovec` and corrected pipeline | Retained |
| OSEC | Multiple stacking variants | `build_osec` plus optional XGBoost meta-learner | Retained as candidate family |
| Base classifiers | KNN, RF, LR, SVC, NB, AdaBoost, tree, XGBoost variants | Explicit factories | Retained with documented defaults |
| Optimization | Notebook GridSearchCV/randomized searches | Inner-fold `GridSearchCV` | Retained with protocol separation |
| Calibration | Notebook `CalibratedClassifierCV` variants | Reliability and uncertainty modules | Retained only when calibration split is explicit |

## Fidelity boundary

The historical workflow contains global encoding, pre-split resampling, and
variant-specific preprocessing. Reproducing those steps exactly would preserve
the methodological defects, so they are available only through the labelled
historical runner and archive. LoRAS and LIME remain documented but are not
silently replaced by unrelated implementations.

