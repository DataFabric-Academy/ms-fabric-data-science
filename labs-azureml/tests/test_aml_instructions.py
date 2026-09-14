"""Guard rails for Azure ML lab instructions (keep Fabric track untouched)."""

from __future__ import annotations

from pathlib import Path

INSTRUCTIONS = Path(__file__).resolve().parents[1] / "instructions"

REQUIRED = [
    "00-workspace-setup.md",
    "01-explore-data.md",
    "02-preprocess-data-wrangler.md",
    "03-automl-classification.md",
    "03-train-track-mlflow.md",
    "04-batch-predict.md",
    "instructor-automl-demo.md",
]


def test_aml_instruction_files_exist_and_stay_on_azure_ml() -> None:
    """Instruction set must be complete and must not point students at Fabric Capacity."""
    for name in REQUIRED:
        path = INSTRUCTIONS / name
        assert path.exists(), f"Missing instruction {name}"
        text = path.read_text(encoding="utf-8")
        assert "Azure" in text
        assert "lh_freshmart" not in text


def test_aml_data_assets_are_required_catalog() -> None:
    """Studio Data assets must be the system of record across labs."""
    lab0 = (INSTRUCTIONS / "00-workspace-setup.md").read_text(encoding="utf-8")
    assert "งานที่ 4: สร้าง Data asset จากหน้า Data" in lab0
    assert "bronze-transactions" in lab0
    assert "scoring-batch" in lab0

    lab2 = (INSTRUCTIONS / "02-preprocess-data-wrangler.md").read_text(encoding="utf-8")
    assert "ทางเลือก" not in lab2
    assert "silver-customer-features" in lab2

    lab3 = (INSTRUCTIONS / "03-automl-classification.md").read_text(encoding="utf-8")
    assert "เลือก Data asset ชั้น Silver" in lab3

    lab4 = (INSTRUCTIONS / "04-batch-predict.md").read_text(encoding="utf-8")
    assert "gold-freshmart-predictions" in lab4
    assert "scoring-batch" in lab4


def test_aml_lab0_mentions_cost_control() -> None:
    """Emergency track must tell learners to stop the compute instance."""
    text = (INSTRUCTIONS / "00-workspace-setup.md").read_text(encoding="utf-8")
    assert "Stop" in text
    assert "Standard_DS11_v2" in text


def test_aml_lab3_automl_is_the_lead_path() -> None:
    """AutoML must be the required student lab, written in Learn exercise style."""
    text = (INSTRUCTIONS / "03-automl-classification.md").read_text(encoding="utf-8")
    assert "ในแบบฝึกหัดนี้ คุณจะเรียนรู้วิธี" in text
    assert "งานที่ 1" in text
    assert "AUC_weighted" in text
    assert "CustomerID" in text
    assert "freshmart-churn-model" in text
    assert "Deploy" in text


def test_aml_manual_mlflow_is_optional_and_renamed() -> None:
    """Hand-trained models must not overwrite the AutoML champion."""
    text = (INSTRUCTIONS / "03-train-track-mlflow.md").read_text(encoding="utf-8")
    assert "ไม่บังคับ" in text
    assert "freshmart-churn-manual" in text


def test_aml_instructor_notes_treat_automl_as_class_lab() -> None:
    """Instructor notes facilitate the student AutoML lab instead of a solo demo."""
    text = (INSTRUCTIONS / "instructor-automl-demo.md").read_text(encoding="utf-8")
    assert "แบบฝึกหัด 3" in text
    assert "freshmart-churn-model" in text
    assert "Deploy" in text
