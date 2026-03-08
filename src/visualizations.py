"""
E-commerce visualizations: revenue trends, conversion funnel, customer segmentation,
top categories, purchase behavior heatmaps, cohort retention.
Static (matplotlib/seaborn) and Plotly figures for dashboard.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Optional

try:
    plt.style.use("seaborn-v0_8-whitegrid")
except OSError:
    try:
        plt.style.use("seaborn-whitegrid")
    except OSError:
        plt.style.use("ggplot")
sns.set_palette("husl")

# Adobe-style accent (optional)
ACCENT = "#FF0000"  # red; can use #1473E6 (blue) for Adobe Analytics style


def _ensure_output_dir(output_dir: str) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    return out


# ---------- Revenue trends ----------


def plot_revenue_trends(
    df: pd.DataFrame,
    output_dir: str = "outputs/charts",
    title: str = "Revenue Over Time",
    time_col: str = "month",
) -> str:
    """Line chart: revenue by month (or date)."""
    out = _ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df[time_col], df["revenue"], marker="o", linewidth=2, markersize=5)
    ax.set_title(title)
    ax.set_ylabel("Revenue")
    ax.set_xlabel(time_col)
    ax.tick_params(axis="x", rotation=45)
    path = out / "revenue_trends.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close()
    return str(path)


def plotly_revenue_trends(df: pd.DataFrame, time_col: str = "month") -> go.Figure:
    """Interactive revenue trend line chart."""
    fig = px.line(
        df, x=time_col, y="revenue",
        title="Revenue Over Time",
        labels={"revenue": "Revenue", time_col: time_col},
    )
    fig.update_layout(template="plotly_white", hovermode="x unified")
    return fig


# ---------- Conversion funnel ----------


def plot_funnel(
    df: pd.DataFrame,
    output_dir: str = "outputs/charts",
    title: str = "Conversion Funnel",
    value_col: str = "users",
) -> str:
    """Horizontal funnel-style bar chart (stages decreasing)."""
    out = _ensure_output_dir(output_dir)
    df = df.sort_values(value_col, ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    stages = df["stage"].astype(str).str.capitalize()
    ax.barh(stages, df[value_col], color=sns.color_palette("husl", len(df)))
    ax.set_title(title)
    ax.set_xlabel(value_col)
    path = out / "conversion_funnel.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close()
    return str(path)


def plotly_funnel(df: pd.DataFrame, value_col: str = "users") -> go.Figure:
    """Interactive funnel chart (Plotly funnel)."""
    fig = go.Figure(
        go.Funnel(
            y=df["stage"].astype(str).str.capitalize().tolist(),
            x=df[value_col].tolist(),
            textinfo="value+percent initial",
        )
    )
    fig.update_layout(
        title="Conversion Funnel",
        template="plotly_white",
        yaxis_title="Stage",
        xaxis_title=value_col,
    )
    return fig


# ---------- Customer segmentation ----------


def plot_customer_segments(
    df: pd.DataFrame,
    output_dir: str = "outputs/charts",
    title: str = "Customer Segmentation",
) -> str:
    """Bar chart: users and revenue by segment."""
    out = _ensure_output_dir(output_dir)
    fig, ax1 = plt.subplots(figsize=(10, 5))
    x = range(len(df))
    w = 0.35
    ax1.bar([i - w / 2 for i in x], df["users"], width=w, label="Users")
    ax1.set_ylabel("Users")
    ax2 = ax1.twinx()
    ax2.bar([i + w / 2 for i in x], df["revenue"], width=w, label="Revenue", alpha=0.8)
    ax2.set_ylabel("Revenue")
    ax1.set_xticks(x)
    ax1.set_xticklabels(df["segment"], rotation=30, ha="right")
    ax1.set_title(title)
    ax1.legend(loc="upper right")
    ax2.legend(loc="upper left")
    path = out / "customer_segments.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close()
    return str(path)


def plotly_customer_segments(df: pd.DataFrame) -> go.Figure:
    """Interactive segment bar chart."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(name="Users", x=df["segment"], y=df["users"]),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(name="Revenue", x=df["segment"], y=df["revenue"]),
        secondary_y=True,
    )
    fig.update_layout(
        title="Customer Segmentation",
        template="plotly_white",
        barmode="group",
    )
    fig.update_yaxes(title_text="Users", secondary_y=False)
    fig.update_yaxes(title_text="Revenue", secondary_y=True)
    return fig


# ---------- Top categories ----------


def plot_top_categories(
    df: pd.DataFrame,
    output_dir: str = "outputs/charts",
    title: str = "Top Categories by Revenue",
    top_n: int = 12,
) -> str:
    """Horizontal bar: revenue by category."""
    out = _ensure_output_dir(output_dir)
    df = df.head(top_n)
    fig, ax = plt.subplots(figsize=(10, 6))
    # Shorten long category labels
    labels = df["category"].astype(str).str[:40] + np.where(
        df["category"].astype(str).str.len() > 40, "...", ""
    )
    sns.barplot(data=df.assign(_label=labels), y="_label", x="revenue", ax=ax, orient="h")
    ax.set_title(title)
    ax.set_xlabel("Revenue")
    path = out / "top_categories.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close()
    return str(path)


