"""
Data Engineering: Load, clean, validate e-commerce behavior data.
Supports Kaggle schema (event_time, event_type, user_session) and normalized schema
(user_id, product_id, category, price, purchase_time, session_id).
"""
import pandas as pd
from pathlib import Path
from typing import Optional

# Column mapping: Kaggle -> normalized
KAGGLE_COLUMN_MAP = {
    "event_time": "event_time",
    "event_type": "event_type",
    "product_id": "product_id",
    "category_id": "category",
    "category_code": "category_code",
    "price": "price",
    "user_id": "user_id",
    "user_session": "session_id",
}

REQUIRED_COLUMNS = ["user_id", "product_id", "price", "event_time", "session_id"]
OPTIONAL_COLUMNS = ["event_type", "category"]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map Kaggle or alternate column names to normalized names."""
    df = df.copy()
    # Prefer category_code over category_id for display
    if "category_code" in df.columns and "category_id" in df.columns:
        df["category"] = df["category_code"].fillna(df["category_id"].astype(str))
        df = df.drop(columns=["category_code", "category_id"], errors="ignore")
    elif "category_code" in df.columns:
        df = df.rename(columns={"category_code": "category"})
    elif "category_id" in df.columns:
        df = df.rename(columns={"category_id": "category"})
    for raw, norm in KAGGLE_COLUMN_MAP.items():
        if raw in df.columns and norm not in df.columns:
            df = df.rename(columns={raw: norm})
    return df


def load_raw_data(data_path: str, nrows: Optional[int] = None) -> pd.DataFrame:
    """Load raw data from CSV. Optional nrows for large files (e.g. Kaggle)."""
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path, nrows=nrows)
    elif path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path, nrows=nrows)
    else:
        raise ValueError(f"Unsupported format: {path.suffix}")

    # Allow alternate names used in user-provided schema
    if "purchase_time" in df.columns and "event_time" not in df.columns:
        df = df.rename(columns={"purchase_time": "event_time"})
    if "session_id" not in df.columns and "user_session" in df.columns:
        df = df.rename(columns={"user_session": "session_id"})

    df = _normalize_columns(df)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean e-commerce data: parse event_time, valid price, drop nulls in key columns.
    """
    df = df.copy()

    # Drop fully empty rows
    df = df.dropna(how="all")

    # event_time: Kaggle uses Unix timestamp (ms) or ISO string
    if "event_time" in df.columns:
        col = df["event_time"]
        if pd.api.types.is_numeric_dtype(col):
            df["event_time"] = pd.to_datetime(col, unit="ms", errors="coerce")
        else:
            df["event_time"] = pd.to_datetime(col, errors="coerce")
        df = df[df["event_time"].notna()]

    # price: non-negative numeric
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df[df["price"].notna() & (df["price"] >= 0)]

    # user_id and product_id: drop if missing
    for col in ["user_id", "product_id", "session_id"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df = df[df[col].notna() & (df[col] != "") & (df[col] != "nan")]

    # category: fill unknown if missing
    if "category" in df.columns:
        df["category"] = df["category"].fillna("unknown").astype(str).str.strip()
    else:
        df["category"] = "unknown"

    # event_type: standardize
    if "event_type" in df.columns:
        df["event_type"] = df["event_type"].astype(str).str.strip().str.lower()

    # Drop duplicates
    df = df.drop_duplicates()

    return df.reset_index(drop=True)


def validate_schema(
    df: pd.DataFrame, required_columns: Optional[list] = None
) -> bool:
    """Validate that required columns exist."""
    required = required_columns or REQUIRED_COLUMNS
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return True


def run_engineering_pipeline(
    data_path: str, nrows: Optional[int] = None
) -> pd.DataFrame:
    """
    Full data engineering pipeline: load -> normalize -> clean -> validate.
    Returns clean DataFrame with columns: user_id, product_id, category, price,
    event_time, session_id, and optionally event_type.
    """
    df = load_raw_data(data_path, nrows=nrows)
    df = clean_data(df)
    validate_schema(df)
    return df
