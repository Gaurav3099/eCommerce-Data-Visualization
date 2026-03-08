"""
Data Churning: E-commerce analytics – revenue trends, funnel, segmentation,
top categories, purchase behavior heatmaps, cohort retention.
"""
import pandas as pd
import numpy as np
from typing import Optional

# Revenue = price for purchase events; if no event_type, treat all rows as purchases
REVENUE_EVENT = "purchase"


def _ensure_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure we have a revenue column: price for purchase events, else price for all."""
    if "revenue" in df.columns:
        return df
    if "event_type" in df.columns:
        df = df.copy()
        df["revenue"] = np.where(df["event_type"] == REVENUE_EVENT, df["price"], 0.0)
    else:
        df = df.copy()
        df["revenue"] = df["price"]
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add event_time-based and segment helpers."""
    df = df.copy()
    if "event_time" not in df.columns:
        return df
    df["date"] = df["event_time"].dt.date
    df["month"] = df["event_time"].dt.to_period("M").astype(str)
    df["year"] = df["event_time"].dt.year
    df["hour"] = df["event_time"].dt.hour
    df["day_of_week"] = df["event_time"].dt.dayofweek  # 0=Monday
    df["week_start"] = df["event_time"].dt.to_period("W-SUN").astype(str)
    return df


# ---------- Revenue trends ----------


def revenue_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """Daily revenue (purchase events only or all if no event_type)."""
    df = _ensure_revenue(df)
    if "event_type" in df.columns:
        purchases = df[df["event_type"] == REVENUE_EVENT]
    else:
        purchases = df
    purchases = add_derived_columns(purchases)
    return (
        purchases.groupby("date", as_index=False)["revenue"]
        .sum()
        .sort_values("date")
    )


def revenue_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly revenue and transaction count."""
    df = _ensure_revenue(df)
    if "event_type" in df.columns:
        purchases = df[df["event_type"] == REVENUE_EVENT]
    else:
        purchases = df
    purchases = add_derived_columns(purchases)
    return (
        purchases.groupby("month", as_index=False)
        .agg(revenue=("revenue", "sum"), transactions=("revenue", "count"))
        .sort_values("month")
    )


# ---------- Conversion funnel ----------


def conversion_funnel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Funnel: unique users/sessions per event_type (view -> cart -> purchase).
    If event_type is missing, returns empty DataFrame.
    """
    if "event_type" not in df.columns:
        return pd.DataFrame()
    # Order: view, cart, purchase (cart often used for add_to_cart)
    order = ["view", "cart", "purchase"]
    types = [t for t in order if t in df["event_type"].unique()]
    if not types:
        return pd.DataFrame()
    rows = []
    for t in types:
        sub = df[df["event_type"] == t]
        rows.append(
            {
                "stage": t,
                "users": sub["user_id"].nunique(),
                "sessions": sub["session_id"].nunique(),
                "events": len(sub),
            }
        )
    return pd.DataFrame(rows)


# ---------- Customer segmentation ----------


def customer_segments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Segment users by revenue and frequency (purchases or events).
    Segments: High Value, Frequent, Regular, Low Activity.
    """
    df = _ensure_revenue(df)
    if "event_type" in df.columns:
        purchases = df[df["event_type"] == REVENUE_EVENT]
    else:
        purchases = df
    user_agg = (
        purchases.groupby("user_id", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("session_id", "nunique"))
    )
    r_50, r_90 = user_agg["revenue"].quantile([0.5, 0.9]).values
    o_50, o_90 = user_agg["orders"].quantile([0.5, 0.9]).values

    def segment(row):
        if row["revenue"] >= r_90 and row["orders"] >= o_50:
            return "High Value"
        if row["orders"] >= o_90:
            return "Frequent"
        if row["revenue"] >= r_50:
            return "Regular"
        return "Low Activity"

    user_agg["segment"] = user_agg.apply(segment, axis=1)
    return (
        user_agg.groupby("segment", as_index=False)
        .agg(users=("user_id", "count"), revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
    )


# ---------- Top categories ----------


def top_categories_by_revenue(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Revenue and transaction count by category (purchases only)."""
    df = _ensure_revenue(df)
    if "event_type" in df.columns:
        purchases = df[df["event_type"] == REVENUE_EVENT]
    else:
        purchases = df
    out = (
        purchases.groupby("category", as_index=False)
        .agg(revenue=("revenue", "sum"), transactions=("revenue", "count"))
        .sort_values("revenue", ascending=False)
        .head(top_n)
    )
    return out


