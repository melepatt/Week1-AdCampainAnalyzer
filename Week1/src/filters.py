"""Shared immutable filter state and campaign filtering."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping

import pandas as pd


@dataclass(frozen=True)
class FilterSelection:
    start_date: date
    end_date: date
    platforms: tuple[str, ...]
    audiences: tuple[str, ...]
    goals: tuple[str, ...]


def reconcile_filter_state(
    frame: pd.DataFrame,
    source_key: str,
    previous: Mapping[str, object],
) -> dict[str, object]:
    """Return valid widget state, resetting fully when the data source changes."""
    min_date = pd.to_datetime(frame["date"]).min().date()
    max_date = pd.to_datetime(frame["date"]).max().date()
    options = {
        "filter_platforms": tuple(sorted(frame["platform"].unique())),
        "filter_audiences": tuple(sorted(frame["audience"].unique())),
        "filter_goals": tuple(sorted(frame["campaign_goal"].unique())),
    }
    defaults: dict[str, object] = {
        "filter_source_key": source_key,
        "filter_dates": (min_date, max_date),
        **{key: list(values) for key, values in options.items()},
    }
    if previous.get("filter_source_key") != source_key:
        return defaults

    selected_dates = previous.get("filter_dates")
    if (
        isinstance(selected_dates, (tuple, list))
        and len(selected_dates) == 2
        and all(isinstance(value, date) for value in selected_dates)
        and min_date <= selected_dates[0] <= selected_dates[1] <= max_date
    ):
        defaults["filter_dates"] = tuple(selected_dates)
    for key, valid_values in options.items():
        selected = previous.get(key)
        if isinstance(selected, (tuple, list)):
            defaults[key] = [value for value in selected if value in valid_values]
    return defaults


def apply_filters(frame: pd.DataFrame, selection: FilterSelection) -> pd.DataFrame:
    """Apply all global filters and return a date-sorted defensive copy."""
    dates = pd.to_datetime(frame["date"])
    mask = dates.between(pd.Timestamp(selection.start_date), pd.Timestamp(selection.end_date), inclusive="both")
    mask &= frame["platform"].isin(selection.platforms)
    mask &= frame["audience"].isin(selection.audiences)
    mask &= frame["campaign_goal"].isin(selection.goals)
    return frame.loc[mask].copy(deep=True).sort_values("date", kind="stable").reset_index(drop=True)
