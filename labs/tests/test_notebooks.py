"""Guard rails for the published student notebooks."""

from __future__ import annotations

import json
from pathlib import Path

NOTEBOOKS = [
    "00-environment-verification.ipynb",
    "01-explore-data.ipynb",
    "02-preprocess-data-wrangler.ipynb",
    "03-train-track-mlflow.ipynb",
    "04-batch-predict.ipynb",
]


def test_notebooks_are_valid_json() -> None:
    """Every published notebook must be parseable and contain verification text."""
    root = Path(__file__).resolve().parents[1] / "notebooks"
    for name in NOTEBOOKS:
        path = root / name
        assert path.exists(), f"Missing notebook {name}"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["nbformat"] == 4
        sources = "".join(
            "".join(cell.get("source", [])) if isinstance(cell.get("source"), list) else cell.get("source", "")
            for cell in payload["cells"]
        )
        assert "verification passed" in sources.lower() or "Lab 0 verification" in sources
        assert "ถ้าติด" in sources or "กฎทอง" in sources or "ความรู้" in sources
