"""Streamlit entry point for the Ad Campaign Performance Analyzer."""

from __future__ import annotations

import logging
import hashlib
from io import BytesIO
from datetime import date

import pandas as pd
import streamlit as st

from src.charts import (
    METRIC_LABELS,
    build_platform_metric_chart,
    build_spend_conversions_chart,
    build_time_series_chart,
)
from src.data_loader import load_sample_data, read_campaign_csv
from src.exporting import dataframe_to_csv_bytes
from src.filters import FilterSelection, apply_filters, reconcile_filter_state
from src.formatting import (
    format_count,
    format_currency,
    format_multiplier,
    format_percent,
    prepare_metric_table,
)
from src.metrics import (
    aggregate_by_campaign,
    aggregate_by_platform,
    aggregate_time_series,
    calculate_summary,
)
from src.validation import ValidationResult, validate_campaign_data


LOGGER = logging.getLogger(__name__)
EMPTY_FILTER_MESSAGE = (
    "No campaign records match the selected filters. Broaden or reset the filters to continue."
)
TABLE_LABELS = {
    "campaign_id": "Campaign ID",
    "campaign_name": "Campaign name",
    "platform": "Platform",
    "audience": "Audience",
    "campaign_goal": "Campaign goal",
    "spend": "Spend (USD)",
    "revenue": "Revenue (USD)",
    "impressions": "Impressions (count)",
    "clicks": "Clicks (count)",
    "conversions": "Conversions (count)",
    "ctr": "CTR (%)",
    "cpc": "CPC (USD/click)",
    "conversion_rate": "Conversion rate (%)",
    "cpa": "CPA (USD/conversion)",
    "roas": "ROAS (multiplier)",
    "roi": "ROI (%)",
}


def _display_table(frame: pd.DataFrame) -> pd.DataFrame:
    return prepare_metric_table(frame).rename(columns=TABLE_LABELS)


def _load_selected_source() -> tuple[ValidationResult | None, str, str]:
    st.subheader("Choose campaign data")
    source_mode = st.radio("Data source", ("Sample data", "Upload CSV"), horizontal=True)
    try:
        if source_mode == "Sample data":
            return validate_campaign_data(load_sample_data()), "Bundled sample data", "sample"
        upload = st.file_uploader("Upload campaign CSV", type=("csv",))
        if upload is None:
            st.info("Upload a campaign CSV to begin analysis.")
            return None, "Uploaded CSV", "upload:none"
        payload = upload.getvalue()
        source_key = f"upload:{hashlib.sha256(payload).hexdigest()}"
        return validate_campaign_data(read_campaign_csv(BytesIO(payload))), upload.name, source_key
    except pd.errors.EmptyDataError:
        st.error("The CSV is empty. Include the required headers and at least one data row.")
        return None, "Unavailable source", "error:empty"
    except (OSError, UnicodeError, pd.errors.ParserError, ValueError) as exc:
        st.error(f"The CSV could not be loaded: {exc}. Check that it is a readable UTF-8 CSV with unique headers.")
        return None, "Unavailable source", "error:load"


def _show_validation(result: ValidationResult | None) -> pd.DataFrame | None:
    if result is None:
        return None
    if result.errors:
        st.error("The selected dataset has blocking validation errors:")
        for error in result.errors:
            st.error(error)
        return None
    if result.warnings:
        with st.expander(f"Validation warnings ({len(result.warnings)})"):
            for warning in result.warnings:
                st.warning(warning)
    return result.data


def _reset_filters(min_date: date, max_date: date, platforms: tuple[str, ...], audiences: tuple[str, ...], goals: tuple[str, ...]) -> None:
    st.session_state.filter_dates = (min_date, max_date)
    st.session_state.filter_platforms = list(platforms)
    st.session_state.filter_audiences = list(audiences)
    st.session_state.filter_goals = list(goals)


def _ensure_filter_state(data: pd.DataFrame, source_key: str) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    platforms = tuple(sorted(data["platform"].unique()))
    audiences = tuple(sorted(data["audience"].unique()))
    goals = tuple(sorted(data["campaign_goal"].unique()))
    reconciled = reconcile_filter_state(data, source_key, dict(st.session_state))
    for key, value in reconciled.items():
        st.session_state[key] = value
    return platforms, audiences, goals


def _render_filters(data: pd.DataFrame, source_key: str) -> FilterSelection:
    platforms, audiences, goals = _ensure_filter_state(data, source_key)
    min_date, max_date = data["date"].min().date(), data["date"].max().date()
    st.sidebar.header("Global filters")
    selected_dates = st.sidebar.date_input(
        "Date range",
        min_value=min_date,
        max_value=max_date,
        key="filter_dates",
    )
    selected_platforms = st.sidebar.multiselect("Channel", platforms, key="filter_platforms")
    selected_audiences = st.sidebar.multiselect("Audience", audiences, key="filter_audiences")
    selected_goals = st.sidebar.multiselect("Campaign goal", goals, key="filter_goals")
    st.sidebar.button(
        "Reset filters",
        on_click=_reset_filters,
        args=(min_date, max_date, platforms, audiences, goals),
        width="stretch",
    )
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 1:
        start_date = end_date = selected_dates[0]
    else:
        start_date = end_date = selected_dates
    st.sidebar.caption(
        f"Active filters: {start_date:%b %d, %Y}–{end_date:%b %d, %Y}; "
        f"{len(selected_platforms)} channel(s), {len(selected_audiences)} audience(s), "
        f"{len(selected_goals)} goal(s)."
    )
    return FilterSelection(
        start_date=start_date,
        end_date=end_date,
        platforms=tuple(selected_platforms),
        audiences=tuple(selected_audiences),
        goals=tuple(selected_goals),
    )


