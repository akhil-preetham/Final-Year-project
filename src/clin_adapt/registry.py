"""Executable and unavailable model registry for CLIN-ADAPT.

The registry is descriptive as well as executable.  Optional libraries are
imported only while constructing the corresponding estimator, so an unavailable
family is recorded rather than silently omitted or falsely marked as evaluated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from sklearn.base import BaseEstimator
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.ensemble import (
    AdaBoostClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.naive_bayes import BernoulliNB, GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


@dataclass(frozen=True)
class ModelSpec:
    """Metadata and deterministic factory information for one candidate."""

    name: str
    family: str
    description: str
    preprocessing: str
    requires: tuple[str, ...] = ()
    supported_modalities: tuple[str, ...] = ("tabular",)
    resource_class: str = "cpu_small"
    status: str = "candidate"
    unavailable_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def build(self, seed: int = 42) -> BaseEstimator:
        """Build a single-threaded estimator with the registry defaults."""

        return _build_estimator(self.name, seed)


def discover_model_registry(seed: int = 42) -> list[ModelSpec]:
    """Return the complete known registry with availability resolved locally.

    Availability is checked without installing packages.  Neural/tabular
    foundation and AutoML entries remain explicit records even when unavailable.
    """

    specs = _core_specs()
    optional = [
        ModelSpec(
            "xgboost",
            "gradient_boosting",
            "Single-threaded XGBoost gradient boosting",
            "tree",
            ("xgboost",),
            resource_class="cpu_medium",
        ),
        ModelSpec(
            "lightgbm",
            "gradient_boosting",
            "Single-threaded LightGBM gradient boosting",
            "tree",
            ("lightgbm",),
            resource_class="cpu_medium",
        ),
        ModelSpec(
            "catboost",
            "gradient_boosting",
            "Single-threaded CatBoost gradient boosting",
            "tree",
            ("catboost",),
            resource_class="cpu_medium",
        ),
    ]
    unavailable_families = [
        ("tabnet", "neural_network", "pytorch_tabnet", "PyTorch TabNet implementation"),
        ("tabm", "tabular_deep_learning", "torch", "TabM implementation"),
        ("node", "tabular_deep_learning", "torch", "NODE implementation"),
        ("saint", "tabular_deep_learning", "torch", "SAINT implementation"),
        ("ft_transformer", "tabular_deep_learning", "torch", "FT-Transformer implementation"),
        ("grande", "tabular_deep_learning", "torch", "GRANDE implementation"),
        ("tabpfn", "tabular_foundation", "tabpfn", "TabPFN package"),
        ("tabicl", "tabular_foundation", "tabicl", "TabICL package"),
        ("tabdpt", "tabular_foundation", "tabdpt", "TabDPT implementation"),
        ("mitra", "tabular_foundation", "autogluon", "Mitra/AutoGluon implementation"),
        ("hyperfast", "meta_learning", "hyperfast", "HyperFast implementation"),
        ("autogluon", "automl", "autogluon", "AutoGluon AutoML"),
        ("autosklearn", "automl", "autosklearn", "auto-sklearn AutoML"),
        ("flaml", "automl", "flaml", "FLAML AutoML"),
        ("h2o_automl", "automl", "h2o", "H2O AutoML"),
    ]
    resolved: list[ModelSpec] = []
    for spec in specs + optional:
        if not spec.requires or _module_available(spec.requires[0]):
            resolved.append(spec)
        else:
            resolved.append(
                ModelSpec(
                    **{
                        **spec.to_dict(),
                        "status": "unavailable",
                        "unavailable_reason": f"missing optional dependency: {spec.requires[0]}",
                    }
                )
            )
    for name, family, module, description in unavailable_families:
        status = "available" if _module_available(module) else "unavailable"
        resolved.append(
            ModelSpec(
                name=name,
                family=family,
                description=description,
                preprocessing="external",
                requires=(module,),
                resource_class="gpu_or_external",
                status=status,
                unavailable_reason=None
                if status == "available"
                else f"missing optional dependency: {module}",
            )
        )
    return resolved


def available_model_specs(seed: int = 42) -> list[ModelSpec]:
    """Return only locally executable registry entries."""

    return [spec for spec in discover_model_registry(seed) if spec.status != "unavailable"]


def _core_specs() -> list[ModelSpec]:
    return [
        ModelSpec("logistic", "linear", "L2 logistic regression", "scaled"),
        ModelSpec(
            "ridge_classifier", "linear", "Ridge classifier with probability calibration", "scaled"
        ),
        ModelSpec("lasso_logistic", "linear", "L1 logistic regression", "scaled"),
        ModelSpec("elastic_net", "linear", "Elastic-net logistic regression", "scaled"),
        ModelSpec("lda", "linear", "Linear discriminant analysis", "scaled"),
        ModelSpec("qda", "linear", "Quadratic discriminant analysis", "scaled"),
        ModelSpec("gaussian_nb", "probabilistic", "Gaussian naive Bayes", "scaled"),
        ModelSpec("bernoulli_nb", "probabilistic", "Bernoulli naive Bayes", "scaled"),
        ModelSpec("decision_tree", "tree", "Regularized decision tree", "tree"),
        ModelSpec("random_forest", "tree", "Random forest", "tree", resource_class="cpu_medium"),
        ModelSpec(
            "extra_trees", "tree", "Extremely randomized trees", "tree", resource_class="cpu_medium"
        ),
        ModelSpec("gradient_boosting", "gradient_boosting", "Gradient boosting", "tree"),
        ModelSpec(
            "hist_gradient_boosting", "gradient_boosting", "Histogram gradient boosting", "tree"
        ),
        ModelSpec("adaboost", "gradient_boosting", "AdaBoost", "tree"),
        ModelSpec(
            "svc_rbf",
            "kernel",
            "RBF support-vector classifier",
            "scaled",
            resource_class="cpu_medium",
        ),
        ModelSpec("knn", "instance_based", "K-nearest neighbours", "scaled"),
        ModelSpec(
            "mlp",
            "neural_network",
            "Small multilayer perceptron",
            "scaled",
            resource_class="cpu_medium",
        ),
    ]


def _build_estimator(name: str, seed: int) -> BaseEstimator:
    common = {"random_state": seed}
    if name == "logistic":
        return LogisticRegression(C=1.0, max_iter=2000, class_weight="balanced", **common)
    if name == "ridge_classifier":
        return RidgeClassifier(alpha=1.0, class_weight="balanced")
    if name == "lasso_logistic":
        return LogisticRegression(
            C=0.5,
            solver="liblinear",
            penalty="l1",
            max_iter=2000,
            class_weight="balanced",
            **common,
        )
    if name == "elastic_net":
        return LogisticRegression(
            C=0.5,
            solver="saga",
            penalty="elasticnet",
            l1_ratio=0.5,
            max_iter=1200,
            class_weight="balanced",
            **common,
        )
    if name == "lda":
        return LinearDiscriminantAnalysis()
    if name == "qda":
        return QuadraticDiscriminantAnalysis(reg_param=0.1)
    if name == "gaussian_nb":
        return GaussianNB()
    if name == "bernoulli_nb":
        return BernoulliNB(alpha=1.0)
    if name == "decision_tree":
        return DecisionTreeClassifier(max_depth=5, min_samples_leaf=10, **common)
    if name == "random_forest":
        return RandomForestClassifier(n_estimators=180, min_samples_leaf=2, n_jobs=1, **common)
    if name == "extra_trees":
        return ExtraTreesClassifier(n_estimators=180, min_samples_leaf=2, n_jobs=1, **common)
    if name == "gradient_boosting":
        return GradientBoostingClassifier(
            n_estimators=140, learning_rate=0.05, max_depth=2, **common
        )
    if name == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(
            max_iter=160, learning_rate=0.06, max_leaf_nodes=15, min_samples_leaf=20, **common
        )
    if name == "adaboost":
        return AdaBoostClassifier(n_estimators=120, learning_rate=0.05, **common)
    if name == "svc_rbf":
        return SVC(C=1.0, gamma="scale", probability=True, class_weight="balanced", **common)
    if name == "knn":
        return KNeighborsClassifier(n_neighbors=11, weights="distance")
    if name == "mlp":
        return MLPClassifier(
            hidden_layer_sizes=(64,),
            alpha=1e-3,
            max_iter=250,
            early_stopping=True,
            random_state=seed,
        )
    if name == "xgboost":
        from xgboost import XGBClassifier

        return XGBClassifier(
            n_estimators=180,
            max_depth=3,
            learning_rate=0.05,
            min_child_weight=3,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_lambda=1.0,
            eval_metric="logloss",
            n_jobs=1,
            **common,
        )
    if name == "lightgbm":
        from lightgbm import LGBMClassifier

        return LGBMClassifier(
            n_estimators=180,
            num_leaves=15,
            learning_rate=0.05,
            min_child_samples=20,
            reg_lambda=1.0,
            verbosity=-1,
            n_jobs=1,
            **common,
        )
    if name == "catboost":
        from catboost import CatBoostClassifier

        return CatBoostClassifier(
            iterations=180,
            depth=5,
            learning_rate=0.05,
            l2_leaf_reg=3.0,
            loss_function="Logloss",
            verbose=False,
            thread_count=1,
            random_seed=seed,
        )
    raise KeyError(f"No estimator factory registered for {name!r}")


def _module_available(module_name: str) -> bool:
    try:
        import importlib.util

        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False
