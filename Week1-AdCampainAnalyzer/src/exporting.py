"""Deterministic in-memory exports for Streamlit download buttons."""

from __future__ import annotations

import pandas as pd


def dataframe_to_csv_bytes(frame: pd.DataFrame) -> bytes:
    """Serialize a DataFrame as UTF-8 CSV with its current column order."""
    return frame.to_csv(index=False, lineterminator="\n").encode("utf-8")
