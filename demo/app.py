"""Launch an offline Tk desktop interface for CARDIODIAG research artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import tkinter as tk
import tomllib
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any

from cardiodiag.demo_app import load_verified_predictor, run_research_demo_prediction

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE = ROOT / "results" / "transfer_20261105_duke_acath_final" / "model_bundle.joblib"
METRICS_PATHS = {
    "Duke ACATH stress test": ROOT
    / "results"
    / "transfer_20261105_duke_acath_final"
    / "study_metrics.json",
    "AngioCAD stress test": ROOT
    / "results"
    / "transfer_20261105_angiocad_domain_guard"
    / "study_metrics.json",
}
FIGURE_DIR = ROOT / "paper" / "figures" / "master_directive_20261105_final"


class CardioDiagApp:
    """Local-only desktop UI for real project artifacts and guarded inference."""

    def __init__(self, root: tk.Tk, bundle_path: Path, predictor=None) -> None:
        self.root = root
        self.bundle_path = bundle_path
        self.predictor = predictor or load_verified_predictor(bundle_path)
        self.root.title("CARDIODIAG | Research Demonstration")
        self.root.geometry("1050x760")
        self.root.minsize(880, 620)
        self.root.configure(bg="#f3f6fa")
        self._build()

    def _build(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), foreground="#17324d")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#526579")
        style.configure("Section.TLabel", font=("Segoe UI", 13, "bold"), foreground="#17324d")
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("CardTitle.TLabel", background="white", font=("Segoe UI", 10, "bold"))
        style.configure("CardValue.TLabel", background="white", font=("Segoe UI", 17, "bold"))
        style.configure("Notice.TLabel", background="#fff4d6", foreground="#634b00", padding=10)

        header = ttk.Frame(self.root, padding=(22, 18, 22, 8))
        header.pack(fill="x")
        ttk.Label(header, text="CARDIODIAG", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Reproducibility, reliability and transportability research",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))
        ttk.Label(
            self.root,
            text=(
                "Research-only experimental output. Not clinically validated. Do not use for "
                "diagnosis, treatment, triage, or decisions about a person’s care. "
                "Use synthetic values only; do not enter patient information."
            ),
            style="Notice.TLabel",
            wraplength=980,
            justify="left",
        ).pack(fill="x", padx=22, pady=(5, 12))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=22, pady=(0, 20))
        self.overview_tab = ttk.Frame(notebook, padding=18)
        self.prediction_tab = ttk.Frame(notebook, padding=18)
        self.evidence_tab = ttk.Frame(notebook, padding=18)
        self.explain_tab = ttk.Frame(notebook, padding=18)
        notebook.add(self.overview_tab, text="Overview")
        notebook.add(self.prediction_tab, text="Research demo input")
        notebook.add(self.evidence_tab, text="Evaluation evidence")
        notebook.add(self.explain_tab, text="Explanation limits")
        self._build_overview()
        self._build_prediction()
        self._build_evidence()
        self._build_explainability()

    def _build_overview(self) -> None:
        tab = self.overview_tab
        ttk.Label(tab, text="Project status", style="Section.TLabel").pack(anchor="w")
        cards = ttk.Frame(tab)
        cards.pack(fill="x", pady=12)
        items = [
            ("Engineering", "GO", "Offline research prototype"),
            ("Independent generalization", "NO-GO", "No verified compatible independent cohort"),
            ("Code release", "BLOCKED", "Redistribution authority not established"),
            ("Journal submission", "NOT READY", "Author and institutional details pending"),
        ]
        for index, (label, value, detail) in enumerate(items):
            card = ttk.Frame(cards, style="Card.TFrame", padding=14)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=5, pady=5)
            ttk.Label(card, text=label, style="CardTitle.TLabel").pack(anchor="w")
            ttk.Label(card, text=value, style="CardValue.TLabel").pack(anchor="w", pady=5)
            ttk.Label(card, text=detail, wraplength=390, background="white").pack(anchor="w")
        for column in range(2):
            cards.columnconfigure(column, weight=1)

        ttk.Label(tab, text="Loaded inference artifact", style="Section.TLabel").pack(
            anchor="w", pady=(16, 6)
        )
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        integrity_path = self.bundle_path.with_name("domain_guard_demo_manifest.json")
        integrity = self._load_json(integrity_path)
        model_version = self.bundle_path.parent.name
        if "duke" in model_version:
            compatibility = (
                "Duke target >=75% stenosis vs UCI source >50%; endpoint-mismatched stress test."
            )
        elif "angiocad" in model_version:
            compatibility = (
                "AngioCAD threshold is nominally aligned; patient linkage is unverified and "
                "target labels were examined previously."
            )
        else:
            compatibility = "Review the dataset-specific protocol before interpreting this bundle."
        domains = ", ".join(sorted(self.predictor.source_domains))
        features = ", ".join(self.predictor.features)
        ttk.Label(
            tab,
            text=(
                f"Research version: {project['version']}\n"
                f"Model version: {model_version} | bundle SHA-256: "
                f"{integrity['model_bundle_sha256'][:12]}…\n"
                f"Dataset compatibility: {compatibility}\n"
                f"Bundle: {self.bundle_path.relative_to(ROOT)}\n"
                f"Registered source domains: {domains}\n"
                f"Feature schema (declared order): {features}\n"
                "Unknown domains and unsupported schemas abstain. Site identity must be trusted "
                "metadata; selecting a domain here is only for synthetic policy demonstration."
            ),
            wraplength=930,
            justify="left",
        ).pack(anchor="w")

    def _build_prediction(self) -> None:
        tab = self.prediction_tab
        ttk.Label(tab, text="Synthetic input only", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            tab,
            text=(
                "The loaded frozen bundle accepts these features: "
                + ", ".join(self.predictor.features)
                + ". Numeric bounds below are demo input sanity checks, not clinical reference "
                "intervals. Model abstention is retained as an outcome."
            ),
            wraplength=920,
            justify="left",
        ).pack(anchor="w", pady=(3, 12))

        form = ttk.Frame(tab)
        form.pack(anchor="w", fill="x")
        self.variables: dict[str, tk.StringVar] = {}
        for row, feature in enumerate(self.predictor.features):
            ttk.Label(form, text=feature, width=18).grid(row=row, column=0, sticky="w", pady=6)
            variable = tk.StringVar()
            self.variables[feature] = variable
            if feature in self.predictor.numeric_features:
                default = "35" if feature == "age" else "180" if feature == "chol" else ""
                variable.set(default)
                ttk.Entry(form, textvariable=variable, width=28).grid(
                    row=row, column=1, sticky="w", pady=6
                )
                unit = "years" if feature == "age" else "mg/dL" if feature == "chol" else "numeric"
                ttk.Label(form, text=unit).grid(row=row, column=2, sticky="w", padx=8)
            else:
                options = self.predictor.allowed_categories.get(feature, [])
                default = options[0] if options else ""
                variable.set(default)
                ttk.Combobox(
                    form,
                    textvariable=variable,
                    values=options,
                    state="readonly" if options else "normal",
                    width=25,
                ).grid(row=row, column=1, sticky="w", pady=6)

        ttk.Label(form, text="Source domain", width=18).grid(
            row=len(self.variables), column=0, sticky="w", pady=6
        )
        self.domain_var = tk.StringVar(value="unknown/unregistered")
        domain_values = ["unknown/unregistered", *sorted(self.predictor.source_domains)]
        ttk.Combobox(
            form,
            textvariable=self.domain_var,
            values=domain_values,
            state="readonly",
            width=25,
        ).grid(row=len(self.variables), column=1, sticky="w", pady=6)
        ttk.Label(
            form,
            text="Use a registered domain only for synthetic in-support/abstention demos.",
            wraplength=370,
        ).grid(row=len(self.variables), column=2, sticky="w", padx=8)

        ttk.Button(tab, text="Run guarded demo", command=self._predict).pack(anchor="w", pady=14)
        self.result_text = tk.Text(
            tab, height=7, wrap="word", state="disabled", font=("Segoe UI", 10)
        )
        self.result_text.pack(fill="x", expand=False)

    def _predict(self) -> None:
        values: dict[str, Any] = {name: variable.get() for name, variable in self.variables.items()}
        domain = self.domain_var.get()
        try:
            result = run_research_demo_prediction(
                self.predictor,
                values,
                None if domain == "unknown/unregistered" else domain,
            )
        except (TypeError, ValueError) as exc:
            messagebox.showerror("Input rejected", str(exc), parent=self.root)
            return

        if result["action"] == "abstain":
            lines = ["ACTION: ABSTAIN", f"Reason: {result['reason']}"]
            if result.get("ood_score") is not None:
                lines.append(
                    f"Feature-support distance: {result['ood_score']:.4f} (diagnostic only)"
                )
            lines.append("No class probability is displayed because the policy withheld it.")
        else:
            lines = [
                "ACTION: CLASSIFY (research demonstration only)",
                f"Predicted class: {result['prediction']}",
                f"Class 1 probability: {result['probability']:.4f}",
                f"Conformal set: {result['prediction_set']}",
                f"Feature-support distance: {result['ood_score']:.4f} (diagnostic only)",
            ]
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "\n".join(lines))
        self.result_text.configure(state="disabled")

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _build_evidence(self) -> None:
        canvas = tk.Canvas(self.evidence_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.evidence_tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        tab = ttk.Frame(canvas, padding=(0, 0, 8, 0))
        canvas_window = canvas.create_window((0, 0), window=tab, anchor="nw")
        tab.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(canvas_window, width=event.width),
        )
        ttk.Label(tab, text="Observed project evidence", style="Section.TLabel").pack(anchor="w")
        nested = ROOT / "results" / "tables" / "nested_summary.csv"
        row_values: list[tuple[str, float]] = []
        with nested.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row["candidate"] == "corrected_ovec":
                    row_values.append((row["dataset"], float(row["roc_auc_mean"])))
        for path in METRICS_PATHS.values():
            if not path.exists():
                continue
            metrics = self._load_json(path)
            if path.parent.name == "transfer_20261105_angiocad_domain_guard":
                ood = metrics.get("ood", {}).get("isolation_forest_domain_robust", {})
                self.angiocad_later_if_ood_auc = ood.get("target_vs_source_auroc")
                knn_ood = metrics.get("ood", {}).get("knn_domain_robust", {})
                self.angiocad_later_knn_ood_auc = knn_ood.get("target_vs_source_auroc")
                self.angiocad_coverage = (
                    metrics.get("conformal", {})
                    .get("combined_selective_summary", {})
                    .get("coverage")
                )
            else:
                self.duke_coverage = (
                    metrics.get("combined_abstention", {}).get("target_summary", {}).get("coverage")
                )
        validity_path = (
            ROOT / "results" / "validity_audit_20261105" / "validity_sensitivity_audit.json"
        )
        if validity_path.exists():
            sensitivity = self._load_json(validity_path).get("angiocad", {}).get("summary", {})
            self.angiocad_primary_ood_auc = sensitivity.get("with_fbs", {}).get("ood_auc")
            self.angiocad_age_sex_ood_auc = sensitivity.get("age_sex_only", {}).get("ood_auc")
        zas_manifest = ROOT / "results" / "transfer_20261105_zas_external" / "run_manifest.json"
        if zas_manifest.exists():
            self.zas_ood_auc = (
                self._load_json(zas_manifest).get("ood", {}).get("source_vs_target_ood_auroc")
            )

        rows = [
            (
                "Internal Heart5 OVEC mean ROC-AUC",
                next((x[1] for x in row_values if x[0] == "heart5.csv"), None),
                "Internal; source data overlap",
            ),
            (
                "Internal Mendeley OVEC mean ROC-AUC",
                next((x[1] for x in row_values if "Mendeley" in x[0]), None),
                "Internal; not independent validation",
            ),
            (
                "CD-XD-004 primary AngioCAD IF OOD AUROC",
                getattr(self, "angiocad_primary_ood_auc", None),
                "95% CI 0.541–0.635; target later examined",
            ),
            (
                "CD-XD-003 Z-Alizadeh Sani OOD AUROC",
                getattr(self, "zas_ood_auc", None),
                "Separate cohort; endpoint >=50% vs source >50%",
            ),
            (
                "CD-XD-006 domain-robust IF AUROC",
                getattr(self, "angiocad_later_if_ood_auc", None),
                "Later post-hoc diagnostic; different score/policy",
            ),
            (
                "CD-XD-006 domain-robust kNN AUROC",
                getattr(self, "angiocad_later_knn_ood_auc", None),
                "Later post-hoc diagnostic; 95% CI 0.527–0.635",
            ),
            (
                "Age/sex-only sensitivity OOD AUROC",
                getattr(self, "angiocad_age_sex_ood_auc", None),
                "Post-hoc sensitivity; 95% CI 0.496–0.592",
            ),
            (
                "AngioCAD combined selective coverage",
                getattr(self, "angiocad_coverage", None),
                "Low; accepted set is not useful validation",
            ),
            (
                "Duke combined selective coverage",
                getattr(self, "duke_coverage", None),
                "Endpoint differs from source",
            ),
        ]
        tree = ttk.Treeview(tab, columns=("metric", "value", "scope"), show="headings", height=9)
        tree.heading("metric", text="Metric")
        tree.heading("value", text="Value")
        tree.heading("scope", text="Interpretation")
        tree.column("metric", width=300)
        tree.column("value", width=120, anchor="center")
        tree.column("scope", width=450)
        tree.pack(fill="x", pady=10)
        for metric, value, scope in rows:
            rendered = "not available" if value is None else f"{value:.4f}"
            tree.insert("", "end", values=(metric, rendered, scope))
        ttk.Label(
            tab,
            text=(
                "Displayed values are loaded from results/tables/nested_summary.csv and saved "
                "study_metrics/validity-sensitivity artifacts. OOD values from CD-XD-004 and "
                "the later CD-XD-006 diagnostics are different runs, not competing estimates. "
                "Internal cross-validation is not external "
                "validation. AngioCAD and Duke evaluations are exploratory stress tests with "
                "endpoint, linkage, exposure, or cohort limitations."
            ),
            wraplength=930,
            justify="left",
        ).pack(anchor="w", pady=(4, 10))

        images = [
            ("Internal ROC / precision-recall", FIGURE_DIR / "nested_roc_pr_curves.png"),
            ("Calibration", FIGURE_DIR / "nested_calibration.png"),
            ("Risk / coverage", FIGURE_DIR / "nested_risk_coverage.png"),
            ("Shift diagnostics", FIGURE_DIR / "distribution_shift_diagnostics.png"),
        ]
        self.figure_refs: list[tk.PhotoImage] = []
        chart_row = ttk.Frame(tab)
        chart_row.pack(fill="both", expand=True)
        for index, (label, path) in enumerate(images):
            if not path.exists():
                continue
            try:
                image = tk.PhotoImage(file=str(path))
            except tk.TclError:
                continue
            scale = max(1, math.ceil(max(image.width() / 430, image.height() / 250)))
            image = image.subsample(scale, scale)
            self.figure_refs.append(image)
            frame = ttk.Frame(chart_row)
            frame.grid(row=index // 2, column=index % 2, padx=4, pady=4, sticky="nsew")
            ttk.Label(frame, text=label).pack(anchor="w")
            ttk.Label(frame, image=image).pack(anchor="w")
        for column in range(2):
            chart_row.columnconfigure(column, weight=1)
        for row in range(2):
            chart_row.rowconfigure(row, weight=1)

    def _build_explainability(self) -> None:
        tab = self.explain_tab
        ttk.Label(tab, text="Explanation scope", style="Section.TLabel").pack(anchor="w")
        text = (
            "The loaded bundle has no validated per-instance SHAP/LIME explanation artifact. "
            "This app therefore does not fabricate feature contributions or describe them as "
            "clinical causes.\n\n"
            "The evaluation record contains global stability and feature-ablation analyses. "
            "Those are model-behavior summaries for the named datasets, not explanations of an "
            "individual input. Review docs/ABLATION_REPORT.md and the corresponding results/ "
            "artifacts before interpreting those analyses.\n\n"
            "For an abstention, the interface reports the exact policy rule that fired: unknown "
            "source domain, unsupported category/schema, non-singleton conformal set, or feature "
            "support distance above the frozen source threshold. These are software-policy "
            "reasons, not clinical conclusions."
        )
        ttk.Label(tab, text=text, wraplength=920, justify="left").pack(anchor="w", pady=8)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    args = parser.parse_args()
    try:
        predictor = load_verified_predictor(args.bundle.resolve())
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    root = tk.Tk()
    CardioDiagApp(root, args.bundle.resolve(), predictor)
    root.mainloop()


if __name__ == "__main__":
    main()
