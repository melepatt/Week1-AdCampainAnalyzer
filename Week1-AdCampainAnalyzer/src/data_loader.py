"""CSV ingestion and column-name normalization."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import BinaryIO

import pandas as pd


REQUIRED_COLUMNS = (
    "date",
    "campaign_id",
    "campaign_name",
    "platform",
    "audience",
    "campaign_goal",
    "spend",
    "impressions",
    "clicks",
    "conversions",
    "revenue",
)
NUMERIC_COLUMNS = ("spend", "impressions", "clicks", "conversions", "revenue")
COUNT_COLUMNS = ("impressions", "clicks", "conversions")
TEXT_COLUMNS = ("campaign_id", "campaign_name", "platform", "audience", "campaign_goal")
SUPPORTED_PLATFORMS = ("Facebook", "Instagram", "Pinterest", "Twitter")


def normalize_column_name(name: object) -> str:
    """Convert a column label to a stable lowercase snake-case name."""
    normalized = re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower())
    return normalized.strip("_")


def read_campaign_csv(source: str | Path | BinaryIO) -> pd.DataFrame:
    """Read a campaign CSV as text and normalize its headers."""
    frame = pd.read_csv(source, dtype=str, keep_default_na=False)
    normalized = [normalize_column_name(column) for column in frame.columns]
    duplicates = sorted(name for name, count in Counter(normalized).items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate columns after normalization: {', '.join(duplicates)}")
    frame.columns = normalized
    return frame


def load_sample_data(path: Path | None = None) -> pd.DataFrame:
    """Load the bundled deterministic sample campaign dataset."""
    sample_path = path or Path(__file__).resolve().parents[1] / "data" / "sample_campaigns.csv"
    return read_campaign_csv(sample_path)
