"""Unit-aware formatting helpers for dashboard values."""

from __future__ import annotations

import math

import pandas as pd

from src.metrics import RATIO_METRICS


def _is_displayable(value: int | float | None) -> bool:
    return value is not None and math.isfinite(float(value))


def format_currency(value: float | None) -> str:
    return f"${value:,.2f}" if _is_displayable(value) else "N/A"


def format_count(value: int | float | None) -> str:
    return f"{value:,.0f}" if _is_displayable(value) else "N/A"


def format_percent(value: float | None) -> str:
    return f"{value:,.1f}%" if _is_displayable(value) else "N/A"


def format_multiplier(value: float | None) -> str:
    return f"{value:,.2f}×" if _is_displayable(value) else "N/A"


def prepare_metric_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Replace missing ratio values with the dashboard's explicit N/A label."""
    result = frame.copy(deep=True)
    for column in RATIO_METRICS:
        if column in result:
            result[column] = result[column].map(lambda value: value if _is_displayable(value) else "N/A")
    return result
