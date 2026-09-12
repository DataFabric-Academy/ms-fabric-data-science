"""Build minimal Delta table folders from FreshMart CSVs for OneLake upload."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / ".local" / "delta_upload"

TABLES = {
    "bronze/transactions": "freshmart_transactions.csv",
    "bronze/customers": "freshmart_customers.csv",
}


def _delta_add_action(path: str, size: int, num_records: int) -> dict:
    """Create a Delta Lake add action for a single parquet file."""
    return {
        "add": {
            "path": path,
            "partitionValues": {},
            "size": size,
            "modificationTime": int(datetime.now(timezone.utc).timestamp() * 1000),
            "dataChange": True,
            "stats": json.dumps({"numRecords": num_records}),
        }
    }


def build() -> None:
    """Write local Delta folders ready for OneLake Tables/ upload."""
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    con = duckdb.connect()
    for table, csv_name in TABLES.items():
        table_dir = OUT / table
        table_dir.mkdir(parents=True)
        parquet_name = "part-00000.parquet"
        parquet_path = table_dir / parquet_name
        csv_path = (DATA / csv_name).as_posix()
        con.execute(
            f"""
            COPY (
                SELECT * FROM read_csv_auto('{csv_path}', header=true)
            ) TO '{parquet_path.as_posix()}' (FORMAT PARQUET)
            """
        )
        row_count = con.execute(
            f"SELECT COUNT(*) FROM read_csv_auto('{csv_path}', header=true)"
        ).fetchone()[0]
        schema = con.execute(
            f"DESCRIBE SELECT * FROM read_csv_auto('{csv_path}', header=true)"
        ).fetchall()
        fields = []
        for col_name, col_type, *_ in schema:
            fields.append(
                {
                    "name": col_name,
                    "type": _map_type(str(col_type)),
                    "nullable": True,
                    "metadata": {},
                }
            )
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
        add = _delta_add_action(parquet_name, parquet_path.stat().st_size, int(row_count))
        log_dir = table_dir / "_delta_log"
        log_dir.mkdir(parents=True)
        commit_path = log_dir / "00000000000000000000.json"
        with commit_path.open("w", encoding="utf-8") as handle:
            handle.write(json.dumps(protocol) + "\n")
            handle.write(json.dumps(metadata) + "\n")
            handle.write(json.dumps(add) + "\n")
        print(f"{table}: rows={row_count}, parquet={parquet_path.stat().st_size} bytes")


def _map_type(duck_type: str) -> str | dict:
    """Map DuckDB types to Delta primitive type names."""
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
    if upper.startswith("DATE"):
        return "date"
    if upper.startswith("TIMESTAMP"):
        return "timestamp"
    return "string"


if __name__ == "__main__":
    build()
