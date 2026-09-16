"""Shared FreshMart feature-engineering pipeline for Fabric labs.

The same fit/transform contract is used by Fabric notebooks, local smoke
tests, and Lab 4 scoring so column names, order, and scale parameters stay
aligned with the registered model signature.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

ID_COLUMN = "CustomerID"
TARGET_COLUMN = "Churn"
CATEGORICAL_COLUMNS = ("MembershipTier", "Gender")
IMPUTE_MEDIAN_COLUMNS = ("Age",)
SCALE_COLUMNS = (
    "MonetaryTotal",
    "AvgBasketSize",
    "RecencyDays",
    "TenureMonths",
)
DUMMY_COLUMNS = (
    "MembershipTier_Bronze",
    "MembershipTier_Gold",
    "MembershipTier_Platinum",
    "MembershipTier_Silver",
    "Gender_F",
    "Gender_M",
    "Gender_Other",
)
PASSTHROUGH_COLUMNS = ("Frequency", "ComplaintCount")
FEATURE_COLUMNS = (
    "Age",
    "TenureMonths",
    "RecencyDays",
    "Frequency",
    "MonetaryTotal",
    "AvgBasketSize",
    "ComplaintCount",
    *DUMMY_COLUMNS,
)

REQUIRED_RAW_COLUMNS = (
    ID_COLUMN,
    "Age",
    "Gender",
    "MembershipTier",
    "TenureMonths",
    "RecencyDays",
    "Frequency",
    "MonetaryTotal",
    "AvgBasketSize",
    "ComplaintCount",
)


@dataclass(frozen=True)
class FeatureParams:
    """Fitted preprocessing parameters reused at scoring time.

    Attributes:
        age_median: Median Age computed from the training customers.
        scale_mins: Per-column minimum used for min-max scaling.
        scale_maxs: Per-column maximum used for min-max scaling.
        dummy_columns: One-hot columns the model expects, in order.
        feature_columns: Final model input columns, in order.
    """

    age_median: float
    scale_mins: dict[str, float]
    scale_maxs: dict[str, float]
    dummy_columns: list[str]
    feature_columns: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Serialize parameters to a JSON-friendly dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "FeatureParams":
        """Create parameters from a dictionary.

        Args:
            payload: Mapping produced by ``to_dict``.

        Returns:
            Validated ``FeatureParams``.

        Raises:
            ValueError: If required keys are missing.
        """
        required = {
            "age_median",
            "scale_mins",
            "scale_maxs",
            "dummy_columns",
            "feature_columns",
        }
        missing = required - set(payload)
        if missing:
            raise ValueError(f"FeatureParams missing keys: {sorted(missing)}")
        return cls(
            age_median=float(payload["age_median"]),
            scale_mins={k: float(v) for k, v in payload["scale_mins"].items()},
            scale_maxs={k: float(v) for k, v in payload["scale_maxs"].items()},
            dummy_columns=list(payload["dummy_columns"]),
            feature_columns=list(payload["feature_columns"]),
        )


def _require_columns(df: pd.DataFrame, columns: tuple[str, ...], *, frame_name: str) -> None:
    """Raise if expected columns are missing."""
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"{frame_name} missing required columns: {missing}")


def _numeric_copy(df: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    """Return a copy with selected columns coerced to numeric."""
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def validate_raw_customers(df: pd.DataFrame, *, require_target: bool = True) -> pd.DataFrame:
    """Validate and normalize a raw FreshMart customer frame.

    Args:
        df: Raw customer records from CSV or ``bronze.customers``.
        require_target: When True, require the ``Churn`` column.

    Returns:
        Copy with numeric columns coerced.

    Raises:
        ValueError: If required columns are missing.
    """
    required = REQUIRED_RAW_COLUMNS + ((TARGET_COLUMN,) if require_target else ())
    _require_columns(df, required, frame_name="customer frame")
    numeric_cols = (
        "Age",
        "TenureMonths",
        "RecencyDays",
        "Frequency",
        "MonetaryTotal",
        "AvgBasketSize",
        "ComplaintCount",
    )
    if require_target:
        numeric_cols = numeric_cols + (TARGET_COLUMN,)
    return _numeric_copy(df, numeric_cols)


def fit_preprocessor(df_raw: pd.DataFrame) -> FeatureParams:
    """Fit imputation and scaling parameters on training customers.

    Args:
        df_raw: Raw customer DataFrame including ``Churn``.

    Returns:
        Fitted parameters that must be reused for scoring.
    """
    df = validate_raw_customers(df_raw, require_target=True)
    age_median = float(df["Age"].median())
    if pd.isna(age_median):
        raise ValueError("Cannot fit preprocessor: Age median is NaN")

    scale_mins: dict[str, float] = {}
    scale_maxs: dict[str, float] = {}
    for col in SCALE_COLUMNS:
        col_min = float(df[col].min())
        col_max = float(df[col].max())
        if col_max <= col_min:
            raise ValueError(f"Cannot scale {col}: min={col_min}, max={col_max}")
        scale_mins[col] = col_min
        scale_maxs[col] = col_max

    params = FeatureParams(
        age_median=age_median,
        scale_mins=scale_mins,
        scale_maxs=scale_maxs,
        dummy_columns=list(DUMMY_COLUMNS),
        feature_columns=list(FEATURE_COLUMNS),
    )
    logger.info(
        "Fitted feature params: age_median=%.1f, scale_columns=%s",
        params.age_median,
        list(SCALE_COLUMNS),
    )
    return params


def _one_hot_categories(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode membership and gender, keeping the expected columns."""
    encoded = pd.get_dummies(df, columns=list(CATEGORICAL_COLUMNS), drop_first=False)
    for col in DUMMY_COLUMNS:
        if col not in encoded.columns:
            encoded[col] = 0
    return encoded


