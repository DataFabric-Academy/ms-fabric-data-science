"""Data-contract tests for published FreshMart lab files."""

from __future__ import annotations

import pandas as pd

TX_COLUMNS = [
    "TransactionID",
    "Date",
    "StoreID",
    "StoreType",
    "ProductID",
    "ProductName",
    "Category",
    "UnitsSold",
    "UnitPrice",
    "DiscountRate",
    "SalesAmount",
    "WasteUnits",
    "WasteCost",
    "IsWeekend",
]
CUST_COLUMNS = [
    "CustomerID",
    "Age",
    "Gender",
    "MembershipTier",
    "TenureMonths",
    "RecencyDays",
    "Frequency",
    "MonetaryTotal",
    "AvgBasketSize",
    "ComplaintCount",
    "Churn",
]
SCORE_COLUMNS = [col for col in CUST_COLUMNS if col != "Churn"]


def test_transaction_contract(transactions_df: pd.DataFrame) -> None:
    """Transactions must match Lab 0/1 expected shape and missingness."""
    assert list(transactions_df.columns) == TX_COLUMNS
    assert len(transactions_df) == 3000
    assert transactions_df["TransactionID"].is_unique
    missing_discount = transactions_df["DiscountRate"].isna().sum()
    assert 70 <= missing_discount <= 130
    assert set(transactions_df["StoreType"]) == {"Hypermarket", "Supermarket", "Express"}
    assert {"Bakery", "Produce", "Dairy", "Beverages"} <= set(transactions_df["Category"])


def test_customer_contract(customers_df: pd.DataFrame) -> None:
    """Customers must include Churn and a realistic missing-Age rate."""
    assert list(customers_df.columns) == CUST_COLUMNS
    assert len(customers_df) == 1500
    assert customers_df["CustomerID"].is_unique
    missing_age = customers_df["Age"].isna().sum()
    assert 20 <= missing_age <= 50
    churn_rate = customers_df["Churn"].mean()
    assert 0.15 <= churn_rate <= 0.40
    assert set(customers_df["Gender"]) == {"F", "M", "Other"}
    assert set(customers_df["MembershipTier"]) == {"Bronze", "Silver", "Gold", "Platinum"}
    assert set(customers_df["Churn"]) == {0, 1}


def test_scoring_batch_contract(scoring_df: pd.DataFrame) -> None:
    """Scoring batch is unlabeled and uses unseen customer IDs."""
    assert list(scoring_df.columns) == SCORE_COLUMNS
    assert len(scoring_df) == 200
    assert scoring_df["CustomerID"].is_unique
    assert "Churn" not in scoring_df.columns
    assert scoring_df["Age"].isna().sum() == 0


def test_scoring_ids_do_not_overlap_training(
    customers_df: pd.DataFrame, scoring_df: pd.DataFrame
) -> None:
    """Lab 4 must score a new cohort, not the training customers."""
    overlap = set(customers_df["CustomerID"]) & set(scoring_df["CustomerID"])
    assert not overlap


def test_bakery_has_highest_waste_cost(transactions_df: pd.DataFrame) -> None:
    """Lab 0 SQL checkpoint: Bakery is the highest waste-cost category."""
    waste = transactions_df.groupby("Category")["WasteCost"].sum().sort_values(ascending=False)
    assert waste.index[0] == "Bakery"
    assert waste.iloc[0] > waste.iloc[1]


def test_eda_story_matches_instructions(transactions_df: pd.DataFrame, customers_df: pd.DataFrame) -> None:
    """Keep the classroom story honest against the published CSV files."""
    store_waste = transactions_df.groupby("StoreType")["WasteUnits"].mean()
    assert store_waste["Express"] > store_waste["Hypermarket"]

    corr = transactions_df[["DiscountRate", "UnitsSold", "WasteUnits"]].corr()
    assert corr.loc["DiscountRate", "UnitsSold"] > 0.20
    assert corr.loc["DiscountRate", "WasteUnits"] < 0

    churned = customers_df["Churn"] == 1
    assert customers_df.loc[churned, "RecencyDays"].mean() > customers_df.loc[~churned, "RecencyDays"].mean()