def top_categories_by_events(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Event count by category (all event types)."""
    out = (
        df.groupby("category", as_index=False)
        .agg(events=("product_id", "count"))
        .sort_values("events", ascending=False)
        .head(top_n)
    )
    return out


# ---------- Purchase behavior heatmaps ----------


def heatmap_hour_dow(df: pd.DataFrame) -> pd.DataFrame:
    """Count of events (or purchases) by hour of day x day of week. Index=hour, columns=day."""
    df = add_derived_columns(df)
    if "event_type" in df.columns:
        use = df[df["event_type"] == REVENUE_EVENT]
    else:
        use = df
    pivot = use.pivot_table(
        index="hour",
        columns="day_of_week",
        values="price",
        aggfunc="count",
    ).fillna(0)
    pivot.columns = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][: pivot.shape[1]]
    return pivot


def heatmap_category_month(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue by category (rows) x month (columns)."""
    df = _ensure_revenue(df)
    if "event_type" in df.columns:
        purchases = df[df["event_type"] == REVENUE_EVENT]
    else:
        purchases = df
    purchases = add_derived_columns(purchases)
    top_cats = (
        purchases.groupby("category")["revenue"]
        .sum()
        .nlargest(12)
        .index.tolist()
    )
    sub = purchases[purchases["category"].isin(top_cats)]
    return (
        sub.pivot_table(
            index="category",
            columns="month",
            values="revenue",
            aggfunc="sum",
        )
        .fillna(0)
    )


# ---------- Cohort retention ----------


def cohort_retention(
    df: pd.DataFrame,
    cohort_period: str = "M",
) -> pd.DataFrame:
    """
    Cohort retention: first purchase month per user -> share of users with purchase in later months.
    Returns wide DataFrame: index=cohort_month, columns=period_offset (0, 1, 2...), values=retention rate.
    """
    df = _ensure_revenue(df)
    if "event_type" in df.columns:
        purchases = df[df["event_type"] == REVENUE_EVENT]
    else:
        purchases = df
    purchases = add_derived_columns(purchases)
    if purchases.empty:
        return pd.DataFrame()

    if cohort_period == "M":
        purchases["cohort_month"] = purchases["event_time"].dt.to_period("M").astype(str)
    else:
        purchases["cohort_month"] = purchases["event_time"].dt.to_period("W-SUN").astype(str)

    first = purchases.groupby("user_id")["cohort_month"].min().reset_index()
    first = first.rename(columns={"cohort_month": "first_month"})
    merged = purchases.merge(first, on="user_id")
    try:
        delta = pd.to_datetime(merged["cohort_month"]) - pd.to_datetime(merged["first_month"])
        merged["period_offset"] = (delta.dt.days // 30).clip(lower=0)
    except Exception:
        merged["period_offset"] = 0

    cohort_sizes = merged.groupby("first_month")["user_id"].nunique()
    retained = (
        merged.groupby(["first_month", "period_offset"])["user_id"]
        .nunique()
        .unstack(fill_value=0)
    )
    retention = retained.div(cohort_sizes, axis=0).fillna(0)
    return retention


def run_churning_pipeline(df: pd.DataFrame) -> dict:
    """Run all e-commerce churning steps. Returns dict of datasets for viz."""
    df = add_derived_columns(df)
    df = _ensure_revenue(df)
    return {
        "revenue_by_day": revenue_by_day(df),
        "revenue_by_month": revenue_by_month(df),
        "conversion_funnel": conversion_funnel(df),
        "customer_segments": customer_segments(df),
        "top_categories_revenue": top_categories_by_revenue(df),
        "top_categories_events": top_categories_by_events(df),
        "heatmap_hour_dow": heatmap_hour_dow(df),
        "heatmap_category_month": heatmap_category_month(df),
        "cohort_retention": cohort_retention(df),
        "enriched": df,
    }
