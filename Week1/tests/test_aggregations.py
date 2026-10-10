import pandas as pd
import pytest

from src.metrics import aggregate_by_campaign, aggregate_by_platform, aggregate_time_series


def _aggregate_frame():
    return pd.DataFrame(
        [
            {"date": pd.Timestamp("2026-01-31"), "campaign_id": "C1", "campaign_name": "Zulu", "platform": "Facebook", "audience": "Adults", "campaign_goal": "Sales", "spend": 100.0, "revenue": 300.0, "impressions": 1000, "clicks": 100, "conversions": 10},
            {"date": pd.Timestamp("2026-02-01"), "campaign_id": "C1", "campaign_name": "Alpha", "platform": "Facebook", "audience": "Students", "campaign_goal": "Traffic", "spend": 50.0, "revenue": 50.0, "impressions": 100, "clicks": 50, "conversions": 25},
            {"date": pd.Timestamp("2026-02-02"), "campaign_id": "C2", "campaign_name": "Beta", "platform": "Instagram", "audience": "Adults", "campaign_goal": "Sales", "spend": 25.0, "revenue": 100.0, "impressions": 500, "clicks": 25, "conversions": 5},
        ]
    )


def test_platform_aggregation_recalculates_ratios_from_totals():
    result = aggregate_by_platform(_aggregate_frame()).set_index("platform")
    facebook = result.loc["Facebook"]
    assert facebook["spend"] == 150.0
    assert facebook["ctr"] == pytest.approx(150 / 1100 * 100)
    assert facebook["roi"] == pytest.approx((350 - 150) / 150 * 100)


def test_campaign_aggregation_uses_sorted_stable_category_labels():
    result = aggregate_by_campaign(_aggregate_frame()).set_index("campaign_id")
    campaign = result.loc["C1"]
    assert campaign["campaign_name"] == "Alpha, Zulu"
    assert campaign["audience"] == "Adults, Students"
    assert campaign["campaign_goal"] == "Sales, Traffic"
    assert campaign["platform"] == "Facebook"
    assert campaign["conversions"] == 35


@pytest.mark.parametrize(
    ("frequency", "expected_dates"),
    [
        ("Daily", ["2026-01-31", "2026-02-01", "2026-02-02"]),
        ("Weekly", ["2026-01-26", "2026-02-02"]),
        ("Monthly", ["2026-01-01", "2026-02-01"]),
    ],
)
def test_time_aggregation_period_labels(frequency, expected_dates):
    result = aggregate_time_series(_aggregate_frame(), frequency)
    assert result["date"].dt.strftime("%Y-%m-%d").tolist() == expected_dates


def test_weekly_aggregation_keeps_sunday_in_monday_start_week():
    result = aggregate_time_series(_aggregate_frame(), "Weekly").set_index("date")
    assert result.loc[pd.Timestamp("2026-01-26"), "spend"] == 150.0
    assert result.loc[pd.Timestamp("2026-02-02"), "spend"] == 25.0


def test_platform_breakdown_retains_each_period_and_platform():
    result = aggregate_time_series(_aggregate_frame(), "Weekly", break_down_by_platform=True)
    assert list(result[["date", "platform"]].itertuples(index=False, name=None)) == [
        (pd.Timestamp("2026-01-26"), "Facebook"),
        (pd.Timestamp("2026-02-02"), "Instagram"),
    ]
