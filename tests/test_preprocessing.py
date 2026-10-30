import pandas as pd

from cardiodiag.preprocessing import TrainingOnlyCleaner


def test_cleaner_uses_training_statistics_only() -> None:
    train = pd.DataFrame({"age": [40, 50, 60], "sex": ["F", "M", "M"]})
    test = pd.DataFrame({"age": [10_000, None], "sex": [None, "F"]})

    cleaner = TrainingOnlyCleaner(lower_quantile=0.0, upper_quantile=1.0).fit(train)
    transformed = cleaner.transform(test)

    assert transformed.loc[0, "age"] == 50
    assert transformed.loc[1, "age"] == 50
    assert transformed.loc[0, "sex"] == "M"


def test_cleaner_rejects_missing_fitted_columns() -> None:
    train = pd.DataFrame({"age": [40, 50], "sex": ["F", "M"]})
    cleaner = TrainingOnlyCleaner().fit(train)

    try:
        cleaner.transform(pd.DataFrame({"age": [45]}))
    except ValueError as error:
        assert "missing fitted columns" in str(error)
    else:
        raise AssertionError("Expected a missing-column error")


def test_cleaner_does_not_apply_numeric_outlier_rules_to_coded_categories() -> None:
    train = pd.DataFrame({"age": [40, 50, 60], "gender": [0, 1, 1]})
    cleaner = TrainingOnlyCleaner(
        lower_quantile=0.0,
        upper_quantile=1.0,
        categorical_columns=["gender"],
    ).fit(train)

    transformed = cleaner.transform(pd.DataFrame({"age": [50], "gender": [0]}))

    assert cleaner.numeric_columns_ == ["age"]
    assert cleaner.categorical_columns_ == ["gender"]
    assert transformed.loc[0, "gender"] == 0
