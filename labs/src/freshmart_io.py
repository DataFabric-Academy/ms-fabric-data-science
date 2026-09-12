"""Local/Fabric data loaders for FreshMart labs.

Notebooks prefer Lakehouse tables when Spark is available, then fall back
to the repo CSV files so the same notebook can be smoke-tested locally.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

LABS_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = LABS_ROOT / "data"

TABLE_TO_CSV = {
    "bronze_transactions": "freshmart_transactions.csv",
    "bronze_customers": "freshmart_customers.csv",
    "silver_customer_features": "silver_customer_features.csv",
    "gold_freshmart_predictions": "gold_freshmart_predictions.csv",
}

SCORING_CSV = "freshmart_scoring_batch.csv"
LOCAL_ARTIFACT_DIR = DATA_DIR / ".local"
FEATURE_PARAMS_PATH = LOCAL_ARTIFACT_DIR / "feature_params.json"


def resolve_data_file(*relative_names: str) -> Path:
    """Find the first existing data file among known locations.

    Args:
        *relative_names: File names or relative paths to try under each root.

    Returns:
        Path of the first existing file.

    Raises:
        FileNotFoundError: If none of the candidates exist.
    """
    roots = [
        DATA_DIR,
        Path("/lakehouse/default/Files/raw"),
        Path("Files/raw"),
        Path("../data"),
        Path("labs/data"),
        Path.cwd(),
    ]
    candidates: list[Path] = []
    for root in roots:
        for name in relative_names:
            candidates.append(Path(root) / name)
            candidates.append(Path(name))
    for path in candidates:
        if path.exists() and path.is_file():
            return path
    raise FileNotFoundError(
        "Could not find FreshMart data file. Tried: "
        + ", ".join(str(path) for path in candidates[:12])
    )


def _spark_table(table_name: str) -> pd.DataFrame | None:
    """Read a Lakehouse table when Spark is available."""
    try:
        spark = globals().get("spark") or __import__("pyspark.sql", fromlist=["SparkSession"]).SparkSession.getActiveSession()
    except Exception:
        spark = None
    if spark is None:
        return None
    try:
        frame = spark.read.table(table_name).toPandas()
        logger.info("Loaded Spark table %s (%s rows)", table_name, len(frame))
        return frame
    except Exception as exc:  # noqa: BLE001 - Fabric/local fallback is intentional
        logger.info("Spark table %s unavailable (%s); falling back to CSV", table_name, exc)
        return None


def load_table_or_csv(table_name: str, csv_name: str | None = None) -> pd.DataFrame:
    """Load a lab table from Spark, then from the published CSV.

    Args:
        table_name: Lakehouse table name.
        csv_name: Optional CSV override. Defaults to the known mapping.

    Returns:
        pandas DataFrame.
    """
    frame = _spark_table(table_name)
    if frame is not None:
        return frame
    file_name = csv_name or TABLE_TO_CSV.get(table_name)
    if not file_name:
        raise FileNotFoundError(f"No CSV mapping for table '{table_name}'")
    path = resolve_data_file(file_name, f".local/{file_name}")
    logger.info("Loaded CSV %s", path)
    return pd.read_csv(path)


def load_scoring_batch() -> pd.DataFrame:
    """Load the 200-row scoring batch used in Lab 4."""
    frame = None
    try:
        spark = globals().get("spark")
        if spark is not None:
            frame = (
                spark.read.format("csv")
                .option("header", "true")
                .option("inferSchema", "true")
                .load("Files/raw/freshmart_scoring_batch.csv")
                .toPandas()
            )
    except Exception as exc:  # noqa: BLE001
        logger.info("Scoring CSV via Spark unavailable (%s)", exc)
        frame = None
    if frame is not None:
        return frame
    path = resolve_data_file(SCORING_CSV)
    return pd.read_csv(path)


def save_local_csv(df: pd.DataFrame, name: str) -> Path:
    """Persist a DataFrame for local verification.

    Args:
        df: Frame to write.
        name: File name under ``data/.local``.

    Returns:
        Written path.
    """
    LOCAL_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = LOCAL_ARTIFACT_DIR / name
    df.to_csv(path, index=False)
    logger.info("Wrote local artifact %s (%s rows)", path, len(df))
    return path
