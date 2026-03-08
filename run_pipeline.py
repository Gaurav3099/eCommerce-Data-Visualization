"""
Uses E-commerce Customer Behavior dataset (Kaggle) or sample data.
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.data_engineering import run_engineering_pipeline
from src.data_churning import run_churning_pipeline
from src.visualizations import generate_all_charts


def main():
    data_path = project_root / "data" / "raw" / "2019-Oct.csv"
    output_dir = project_root / "outputs" / "charts"

    if not data_path.exists():
        print(f"Data not found: {data_path}")
        print("Add ecommerce_sample.csv or download from Kaggle (see README).")
        return

    print("Step 1: Data Engineering (load, clean, validate)...")
    df_clean = run_engineering_pipeline(str(data_path))
    print(f"  Clean rows: {len(df_clean)}")

    print("Step 2: Data Churning (revenue, funnel, segments, categories, heatmaps, cohorts)...")
    churned = run_churning_pipeline(df_clean)
    print("  Done.")

    print("Step 3: Generating static charts...")
    paths = generate_all_charts(churned, output_dir=str(output_dir))
    for p in paths:
        print(f"  Saved: {p}")
    print(f"\nDone. {len(paths)} chart(s) saved to {output_dir}")


if __name__ == "__main__":
    main()
