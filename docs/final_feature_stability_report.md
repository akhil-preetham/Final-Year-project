# Feature-stability comparison

The corrected stability artifacts compare StableXAIHDRC with a matched
one-shot selector using Nogueira stability. The standalone stability protocol
uses five folds, three repeats, eight selector resamples, fixed stability
threshold 0.75, and relevance threshold 0.02. Nested/linkage pipelines use
six selector resamples and are not numerically interchangeable.

On the Kaggle 70k benchmark, the corrected stability artifact reports mean
repeat Nogueira stability 0.8432 for StableXAIHDRC and 0.8429 for the
one-shot comparator; the difference is 0.00036 with descriptive interval
[0.00000, 0.00109], and the positive-evidence flag is false.

On the reduced Kaggle nested pair, stable logistic ROC-AUC was 0.78862 versus
0.78930 for corrected logistic. The stable method therefore did not improve
the predictive endpoint in that reduced analysis.

These are benchmark-specific, dependent resampling results and do not
establish generalization to a new population.
