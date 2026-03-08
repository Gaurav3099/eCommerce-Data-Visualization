"""
Run: streamlit run dashboard.py
"""
import sys
from pathlib import Path
from typing import Optional

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd

from src.data_engineering import run_engineering_pipeline
from src.data_churning import run_churning_pipeline
from src import visualizations as viz

# Page config
st.set_page_config(
    page_title="E-commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar: data source and filters
st.sidebar.header("Data & filters")

data_dir = project_root / "data" / "raw"
csv_files = list(data_dir.glob("*.csv")) if data_dir.exists() else []
default_path = str(project_root / "data" / "raw" / "2019-Oct.csv")
if csv_files:
    options = [str(p) for p in csv_files]
    data_path = st.sidebar.selectbox(
        "Dataset",
        options,
        index=0 if default_path not in options else options.index(default_path),
    )
else:
    data_path = st.sidebar.text_input("Path to CSV", value=default_path)

nrows = st.sidebar.number_input(
    "Max rows (0 = all)",
    min_value=0,
    value=100_000,
    step=50_000,
    help="Limit rows for large files.",
)
nrows = None if nrows == 0 else nrows

# Load and process
@st.cache_data(ttl=300)
def load_and_churn(path: str, nrows: Optional[int]):
    try:
        df = run_engineering_pipeline(path, nrows=nrows)
        churned = run_churning_pipeline(df)
        return df, churned
    except Exception as e:
        return None, str(e)


if "churned" not in st.session_state:
    if Path(data_path).exists():
        with st.spinner("Loading and processing data..."):
            result = load_and_churn(data_path, nrows)
            if result[0] is not None:
                st.session_state["raw_df"] = result[0]
                st.session_state["churned"] = result[1]
            else:
                st.session_state["load_error"] = result[1]
                st.session_state["raw_df"] = None
                st.session_state["churned"] = None
    else:
        st.session_state["raw_df"] = None
        st.session_state["churned"] = None
        st.session_state["load_error"] = None

if st.sidebar.button("Reload data"):
    load_and_churn.clear()
    for k in ("churned", "raw_df", "load_error"):
        st.session_state.pop(k, None)
    st.rerun()

churned = st.session_state.get("churned")
raw_df = st.session_state.get("raw_df")
load_error = st.session_state.get("load_error")

if churned is None or raw_df is None:
    if load_error:
        st.error(f"Pipeline error: {load_error}")
    st.info(
        "Place the `data/raw/`"
        
    )
    st.stop()

# Category filter (options from loaded data)
if "category" in raw_df.columns:
    all_cats = sorted(raw_df["category"].unique().tolist())[:100]
    category_filter = st.sidebar.multiselect(
        "Filter by category (optional)",
        options=all_cats,
        default=[],
        help="Show only data for selected categories.",
    )
    if category_filter:
        filtered_raw = raw_df[raw_df["category"].isin(category_filter)]
        if not filtered_raw.empty:
            churned = run_churning_pipeline(filtered_raw)
else:
    category_filter = []

# Main content
st.title("E-commerce Analytics Dashboard")
st.caption("Revenue trends, conversion funnel, segmentation, top categories, heatmaps, cohort retention.")

tabs = st.tabs(
    [
        "Revenue trends",
        "Conversion funnel",
        "Customer segmentation",
        "Top categories",
        "Purchase heatmaps",
        "Cohort retention",
    ]
)

with tabs[0]:
    if not churned["revenue_by_month"].empty:
        fig = viz.plotly_revenue_trends(churned["revenue_by_month"], time_col="month")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No monthly revenue data (e.g. need purchase events).")

with tabs[1]:
    if not churned["conversion_funnel"].empty:
        fig = viz.plotly_funnel(churned["conversion_funnel"], value_col="users")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(churned["conversion_funnel"], use_container_width=True)
    else:
        st.write("Funnel requires `event_type` (view, cart, purchase) in the dataset.")

with tabs[2]:
    if not churned["customer_segments"].empty:
        fig = viz.plotly_customer_segments(churned["customer_segments"])
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(churned["customer_segments"], use_container_width=True)
    else:
        st.write("No segment data.")

with tabs[3]:
    if not churned["top_categories_revenue"].empty:
        top_n = st.slider("Top N categories", 5, 30, 15, key="top_n_cat")
        fig = viz.plotly_top_categories(churned["top_categories_revenue"], top_n=top_n)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(churned["top_categories_revenue"].head(20), use_container_width=True)
    else:
        st.write("No category revenue data.")

with tabs[4]:
    c1, c2 = st.columns(2)
    with c1:
        if not churned["heatmap_hour_dow"].empty:
            fig = viz.plotly_heatmap_hour_dow(churned["heatmap_hour_dow"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No hour/dow heatmap data.")
    with c2:
        if not churned["heatmap_category_month"].empty:
            fig = viz.plotly_heatmap_category_month(churned["heatmap_category_month"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No category/month heatmap data.")

with tabs[5]:
    if not churned["cohort_retention"].empty:
        fig = viz.plotly_cohort_retention(churned["cohort_retention"])
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Retention = share of cohort users with a purchase in that month.")
    else:
        st.write("Cohort retention requires purchase events over time.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset:** [E-commerce behavior data (Kaggle)](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store)")
