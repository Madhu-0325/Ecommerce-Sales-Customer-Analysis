"""Page 1 - Sales Performance."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from components import insight, page_header, render_kpi_row, section_header
from data_loader import (
    choose_palette,
    code_label,
    compute_kpis,
    format_compact,
    format_int,
    format_number,
    format_pct,
    segment_summary,
)
from theme import COLORS, PLOTLY_CONFIG, style_figure


def _monthly_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df.dropna(subset=["visit_date_parsed"])
    if data.empty:
        return pd.DataFrame(columns=["year_month", "revenue", "purchases", "sessions"])
    return (
        data.groupby("year_month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            purchases=("purchased", "sum"),
            sessions=("session_id", "count"),
        )
        .sort_values("year_month")
    )


def _render_monthly(monthly: pd.DataFrame) -> None:
    if monthly.empty:
        st.info("No dated sessions are available for the selected filters.")
        return
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=monthly["year_month"],
            y=monthly["purchases"],
            name="Purchase sessions",
            marker=dict(color=COLORS["purple"], opacity=0.55, line=dict(width=0)),
            hovertemplate="Purchases: %{y:,}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["year_month"],
            y=monthly["revenue"],
            name="Revenue",
            mode="lines+markers",
            line=dict(color=COLORS["cyan"], width=3),
            marker=dict(size=6, color=COLORS["cyan"], line=dict(color="#0B1220", width=2)),
            fill="tozeroy",
            fillcolor="rgba(34, 211, 238, 0.08)",
            hovertemplate="Revenue: %{y:,.0f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.update_yaxes(title_text="Revenue (dataset units)", tickformat=",.0f", secondary_y=False)
    fig.update_yaxes(title_text="Purchases", tickformat=",", showgrid=False, secondary_y=True)
    fig.update_xaxes(tickformat="%b %Y")
    style_figure(fig, height=400, title="Monthly revenue and purchase trend")
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_category(category: pd.DataFrame) -> None:
    if category.empty:
        st.info("No category data is available for the selected filters.")
        return
    order = category.sort_values("revenue", ascending=True)
    labels = [code_label("product_category", value) for value in order["product_category"]]
    fig = go.Figure(
        go.Bar(
            x=order["revenue"],
            y=labels,
            orientation="h",
            marker=dict(color=choose_palette(len(order)), line=dict(width=0)),
            text=[format_compact(value) for value in order["revenue"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>Revenue: %{x:,.0f}<extra></extra>",
        )
    )
    fig.update_xaxes(tickformat=",.0f", title_text="Revenue (dataset units)")
    style_figure(fig, height=400, title="Revenue by product category", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_category_quality(category: pd.DataFrame) -> None:
    if category.empty:
        st.info("No category data is available for the selected filters.")
        return
    order = category.sort_values("revenue", ascending=False)
    labels = [code_label("product_category", value) for value in order["product_category"]]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=labels,
            y=order["conversion_rate_pct"],
            name="Conversion rate",
            marker=dict(color=COLORS["blue"], opacity=0.75, line=dict(width=0)),
            hovertemplate="Conversion: %{y:.2f}%<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=order["aov"],
            name="Average order value",
            mode="lines+markers",
            line=dict(color=COLORS["cyan"], width=2.5),
            marker=dict(size=6, color=COLORS["cyan"]),
            hovertemplate="AOV: %{y:,.0f}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Conversion rate", ticksuffix="%", secondary_y=False)
    fig.update_yaxes(title_text="AOV (dataset units)", tickformat=",.0f", showgrid=False, secondary_y=True)
    fig.update_xaxes(tickangle=-32)
    style_figure(fig, height=400, title="Conversion and average order value by category")
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_payment(payment: pd.DataFrame) -> None:
    if payment.empty:
        st.info("No payment-method data is available for the selected filters.")
        return
    order = payment.sort_values("payment_method")
    labels = [code_label("payment_method", value) for value in order["payment_method"]]
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Revenue", "Purchase sessions"),
        horizontal_spacing=0.14,
    )
    fig.add_trace(
        go.Bar(
            x=labels,
            y=order["revenue"],
            marker=dict(color=COLORS["blue"], line=dict(width=0)),
            hovertemplate="%{x}<br>Revenue: %{y:,.0f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=labels,
            y=order["orders"],
            marker=dict(color=COLORS["purple"], line=dict(width=0)),
            hovertemplate="%{x}<br>Purchases: %{y:,}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    fig.update_yaxes(tickformat=",.0f", row=1, col=1)
    fig.update_yaxes(tickformat=",", row=1, col=2)
    fig.update_xaxes(tickangle=-30, row=1, col=1)
    fig.update_xaxes(tickangle=-30, row=1, col=2)
    fig.update_annotations(font_color=COLORS["muted"], font_size=12)
    style_figure(fig, height=390, title="Payment method analysis", legend=False, hovermode="closest")
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def render(df: pd.DataFrame, context: str) -> None:
    page_header(
        "01",
        "Sales Performance",
        "Revenue, orders, conversion and payment behaviour across the filtered sessions.",
        context,
    )

    kpis = compute_kpis(df)
    render_kpi_row(
        [
            {
                "label": "Total Revenue",
                "value": format_compact(kpis["revenue"]),
                "helper": "Sum of revenue in dataset units",
                "icon": "revenue",
                "accent": "blue",
            },
            {
                "label": "Total Purchases",
                "value": format_int(kpis["purchases"]),
                "helper": "Sessions that ended in a purchase",
                "icon": "purchases",
                "accent": "purple",
            },
            {
                "label": "Total Sessions",
                "value": format_int(kpis["sessions"]),
                "helper": "Website visits in the current scope",
                "icon": "sessions",
                "accent": "cyan",
            },
            {
                "label": "Conversion Rate",
                "value": format_pct(kpis["conversion_rate"]),
                "helper": "Purchases ÷ sessions × 100",
                "icon": "conversion",
                "accent": "indigo",
            },
            {
                "label": "Average Order Value",
                "value": format_number(kpis["aov"]),
                "helper": "Revenue ÷ purchase sessions",
                "icon": "aov",
                "accent": "green",
            },
        ]
    )

    if df.empty:
        st.warning("No sessions match the current filters. Adjust the filters to continue.")
        return

    monthly = _monthly_frame(df)
    if not monthly.empty:
        best_month = monthly.loc[monthly["revenue"].idxmax()]
        insight(
            "The strongest month in this selection is "
            f"{best_month['year_month']:%B %Y} with {format_compact(best_month['revenue'])} in revenue "
            f"from {format_int(best_month['purchases'])} purchase sessions."
        )

    section_header("Revenue trend", "Monthly revenue with purchase volume on the secondary axis.")
    with st.container(border=True):
        _render_monthly(monthly)

    category = segment_summary(df, "product_category")
    section_header("Product category performance", "Categories are numeric codes; no names were invented.")
    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(border=True):
            _render_category(category)
    with right:
        with st.container(border=True):
            _render_category_quality(category)

    payment = segment_summary(df, "payment_method")
    section_header("Payment method analysis", "Revenue and purchase sessions by stored payment code.")
    with st.container(border=True):
        _render_payment(payment)

    if not category.empty:
        top_category = category.iloc[0]
        total_revenue = category["revenue"].sum()
        share = 100 * top_category["revenue"] / total_revenue if total_revenue else 0
        insight(
            f"{code_label('product_category', top_category['product_category'])} contributes "
            f"{format_pct(share, 1)} of filtered revenue. Categories differ more in order value than in "
            "conversion rate in this dataset."
        )

    with st.expander("View category and payment detail tables"):
        st.markdown("**Category summary**")
        category_table = category.copy()
        category_table["product_category"] = category_table["product_category"].map(
            lambda value: code_label("product_category", value)
        )
        category_table = category_table.rename(
            columns={
                "product_category": "Category",
                "sessions": "Sessions",
                "orders": "Purchases",
                "revenue": "Revenue",
                "conversion_rate_pct": "Conversion %",
                "aov": "AOV",
            }
        )
        st.dataframe(
            category_table[["Category", "Sessions", "Purchases", "Revenue", "Conversion %", "AOV"]],
            width="stretch",
            hide_index=True,
            column_config={
                "Revenue": st.column_config.NumberColumn(format="%.2f"),
                "Conversion %": st.column_config.NumberColumn(format="%.2f"),
                "AOV": st.column_config.NumberColumn(format="%.2f"),
            },
        )

        st.markdown("**Payment method summary**")
        payment_table = payment.copy()
        payment_table["payment_method"] = payment_table["payment_method"].map(
            lambda value: code_label("payment_method", value)
        )
        payment_table = payment_table.rename(
            columns={
                "payment_method": "Payment method",
                "sessions": "Sessions",
                "orders": "Purchases",
                "revenue": "Revenue",
                "conversion_rate_pct": "Conversion %",
                "aov": "AOV",
            }
        )
        st.dataframe(
            payment_table[["Payment method", "Sessions", "Purchases", "Revenue", "Conversion %", "AOV"]],
            width="stretch",
            hide_index=True,
            column_config={
                "Revenue": st.column_config.NumberColumn(format="%.2f"),
                "Conversion %": st.column_config.NumberColumn(format="%.2f"),
                "AOV": st.column_config.NumberColumn(format="%.2f"),
            },
        )
