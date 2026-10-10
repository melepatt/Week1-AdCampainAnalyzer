import pandas as pd
import pytest

from src.charts import (
    METRIC_LABELS,
    METRIC_UNITS,
    build_platform_metric_chart,
    build_spend_conversions_chart,
    build_time_series_chart,
)


@pytest.fixture
def time_frame():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "platform": ["Facebook", "Instagram"],
            "spend": [100.0, 75.0],
            "revenue": [250.0, 180.0],
            "impressions": [1000, 800],
            "clicks": [100, 60],
            "conversions": [10, 8],
            "ctr": [10.0, 7.5],
            "cpc": [1.0, 1.25],
            "conversion_rate": [10.0, 13.33],
            "cpa": [10.0, 9.375],
            "roas": [2.5, 2.4],
            "roi": [150.0, 140.0],
        }
    )


@pytest.fixture
def platform_frame(time_frame):
    return time_frame.drop(columns="date")


def test_overview_chart_has_labeled_spend_bar_and_conversions_line(time_frame):
    figure = build_spend_conversions_chart(time_frame)

    assert [trace.name for trace in figure.data] == ["Spend (USD)", "Conversions (count)"]
    assert figure.data[0].type == "bar"
    assert figure.data[1].type == "scatter"
    assert figure.data[1].yaxis == "y2"
    assert "USD" in figure.layout.yaxis.title.text
    assert "count" in figure.layout.yaxis2.title.text


@pytest.mark.parametrize("metric", ["spend", "conversions", "roi", "roas"])
def test_platform_chart_labels_units_hover_and_order(platform_frame, metric):
    figure = build_platform_metric_chart(platform_frame, metric)

    assert METRIC_LABELS[metric] in figure.layout.title.text
    assert METRIC_UNITS[metric] in figure.layout.xaxis.title.text
    assert METRIC_UNITS[metric] in figure.data[0].hovertemplate
    assert list(figure.data[0].y) == ["Facebook", "Instagram"]
    assert figure.data[0].orientation == "h"


@pytest.mark.parametrize("metric", ["revenue", "clicks", "ctr", "cpc", "roas"])
def test_time_series_chart_labels_units_and_hover(time_frame, metric):
    figure = build_time_series_chart(time_frame, metric)

    assert METRIC_LABELS[metric] in figure.layout.title.text
    assert METRIC_UNITS[metric] in figure.layout.yaxis.title.text
    assert METRIC_UNITS[metric] in figure.data[0].hovertemplate


def test_platform_time_series_creates_labeled_traces(time_frame):
    figure = build_time_series_chart(time_frame, "spend", break_down_by_platform=True)
    assert [trace.name for trace in figure.data] == ["Facebook", "Instagram"]


@pytest.mark.parametrize(
    "builder,args",
    [
        (build_spend_conversions_chart, (pd.DataFrame(),)),
        (build_platform_metric_chart, (pd.DataFrame(), "roi")),
        (build_time_series_chart, (pd.DataFrame(), "spend")),
    ],
)
def test_empty_input_returns_no_data_annotation(builder, args):
    figure = builder(*args)
    assert len(figure.data) == 0
    assert figure.layout.annotations[0].text == "No data"
