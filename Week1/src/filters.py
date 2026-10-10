"""Shared immutable filter state and campaign filtering."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True)
class FilterSelection:
    start_date: date
    end_date: date
    platforms: tuple[str, ...]
    audiences: tuple[str, ...]
    goals: tuple[str, ...]


def apply_filters(frame: pd.DataFrame, selection: FilterSelection) -> pd.DataFrame:
    """Apply all global filters and return a date-sorted defensive copy."""
    dates = pd.to_datetime(frame["date"])
    mask = dates.between(pd.Timestamp(selection.start_date), pd.Timestamp(selection.end_date), inclusive="both")
    mask &= frame["platform"].isin(selection.platforms)
    mask &= frame["audience"].isin(selection.audiences)
    mask &= frame["campaign_goal"].isin(selection.goals)
    return frame.loc[mask].copy(deep=True).sort_values("date", kind="stable").reset_index(drop=True)
