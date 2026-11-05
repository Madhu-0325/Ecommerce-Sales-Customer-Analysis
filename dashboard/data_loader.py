"""Data loading, validation, filtering and KPI calculations for the dashboard.

All figures are computed from the real dataset in ``data/Ecommerce_sales.csv``.
Numeric code columns are never mapped to invented business names.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "data" / "Ecommerce_sales.csv"

CODE_COLUMNS = {
    "device_type": "Device",
    "user_type": "User type",
    "marketing_channel": "Channel",
    "product_category": "Category",
    "payment_method": "Payment",
    "location": "Location",
    "visit_season": "Season",
}

# The dataset ships without a data dictionary, so the names below are inferred
# from common e-commerce conventions and the observed distributions. They are
# marked with a trailing "*" in the UI to make clear they are not ground truth.
INFERRED_CODE_LABELS = {
    "device_type": {
        0: "Desktop",
        1: "Mobile",
        2: "Tablet",
    },
    "user_type": {
        0: "New visitor",
        1: "Returning customer",
    },
    "marketing_channel": {
        0: "Organic search",
        1: "Paid search",
        2: "Social media",
        3: "Email",
        4: "Referral",
        5: "Direct",
    },
    "payment_method": {
        0: "Credit card",
        1: "Debit card",
        2: "PayPal",
        3: "Digital wallet",
        4: "Net banking",
        5: "Cash on delivery",
    },
    "product_category": {
        0: "Electronics",
        1: "Clothing",
        2: "Home & kitchen",
        3: "Beauty",
        4: "Sports",
        5: "Books",
        6: "Toys",
        7: "Grocery",
    },
}

FLAG_COLUMNS = ["added_to_cart", "purchased", "cart_abandoned"]
REVENUE_COLUMNS = ["unit_price", "quantity", "discount_percent", "discount_amount", "revenue"]
ENGAGEMENT_COLUMNS = ["pages_viewed", "time_on_site_sec", "rating", "review_helpful_votes"]

DURATION_ORDER = ["Very Short", "Short", "Long", "Very Long"]
WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_ORDER = list(range(1, 13))

PALETTE = ["#3B82F6", "#22D3EE", "#A855F7", "#818CF8", "#38BDF8", "#C084FC", "#60A5FA", "#F472B6"]


@st.cache_data(show_spinner=False)
def load_data(path: str | Path = DATA_PATH) -> tuple[pd.DataFrame, dict]:
    """Load and defensively clean the CSV once per session."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    original_rows = len(df)

    for column in REVENUE_COLUMNS + ENGAGEMENT_COLUMNS + FLAG_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    for column in FLAG_COLUMNS:
        df[column] = df[column].fillna(0).clip(0, 1).astype(int)

    df["visit_date_parsed"] = pd.to_datetime(
        df["visit_date"], format="%d-%m-%Y", errors="coerce"
    )
    invalid_dates = int(df["visit_date_parsed"].isna().sum())

    duplicates_removed = 0
    if "session_id" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["session_id"], keep="first")
        duplicates_removed = before - len(df)

    for column in ["revenue", "discount_amount", "unit_price", "quantity"]:
        if column in df.columns:
            df[column] = df[column].fillna(0).clip(lower=0)

    df["year_month"] = df["visit_date_parsed"].dt.to_period("M").dt.to_timestamp()
    df["month_label"] = df["year_month"].dt.strftime("%b %Y")
    df["year"] = df["visit_date_parsed"].dt.year
    df["weekday_name"] = df["visit_date_parsed"].dt.day_name()
    if "session_duration_bucket" in df.columns:
        df["session_duration_bucket"] = pd.Categorical(
            df["session_duration_bucket"], categories=DURATION_ORDER, ordered=True
        )

    meta = {
        "rows": len(df),
        "original_rows": original_rows,
        "invalid_dates": invalid_dates,
        "duplicates_removed": duplicates_removed,
        "min_date": df["visit_date_parsed"].min(),
        "max_date": df["visit_date_parsed"].max(),
        "columns": list(df.columns),
    }
    return df, meta


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply the global sidebar filters. Empty selections mean 'all'."""
    out = df.copy()

    start, end = filters.get("date_range", (None, None))
    if start is not None and end is not None:
        mask = df["visit_date_parsed"].notna()
        if start > end:
            start, end = end, start
        mask &= df["visit_date_parsed"].dt.date.between(start, end)
        out = out[mask]

    for column in CODE_COLUMNS:
        values = filters.get(column)
        if values:
            out = out[out[column].isin(values)]

    return out


def safe_div(numerator, denominator, default: float = 0.0) -> float:
    """Divide without raising on zero or missing denominators."""
    try:
        if denominator is None or denominator == 0 or pd.isna(denominator):
            return default
        return float(numerator) / float(denominator)
    except (TypeError, ZeroDivisionError):
        return default


def compute_kpis(df: pd.DataFrame) -> dict:
    sessions = int(len(df))
    purchases = int(df["purchased"].sum())
    revenue = float(df["revenue"].sum())
    buyers = df.loc[df["purchased"] == 1, "customer_id"].nunique()
    return {
        "sessions": sessions,
        "purchases": purchases,
        "revenue": revenue,
        "conversion_rate": 100 * safe_div(purchases, sessions),
        "aov": safe_div(revenue, purchases),
        "unique_customers": int(df["customer_id"].nunique()),
        "buying_customers": int(buyers),
        "avg_revenue_per_customer": safe_div(revenue, buyers),
    }


def customer_metrics(df: pd.DataFrame) -> dict:
    purchases = df[df["purchased"] == 1]
    buyer_orders = purchases.groupby("customer_id")["session_id"].nunique()
    repeat_customers = int((buyer_orders > 1).sum())
    metrics = compute_kpis(df)
    metrics.update(
        {
            "repeat_customers": repeat_customers,
            "repeat_rate": 100 * safe_div(repeat_customers, len(buyer_orders)),
            "avg_orders_per_buyer": safe_div(len(purchases), len(buyer_orders)),
            "avg_sessions_per_customer": safe_div(len(df), df["customer_id"].nunique()),
        }
    )
    return metrics


def behaviour_metrics(df: pd.DataFrame) -> dict:
    cart_adds = int(df["added_to_cart"].sum())
    abandoned = int(df["cart_abandoned"].sum())
    purchases = int(df["purchased"].sum())
    avg_time_buyers = df.loc[df["purchased"] == 1, "time_on_site_sec"].mean()
    avg_time_non_buyers = df.loc[df["purchased"] == 0, "time_on_site_sec"].mean()
    avg_pages_buyers = df.loc[df["purchased"] == 1, "pages_viewed"].mean()
    avg_pages_non_buyers = df.loc[df["purchased"] == 0, "pages_viewed"].mean()
    return {
        "cart_adds": cart_adds,
        "abandoned": abandoned,
        "purchases": purchases,
        "abandonment_rate": 100 * safe_div(abandoned, cart_adds),
        "cart_purchase_rate": 100 * safe_div(purchases, cart_adds),
        "avg_time": float(df["time_on_site_sec"].mean()) if len(df) else 0.0,
        "avg_pages": float(df["pages_viewed"].mean()) if len(df) else 0.0,
        "avg_time_buyers": float(avg_time_buyers) if pd.notna(avg_time_buyers) else 0.0,
        "avg_time_non_buyers": float(avg_time_non_buyers) if pd.notna(avg_time_non_buyers) else 0.0,
        "avg_pages_buyers": float(avg_pages_buyers) if pd.notna(avg_pages_buyers) else 0.0,
        "avg_pages_non_buyers": float(avg_pages_non_buyers) if pd.notna(avg_pages_non_buyers) else 0.0,
    }


def segment_summary(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Session, order, revenue, conversion and AOV summary for a code column."""
    if df.empty:
        return pd.DataFrame(columns=[column, "sessions", "orders", "revenue", "conversion_rate_pct", "aov"])
    grouped = df.groupby(column, observed=True).agg(
        sessions=("session_id", "count"),
        orders=("purchased", "sum"),
        revenue=("revenue", "sum"),
    )
    grouped["conversion_rate_pct"] = 100 * grouped["orders"] / grouped["sessions"].replace(0, np.nan)
    grouped["aov"] = grouped["revenue"] / grouped["orders"].replace(0, np.nan)
    grouped["conversion_rate_pct"] = grouped["conversion_rate_pct"].fillna(0.0)
    grouped["aov"] = grouped["aov"].fillna(0.0)
    return grouped.reset_index().sort_values("revenue", ascending=False)


