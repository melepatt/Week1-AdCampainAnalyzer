"""Aggregate campaign metric calculations."""

from __future__ import annotations

import math

import pandas as pd


ADDITIVE_METRICS = ("spend", "revenue", "impressions", "clicks", "conversions")
RATIO_METRICS = ("ctr", "cpc", "conversion_rate", "cpa", "roas", "roi")


def safe_ratio(numerator: float, denominator: float, scale: float = 1.0) -> float | None:
    """Divide finite values without ever producing infinity."""
    if not math.isfinite(float(numerator)) or not math.isfinite(float(denominator)) or denominator == 0:
        return None
    result = float(numerator) / float(denominator) * scale
    return result if math.isfinite(result) else None


def _ratios(spend: float, revenue: float, impressions: int, clicks: int, conversions: int) -> dict[str, float | None]:
    return {
        "ctr": safe_ratio(clicks, impressions, 100.0),
        "cpc": safe_ratio(spend, clicks),
        "conversion_rate": safe_ratio(conversions, clicks, 100.0),
        "cpa": safe_ratio(spend, conversions),
        "roas": safe_ratio(revenue, spend),
        "roi": safe_ratio(revenue - spend, spend, 100.0),
    }


def calculate_summary(frame: pd.DataFrame) -> dict[str, int | float | None]:
    """Return totals and ratios calculated from those totals."""
    totals: dict[str, int | float | None] = {
        "spend": float(frame["spend"].sum()),
        "revenue": float(frame["revenue"].sum()),
        "impressions": int(frame["impressions"].sum()),
        "clicks": int(frame["clicks"].sum()),
        "conversions": int(frame["conversions"].sum()),
    }
    totals.update(
        _ratios(
            float(totals["spend"]),
            float(totals["revenue"]),
            int(totals["impressions"]),
            int(totals["clicks"]),
            int(totals["conversions"]),
        )
    )
    return totals


def add_ratio_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Append ratio columns to aggregate rows without mutating the input."""
    result = frame.copy(deep=True)
    ratio_rows = [
        _ratios(row.spend, row.revenue, row.impressions, row.clicks, row.conversions)
        for row in result.itertuples(index=False)
    ]
    for metric in RATIO_METRICS:
        result[metric] = [values[metric] for values in ratio_rows]
    return result
