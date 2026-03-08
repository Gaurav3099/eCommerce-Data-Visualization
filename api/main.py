"""
FastAPI backend: run data engineering + churning, expose JSON for React frontend.
"""
import sys
from pathlib import Path
from typing import List, Optional

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.data_engineering import run_engineering_pipeline
from src.data_churning import run_churning_pipeline

app = FastAPI(title="E-commerce Analytics API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _df_to_json(df: pd.DataFrame) -> List[dict]:
    """DataFrame to list of dicts (NaN -> null)."""
    if df is None or df.empty:
        return []
    return df.fillna(0).to_dict(orient="records")


def _pivot_to_json(df: pd.DataFrame) -> dict:
    """Pivot/heatmap DataFrame to { rows, columns, data } for frontend."""
    if df is None or df.empty:
        return {"rows": [], "columns": [], "data": []}
    return {
        "rows": list(df.index.astype(str)),
        "columns": list(df.columns.astype(str)),
        "data": df.fillna(0).values.tolist(),
    }


def _safe_churn(path: str, nrows: Optional[int], categories: Optional[List[str]]):
    """Run pipeline and return serializable dict; filter by categories if provided."""
    df = run_engineering_pipeline(path, nrows=nrows)
    if categories and "category" in df.columns:
        df = df[df["category"].isin(categories)]
    churned = run_churning_pipeline(df)
    # Don't send full enriched (can be huge)
    churned.pop("enriched", None)
    return churned


def serialize_churned(churned: dict) -> dict:
    """Convert churned dict to JSON-serializable."""
    out = {}
    out["revenue_by_day"] = _df_to_json(churned.get("revenue_by_day"))
    out["revenue_by_month"] = _df_to_json(churned.get("revenue_by_month"))
    out["conversion_funnel"] = _df_to_json(churned.get("conversion_funnel"))
    out["customer_segments"] = _df_to_json(churned.get("customer_segments"))
    out["top_categories_revenue"] = _df_to_json(churned.get("top_categories_revenue"))
    out["top_categories_events"] = _df_to_json(churned.get("top_categories_events"))
    out["heatmap_hour_dow"] = _pivot_to_json(churned.get("heatmap_hour_dow"))
    out["heatmap_category_month"] = _pivot_to_json(churned.get("heatmap_category_month"))
    out["cohort_retention"] = _pivot_to_json(churned.get("cohort_retention"))
    return out


DEFAULT_DATA_PATH = str(project_root / "data" / "raw" / "ecommerce_sample.csv")


@app.get("/")
def root():
    return {"message": "E-commerce Analytics API", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/categories")
def get_categories(
    path: str = Query(default=DEFAULT_DATA_PATH, description="Path to CSV"),
    nrows: int = Query(default=100_000, ge=0, description="Max rows (0 = all)"),
):
    """Return list of categories for filter dropdown."""
    nrows = None if nrows == 0 else nrows
    try:
        df = run_engineering_pipeline(path, nrows=nrows)
        if "category" not in df.columns:
            return {"categories": []}
        cats = sorted(df["category"].unique().astype(str).tolist())
        return {"categories": cats[:200]}
    except Exception as e:
        return {"categories": [], "error": str(e)}


@app.get("/api/data")
def get_data(
    path: str = Query(default=DEFAULT_DATA_PATH, description="Path to CSV"),
    nrows: int = Query(default=100_000, ge=0),
    categories: str = Query(default="", description="Comma-separated category filter"),
):
    """Run pipeline and return all chart data as JSON."""
    nrows = None if nrows == 0 else nrows
    cat_list = [c.strip() for c in categories.split(",") if c.strip()] or None
    try:
        churned = _safe_churn(path, nrows, cat_list)
        return serialize_churned(churned)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