def discount_summary(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("discount_percent", observed=True).agg(
        sessions=("session_id", "count"),
        orders=("purchased", "sum"),
        revenue=("revenue", "sum"),
        discount_amount=("discount_amount", "sum"),
    )
    grouped["conversion_rate_pct"] = 100 * grouped["orders"] / grouped["sessions"].replace(0, np.nan)
    grouped["aov"] = grouped["revenue"] / grouped["orders"].replace(0, np.nan)
    return grouped.fillna(0.0).reset_index().sort_values("discount_percent")


def top_products(df: pd.DataFrame, limit: int = 10, min_orders: int = 1) -> pd.DataFrame:
    purchases = df[df["purchased"] == 1]
    if purchases.empty:
        return pd.DataFrame(columns=["product_id", "orders", "units", "revenue", "avg_rating"])
    grouped = purchases.groupby("product_id", observed=True).agg(
        orders=("session_id", "nunique"),
        units=("quantity", "sum"),
        revenue=("revenue", "sum"),
        avg_rating=("rating", "mean"),
    )
    grouped = grouped[grouped["orders"] >= min_orders]
    return grouped.sort_values(["revenue", "units"], ascending=False).head(limit).reset_index()


def customer_table(df: pd.DataFrame) -> pd.DataFrame:
    purchases = df[df["purchased"] == 1]
    if purchases.empty:
        return pd.DataFrame(columns=["customer_id", "sessions", "orders", "units", "revenue", "aov"])
    sessions = df.groupby("customer_id")["session_id"].nunique().rename("sessions")
    grouped = purchases.groupby("customer_id", observed=True).agg(
        orders=("session_id", "nunique"),
        units=("quantity", "sum"),
        revenue=("revenue", "sum"),
    ).join(sessions)
    grouped["aov"] = grouped["revenue"] / grouped["orders"].replace(0, np.nan)
    return grouped.fillna(0.0).reset_index().sort_values("revenue", ascending=False)


def code_label(column: str, value) -> str:
    """Human-readable label for a numeric code.

    Labels ending in "*" are inferred guesses, not names supplied by the dataset.
    """
    if pd.isna(value):
        return "Unknown"
    try:
        code = int(value)
    except (TypeError, ValueError):
        return str(value)
    inferred = INFERRED_CODE_LABELS.get(column, {})
    if code in inferred:
        return f"{inferred[code]}*"
    prefix = CODE_COLUMNS.get(column, "Code")
    return f"{prefix} {code}"


def format_compact(value: float, decimals: int = 2) -> str:
    """Compact number formatting without inventing a currency symbol."""
    if value is None or pd.isna(value):
        return "0"
    value = float(value)
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.{decimals}f}B"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.{decimals}f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:,.{decimals}f}K"
    return f"{value:,.0f}"


def format_int(value: float) -> str:
    return f"{int(round(value)):,}" if value is not None and not pd.isna(value) else "0"


def format_pct(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}%"


def format_number(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}" if value is not None and not pd.isna(value) else "0"


def choose_palette(count: int) -> list[str]:
    """Repeat the palette safely for any number of chart categories."""
    return [PALETTE[index % len(PALETTE)] for index in range(max(count, 0))]
