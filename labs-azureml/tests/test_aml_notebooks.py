"""Guard rails for the published Azure ML student notebooks."""

from __future__ import annotations

import json
from pathlib import Path

NOTEBOOKS = [
    "00-environment-verification.ipynb",
    "01-explore-data.ipynb",
    "02-preprocess-data-wrangler.ipynb",
    "03-automl-classification.ipynb",
    "03-train-track-mlflow.ipynb",
    "04-batch-predict.ipynb",
]


def _notebook_source(name: str) -> str:
    root = Path(__file__).resolve().parents[1] / "notebooks"
    path = root / name
    assert path.exists(), f"Missing notebook {name}"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["nbformat"] == 4
    return "".join(
        "".join(cell.get("source", [])) if isinstance(cell.get("source"), list) else cell.get("source", "")
        for cell in payload["cells"]
    )


def test_aml_notebooks_are_valid_json_and_verify() -> None:
    """Every published notebook must be parseable and contain verification text."""
    for name in NOTEBOOKS:
        sources = _notebook_source(name)
        assert "verification passed" in sources.lower()
        assert "Azure Machine Learning" in sources
        assert "lh_freshmart" not in sources
        assert "spark.read.table" not in sources


def test_aml_notebooks_keep_freshmart_story() -> None:
    """Classroom numbers and the AutoML champion name must stay aligned."""
    lab1 = _notebook_source("01-explore-data.ipynb")
    assert "19.3%" in lab1
    assert "37" in lab1

    lab3 = _notebook_source("03-automl-classification.ipynb")
    assert "freshmart-churn-model" in lab3
    assert "freshmart-churn-prediction" in lab3
    assert "AUC_weighted" in lab3

    lab3b = _notebook_source("03-train-track-mlflow.ipynb")
    assert "freshmart-churn-manual" in lab3b

    lab4 = _notebook_source("04-batch-predict.ipynb")
    assert "feature_params.json" in lab4
    assert "models:/freshmart-churn-model/1" in lab4
    assert "mlflow.pyfunc" in lab4
    assert "ไม่สร้าง Batch Endpoint" in lab4


def test_aml_loader_does_not_depend_on_fabric_lakehouse() -> None:
    """Azure ML notebooks must resolve CSVs from repo or data/raw."""
    lab0 = _notebook_source("00-environment-verification.ipynb")
    assert "labs/data" in lab0
    assert "data/raw" in lab0 or "data\") / \"raw\"" in lab0
    assert "save_layer" in lab0
    assert "bronze-transactions" in lab0
    assert "register_data_asset" in lab0
