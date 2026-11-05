"""Page 3 - Customer Behaviour."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from components import insight, note, page_header, render_kpi_row, section_header
from data_loader import (
    behaviour_metrics,
    choose_palette,
    code_label,
    format_int,
    format_number,
    format_pct,
    safe_div,
    segment_summary,
)
from theme import COLORS, PLOTLY_CONFIG, style_figure

PAGE_BINS = [0, 6, 12, 18, 24]
PAGE_LABELS = ["1-6 pages", "7-12 pages", "13-18 pages", "19-24 pages"]


def _render_funnel(metrics: dict, sessions: int) -> None:
    stages = ["Sessions", "Added to cart", "Purchased"]
    values = [sessions, metrics["cart_adds"], metrics["purchases"]]
    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            textfont=dict(color="#FFFFFF", size=12),
            marker=dict(color=[COLORS["blue"], COLORS["cyan"], COLORS["purple"]]),
            connector=dict(line=dict(color="rgba(148,163,184,0.25)", width=1)),
            hovertemplate="%{y}<br>Sessions: %{x:,}<extra></extra>",
        )
    )
    style_figure(fig, height=410, title="Shopping funnel: visit to purchase", legend=False, hovermode="closest")
    fig.update_layout(margin=dict(l=120, r=24, t=56, b=20))
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_device(device: pd.DataFrame) -> None:
    if device.empty:
        st.info("No device data is available for the selected filters.")
        return
    order = device.sort_values("device_type")
    labels = [code_label("device_type", value) for value in order["device_type"]]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=labels,
            y=order["orders"],
            name="Purchase sessions",
            marker=dict(color=COLORS["blue"], line=dict(width=0)),
            hovertemplate="%{x}<br>Purchases: %{y:,}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=order["conversion_rate_pct"],
            name="Conversion rate",
            mode="lines+markers",
            line=dict(color=COLORS["cyan"], width=3),
            marker=dict(size=8, color=COLORS["cyan"]),
            hovertemplate="%{x}<br>Conversion: %{y:.2f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Purchases", tickformat=",", secondary_y=False)
    fig.update_yaxes(title_text="Conversion rate", ticksuffix="%", showgrid=False, secondary_y=True)
    style_figure(fig, height=380, title="Device-wise purchases and conversion")
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_device_revenue(device: pd.DataFrame) -> None:
    if device.empty:
        return
    order = device.sort_values("revenue", ascending=True)
    labels = [code_label("device_type", value) for value in order["device_type"]]
    fig = go.Figure(
        go.Bar(
            x=order["revenue"],
            y=labels,
            orientation="h",
            marker=dict(color=choose_palette(len(order)), line=dict(width=0)),
            text=[f"{value:,.0f}" for value in order["revenue"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>Revenue: %{x:,.0f}<extra></extra>",
        )
    )
    fig.update_xaxes(tickformat=",.0f", title_text="Revenue (dataset units)")
    style_figure(fig, height=380, title="Revenue by device", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_time(metrics: dict) -> None:
    labels = ["No purchase", "Purchased"]
    minutes = [metrics["avg_time_non_buyers"] / 60, metrics["avg_time_buyers"] / 60]
    fig = go.Figure(
        go.Bar(
            x=labels,
            y=minutes,
            marker=dict(color=[COLORS["indigo"], COLORS["cyan"]], line=dict(width=0)),
            text=[f"{value:.1f} min" for value in minutes],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}<br>Average time: %{y:.1f} minutes<extra></extra>",
        )
    )
    fig.update_yaxes(title_text="Average minutes on site")
    style_figure(fig, height=380, title="Average time on site by purchase outcome", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _duration_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df.dropna(subset=["session_duration_bucket"])
    if data.empty:
        return pd.DataFrame(columns=["session_duration_bucket", "sessions", "orders", "conversion_rate_pct"])
    grouped = data.groupby("session_duration_bucket", observed=True).agg(
        sessions=("session_id", "count"), orders=("purchased", "sum")
    )
    grouped["conversion_rate_pct"] = 100 * grouped["orders"] / grouped["sessions"].replace(0, pd.NA)
    return grouped.fillna(0).reset_index()


def _render_duration(duration: pd.DataFrame) -> None:
    if duration.empty:
        st.info("No duration-bucket data is available for the selected filters.")
        return
    fig = go.Figure(
        go.Bar(
            x=duration["session_duration_bucket"].astype(str),
            y=duration["conversion_rate_pct"],
            marker=dict(color=choose_palette(len(duration)), line=dict(width=0)),
            text=[f"{value:.1f}%" for value in duration["conversion_rate_pct"]],
            textposition="outside",
            cliponaxis=False,
            customdata=duration["sessions"],
            hovertemplate="%{x}<br>Conversion: %{y:.2f}%<br>Sessions: %{customdata:,}<extra></extra>",
        )
    )
    fig.update_yaxes(title_text="Conversion rate", ticksuffix="%")
    style_figure(fig, height=380, title="Conversion rate by session duration bucket", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _pages_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["pages_band"] = pd.cut(data["pages_viewed"], bins=PAGE_BINS, labels=PAGE_LABELS, include_lowest=True)
    grouped = data.groupby("pages_band", observed=True).agg(
        sessions=("session_id", "count"), orders=("purchased", "sum")
    )
    grouped["conversion_rate_pct"] = 100 * grouped["orders"] / grouped["sessions"].replace(0, pd.NA)
    return grouped.fillna(0).reset_index()


def _render_pages(metrics: dict, pages: pd.DataFrame) -> None:
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Average pages viewed", "Conversion by pages viewed"),
        horizontal_spacing=0.18,
    )
    fig.add_trace(
        go.Bar(
            x=["No purchase", "Purchased"],
            y=[metrics["avg_pages_non_buyers"], metrics["avg_pages_buyers"]],
            marker=dict(color=[COLORS["indigo"], COLORS["cyan"]], line=dict(width=0)),
            text=[f"{metrics['avg_pages_non_buyers']:.1f}", f"{metrics['avg_pages_buyers']:.1f}"],
            textposition="outside",
            cliponaxis=False,
            showlegend=False,
            hovertemplate="%{x}<br>Average pages: %{y:.2f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    if not pages.empty:
        fig.add_trace(
            go.Bar(
                x=pages["pages_band"].astype(str),
                y=pages["conversion_rate_pct"],
                marker=dict(color=choose_palette(len(pages)), line=dict(width=0)),
                showlegend=False,
                hovertemplate="%{x}<br>Conversion: %{y:.2f}%<extra></extra>",
            ),
            row=1,
            col=2,
        )
    fig.update_yaxes(title_text="Average pages", row=1, col=1)
    fig.update_yaxes(title_text="Conversion rate", ticksuffix="%", row=1, col=2)
    fig.update_xaxes(tickangle=-20, row=1, col=2)
    fig.update_annotations(font_color=COLORS["muted"], font_size=12)
    style_figure(fig, height=380, title="Pages viewed versus purchase behaviour", legend=False, hovermode="closest")
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def render(df: pd.DataFrame, context: str) -> None:
    page_header(
        "03",
        "Customer Behaviour",
        "Funnel leakage, cart abandonment, device behaviour and browsing engagement.",
        context,
    )

    metrics = behaviour_metrics(df)
    sessions = int(len(df))
    render_kpi_row(
        [
            {
                "label": "Add-to-Cart Sessions",
                "value": format_int(metrics["cart_adds"]),
                "helper": f"{format_pct(safe_div(metrics['cart_adds'], sessions) * 100, 1)} of sessions",
                "icon": "cart",
                "accent": "blue",
            },
            {
                "label": "Cart Abandonment Rate",
                "value": format_pct(metrics["abandonment_rate"]),
                "helper": "Abandoned carts ÷ add-to-cart sessions",
                "icon": "abandon",
                "accent": "red",
            },
            {
                "label": "Abandoned Carts",
                "value": format_int(metrics["abandoned"]),
                "helper": "Carts that were not purchased",
                "icon": "cart",
                "accent": "amber",
            },
            {
                "label": "Avg Time on Site",
                "value": f"{metrics['avg_time'] / 60:,.1f} min",
                "helper": "Mean of time_on_site_sec",
                "icon": "time",
                "accent": "cyan",
            },
            {
                "label": "Avg Pages Viewed",
                "value": format_number(metrics["avg_pages"], 1),
                "helper": "Mean pages per session",
                "icon": "pages",
                "accent": "purple",
            },
        ]
    )

    if df.empty:
        st.warning("No sessions match the current filters. Adjust the filters to continue.")
        return

    insight(
        f"{format_pct(metrics['abandonment_rate'], 1)} of add-to-cart sessions were abandoned, and only "
        f"{format_pct(metrics['cart_purchase_rate'], 1)} of cart sessions became purchases. This is the largest "
        "conversion gap visible in the dataset."
    )

    section_header("Shopping funnel", "Session progression from visit to cart to completed purchase.")
    with st.container(border=True):
        _render_funnel(metrics, sessions)

    device = segment_summary(df, "device_type")
    section_header("Device performance", "All device values are stored codes; no device names were assumed.")
    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(border=True):
            _render_device(device)
    with right:
        with st.container(border=True):
            _render_device_revenue(device)

    section_header("Engagement", "Time on site, duration buckets and pages viewed against purchase behaviour.")
    duration = _duration_frame(df)
    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(border=True):
            _render_time(metrics)
    with right:
        with st.container(border=True):
            _render_duration(duration)

    pages = _pages_frame(df)
    with st.container(border=True):
        _render_pages(metrics, pages)
    note(
        "Pages viewed is recorded per session, so the left panel compares the average for purchase and "
        "non-purchase sessions directly."
    )

    if not device.empty:
        best_device = device.sort_values("conversion_rate_pct", ascending=False).iloc[0]
        insight(
            f"{code_label('device_type', best_device['device_type'])} has the highest filtered conversion rate "
            f"at {format_pct(best_device['conversion_rate_pct'])}. Device is a stored code, so this identifies "
            "where to investigate, not what the device actually is."
        )

    if not duration.empty:
        duration_sorted = duration.sort_values("conversion_rate_pct", ascending=False)
        best = duration_sorted.iloc[0]
        note(
            f"Highest duration-bucket conversion: {best['session_duration_bucket']} at "
            f"{format_pct(best['conversion_rate_pct'])}. This is an association, not proof that longer visits cause purchases."
        )
