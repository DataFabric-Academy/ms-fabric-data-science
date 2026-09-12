"""Instructor migration: flat dbo tables → bronze.* / silver.* / gold.* schemas.

Run inside a Fabric notebook attached to ``lh_freshmart`` (or any Spark session
with that lakehouse as default). Safe to re-run: uses CREATE SCHEMA IF NOT EXISTS
and CREATE OR REPLACE TABLE.
"""

from __future__ import annotations

# Mapping: (canonical schema.table, legacy flat name)
MIGRATIONS: list[tuple[str, str]] = [
    ("bronze.transactions", "bronze_transactions"),
    ("bronze.customers", "bronze_customers"),
    ("silver.customer_features", "silver_customer_features"),
    ("gold.freshmart_predictions", "gold_freshmart_predictions"),
]


def migrate(spark, *, drop_legacy: bool = False) -> None:
    """Create medallion schemas and copy legacy tables into them.

    Args:
        spark: Active SparkSession bound to the classroom lakehouse.
        drop_legacy: When True, drop flat dbo tables after a successful copy.
    """
    for schema in ("bronze", "silver", "gold"):
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        print(f"schema ready: {schema}")

    for canonical, legacy in MIGRATIONS:
        legacy_exists = spark.catalog.tableExists(legacy)
        if not legacy_exists:
            print(f"skip {canonical}: legacy `{legacy}` not found")
            continue
        spark.sql(f"CREATE OR REPLACE TABLE {canonical} AS SELECT * FROM {legacy}")
        count = spark.table(canonical).count()
        print(f"migrated {legacy} -> {canonical} ({count:,} rows)")
        if drop_legacy:
            spark.sql(f"DROP TABLE IF EXISTS {legacy}")
            print(f"dropped legacy {legacy}")

    print("Migration complete. Learners should use bronze.*/silver.*/gold.* names.")


if __name__ == "__main__":
    try:
        from pyspark.sql import SparkSession
    except ImportError as exc:  # pragma: no cover - Fabric-only entrypoint
        raise SystemExit(
            "Run this script in a Fabric notebook Spark session, not on a bare laptop."
        ) from exc

    session = SparkSession.getActiveSession()
    if session is None:
        raise SystemExit("No active Spark session. Attach lh_freshmart and retry.")
    migrate(session, drop_legacy=False)
