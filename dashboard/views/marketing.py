"""Page 4 - Marketing and Product Analysis."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from components import insight, note, page_header, render_kpi_row, section_header
from data_loader import (
    choose_palette,
    code_label,
    compute_kpis,
    discount_summary,
    format_compact,
    format_int,
    format_number,
    format_pct,
    safe_div,
    segment_summary,
)
from theme import COLORS, PLOTLY_CONFIG, style_figure


def _render_channel_revenue(channel: pd.DataFrame) -> None:
    if channel.empty:
        st.info("No marketing-channel data is available for the selected filters.")
        return
    order = channel.sort_values("revenue", ascending=True)
    labels = [code_label("marketing_channel", value) for value in order["marketing_channel"]]
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
    style_figure(fig, height=380, title="Revenue by marketing channel", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_channel_purchases(channel: pd.DataFrame) -> None:
    if channel.empty:
        return
    order = channel.sort_values("orders", ascending=True)
    labels = [code_label("marketing_channel", value) for value in order["marketing_channel"]]
    fig = go.Figure(
        go.Bar(
            x=order["orders"],
            y=labels,
            orientation="h",
            marker=dict(color=choose_palette(len(order)), line=dict(width=0)),
            text=[format_int(value) for value in order["orders"]],
            textposition="outside",
            cliponaxis=False,
            customdata=order["conversion_rate_pct"],
            hovertemplate="%{y}<br>Purchases: %{x:,}<br>Conversion: %{customdata:.2f}%<extra></extra>",
        )
    )
    fig.update_xaxes(tickformat=",", title_text="Purchase sessions")
    style_figure(fig, height=380, title="Purchases by marketing channel", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_category(category: pd.DataFrame) -> None:
    if category.empty:
        st.info("No category data is available for the selected filters.")
        return
    order = category.sort_values("revenue", ascending=False)
    labels = [code_label("product_category", value) for value in order["product_category"]]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=labels,
            y=order["revenue"],
            name="Revenue",
            marker=dict(color=COLORS["purple"], line=dict(width=0)),
            hovertemplate="%{x}<br>Revenue: %{y:,.0f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=order["conversion_rate_pct"],
            name="Conversion rate",
            mode="lines+markers",
            line=dict(color=COLORS["cyan"], width=2.5),
            marker=dict(size=7, color=COLORS["cyan"]),
            hovertemplate="%{x}<br>Conversion: %{y:.2f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Revenue (dataset units)", tickformat=",.0f", secondary_y=False)
    fig.update_yaxes(title_text="Conversion rate", ticksuffix="%", showgrid=False, secondary_y=True)
    fig.update_xaxes(tickangle=-32)
    style_figure(fig, height=390, title="Category revenue and conversion", legend=True)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_discount(discount: pd.DataFrame) -> None:
    if discount.empty:
        st.info("No discount data is available for the selected filters.")
        return
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=discount["discount_percent"],
            y=discount["aov"],
            name="Average order value",
            marker=dict(color=COLORS["blue"], line=dict(width=0)),
            hovertemplate="Discount %{x}%<br>AOV: %{y:,.0f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=discount["discount_percent"],
            y=discount["conversion_rate_pct"],
            name="Conversion rate",
            mode="lines+markers",
            line=dict(color=COLORS["cyan"], width=3),
            marker=dict(size=8, color=COLORS["cyan"]),
            hovertemplate="Discount %{x}%<br>Conversion: %{y:.2f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_xaxes(title_text="Discount percent", ticksuffix="%")
    fig.update_yaxes(title_text="AOV (dataset units)", tickformat=",.0f", secondary_y=False)
    fig.update_yaxes(title_text="Conversion rate", ticksuffix="%", showgrid=False, secondary_y=True)
    style_figure(fig, height=390, title="Discount level: conversion and average order value")
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _rating_by_category(purchases: pd.DataFrame) -> pd.DataFrame:
    if purchases.empty:
        return pd.DataFrame(columns=["product_category", "orders", "avg_rating"])
    grouped = purchases.groupby("product_category", observed=True).agg(
        orders=("session_id", "nunique"), avg_rating=("rating", "mean")
    )
    return grouped.reset_index().sort_values("avg_rating", ascending=False)


def _render_rating_category(rating: pd.DataFrame) -> None:
    if rating.empty:
        st.info("No purchase ratings are available for the selected filters.")
        return
    order = rating.sort_values("avg_rating", ascending=True)
    labels = [code_label("product_category", value) for value in order["product_category"]]
    fig = go.Figure(
        go.Bar(
            x=order["avg_rating"],
            y=labels,
            orientation="h",
            marker=dict(color=choose_palette(len(order)), line=dict(width=0)),
            text=[f"{value:.2f}" for value in order["avg_rating"]],
            textposition="outside",
            cliponaxis=False,
            customdata=order["orders"],
            hovertemplate="%{y}<br>Average rating: %{x:.2f}<br>Purchases: %{customdata:,}<extra></extra>",
        )
    )
    fig.update_xaxes(range=[0, 5.4], title_text="Average rating (purchasing sessions)")
    style_figure(fig, height=380, title="Product ratings by category", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _quantity_by_category(purchases: pd.DataFrame) -> pd.DataFrame:
    if purchases.empty:
        return pd.DataFrame(columns=["product_category", "units", "orders", "revenue"])
    grouped = purchases.groupby("product_category", observed=True).agg(
        units=("quantity", "sum"),
        orders=("session_id", "nunique"),
        revenue=("revenue", "sum"),
    )
    grouped["units_per_order"] = grouped["units"] / grouped["orders"].replace(0, pd.NA)
    return grouped.fillna(0).reset_index().sort_values("units", ascending=False)


def _render_quantity(quantity: pd.DataFrame) -> None:
    if quantity.empty:
        st.info("No purchase quantity data is available for the selected filters.")
        return
    order = quantity.sort_values("units", ascending=True)
    labels = [code_label("product_category", value) for value in order["product_category"]]
    fig = go.Figure(
        go.Bar(
            x=order["units"],
            y=labels,
            orientation="h",
            marker=dict(color=choose_palette(len(order)), line=dict(width=0)),
            text=[format_int(value) for value in order["units"]],
            textposition="outside",
            cliponaxis=False,
            customdata=order["revenue"],
            hovertemplate="%{y}<br>Units sold: %{x:,}<br>Revenue: %{customdata:,.0f}<extra></extra>",
        )
    )
    fig.update_xaxes(tickformat=",", title_text="Units sold on purchase sessions")
    style_figure(fig, height=380, title="Quantity sold by product category", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def render(df: pd.DataFrame, context: str) -> None:
    page_header(
        "04",
        "Marketing & Product Analysis",
        "Channel effectiveness, category economics, discount behaviour and product quality signals.",
        context,
    )

    kpis = compute_kpis(df)
    purchases = df[df["purchased"] == 1]
    discount_amount = float(df["discount_amount"].sum())
    units_sold = int(purchases["quantity"].sum())
    avg_discount = float(df["discount_percent"].mean()) if len(df) else 0.0
    render_kpi_row(
        [
            {
                "label": "Marketing Revenue",
                "value": format_compact(kpis["revenue"]),
                "helper": "Revenue in the filtered scope",
                "icon": "channel",
                "accent": "blue",
            },
            {
                "label": "Purchase Sessions",
                "value": format_int(kpis["purchases"]),
                "helper": "Sessions ending in purchase",
                "icon": "purchases",
                "accent": "purple",
            },
            {
                "label": "Discount Given",
                "value": format_compact(discount_amount),
                "helper": "Sum of discount_amount",
                "icon": "discount",
                "accent": "amber",
            },
            {
                "label": "Units Sold",
                "value": format_int(units_sold),
                "helper": "Quantity on purchasing sessions",
                "icon": "units",
                "accent": "cyan",
            },
            {
                "label": "Avg Discount",
                "value": format_pct(avg_discount, 1),
                "helper": "Mean discount_percent per session",
                "icon": "discount",
                "accent": "indigo",
            },
        ]
    )

    if df.empty:
        st.warning("No sessions match the current filters. Adjust the filters to continue.")
        return

    channel = segment_summary(df, "marketing_channel")
    if not channel.empty:
        top_channel = channel.iloc[0]
        insight(
            f"{code_label('marketing_channel', top_channel['marketing_channel'])} generates the most filtered "
            f"revenue ({format_compact(top_channel['revenue'])}) with "
            f"{format_pct(top_channel['conversion_rate_pct'])} conversion. Channel values are stored codes."
        )

    section_header("Marketing channel performance", "Revenue and purchase volume by stored channel code.")
    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(border=True):
            _render_channel_revenue(channel)
    with right:
        with st.container(border=True):
            _render_channel_purchases(channel)

    category = segment_summary(df, "product_category")
    section_header("Product category performance", "Revenue and conversion by category code.")
    with st.container(border=True):
        _render_category(category)

    discount = discount_summary(df)
    section_header("Discount analysis", "Actual discount values in the dataset (0% to 30%).")
    with st.container(border=True):
        _render_discount(discount)

    if len(discount) >= 2:
        zero_rows = discount[discount["discount_percent"] == 0]
        max_rows = discount[discount["discount_percent"] == discount["discount_percent"].max()]
        if not zero_rows.empty and not max_rows.empty:
            zero = zero_rows.iloc[0]
            maximum = max_rows.iloc[0]
            insight(
                f"At 0% discount, conversion is {format_pct(zero['conversion_rate_pct'])} with AOV "
                f"{format_number(zero['aov'])}. At {int(maximum['discount_percent'])}% discount, conversion is "
                f"{format_pct(maximum['conversion_rate_pct'])} with AOV {format_number(maximum['aov'])}. "
                "This is an association in the data, not proof that discounts caused the change."
            )

    rating = _rating_by_category(purchases)
    quantity = _quantity_by_category(purchases)
    section_header("Product quality and volume", "Ratings use purchasing sessions only; units use purchase quantity.")
    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(border=True):
            _render_rating_category(rating)
    with right:
        with st.container(border=True):
            _render_quantity(quantity)
    note("Non-purchasing sessions all carry the same rating (4), so product-rating results use purchases only.")

    with st.expander("View category, channel, discount and top-product tables"):
        st.markdown("**Category performance**")
        category_display = category.copy()
        category_display["product_category"] = category_display["product_category"].map(
            lambda value: code_label("product_category", value)
        )
        category_display = category_display.rename(
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
            category_display[["Category", "Sessions", "Purchases", "Revenue", "Conversion %", "AOV"]],
            width="stretch",
            hide_index=True,
        )

        st.markdown("**Marketing channel performance**")
        channel_display = channel.copy()
        channel_display["marketing_channel"] = channel_display["marketing_channel"].map(
            lambda value: code_label("marketing_channel", value)
        )
        channel_display = channel_display.rename(
            columns={
                "marketing_channel": "Channel",
                "sessions": "Sessions",
                "orders": "Purchases",
                "revenue": "Revenue",
                "conversion_rate_pct": "Conversion %",
                "aov": "AOV",
            }
        )
        st.dataframe(
            channel_display[["Channel", "Sessions", "Purchases", "Revenue", "Conversion %", "AOV"]],
            width="stretch",
            hide_index=True,
        )

        st.markdown("**Discount performance**")
        discount_display = discount.rename(
            columns={
                "discount_percent": "Discount %",
                "sessions": "Sessions",
                "orders": "Purchases",
                "revenue": "Revenue",
                "discount_amount": "Discount amount",
                "conversion_rate_pct": "Conversion %",
                "aov": "AOV",
            }
        )
        st.dataframe(discount_display, width="stretch", hide_index=True)

        st.markdown("**Top 10 products by revenue**")
        if purchases.empty:
            st.info("No products were purchased in this selection.")
        else:
            products = purchases.groupby("product_id", observed=True).agg(
                orders=("session_id", "nunique"),
                units=("quantity", "sum"),
                revenue=("revenue", "sum"),
                avg_rating=("rating", "mean"),
            ).sort_values("revenue", ascending=False).head(10).reset_index()
            products["product_id"] = products["product_id"].map(lambda value: f"Product {int(value)}")
            products = products.rename(
                columns={
                    "product_id": "Product",
                    "orders": "Purchases",
                    "units": "Units",
                    "revenue": "Revenue",
                    "avg_rating": "Avg rating",
                }
            )
            st.dataframe(
                products,
                width="stretch",
                hide_index=True,
                column_config={
                    "Revenue": st.column_config.NumberColumn(format="%.2f"),
                    "Avg rating": st.column_config.NumberColumn(format="%.2f"),
                },
            )

    if not rating.empty:
        best = rating.iloc[0]
        insight(
            f"{code_label('product_category', best['product_category'])} has the highest average purchase rating "
            f"({best['avg_rating']:.2f} from {format_int(best['orders'])} purchases). Use this as a starting point "
            "for quality investigation rather than a definitive ranking."
        )