def _min_max_scale(series: pd.Series, col_min: float, col_max: float) -> pd.Series:
    """Scale a series to [0, 1] using fitted min/max."""
    return (series - col_min) / (col_max - col_min + 1e-6)


def transform_customers(
    df_raw: pd.DataFrame,
    params: FeatureParams,
    *,
    require_target: bool = False,
) -> pd.DataFrame:
    """Apply the fitted FreshMart preprocessing contract.

    Args:
        df_raw: Raw customer records (training or scoring batch).
        params: Parameters from ``fit_preprocessor``.
        require_target: When True, keep and validate ``Churn``.

    Returns:
        Feature frame with ``CustomerID``, model columns, and optional ``Churn``.
    """
    df = validate_raw_customers(df_raw, require_target=require_target)
    work = df.copy()
    work["Age"] = work["Age"].fillna(params.age_median)

    work = _one_hot_categories(work)
    for col in SCALE_COLUMNS:
        work[col] = _min_max_scale(
            work[col],
            params.scale_mins[col],
            params.scale_maxs[col],
        )

    bool_cols = work.select_dtypes(include="bool").columns
    work[bool_cols] = work[bool_cols].astype(int)

    ordered = [ID_COLUMN, *params.feature_columns]
    if require_target or TARGET_COLUMN in work.columns:
        ordered.append(TARGET_COLUMN)
    missing = [col for col in ordered if col not in work.columns]
    if missing:
        raise ValueError(f"Transformed frame missing columns: {missing}")

    result = work[ordered].copy()
    feature_frame = result[list(params.feature_columns)]
    if feature_frame.isna().any().any():
        bad = feature_frame.columns[feature_frame.isna().any()].tolist()
        raise ValueError(f"NaN remaining in feature columns: {bad}")
    return result


def clean_data(df_input: pd.DataFrame) -> pd.DataFrame:
    """Convenience wrapper matching the Data Wrangler export name.

    Fits and transforms in one step. Use only on the training customers.
    Lab 4 must call ``fit_preprocessor`` once, persist params, then
    ``transform_customers``.

    Args:
        df_input: Raw training customers.

    Returns:
        Cleaned silver-style feature frame including ``Churn``.
    """
    params = fit_preprocessor(df_input)
    return transform_customers(df_input, params, require_target=True)


def save_feature_params(params: FeatureParams, path: str | Path) -> Path:
    """Write feature parameters to a JSON file.

    Args:
        params: Fitted parameters.
        path: Destination JSON path.

    Returns:
        Resolved output path.
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(params.to_dict(), indent=2), encoding="utf-8")
    logger.info("Saved feature params to %s", out)
    return out


def load_feature_params(path: str | Path) -> FeatureParams:
    """Load feature parameters from a JSON file.

    Args:
        path: JSON path written by ``save_feature_params``.

    Returns:
        Fitted parameters.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Feature params not found: {src}")
    payload = json.loads(src.read_text(encoding="utf-8"))
    return FeatureParams.from_dict(payload)


def model_matrix(df_features: pd.DataFrame, params: FeatureParams) -> pd.DataFrame:
    """Return the model input matrix in signature order.

    Args:
        df_features: Output of ``transform_customers``.
        params: Fitted parameters.

    Returns:
        DataFrame with only model feature columns.
    """
    _require_columns(df_features, tuple(params.feature_columns), frame_name="feature frame")
    return df_features[list(params.feature_columns)].astype(float)
