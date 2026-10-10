import math

import pandas as pd
import pytest

from src.metrics import add_ratio_metrics, calculate_summary, safe_ratio


@pytest.fixture
def uneven_metric_frame():
    return pd.DataFrame(
        {
            "spend": [100.0, 100.0],
            "revenue": [300.0, 100.0],
            "impressions": [1000, 100],
            "clicks": [100, 50],
            "conversions": [10, 25],
        }
    )


def test_summary_uses_aggregate_totals_for_every_ratio(uneven_metric_frame):
    summary = calculate_summary(uneven_metric_frame)

    assert summary["spend"] == 200.0
    assert summary["revenue"] == 400.0
    assert summary["impressions"] == 1100
    assert summary["clicks"] == 150
    assert summary["conversions"] == 35
    assert summary["ctr"] == pytest.approx(150 / 1100 * 100)
    assert summary["cpc"] == pytest.approx(200 / 150)
    assert summary["conversion_rate"] == pytest.approx(35 / 150 * 100)
    assert summary["cpa"] == pytest.approx(200 / 35)
    assert summary["roas"] == pytest.approx(2.0)
    assert summary["roi"] == pytest.approx(100.0)


@pytest.mark.parametrize("numerator", [0.0, 10.0])
def test_safe_ratio_returns_none_for_zero_denominator(numerator):
    assert safe_ratio(numerator, 0) is None


def test_empty_summary_has_zero_totals_and_no_ratios():
    frame = pd.DataFrame(columns=["spend", "revenue", "impressions", "clicks", "conversions"])
    summary = calculate_summary(frame)

    assert summary["spend"] == 0
    assert all(summary[key] is None for key in ("ctr", "cpc", "conversion_rate", "cpa", "roas", "roi"))


def test_add_ratio_metrics_does_not_mutate_input():
    aggregate = pd.DataFrame(
        [{"platform": "Facebook", "spend": 50.0, "revenue": 150.0, "impressions": 1000, "clicks": 100, "conversions": 20}]
    )
    original = aggregate.copy(deep=True)

    result = add_ratio_metrics(aggregate)

    pd.testing.assert_frame_equal(aggregate, original)
    assert result.loc[0, "ctr"] == 10.0
    assert result.loc[0, "roas"] == 3.0
    assert all(not math.isinf(value) for value in result.select_dtypes("number").iloc[0])
