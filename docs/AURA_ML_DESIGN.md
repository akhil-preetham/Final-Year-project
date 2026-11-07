# AURA-ML: design, formulation, and evidence policy

**Status:** research prototype; the algorithmic contribution is provisional and
is not yet a claim of established novelty.

## Scientific position

Dataset profiling, adaptive preprocessing, spline features, stable selection,
calibration, and ensembles are established techniques. AURA-ML does not claim
that their mere combination is novel. Its testable methodological contribution
is a **reliability-aware selection policy**: on training-side out-of-fold
predictions, it jointly considers discrimination, PR performance, calibration,
fold instability, and computation, then chooses either the best single
representation/model candidate or a disagreement-gated fusion. The outer test
fold is never used for that decision.

The policy is falsifiable. If the fusion or the reliability objective does not
improve paired outer predictions over the prespecified baseline, the result is a
negative or inconclusive AURA-ML finding rather than evidence of novelty.

## Formal formulation

Let the outer training sample be
\(D_{tr}=\{(x_i,y_i)\}_{i=1}^n\). The outer test sample is not available to
any operation below.

### Dataset intelligence

\[
z = I(D_{tr}) = (n,p,m,c,h,o,s,r,q,\pi,\rho),
\]

where \(n\) is sample size, \(p\) feature count, \(m,c\) are numeric and
categorical feature sets, \(h\) missingness, \(o\) mean IQR outlier rate,
\(s\) mean absolute numeric skewness, \(r\) redundant-pair fraction, \(q=n/p\),
and \(\pi,\rho\) are prevalence and class-imbalance ratio. \(I\) uses only
training rows; labels are used only for prevalence and candidate validation.

### Adaptive preprocessing and representation

The policy \(P(z)\) chooses robust scaling when \(o\geq0.05\), otherwise
standard scaling; imputers and category handling are fitted on the current
training fold. A candidate representation is

\[
R_v(x;D_{tr}) = [T(x;D_{tr}),\;1_{v=multi}S(T_N(x;D_{tr}))],
\]

where \(T\) is the encoded original view, \(T_N\) is its cleaned numeric
view, and \(S\) is a bounded degree-two spline expansion. No all-pairs
expansion is used.

### Stable and redundancy-aware selection

For transformed feature \(k\), let \(M_k\) be normalized mutual information,
\(L_k\) normalized absolute L1-logistic coefficient, and \(F_k\) its bootstrap
selection frequency. The relevance score is

\[
Q_k=\tfrac12M_k+\tfrac12L_k.
\]

Features with \(F_k\geq\tau\) are considered in descending \(Q_k\) order;
feature \(k\) is admitted only if its absolute correlation with every admitted
feature is below \(\delta\), with a maximum of \(K\) features. If no feature
passes, the top-ranked feature is retained. All quantities are training-only.

### Model and output selection

For candidate \(j\), inner out-of-fold probabilities \(p_j\) and fold AUCs
\(a_{j\ell}\) produce

\[
U_j=0.60A_j+0.20\frac{P_j-\pi}{1-\pi}+0.10(1-B_j)+0.05(1-E_j)
      -0.10\operatorname{sd}_\ell(a_{j\ell})
      -10^{-5}\log(1+t_j),
\]

where \(A_j\) is ROC-AUC, \(P_j\) PR-AUC, \(B_j\) Brier score, \(E_j\) the
uniform-bin ECE, and \(t_j\) fitting time. The coefficients are fixed before
outer evaluation and are not tuned on outer labels.

For a candidate set \(J\), base weights are

\[
\alpha_j=\frac{\exp(U_j/T)}{\sum_{k\in J}\exp(U_k/T)}.
\]

For row \(x\), the weighted consensus is \(\bar p(x)=\sum_j\alpha_jp_j(x)\),
and reliability-gated weights are

\[
w_j(x)=\alpha_j\exp[-\gamma|p_j(x)-\bar p(x)|],\qquad
p_F(x)=\frac{\sum_jw_j(x)p_j(x)}{\sum_jw_j(x)}.
\]

Fusion is retained only when its inner utility exceeds the best single
candidate by the prespecified minimum margin. Otherwise AURA-ML returns the
best single candidate. A sigmoid calibrator is selected only when its
cross-fitted inner Brier score improves over the uncalibrated output.

### Reliability output

The implementation records candidate disagreement, calibration method, Brier,
ECE, fold AUC standard deviation, and selected output. These are internal
reliability diagnostics, not guarantees of clinical uncertainty or safety.

## Pseudocode

```text
for each outer training fold D_tr:
    z <- profile(D_tr.X, D_tr.y)
    for each prespecified (model, view, selector) candidate:
        for each inner split:
            fit preprocessing/view/selector on inner-train only
            fit candidate model on inner-train only
            predict inner-validation rows
        compute U_j from pooled inner predictions and fold dispersion
    compute reliability-gated fusion from inner predictions
    choose fusion only if its U exceeds best single U by the fixed margin
    choose sigmoid calibration using cross-fitted inner predictions
    refit only selected candidate(s), preprocessing, selector, and calibrator
        on D_tr
    predict the untouched outer test fold
```

## Complexity and feasibility

For \(J\) candidates, \(K\) inner folds, \(n\) rows, and \(p'\) encoded
features, model cost is approximately \(O(JK\,C_{model}(n,p'))\). The spline
view is linear in numeric feature count and spline basis width. Stable selection
adds \(O(B\,C_{L1}+p'^2)\) in its current implementation because redundancy is
computed as a correlation matrix; this is suitable for the repository schemas
but should be replaced by blocked/grouped redundancy for very high-dimensional
data. Prediction storage is \(O(nJ)\) for inner candidates and \(O(n)\) for
the selected outer output.

## Evidence boundary

The current 2x2 runs are exploratory. Two outer folds are insufficient for a
definitive superiority claim. The 70K task is a separate-schema benchmark, not
external validation of heart5 or Mendeley. No result supports clinical utility,
deployment, or universal generalization.
