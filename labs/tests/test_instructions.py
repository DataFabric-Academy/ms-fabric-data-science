"""Guard rails for Fabric lab instructions."""

from __future__ import annotations

from pathlib import Path

INSTRUCTIONS = Path(__file__).resolve().parents[1] / "instructions"

LAB_IMPORTS = [
    ("00-lakehouse-setup.md", "00-environment-verification.ipynb"),
    ("01-explore-data.md", "01-explore-data.ipynb"),
    ("02-preprocess-data-wrangler.md", "02-preprocess-data-wrangler.ipynb"),
    ("03-train-track-mlflow.md", "03-train-track-mlflow.ipynb"),
    ("04-batch-predict.md", "04-batch-predict.ipynb"),
]


def test_lab0_imports_notebook_without_creating_a_blank_item() -> None:
    """Importing an .ipynb creates the notebook item; do not + New item first."""
    text = (INSTRUCTIONS / "00-lakehouse-setup.md").read_text(encoding="utf-8")
    import_section = text.split("## นำเข้า notebook แล้วสร้างตาราง Bronze", 1)[1]
    import_section = import_section.split("## ตรวจตาราง Bronze", 1)[0]

    assert "กด **Import**" in import_section
    assert "00-environment-verification.ipynb" in import_section
    assert "เลือก **Notebook** จากนั้น **Create**" not in import_section
    assert "File / …" not in import_section
    assert "+ New item** เพื่อสร้าง notebook ว่าง" in text

    lakehouse_section = text.split("## สร้าง Lakehouse", 1)[1].split(
        "## นำเข้า notebook", 1
    )[0]
    assert "+ New item** แล้วเลือก **Lakehouse**" in lakehouse_section


def test_later_labs_import_notebooks_without_new_item() -> None:
    """Labs 1–4 must import from the workspace, not create a blank notebook."""
    for name, notebook in LAB_IMPORTS[1:]:
        text = (INSTRUCTIONS / name).read_text(encoding="utf-8")
        assert notebook in text
        assert "**Import**" in text
        assert "ไม่ต้อง **+ New item**" in text


def test_run_checklist_imports_without_creating_a_blank_notebook() -> None:
    """Pre-lab checklist must not tell learners to create then import."""
    text = (INSTRUCTIONS / "run-checklist-lab0-2.md").read_text(encoding="utf-8")
    assert "**Import** > **Notebook**" in text
    assert "ไม่ต้อง **+ New item**" in text
    assert "สร้าง Notebook แล้ว" not in text
