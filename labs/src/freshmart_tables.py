"""Canonical Lakehouse table names for FreshMart medallion schemas.

Learner-facing names use ``layer.table`` so the path stays short while matching
schema-enabled Fabric lakehouses (preferred medallion layout).

Legacy flat names (``bronze_transactions``) remain resolvable for one release so
instructor workspaces can migrate without breaking mid-class notebooks.
"""

from __future__ import annotations

# Canonical Spark / SQL names (schema-qualified)
BRONZE_TRANSACTIONS = "bronze.transactions"
BRONZE_CUSTOMERS = "bronze.customers"
SILVER_CUSTOMER_FEATURES = "silver.customer_features"
GOLD_PREDICTIONS = "gold.freshmart_predictions"

# Local CSV / artifact file names (unchanged for learners cloning the repo)
CSV_TRANSACTIONS = "freshmart_transactions.csv"
CSV_CUSTOMERS = "freshmart_customers.csv"
CSV_SCORING = "freshmart_scoring_batch.csv"
CSV_SILVER_FEATURES = "silver_customer_features.csv"
CSV_GOLD_PREDICTIONS = "gold_freshmart_predictions.csv"

TABLE_TO_CSV: dict[str, str] = {
    BRONZE_TRANSACTIONS: CSV_TRANSACTIONS,
    BRONZE_CUSTOMERS: CSV_CUSTOMERS,
    SILVER_CUSTOMER_FEATURES: CSV_SILVER_FEATURES,
    GOLD_PREDICTIONS: CSV_GOLD_PREDICTIONS,
    # Legacy flat names → same CSV fallbacks
    "bronze_transactions": CSV_TRANSACTIONS,
    "bronze_customers": CSV_CUSTOMERS,
    "silver_customer_features": CSV_SILVER_FEATURES,
    "gold_freshmart_predictions": CSV_GOLD_PREDICTIONS,
}

LEGACY_TO_CANONICAL: dict[str, str] = {
    "bronze_transactions": BRONZE_TRANSACTIONS,
    "bronze_customers": BRONZE_CUSTOMERS,
    "silver_customer_features": SILVER_CUSTOMER_FEATURES,
    "gold_freshmart_predictions": GOLD_PREDICTIONS,
}

CANONICAL_TABLES: tuple[str, ...] = (
    BRONZE_TRANSACTIONS,
    BRONZE_CUSTOMERS,
    SILVER_CUSTOMER_FEATURES,
    GOLD_PREDICTIONS,
)


def canonicalize_table_name(table_name: str) -> str:
    """Map a legacy flat name to the schema-qualified name when needed.

    Args:
        table_name: Flat or schema-qualified table identifier.

    Returns:
        Canonical ``schema.table`` name when known, otherwise the input unchanged.
    """
    return LEGACY_TO_CANONICAL.get(table_name, table_name)


def spark_table_candidates(table_name: str) -> list[str]:
    """Ordered Spark table names to try (canonical first, then legacy).

    Args:
        table_name: Requested table identifier.

    Returns:
        Candidate names for ``spark.read.table``.
    """
    canonical = canonicalize_table_name(table_name)
    candidates = [canonical]
    for legacy, target in LEGACY_TO_CANONICAL.items():
        if target == canonical and legacy not in candidates:
            candidates.append(legacy)
    if table_name not in candidates:
        candidates.append(table_name)
    return candidates
