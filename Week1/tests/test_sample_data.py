import pandas as pd

from scripts.generate_sample_data import generate_sample_data


REQUIRED_COLUMNS = [
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
]


def test_generate_sample_data_has_required_shape_and_dates():
    frame = generate_sample_data()

    assert list(frame.columns) == REQUIRED_COLUMNS
    assert len(frame) == 1080
    assert frame["date"].min() == pd.Timestamp("2026-01-01")
    assert frame["date"].max() == pd.Timestamp("2026-03-31")
    assert frame["campaign_id"].nunique() == 12
    assert (frame[["spend", "impressions", "clicks", "conversions", "revenue"]] >= 0).all().all()


def test_generate_sample_data_balances_platforms():
    frame = generate_sample_data()

    assert set(frame["platform"]) == {"Facebook", "Instagram", "Pinterest", "Twitter"}
    assert frame.groupby("platform")["campaign_id"].nunique().to_dict() == {
        "Facebook": 3,
        "Instagram": 3,
        "Pinterest": 3,
        "Twitter": 3,
    }


def test_generate_sample_data_is_deterministic():
    pd.testing.assert_frame_equal(generate_sample_data(), generate_sample_data())
    assert not generate_sample_data(seed=7).equals(generate_sample_data(seed=42))