def plotly_top_categories(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Interactive top categories bar chart."""
    df = df.head(top_n)
    fig = px.bar(
        df, y="category", x="revenue",
        title="Top Categories by Revenue",
        labels={"revenue": "Revenue", "category": "Category"},
        orientation="h",
    )
    fig.update_layout(template="plotly_white", yaxis={"categoryorder": "total ascending"})
    return fig


# ---------- Purchase behavior heatmaps ----------


def plot_heatmap_hour_dow(
    pivot: pd.DataFrame,
    output_dir: str = "outputs/charts",
    title: str = "Purchase Behavior by Hour & Day of Week",
) -> str:
    """Heatmap: hour x day of week."""
    out = _ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot, annot=False, fmt=".0f", cmap="YlOrRd", ax=ax)
    ax.set_title(title)
    ax.set_ylabel("Hour of day")
    path = out / "heatmap_hour_dow.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close()
    return str(path)


def plotly_heatmap_hour_dow(pivot: pd.DataFrame) -> go.Figure:
    """Interactive heatmap hour x day of week."""
    fig = px.imshow(
        pivot,
        labels=dict(x="Day of week", y="Hour", color="Events"),
        title="Purchase Behavior by Hour & Day of Week",
        aspect="auto",
        color_continuous_scale="YlOrRd",
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_heatmap_category_month(
    pivot: pd.DataFrame,
    output_dir: str = "outputs/charts",
    title: str = "Revenue by Category & Month",
) -> str:
    """Heatmap: category x month."""
    out = _ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot, annot=False, fmt=".0f", cmap="Blues", ax=ax)
    ax.set_title(title)
    path = out / "heatmap_category_month.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close()
    return str(path)


def plotly_heatmap_category_month(pivot: pd.DataFrame) -> go.Figure:
    """Interactive heatmap category x month."""
    fig = px.imshow(
        pivot,
        labels=dict(x="Month", y="Category", color="Revenue"),
        title="Revenue by Category & Month",
        aspect="auto",
        color_continuous_scale="Blues",
    )
    fig.update_layout(template="plotly_white")
    return fig


# ---------- Cohort retention ----------


def plot_cohort_retention(
    retention: pd.DataFrame,
    output_dir: str = "outputs/charts",
    title: str = "Cohort Retention (by first purchase month)",
) -> str:
    """Heatmap: cohort month x period offset, color = retention rate."""
    out = _ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(
        retention,
        annot=True,
        fmt=".0%",
        cmap="RdYlGn",
        ax=ax,
        vmin=0,
        vmax=1,
    )
    ax.set_title(title)
    ax.set_xlabel("Months since first purchase")
    ax.set_ylabel("Cohort (first purchase month)")
    path = out / "cohort_retention.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close()
    return str(path)


def plotly_cohort_retention(retention: pd.DataFrame) -> go.Figure:
    """Interactive cohort retention heatmap."""
    fig = px.imshow(
        retention,
        labels=dict(x="Months since first purchase", y="Cohort", color="Retention"),
        title="Cohort Retention",
        aspect="auto",
        color_continuous_scale="RdYlGn",
    )
    fig.update_layout(template="plotly_white")
    return fig


# ---------- Generate all static charts ----------


def generate_all_charts(
    churned: dict,
    output_dir: str = "outputs/charts",
) -> list[str]:
    """Generate all static PNG charts from churned e-commerce data."""
    paths = []

    if not churned["revenue_by_month"].empty:
        paths.append(
            plot_revenue_trends(
                churned["revenue_by_month"],
                output_dir=output_dir,
                time_col="month",
            )
        )
    if not churned["conversion_funnel"].empty:
        paths.append(
            plot_funnel(churned["conversion_funnel"], output_dir=output_dir)
        )
    if not churned["customer_segments"].empty:
        paths.append(
            plot_customer_segments(churned["customer_segments"], output_dir=output_dir)
        )
    if not churned["top_categories_revenue"].empty:
        paths.append(
            plot_top_categories(
                churned["top_categories_revenue"],
                output_dir=output_dir,
            )
        )
    if not churned["heatmap_hour_dow"].empty:
        paths.append(
            plot_heatmap_hour_dow(churned["heatmap_hour_dow"], output_dir=output_dir)
        )
    if not churned["heatmap_category_month"].empty:
        paths.append(
            plot_heatmap_category_month(
                churned["heatmap_category_month"],
                output_dir=output_dir,
            )
        )
    if not churned["cohort_retention"].empty:
        paths.append(
            plot_cohort_retention(churned["cohort_retention"], output_dir=output_dir)
        )

    return paths
