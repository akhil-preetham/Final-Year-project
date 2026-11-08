# Manuscript finalization report

The versioned LaTeX manuscript is `paper/multi_dataset_study_20261108/main.tex`, with its bibliography, table fragments and figure sources kept in that directory. The manuscript preserves the established terminology and reports the primary frozen run. Its results are traceable to the experiment metrics and manifest; the additional completion diagnostics expand the technical project report and do not silently replace the original paper's prespecified primary results.

The current manuscript's main scope is a multi-dataset experimental evaluation. It separates angiographic CAD from heart-failure death, MI complication and SPECT imaging. It describes the four CAD cohorts as retrospective stress tests because they are in Heart5 lineage; it does not assert patient independence or clinical validation. The 80/90/95 conformal replay is a supplemental diagnostic and the manuscript retains the original nominal-90% primary table.

Before submission, confirm author names/order, affiliations, institutional declarations, ethics determination, funding, conflicts, data-use statements, acknowledgements and target venue. These facts are not invented in the source. The final verification entry records LaTeX compilation and visual PDF checks, citation/reference resolution, figure/table inclusion and page count.

<!-- DEDUP_SAFE_MANUSCRIPT START -->
## Versioned duplicate-safe manuscript

The revised source bundle is `paper/multi_dataset_study_20261108_dedup_safe/`; its seven-page PDF is `output/pdf/CARDIODIAG_MultiDataset_Experimental_Evaluation_20261108_DedupSafe.pdf`. Tectonic 0.17.0 compiled the current source successfully. All citation keys, cross-references, inputs, and figures resolved; extracted text had no unresolved markers; every rendered page was visually inspected. The build hashes and nonfatal layout/font warnings are recorded in the bundle BUILD_MANIFEST.json. The original source and PDF remain preserved.

Author order, affiliations, institutional ethics determination, funding, conflicts, contribution statements, data-use declarations, and venue remain to be confirmed by the project team; the manuscript is therefore a compiled working draft, not submission-ready.
<!-- DEDUP_SAFE_MANUSCRIPT END -->

## Versioned calibration and ablation manuscript

The current revised bundle is `paper/multi_dataset_study_20261108_dedup_safe_ablation_calibration/`; its eight-page PDF is `output/pdf/CARDIODIAG_MultiDataset_Experimental_Evaluation_20261108_DedupSafe_Ablations_Calibration.pdf`. It adds held-out Platt/isotonic/beta/temperature comparisons, the fixed-default versus inner-tuned OSEC meta-estimator ablation, and a calibration-change heatmap. The previous six-page and seven-page bundles and PDFs remain preserved.

Tectonic 0.17.0 compiled the source successfully on 2026-11-08. The build has 11 resolved citation entries, no unresolved references, missing inputs, or missing figures, and no `??` or `undefined` text markers. All eight pages were visually reviewed; pages 4–8 were also rendered at 180 dpi. No clipping was observed. Nonfatal warnings include Fontconfig configuration, underfull boxes, and the pre-existing 11.8-point overfull box in the selector-ablation table. Full hashes and page review details are in the bundle `BUILD_MANIFEST.json`.

The source text includes the newly checked metric values and states that recalibrated conformal coverage is not claimed because the same calibration partition cannot serve as an independent conformal set. Author order, affiliations, institutional ethics determination, funding/conflict/contribution declarations, data-use wording, and venue remain pending team confirmation.
