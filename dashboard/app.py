"""E-Commerce Sales and Customer Analysis - interactive Streamlit dashboard.

Run from the project root:
    python -m streamlit run dashboard/app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from components import sidebar_brand, sidebar_section
from data_loader import (
    CODE_COLUMNS,
    DATA_PATH,
    apply_filters,
    code_label,
    format_int,
    load_data,
)
from theme import load_css, register_theme
from views import behaviour, customers, marketing, sales

BASE_DIR = Path(__file__).resolve().parent
FAVICON = BASE_DIR / "assets" / "favicon.svg"

st.set_page_config(
    page_title="E-Commerce Analytics | Sales & Customer Intelligence",
    page_icon=str(FAVICON) if FAVICON.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

register_theme()
st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)

PAGES = {
    "Sales Performance": sales.render,
    "Customer Analysis": customers.render,
    "Customer Behaviour": behaviour.render,
    "Marketing & Product": marketing.render,
}

FILTER_KEYS = [
    "filter_start",
    "filter_end",
    "filter_category",
    "filter_channel",
    "filter_device",
    "filter_user",
    "filter_payment",
]

try:
    df, meta = load_data(DATA_PATH)
except Exception as exc:  # pragma: no cover - defensive startup guard
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

if df.empty:
    st.error(
        "The dataset loaded with zero rows. Add data/Ecommerce_sales.csv to the project and reload."
    )
    st.stop()

min_date = meta["min_date"].date()
max_date = meta["max_date"].date()

with st.sidebar:
    sidebar_brand()
    sidebar_section("Navigation")
    page_name = st.radio(
        "Navigation",
        options=list(PAGES.keys()),
        label_visibility="collapsed",
    )

    sidebar_section("Filters")
    st.date_input(
        "Start date",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY",
        key="filter_start",
    )
    st.date_input(
        "End date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY",
        key="filter_end",
    )

    filter_widgets = [
        ("filter_category", "product_category", "Product category"),
        ("filter_channel", "marketing_channel", "Marketing channel"),
        ("filter_device", "device_type", "Device type"),
        ("filter_user", "user_type", "User type"),
        ("filter_payment", "payment_method", "Payment method"),
    ]
    for widget_key, column, label in filter_widgets:
        options = sorted(df[column].dropna().unique().tolist())
        st.multiselect(
            label,
            options=options,
            format_func=lambda value, column=column: code_label(column, value),
            placeholder="All",
            key=widget_key,
            help="Leave empty to include every stored code.",
        )

    if st.button("Reset filters", width="stretch"):
        for key in FILTER_KEYS:
            st.session_state.pop(key, None)
        st.rerun()

    start = st.session_state.get("filter_start", min_date)
    end = st.session_state.get("filter_end", max_date)
    if start > end:
        st.warning("Start date is after end date; the range was applied in reverse order.")

    filters = {
        "date_range": (start, end),
        "product_category": st.session_state.get("filter_category", []),
        "marketing_channel": st.session_state.get("filter_channel", []),
        "device_type": st.session_state.get("filter_device", []),
        "user_type": st.session_state.get("filter_user", []),
        "payment_method": st.session_state.get("filter_payment", []),
    }
    filtered = apply_filters(df, filters)

    st.markdown(
        f"""
        <div class="sidebar-foot">
            <strong>{format_int(len(filtered))}</strong> of {format_int(len(df))} sessions selected<br>
            Names marked * are inferred, not from the dataset. No currency is declared.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.download_button(
        "Download filtered data",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="ecommerce_filtered_sessions.csv",
        mime="text/csv",
        width="stretch",
    )

    with st.expander("Data quality notes"):
        st.write(
            f"- Rows loaded: **{format_int(meta['original_rows'])}**\n"
            f"- Invalid visit dates: **{format_int(meta['invalid_dates'])}**\n"
            f"- Duplicate sessions removed: **{format_int(meta['duplicates_removed'])}**\n"
            f"- Date coverage: **{meta['min_date']:%d %b %Y} to {meta['max_date']:%d %b %Y}**\n"
            f"- Columns: **{len(meta['columns'])}**"
        )
        st.caption(
            "Revenue is shown in the dataset's native units because no currency is specified. "
            "The dataset has no code dictionary, so category, device, channel, payment and "
            "user-type names marked with * are inferred guesses, not official values."
        )

if len(filtered) == 0:
    context = "0 sessions selected"
elif pd.isna(filtered["visit_date_parsed"]).all():
    context = f"{format_int(len(filtered))} sessions selected"
else:
    first_date = filtered["visit_date_parsed"].min()
    last_date = filtered["visit_date_parsed"].max()
    context = (
        f"{format_int(len(filtered))} sessions | "
        f"{first_date:%d %b %Y} to {last_date:%d %b %Y}"
    )

PAGES[page_name](filtered, context)

st.markdown(
    """
    <div class="app-footer">
        <span>E-Commerce Sales &amp; Customer Analysis</span>
        <span>Industrial Training Project &middot; Streamlit + Plotly</span>
        <span>Revenue in dataset units &middot; Names marked * are inferred</span>
    </div>
    """,
    unsafe_allow_html=True,
)
