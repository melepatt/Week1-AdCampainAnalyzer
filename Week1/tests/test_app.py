from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def _run_app() -> AppTest:
    return AppTest.from_file(str(APP_PATH)).run(timeout=30)


def test_sample_app_renders_four_synchronized_views():
    app = _run_app()

    assert not app.exception
    assert any(title.value == "Ad Campaign Performance Analyzer" for title in app.title)
    assert [tab.label for tab in app.tabs] == [
        "Overview",
        "Platform Comparison",
        "Campaign Details",
        "Time Series",
    ]
    assert [widget.label for widget in app.sidebar.multiselect] == [
        "Channel",
        "Audience",
        "Campaign goal",
    ]
    assert any(widget.label == "Date range" for widget in app.sidebar.date_input)
    metric_labels = {metric.label for metric in app.metric}
    assert {"Spend (USD)", "Revenue (USD)", "Conversions (count)", "ROI (%)"} <= metric_labels


def test_clearing_a_category_filter_shows_shared_empty_state():
    app = _run_app()
    app.sidebar.multiselect[0].set_value([]).run(timeout=30)

    messages = [item.value for item in app.info]
    assert "No campaign records match the selected filters. Broaden or reset the filters to continue." in messages


def test_app_uses_streamlit_150_width_apis():
    source = APP_PATH.read_text(encoding="utf-8")
    plotly_calls = [line for line in source.splitlines() if "st.plotly_chart" in line]
    assert len(plotly_calls) == 4
    assert all("use_container_width=True" in line for line in plotly_calls)
