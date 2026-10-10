"""Pure Plotly figure factories for the four dashboard views."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


METRIC_LABELS = {
    "spend": "Spend",
    "revenue": "Revenue",
    "impressions": "Impressions",
    "clicks": "Clicks",
    "conversions": "Conversions",
    "ctr": "Click-through rate",
    "cpc": "Cost per click",
    "conversion_rate": "Conversion rate",
    "cpa": "Cost per acquisition",
    "roas": "Return on ad spend",
    "roi": "Return on investment",
}
METRIC_UNITS = {
    "spend": "USD",
    "revenue": "USD",
    "impressions": "count",
    "clicks": "count",
    "conversions": "count",
    "ctr": "%",
    "cpc": "USD per click",
    "conversion_rate": "%",
    "cpa": "USD per conversion",
    "roas": "multiplier",
    "roi": "%",
}
PLATFORM_COLORS = {
    "Facebook": "#3568D4",
    "Instagram": "#C84C93",
    "Pinterest": "#C83737",
    "Twitter": "#3182A8",
}
PLATFORM_ORDER = tuple(PLATFORM_COLORS)


def _empty_figure(title: str = "") -> go.Figure:
    figure = go.Figure()
    figure.update_layout(title=title, margin=dict(l=36, r=28, t=64, b=36))
    figure.add_annotation(text="No data", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    return figure


def _validate_metric(metric: str) -> None:
    if metric not in METRIC_LABELS:
        raise ValueError(f"Unsupported metric: {metric}")


def build_spend_conversions_chart(time_frame: pd.DataFrame) -> go.Figure:
    """Build the Overview dual-axis spend and conversion trend."""
    title = "Spend versus conversions over time"
    if time_frame.empty:
        return _empty_figure(title)
    figure = go.Figure()
    figure.add_bar(
        x=time_frame["date"],
        y=time_frame["spend"],
        name="Spend (USD)",
        marker_color="#5877D8",
        hovertemplate="%{x|%b %d, %Y}<br>Spend: $%{y:,.2f} USD<extra></extra>",
    )
    figure.add_scatter(
        x=time_frame["date"],
        y=time_frame["conversions"],
        name="Conversions (count)",
        mode="lines+markers",
        line=dict(color="#E68A3B", width=3),
        yaxis="y2",
        hovertemplate="%{x|%b %d, %Y}<br>Conversions: %{y:,.0f} count<extra></extra>",
    )
    figure.update_layout(
        title=title,
        xaxis_title="Reporting period",
        yaxis=dict(title="Spend (USD)", rangemode="tozero"),
        yaxis2=dict(title="Conversions (count)", overlaying="y", side="right", rangemode="tozero"),
        legend=dict(orientation="h", y=1.12, x=0),
        hovermode="x unified",
        margin=dict(l=48, r=48, t=82, b=42),
    )
    return figure


def build_platform_metric_chart(platform_frame: pd.DataFrame, metric: str) -> go.Figure:
    """Build a horizontal platform comparison for one selected metric."""
    _validate_metric(metric)
    title = f"{METRIC_LABELS[metric]} by platform"
    if platform_frame.empty:
        return _empty_figure(title)
    order = {platform: index for index, platform in enumerate(PLATFORM_ORDER)}
    data = platform_frame.copy().sort_values(
        "platform", key=lambda values: values.map(order).fillna(len(order)), kind="stable"
    )
    unit = METRIC_UNITS[metric]
    figure = go.Figure(
        go.Bar(
            x=data[metric],
            y=data["platform"],
            orientation="h",
            name=METRIC_LABELS[metric],
            marker_color=[PLATFORM_COLORS.get(platform, "#687386") for platform in data["platform"]],
            hovertemplate=f"%{{y}}<br>{METRIC_LABELS[metric]}: %{{x:,.2f}} {unit}<extra></extra>",
        )
    )
    figure.update_layout(
        title=title,
        xaxis_title=f"{METRIC_LABELS[metric]} ({unit})",
        yaxis_title="Advertising platform",
        margin=dict(l=48, r=28, t=64, b=42),
        showlegend=False,
    )
    return figure


def build_time_series_chart(
    time_frame: pd.DataFrame,
    metric: str,
    break_down_by_platform: bool = False,
) -> go.Figure:
    """Build a trend chart for one metric, optionally split by platform."""
    _validate_metric(metric)
    title = f"{METRIC_LABELS[metric]} over time"
    if time_frame.empty:
        return _empty_figure(title)
    unit = METRIC_UNITS[metric]
    figure = go.Figure()
    if break_down_by_platform:
        platforms = sorted(
            time_frame["platform"].unique(),
            key=lambda platform: PLATFORM_ORDER.index(platform) if platform in PLATFORM_ORDER else len(PLATFORM_ORDER),
        )
        for platform in platforms:
            data = time_frame.loc[time_frame["platform"] == platform]
            figure.add_scatter(
                x=data["date"],
                y=data[metric],
                name=platform,
                mode="lines+markers",
                line=dict(color=PLATFORM_COLORS.get(platform, "#687386"), width=2.5),
                hovertemplate=f"%{{x|%b %d, %Y}}<br>{METRIC_LABELS[metric]}: %{{y:,.2f}} {unit}<extra>{platform}</extra>",
            )
    else:
        figure.add_scatter(
            x=time_frame["date"],
            y=time_frame[metric],
            name=METRIC_LABELS[metric],
            mode="lines+markers",
            line=dict(color="#5877D8", width=3),
            hovertemplate=f"%{{x|%b %d, %Y}}<br>{METRIC_LABELS[metric]}: %{{y:,.2f}} {unit}<extra></extra>",
        )
    figure.update_layout(
        title=title,
        xaxis_title="Reporting period",
        yaxis_title=f"{METRIC_LABELS[metric]} ({unit})",
        legend_title="Platform" if break_down_by_platform else None,
        hovermode="x unified",
        margin=dict(l=48, r=28, t=64, b=42),
    )
    return figure
