"""Build Delta folders for silver/gold from local pipeline CSVs."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "data" / ".local"
OUT = LOCAL / "delta_upload"

TABLES = {
    "silver/customer_features": LOCAL / "silver_customer_features.csv",
    "gold/freshmart_predictions": LOCAL / "gold_freshmart_predictions.csv",
}


def _map_type(duck_type: str) -> str:
    """Map DuckDB types to Delta primitive names."""
    upper = duck_type.upper()
    if upper.startswith("VARCHAR") or upper.startswith("STRING"):
        return "string"
    if upper.startswith("BIGINT") or upper == "HUGEINT":
        return "long"
    if upper.startswith("INTEGER") or upper == "INT":
        return "integer"
    if upper.startswith("DOUBLE") or upper.startswith("FLOAT") or upper.startswith("DECIMAL"):
        return "double"
    if upper.startswith("BOOLEAN"):
        return "boolean"
    return "string"


def write_delta(table: str, csv_path: Path) -> None:
    """Write one Delta table folder under OUT."""
    df = pd.read_csv(csv_path)
    table_dir = OUT / table
    if table_dir.exists():
        shutil.rmtree(table_dir)
    table_dir.mkdir(parents=True)
    parquet_name = "part-00000.parquet"
    parquet_path = table_dir / parquet_name
    con = duckdb.connect()
    con.register("tmp_df", df)
    con.execute(f"COPY tmp_df TO '{parquet_path.as_posix()}' (FORMAT PARQUET)")
    schema = con.execute("DESCRIBE SELECT * FROM tmp_df").fetchall()
    fields = [
        {
            "name": col_name,
            "type": _map_type(str(col_type)),
            "nullable": True,
            "metadata": {},
        }
        for col_name, col_type, *_ in schema
    ]
    protocol = {"protocol": {"minReaderVersion": 1, "minWriterVersion": 2}}
    metadata = {
        "metaData": {
            "id": f"freshmart-{table.replace('/', '-')}",
            "format": {"provider": "parquet", "options": {}},
            "schemaString": json.dumps(
                {"type": "struct", "fields": fields}, separators=(",", ":")
            ),
            "partitionColumns": [],
            "configuration": {},
            "createdTime": int(datetime.now(timezone.utc).timestamp() * 1000),
        }
    }
    add = {
        "add": {
            "path": parquet_name,
            "partitionValues": {},
            "size": parquet_path.stat().st_size,
            "modificationTime": int(datetime.now(timezone.utc).timestamp() * 1000),
            "dataChange": True,
            "stats": json.dumps({"numRecords": int(len(df))}),
        }
    }
    log_dir = table_dir / "_delta_log"
    log_dir.mkdir(parents=True)
    with (log_dir / "00000000000000000000.json").open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(protocol) + "\n")
        handle.write(json.dumps(metadata) + "\n")
        handle.write(json.dumps(add) + "\n")
    print(f"{table}: rows={len(df)}, parquet={parquet_path.stat().st_size} bytes")


def build() -> None:
    """Build silver and gold Delta folders."""
    OUT.mkdir(parents=True, exist_ok=True)
    for table, csv_path in TABLES.items():
        write_delta(table, csv_path)


if __name__ == "__main__":
    build()
