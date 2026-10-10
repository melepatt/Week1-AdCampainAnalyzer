from io import BytesIO

import pytest

from src.data_loader import load_sample_data, normalize_column_name, read_campaign_csv


def test_normalize_column_name_uses_lowercase_snake_case():
    assert normalize_column_name("  Campaign ID  ") == "campaign_id"
    assert normalize_column_name("Campaign-Goal") == "campaign_goal"


def test_read_campaign_csv_normalizes_headers_and_preserves_ids():
    source = BytesIO(
        b" Date ,Campaign ID,Campaign Name,Platform,Audience,Campaign Goal,Spend,Impressions,Clicks,Conversions,Revenue\n"
        b"2026-01-01,0012,Launch, Facebook ,Adults,Sales,10,100,8,1,20\n"
    )

    frame = read_campaign_csv(source)

    assert "campaign_id" in frame.columns
    assert frame.loc[0, "campaign_id"] == "0012"
    assert frame.loc[0, "platform"] == " Facebook "


def test_load_sample_data_reads_bundled_csv():
    frame = load_sample_data()

    assert len(frame) == 1080
    assert frame.loc[0, "campaign_id"].startswith(("FB", "IG", "PI", "TW"))


def test_read_campaign_csv_rejects_duplicate_normalized_headers():
    source = BytesIO(b"Campaign ID,campaign_id\nC1,C2\n")

    with pytest.raises(ValueError, match="Duplicate columns after normalization: campaign_id"):
        read_campaign_csv(source)
