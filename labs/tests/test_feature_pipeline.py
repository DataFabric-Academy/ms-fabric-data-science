"""Feature-pipeline tests that Lab 2 and Lab 4 must share."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from freshmart_features import (
    DUMMY_COLUMNS,
    FEATURE_COLUMNS,
    FeatureParams,
    fit_preprocessor,
    load_feature_params,
    model_matrix,
    save_feature_params,
    transform_customers,
)


def test_fit_and_transform_training_customers(customers_df: pd.DataFrame) -> None:
    """Silver features have no NaN and keep the model signature order."""
    params = fit_preprocessor(customers_df)
    silver = transform_customers(customers_df, params, require_target=True)

    assert list(silver.columns) == ["CustomerID", *FEATURE_COLUMNS, "Churn"]
    assert len(silver) == 1500
    assert silver[list(FEATURE_COLUMNS)].isna().sum().sum() == 0
    assert silver["Age"].between(18, 75).all()
    for col in ("MonetaryTotal", "AvgBasketSize", "RecencyDays", "TenureMonths"):
        assert silver[col].min() >= 0
        assert silver[col].max() <= 1.000001
    assert set(DUMMY_COLUMNS) <= set(silver.columns)
    assert silver[list(DUMMY_COLUMNS)].isin([0, 1]).all().all()


def test_age_median_matches_training_data(customers_df: pd.DataFrame) -> None:
    """Persisted Age median must come from the training customers."""
    params = fit_preprocessor(customers_df)
    expected = float(customers_df["Age"].median())
    assert params.age_median == pytest.approx(expected)


def test_scoring_uses_training_scale_not_batch_scale(
    customers_df: pd.DataFrame, scoring_df: pd.DataFrame
) -> None:
    """Re-fitting min/max on the scoring batch would break the model."""
    train_params = fit_preprocessor(customers_df)
    aligned = transform_customers(scoring_df, train_params, require_target=False)

    scoring_like_train = scoring_df.copy()
    scoring_like_train["Churn"] = 0
    leaked_params = fit_preprocessor(scoring_like_train)
    leaked = transform_customers(scoring_df, leaked_params, require_target=False)

    assert not aligned["MonetaryTotal"].equals(leaked["MonetaryTotal"])
    assert list(aligned.columns) == ["CustomerID", *FEATURE_COLUMNS]
    assert "Churn" not in aligned.columns
    assert aligned[list(FEATURE_COLUMNS)].isna().sum().sum() == 0


def test_missing_gender_other_is_filled(customers_df: pd.DataFrame) -> None:
    """Scoring batches without Gender=Other still get Gender_Other=0."""
    params = fit_preprocessor(customers_df)
    batch = pd.DataFrame(
        [
            {
                "CustomerID": "CUST_99999",
                "Age": 40,
                "Gender": "F",
                "MembershipTier": "Gold",
                "TenureMonths": 12,
                "RecencyDays": 10,
                "Frequency": 8,
                "MonetaryTotal": 5000,
                "AvgBasketSize": 625,
                "ComplaintCount": 0,
            }
        ]
    )
    out = transform_customers(batch, params, require_target=False)
    assert out.loc[0, "Gender_F"] == 1
    assert out.loc[0, "Gender_Other"] == 0
    assert out.loc[0, "MembershipTier_Gold"] == 1
    assert out.loc[0, "MembershipTier_Bronze"] == 0


def test_feature_params_roundtrip(customers_df: pd.DataFrame, tmp_path: Path) -> None:
    """Lab 2 JSON params must reload identically for Lab 4."""
    params = fit_preprocessor(customers_df)
    path = save_feature_params(params, tmp_path / "feature_params.json")
    loaded = load_feature_params(path)
    assert loaded == params
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert FeatureParams.from_dict(payload) == params


def test_model_matrix_column_order(customers_df: pd.DataFrame) -> None:
    """MLflow signature order is the published FEATURE_COLUMNS list."""
    params = fit_preprocessor(customers_df)
    silver = transform_customers(customers_df, params, require_target=True)
    matrix = model_matrix(silver, params)
    assert list(matrix.columns) == list(FEATURE_COLUMNS)


def test_missing_column_raises(customers_df: pd.DataFrame) -> None:
    """Broken uploads fail fast instead of silently training."""
    broken = customers_df.drop(columns=["ComplaintCount"])
    with pytest.raises(ValueError, match="missing required columns"):
        fit_preprocessor(broken)
