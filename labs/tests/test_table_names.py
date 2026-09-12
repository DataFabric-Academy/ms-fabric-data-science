"""Tests for schema-qualified FreshMart table names."""

from __future__ import annotations

from freshmart_tables import (
    BRONZE_CUSTOMERS,
    BRONZE_TRANSACTIONS,
    GOLD_PREDICTIONS,
    SILVER_CUSTOMER_FEATURES,
    canonicalize_table_name,
    spark_table_candidates,
)


def test_canonical_names_use_medallion_schemas() -> None:
    """Published names must be schema.table under bronze/silver/gold."""
    assert BRONZE_TRANSACTIONS == "bronze.transactions"
    assert BRONZE_CUSTOMERS == "bronze.customers"
    assert SILVER_CUSTOMER_FEATURES == "silver.customer_features"
    assert GOLD_PREDICTIONS == "gold.freshmart_predictions"


def test_legacy_flat_names_map_to_canonical() -> None:
    """Old dbo flat names remain resolvable during migration."""
    assert canonicalize_table_name("bronze_transactions") == BRONZE_TRANSACTIONS
    assert canonicalize_table_name("bronze.customers") == BRONZE_CUSTOMERS


def test_spark_candidates_prefer_canonical_then_legacy() -> None:
    """Loader should try schema-qualified name before the legacy flat name."""
    candidates = spark_table_candidates("bronze.transactions")
    assert candidates[0] == "bronze.transactions"
    assert "bronze_transactions" in candidates
