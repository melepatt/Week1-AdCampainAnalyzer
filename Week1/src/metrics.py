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


def aggregate_by_platform(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate additive and ratio metrics for each advertising platform."""
    aggregate = (
        frame.groupby("platform", as_index=False, sort=True)[list(ADDITIVE_METRICS)]
        .sum()
        .sort_values("platform", kind="stable")
        .reset_index(drop=True)
    )
    return add_ratio_metrics(aggregate)


def _join_labels(values: pd.Series) -> str:
    return ", ".join(sorted({str(value) for value in values}))


def aggregate_by_campaign(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate campaigns, retaining deterministic labels for conflicts."""
    aggregate = frame.groupby("campaign_id", as_index=False, sort=True).agg(
        campaign_name=("campaign_name", _join_labels),
        platform=("platform", _join_labels),
        audience=("audience", _join_labels),
        campaign_goal=("campaign_goal", _join_labels),
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
    )
    return add_ratio_metrics(aggregate)


def aggregate_time_series(
    frame: pd.DataFrame,
    frequency: str,
    break_down_by_platform: bool = False,
) -> pd.DataFrame:
    """Aggregate metrics into daily, Monday-start weekly, or monthly periods."""
    data = frame.copy(deep=True)
    dates = pd.to_datetime(data["date"])
    if frequency == "Daily":
        data["date"] = dates.dt.normalize()
    elif frequency == "Weekly":
        data["date"] = dates.dt.to_period("W-SUN").dt.start_time
    elif frequency == "Monthly":
        data["date"] = dates.dt.to_period("M").dt.start_time
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")

    group_columns = ["date"]
    if break_down_by_platform:
        group_columns.append("platform")
    aggregate = (
        data.groupby(group_columns, as_index=False, sort=True)[list(ADDITIVE_METRICS)]
        .sum()
        .sort_values(group_columns, kind="stable")
        .reset_index(drop=True)
    )
    return add_ratio_metrics(aggregate)
