"""Shared pytest fixtures for FreshMart lab verification."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

LABS_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = LABS_ROOT / "src"
DATA_DIR = LABS_ROOT / "data"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Return the published lab data directory."""
    return DATA_DIR


@pytest.fixture(scope="session")
def transactions_df(data_dir: Path) -> pd.DataFrame:
    """Load bronze transaction CSV."""
    return pd.read_csv(data_dir / "freshmart_transactions.csv")


@pytest.fixture(scope="session")
def customers_df(data_dir: Path) -> pd.DataFrame:
    """Load bronze customer CSV."""
    return pd.read_csv(data_dir / "freshmart_customers.csv")


@pytest.fixture(scope="session")
def scoring_df(data_dir: Path) -> pd.DataFrame:
    """Load scoring-batch CSV."""
    return pd.read_csv(data_dir / "freshmart_scoring_batch.csv")
