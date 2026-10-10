"""Schema validation and type coercion for campaign data."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import numpy as np
import pandas as pd

from src.data_loader import (
    COUNT_COLUMNS,
    NUMERIC_COLUMNS,
    REQUIRED_COLUMNS,
    SUPPORTED_PLATFORMS,
    TEXT_COLUMNS,
)


@dataclass(frozen=True)
class ValidationResult:
    data: pd.DataFrame | None
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def _row_count(mask: pd.Series) -> int:
    return int(mask.fillna(False).sum())


def _parse_decimal(value: str) -> Decimal | None:
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def validate_campaign_data(frame: pd.DataFrame) -> ValidationResult:
    """Validate all blocking rules, then return a typed defensive copy."""
    errors: list[str] = []
    warnings: list[str] = []
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    errors.extend(f"Missing required column: {column}" for column in missing)
    if frame.empty:
        errors.append("Dataset is empty.")
    if frame.empty:
        return ValidationResult(None, tuple(sorted(errors)), ())

    data = frame.copy(deep=True)
    for column in TEXT_COLUMNS:
        if column in data:
            data[column] = data[column].astype("string").fillna("").str.strip()

    for column in ("campaign_id", "campaign_name"):
        if column not in data:
            continue
        blank = data[column].eq("")
        if blank.any():
            errors.append(f"Column '{column}' has {_row_count(blank)} blank value(s).")

    if "date" in data:
        raw_dates = data["date"].astype("string").fillna("").str.strip()
        parsed_dates = pd.to_datetime(raw_dates, format="%Y-%m-%d", errors="coerce")
        invalid_dates = parsed_dates.isna()
        if invalid_dates.any():
            errors.append(f"Column 'date' has {_row_count(invalid_dates)} invalid or blank value(s).")
        data["date"] = parsed_dates

    canonical_platforms = {platform.casefold(): platform for platform in SUPPORTED_PLATFORMS}
    if "platform" in data:
        platform_keys = data["platform"].str.casefold()
        unsupported = ~platform_keys.isin(canonical_platforms)
        if unsupported.any():
            values = sorted(data.loc[unsupported, "platform"].unique().tolist())
            errors.append(f"Column 'platform' has unsupported value(s): {', '.join(values)}.")
        data["platform"] = platform_keys.map(canonical_platforms).fillna(data["platform"])

    numeric_values: dict[str, pd.Series] = {}
    for column in NUMERIC_COLUMNS:
        if column not in data:
            continue
        raw = data[column].astype("string").fillna("").str.strip()
        if column in COUNT_COLUMNS:
            decimals = raw.map(_parse_decimal)
            non_numeric = decimals.map(lambda value: value is None)
            finite = decimals.map(lambda value: value is not None and value.is_finite())
            non_finite = ~non_numeric & ~finite
            negative = decimals.map(
                lambda value: value is not None and value.is_finite() and value < 0
            )
            fractional = decimals.map(
                lambda value: value is not None
                and value.is_finite()
                and value != value.to_integral_value()
            )
            out_of_range = decimals.map(
                lambda value: value is not None
                and value.is_finite()
                and value > np.iinfo(np.int64).max
            )
            numeric_values[column] = decimals.map(
                lambda value: int(value) if value is not None and value.is_finite() else None
            )
        else:
            numeric = pd.to_numeric(raw, errors="coerce")
            non_numeric = numeric.isna()
            finite = pd.Series(np.isfinite(numeric.to_numpy(dtype=float)), index=data.index)
            non_finite = numeric.notna() & ~finite
            negative = finite & numeric.lt(0)
            fractional = pd.Series(False, index=data.index)
            out_of_range = pd.Series(False, index=data.index)
            numeric_values[column] = numeric
        if non_numeric.any():
            errors.append(f"Column '{column}' has {_row_count(non_numeric)} non-numeric value(s).")
        if non_finite.any():
            errors.append(f"Column '{column}' has {_row_count(non_finite)} non-finite value(s).")
        if negative.any():
            errors.append(f"Column '{column}' has {_row_count(negative)} negative value(s).")
        if column in COUNT_COLUMNS:
            if fractional.any():
                errors.append(f"Column '{column}' has {_row_count(fractional)} fractional count(s).")
            if out_of_range.any():
                errors.append(
                    f"Column '{column}' has {_row_count(out_of_range)} value(s) outside the supported integer range."
                )

    if errors:
        return ValidationResult(None, tuple(sorted(set(errors))), ())

    for column, numeric in numeric_values.items():
        data[column] = numeric.astype("int64" if column in COUNT_COLUMNS else "float64")

    grain = ["date", "campaign_id", "platform", "audience", "campaign_goal"]
    duplicate_rows = data.duplicated(grain, keep=False)
    if duplicate_rows.any():
        warnings.append(f"Found {_row_count(duplicate_rows)} rows at a duplicate reporting grain; all rows were retained.")
    clicks_over = data["clicks"] > data["impressions"]
    if clicks_over.any():
        warnings.append(f"Found {_row_count(clicks_over)} row(s) where clicks exceed impressions.")
    conversions_over = data["conversions"] > data["clicks"]
    if conversions_over.any():
        warnings.append(f"Found {_row_count(conversions_over)} row(s) where conversions exceed clicks.")
    zero_spend_revenue = data["spend"].eq(0) & data["revenue"].gt(0)
    if zero_spend_revenue.any():
        warnings.append(f"Found {_row_count(zero_spend_revenue)} row(s) with zero spend and positive revenue.")
    conflicting_ids = data.groupby("campaign_id", sort=True)["campaign_name"].nunique()
    conflicting_ids = conflicting_ids[conflicting_ids > 1]
    if not conflicting_ids.empty:
        warnings.append(
            "Campaign ID(s) mapped to multiple campaign names: "
            + ", ".join(conflicting_ids.index.astype(str))
            + "."
        )

    return ValidationResult(data, (), tuple(sorted(warnings)))