def _render_overview(filtered: pd.DataFrame, source_name: str) -> None:
    summary = calculate_summary(filtered)
    columns = st.columns(4)
    columns[0].metric("Spend (USD)", format_currency(summary["spend"]))
    columns[1].metric("Revenue (USD)", format_currency(summary["revenue"]))
    columns[2].metric("Conversions (count)", format_count(summary["conversions"]))
    columns[3].metric("ROI (%)", format_percent(summary["roi"]), help="ROI is profit divided by spend, expressed as a percentage.")
    supporting = st.columns(2)
    supporting[0].metric("CPA (USD/conversion)", format_currency(summary["cpa"]), help="CPA is spend divided by conversions.")
    supporting[1].metric("ROAS (multiplier)", format_multiplier(summary["roas"]), help="ROAS is revenue divided by spend.")
    st.caption(f"Source: {source_name} · {len(filtered):,} filtered daily record(s)")
    weekly = aggregate_time_series(filtered, "Weekly")
    st.plotly_chart(build_spend_conversions_chart(weekly), use_container_width=True)
    platforms = aggregate_by_platform(filtered)
    st.plotly_chart(build_platform_metric_chart(platforms, "roi"), use_container_width=True)


def _render_platform_comparison(filtered: pd.DataFrame) -> None:
    platform_frame = aggregate_by_platform(filtered)
    st.subheader("Compare channel volume and efficiency")
    metric_options = ["spend", "revenue", "clicks", "conversions", "cpa", "roas", "roi"]
    metric = st.selectbox(
        "Platform comparison metric",
        metric_options,
        format_func=lambda value: METRIC_LABELS[value],
        help="CPA is spend per conversion; ROAS is revenue divided by spend; ROI is profit divided by spend.",
    )
    st.plotly_chart(build_platform_metric_chart(platform_frame, metric), use_container_width=True)
    missing = sorted({"Facebook", "Instagram", "Pinterest", "Twitter"} - set(platform_frame["platform"]))
    if missing:
        st.caption("No matching records for: " + ", ".join(missing))
    selected_columns = ["platform", "spend", "clicks", "conversions", "revenue", "cpa", "roas", "roi"]
    display_frame = _display_table(platform_frame[selected_columns])
    st.dataframe(display_frame, hide_index=True, width="stretch")
    st.download_button(
        "Download platform summary CSV",
        dataframe_to_csv_bytes(display_frame),
        "platform-summary.csv",
        "text/csv",
    )


def _render_campaign_details(filtered: pd.DataFrame) -> None:
    campaign_frame = aggregate_by_campaign(filtered)
    query = st.text_input("Search campaign ID or name", placeholder="Example: FB001 or Holiday")
    if query.strip():
        match = campaign_frame["campaign_id"].str.contains(query, case=False, na=False, regex=False)
        match |= campaign_frame["campaign_name"].str.contains(query, case=False, na=False, regex=False)
        campaign_frame = campaign_frame.loc[match].reset_index(drop=True)
    st.caption(f"Showing {len(campaign_frame):,} campaign(s)")
    st.caption("CTR is clicks per impression; CPC is spend per click. Ratio values with zero denominators display as N/A.")
    display_frame = _display_table(campaign_frame)
    st.dataframe(display_frame, hide_index=True, width="stretch")
    st.download_button(
        "Download campaign details CSV",
        dataframe_to_csv_bytes(display_frame),
        "campaign-details.csv",
        "text/csv",
    )


def _render_time_series(filtered: pd.DataFrame) -> None:
    controls = st.columns(3)
    metric_options = ["spend", "revenue", "clicks", "conversions", "ctr", "cpa", "roas", "roi"]
    metric = controls[0].selectbox(
        "Time series metric",
        metric_options,
        format_func=lambda value: METRIC_LABELS[value],
        help="CTR is clicks per impression; CPA is spend per conversion; ROAS and ROI compare revenue with spend.",
    )
    frequency = controls[1].selectbox("Time aggregation", ("Daily", "Weekly", "Monthly"), index=1)
    breakdown = controls[2].toggle("Break down by platform", value=False)
    time_frame = aggregate_time_series(filtered, frequency, breakdown)
    st.plotly_chart(build_time_series_chart(time_frame, metric, breakdown), use_container_width=True)


def render_dashboard() -> None:
    st.title("Ad Campaign Performance Analyzer")
    st.write("See which campaigns and advertising channels are delivering results.")
    validation, source_name, source_key = _load_selected_source()
    data = _show_validation(validation)
    if data is None:
        return

    selection = _render_filters(data, source_key)
    filtered = apply_filters(data, selection)
    if filtered.empty:
        st.info(EMPTY_FILTER_MESSAGE)
        st.button(
            "Reset filters to show all campaigns",
            on_click=_reset_filters,
            args=(
                data["date"].min().date(),
                data["date"].max().date(),
                tuple(sorted(data["platform"].unique())),
                tuple(sorted(data["audience"].unique())),
                tuple(sorted(data["campaign_goal"].unique())),
            ),
        )
        return

    overview_tab, platform_tab, details_tab, time_tab = st.tabs(
        ("Overview", "Platform Comparison", "Campaign Details", "Time Series")
    )
    with overview_tab:
        _render_overview(filtered, source_name)
    with platform_tab:
        _render_platform_comparison(filtered)
    with details_tab:
        _render_campaign_details(filtered)
    with time_tab:
        _render_time_series(filtered)


def main() -> None:
    st.set_page_config(page_title="Ad Campaign Performance Analyzer", page_icon="📈", layout="wide")
    try:
        render_dashboard()
    except Exception:
        LOGGER.exception("Unexpected dashboard rendering error")
        st.error("Something unexpected went wrong while rendering the dashboard. Please check the data and try again.")


main()
