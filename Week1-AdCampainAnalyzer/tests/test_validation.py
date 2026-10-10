import math

import pandas as pd
import pytest

from src.validation import validate_campaign_data


def test_valid_data_is_trimmed_canonicalized_and_typed(valid_campaign_frame):
    valid_campaign_frame.loc[0, "platform"] = " facebook "
    valid_campaign_frame.loc[0, "campaign_name"] = "  New Year Awareness "

    result = validate_campaign_data(valid_campaign_frame)

    assert result.errors == ()
    assert result.data is not None
    assert result.data.loc[0, "platform"] == "Facebook"
    assert result.data.loc[0, "campaign_name"] == "New Year Awareness"
    assert result.data.loc[1, "campaign_id"] == "0012"
    assert pd.api.types.is_datetime64_any_dtype(result.data["date"])
    assert result.data["impressions"].dtype.kind in "iu"
    assert result.data["spend"].dtype.kind == "f"


def test_every_missing_column_is_reported(valid_campaign_frame):
    result = validate_campaign_data(valid_campaign_frame.drop(columns=["date", "revenue"]))

    assert any("date" in message for message in result.errors)
    assert any("revenue" in message for message in result.errors)


def test_empty_frame_is_rejected(valid_campaign_frame):
    result = validate_campaign_data(valid_campaign_frame.iloc[0:0])
    assert any("empty" in message.lower() for message in result.errors)


@pytest.mark.parametrize(
    ("column", "value", "message_fragment"),
    [
        ("date", "not-a-date", "date"),
        ("date", "", "date"),
        ("campaign_id", "  ", "campaign_id"),
        ("campaign_name", "", "campaign_name"),
        ("platform", "TikTok", "platform"),
        ("spend", "oops", "spend"),
        ("spend", "-1", "spend"),
        ("impressions", "10.5", "impressions"),
        ("clicks", "inf", "clicks"),
        ("revenue", "-inf", "revenue"),
        ("conversions", "NaN", "conversions"),
    ],
)
def test_blocking_validation_rules(valid_campaign_frame, column, value, message_fragment):
    valid_campaign_frame.loc[0, column] = value

    result = validate_campaign_data(valid_campaign_frame)

    assert result.data is None
    assert any(message_fragment in message for message in result.errors)


@pytest.mark.parametrize(
    ("changes", "message_fragment"),
    [
        ({"clicks": "10001"}, "clicks exceed impressions"),
        ({"conversions": "401"}, "conversions exceed clicks"),
        ({"spend": "0", "revenue": "10"}, "zero spend"),
    ],
)
def test_row_level_anomalies_return_warnings(valid_campaign_frame, changes, message_fragment):
    for column, value in changes.items():
        valid_campaign_frame.loc[0, column] = value

    result = validate_campaign_data(valid_campaign_frame)

    assert result.errors == ()
    assert any(message_fragment in warning.lower() for warning in result.warnings)


def test_duplicate_grain_returns_warning(valid_campaign_frame):
    duplicated = pd.concat([valid_campaign_frame, valid_campaign_frame.iloc[[0]]], ignore_index=True)
    result = validate_campaign_data(duplicated)
    assert any("duplicate" in warning.lower() for warning in result.warnings)


def test_campaign_id_name_conflict_returns_warning(valid_campaign_frame):
    valid_campaign_frame.loc[1, "campaign_id"] = "C001"
    valid_campaign_frame.loc[1, "campaign_name"] = "A Different Name"
    result = validate_campaign_data(valid_campaign_frame)
    assert any("multiple campaign names" in warning.lower() for warning in result.warnings)


def test_validation_never_returns_non_finite_numeric_values(valid_campaign_frame):
    result = validate_campaign_data(valid_campaign_frame)
    assert result.data is not None
    assert all(
        math.isfinite(value)
        for column in ("spend", "revenue")
        for value in result.data[column]
    )


@pytest.mark.parametrize("value", [str(2**63), "9.223372036854777e18"])
def test_count_larger_than_int64_is_rejected(valid_campaign_frame, value):
    valid_campaign_frame.loc[0, "impressions"] = value
    result = validate_campaign_data(valid_campaign_frame)
    assert result.data is None
    assert any("impressions" in message and "integer range" in message for message in result.errors)


def test_missing_columns_do_not_hide_other_detectable_errors(valid_campaign_frame):
    frame = valid_campaign_frame.drop(columns="revenue")
    frame.loc[0, "date"] = "not-a-date"
    frame.loc[0, "campaign_id"] = ""
    frame.loc[0, "platform"] = "TikTok"
    frame.loc[0, "spend"] = "-1"

    result = validate_campaign_data(frame)

    combined = " ".join(result.errors)
    assert all(term in combined for term in ("revenue", "date", "campaign_id", "platform", "spend"))
