"""Page 2 - Customer Analysis."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components import insight, note, page_header, render_kpi_row, section_header
from data_loader import (
    choose_palette,
    customer_metrics,
    customer_table,
    format_compact,
    format_int,
    format_number,
    format_pct,
    safe_div,
)
from theme import COLORS, PLOTLY_CONFIG, style_figure


def _frequency_frame(purchases: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    orders_per_buyer = purchases.groupby("customer_id")["session_id"].nunique()
    frequency = orders_per_buyer.value_counts().sort_index()
    rows = []
    for label, lower, upper in [
        ("1 purchase", 1, 1),
        ("2 purchases", 2, 2),
        ("3 purchases", 3, 3),
        ("4+ purchases", 4, 10**9),
    ]:
        count = int(frequency[(frequency.index >= lower) & (frequency.index <= upper)].sum())
        rows.append({"segment": label, "buyers": count})
    frame = pd.DataFrame(rows)
    total = frame["buyers"].sum()
    frame["share_pct"] = 100 * frame["buyers"] / total if total else 0
    return frame, {"orders_per_buyer": orders_per_buyer, "total": total}


def _render_top_customers(table: pd.DataFrame) -> None:
    top = table.head(10).copy()
    if top.empty:
        st.info("No purchasing customers match the current filters.")
        return
    top = top.sort_values("revenue", ascending=True)
    labels = [f"#{int(value)}" for value in top["customer_id"]]
    fig = go.Figure(
        go.Bar(
            x=top["revenue"],
            y=labels,
            orientation="h",
            marker=dict(color=choose_palette(len(top)), line=dict(width=0)),
            text=[format_compact(value) for value in top["revenue"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="Customer %{y}<br>Revenue: %{x:,.0f}<extra></extra>",
        )
    )
    fig.update_xaxes(tickformat=",.0f", title_text="Revenue (dataset units)")
    style_figure(fig, height=380, title="Top 10 customers by revenue", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_frequency(frequency: pd.DataFrame) -> None:
    fig = go.Figure(
        go.Bar(
            x=frequency["segment"],
            y=frequency["buyers"],
            marker=dict(color=choose_palette(len(frequency)), line=dict(width=0)),
            text=[format_int(value) for value in frequency["buyers"]],
            textposition="outside",
            cliponaxis=False,
            customdata=frequency["share_pct"],
            hovertemplate="%{x}<br>Buyers: %{y:,}<br>Share: %{customdata:.1f}%<extra></extra>",
        )
    )
    fig.update_yaxes(title_text="Customers", tickformat=",")
    style_figure(fig, height=380, title="Purchase frequency per customer", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _segment_revenue(purchases: pd.DataFrame) -> pd.DataFrame:
    if purchases.empty:
        return pd.DataFrame(columns=["segment", "buyers", "revenue", "share_pct"])
    grouped = purchases.groupby("customer_id").agg(
        orders=("session_id", "nunique"), revenue=("revenue", "sum")
    )
    grouped["segment"] = pd.cut(
        grouped["orders"],
        bins=[0, 1, 3, 10**9],
        labels=["1 purchase", "2-3 purchases", "4+ purchases"],
        right=True,
    )
    summary = grouped.groupby("segment", observed=True).agg(
        buyers=("revenue", "size"), revenue=("revenue", "sum")
    ).reset_index()
    total = summary["revenue"].sum()
    summary["share_pct"] = 100 * summary["revenue"] / total if total else 0
    return summary


def _render_segment_revenue(segments: pd.DataFrame) -> None:
    if segments.empty:
        st.info("No purchasing customers match the current filters.")
        return
    fig = go.Figure(
        go.Pie(
            labels=segments["segment"].astype(str),
            values=segments["revenue"],
            hole=0.62,
            marker=dict(colors=choose_palette(len(segments)), line=dict(color="#0B1220", width=2)),
            textinfo="percent",
            textfont=dict(color="#FFFFFF", size=12),
            hovertemplate="%{label}<br>Revenue: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
        )
    )
    fig.update_layout(
        annotations=[
            dict(
                text="Revenue<br>mix",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=13, color=COLORS["muted"]),
            )
        ]
    )
    style_figure(fig, height=380, title="Revenue by purchase-frequency segment", legend=True)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def _render_ratings(purchases: pd.DataFrame) -> None:
    rating = purchases["rating"].dropna()
    if rating.empty:
        st.info("No ratings are available for purchasing sessions in this selection.")
        return
    counts = rating.value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
    colors = [COLORS["red"], COLORS["amber"], COLORS["sky"], COLORS["blue"], COLORS["green"]]
    fig = go.Figure(
        go.Bar(
            x=[f"{int(value)} star" for value in counts.index],
            y=counts.values,
            marker=dict(color=colors, line=dict(width=0)),
            text=[format_int(value) for value in counts.values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}<br>Reviews: %{y:,}<extra></extra>",
        )
    )
    fig.update_yaxes(title_text="Number of purchases", tickformat=",")
    style_figure(fig, height=380, title="Rating distribution (purchasing sessions only)", legend=False)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, theme=None)


def render(df: pd.DataFrame, context: str) -> None:
    page_header(
        "02",
        "Customer Analysis",
        "Who buys, how often they return, and how purchasing customers rate their experience.",
        context,
    )

    metrics = customer_metrics(df)
    render_kpi_row(
        [
            {
                "label": "Unique Customers",
                "value": format_int(metrics["unique_customers"]),
                "helper": "Distinct customer IDs in scope",
                "icon": "customers",
                "accent": "blue",
            },
            {
                "label": "Buying Customers",
                "value": format_int(metrics["buying_customers"]),
                "helper": "Customers with at least one purchase",
                "icon": "purchases",
                "accent": "purple",
            },
            {
                "label": "Repeat Customers",
                "value": format_int(metrics["repeat_customers"]),
                "helper": "Buyers with 2 or more purchase sessions",
                "icon": "repeat",
                "accent": "cyan",
            },
            {
                "label": "Repeat Customer Rate",
                "value": format_pct(metrics["repeat_rate"]),
                "helper": "Repeat buyers ÷ buying customers",
                "icon": "conversion",
                "accent": "indigo",
            },
            {
                "label": "Avg Revenue / Buyer",
                "value": format_number(metrics["avg_revenue_per_customer"]),
                "helper": "Revenue ÷ buying customers",
                "icon": "revenue",
                "accent": "green",
            },
        ]
    )

    if df.empty:
        st.warning("No sessions match the current filters. Adjust the filters to continue.")
        return

    purchases = df[df["purchased"] == 1]
    table = customer_table(df)

    if not table.empty:
        top10_share = 100 * safe_div(table.head(10)["revenue"].sum(), table["revenue"].sum())
        insight(
            f"{format_int(metrics['repeat_customers'])} of {format_int(metrics['buying_customers'])} buying "
            f"customers returned for another purchase ({format_pct(metrics['repeat_rate'])}). The top 10 "
            f"customers account for {format_pct(top10_share, 1)} of filtered revenue."
        )

    section_header(
        "Top customers",
        "Ranked by revenue recorded in the filtered sessions; IDs are shown as stored in the dataset.",
    )
    left, right = st.columns([1.25, 1], gap="medium")
    with left:
        with st.container(border=True):
            _render_top_customers(table)
    with right:
        with st.container(border=True):
            st.markdown('<div class="mini-table-title">Top 10 customer detail</div>', unsafe_allow_html=True)
            display = table.head(10).copy()
            display["customer_id"] = display["customer_id"].map(lambda value: f"#{int(value)}")
            display = display.rename(
                columns={
                    "customer_id": "Customer",
                    "sessions": "Sessions",
                    "orders": "Purchases",
                    "units": "Units",
                    "revenue": "Revenue",
                    "aov": "AOV",
                }
            )
            st.dataframe(
                display[["Customer", "Sessions", "Purchases", "Units", "Revenue", "AOV"]],
                width="stretch",
                hide_index=True,
                height=340,
                column_config={
                    "Revenue": st.column_config.NumberColumn(format="%.2f"),
                    "AOV": st.column_config.NumberColumn(format="%.2f"),
                },
            )

    frequency, _ = _frequency_frame(purchases)
    segments = _segment_revenue(purchases)
    section_header("Purchase patterns", "How many buying customers come back, and where revenue concentrates.")
    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(border=True):
            _render_frequency(frequency)
    with right:
        with st.container(border=True):
            _render_segment_revenue(segments)

    section_header("Customer ratings", "Only purchasing sessions carry meaningful ratings in this dataset.")
    with st.container(border=True):
        _render_ratings(purchases)
    note("Non-purchasing sessions all have the same rating (4), so they are excluded from the rating analysis.")

    if not purchases.empty:
        rating = purchases["rating"].dropna()
        if not rating.empty:
            low_share = 100 * safe_div((rating <= 2).sum(), len(rating))
            insight(
                f"The average rating for filtered purchases is {rating.mean():.2f}, and "
                f"{format_pct(low_share, 1)} of rated purchases gave 1 or 2 stars. This is a service-quality "
                "signal worth investigating, not proof of a specific cause."
            )

    with st.expander("View customer purchase-frequency detail"):
        detail = frequency.copy()
        detail["share_pct"] = detail["share_pct"].map(lambda value: f"{value:.2f}%")
        detail = detail.rename(columns={"segment": "Segment", "buyers": "Buyers", "share_pct": "Share"})
        st.dataframe(detail, width="stretch", hide_index=True)
        if not table.empty:
            st.markdown("**Averages in the current selection**")
            st.write(
                f"- Average sessions per customer: **{metrics['avg_sessions_per_customer']:.2f}**\n"
                f"- Average purchase sessions per buying customer: **{metrics['avg_orders_per_buyer']:.2f}**"
            )
