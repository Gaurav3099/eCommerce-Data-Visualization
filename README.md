# E-commerce Data Visualization Project

Data **engineering**, **churning**, and **visualization** for the [E-commerce Customer Behavior Dataset (Kaggle)](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store). Built for realistic business analytics.

## Dataset

- **Source:** [eCommerce behavior data from multi category store](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store)
- **Fields:** `event_time`, `event_type`, `product_id`, `category_id` / `category_code`, `price`, `user_id`, `user_session`
- **Event types:** `view`, `cart`, `remove_from_cart`, `purchase`

### Getting the data

1. Install [Kaggle CLI](https://github.com/Kaggle/kaggle-api) and set up API credentials.
2. Download (e.g. one month):
   ```bash
   kaggle datasets download -d mkechinov/ecommerce-behavior-data-from-multi-category-store
   unzip ecommerce-behavior-data-from-multi-category-store.zip -d data/raw/
   ```
3. Or download manually from the Kaggle page and place any CSV (e.g. `2019-Oct.csv`) in `data/raw/`. Rename to `ecommerce_sample.csv` or select it in the dashboard.

A small **sample CSV** is included at `data/raw/ecommerce_sample.csv` so you can run the pipeline and dashboard without downloading the full dataset.

## Project structure

```
Data Visualization/
├── data/
│   └── raw/
│       └── ecommerce_sample.csv   # Sample or your Kaggle CSV
├── src/
│   ├── data_engineering.py       # Load, normalize, clean, validate
│   ├── data_churning.py          # Revenue, funnel, segments, heatmaps, cohorts
│   └── visualizations.py         # Static + Plotly charts
├── api/
│   └── main.py                   # FastAPI backend for React
├── frontend/                     # React (Vite + TypeScript + Recharts)
├── outputs/
│   └── charts/                   # Generated PNGs
├── run_pipeline.py               # Batch: engineering → churning → static charts
├── dashboard.py                  # Streamlit dashboard (Python)
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv venv
# Windows:
venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Run static pipeline

Generates PNGs in `outputs/charts/`:

```bash
python run_pipeline.py
```

**Charts produced:**

- **Revenue trends** – revenue over time (monthly)
- **Conversion funnel** – view → cart → purchase (users/sessions)
- **Customer segmentation** – High Value, Frequent, Regular, Low Activity
- **Top categories** – revenue by category
- **Purchase behavior heatmaps** – hour × day of week; category × month
- **Cohort retention** – retention by first-purchase month

## React frontend (recommended)

Web dashboard with the same analytics, category filter, and interactive charts:

**Terminal 1 – API (from project root):**
```bash
venv\Scripts\Activate.ps1   # or source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 – React app:**
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The app proxies `/api` to the backend.

- **Tabs:** Revenue trends, Conversion funnel, Customer segmentation, Top categories, Purchase heatmaps, Cohort retention
- **Header:** Category filter (multi-select), Refresh
- **Charts:** Recharts (line, bar, heatmap tables)

## Streamlit dashboard (Python)

Alternative interactive dashboard:

```bash
streamlit run dashboard.py
```

- **Tabs:** Same as above
- **Sidebar:** Dataset choice, max rows, **category filter**
- **Charts:** Plotly (zoom, hover)

## Data engineering

- **Load:** CSV (and optional column mapping from Kaggle schema).
- **Normalize:** `event_time`, `user_session` → `session_id`, `category_code` / `category_id` → `category`.
- **Clean:** Parse `event_time`, valid `price`, drop nulls in `user_id` / `product_id` / `session_id`, standardize `event_type`.
- **Validate:** Required columns present.

## Data churning

- **Revenue:** From `price` on `event_type == "purchase"` (or all rows if no `event_type`).
- **Funnel:** Unique users/sessions per stage (view, cart, purchase).
- **Segments:** Revenue and order count per user → High Value / Frequent / Regular / Low Activity.
- **Top categories:** Revenue and event counts by category.
- **Heatmaps:** Events/purchases by hour × day of week; revenue by category × month.
- **Cohort retention:** First-purchase month → share of users with a purchase in later months.

## UI ideas (implemented)

- **Interactive funnel charts** – Plotly funnel in dashboard
- **Cohort retention charts** – Heatmap in dashboard + static PNG
- **Category filters** – Sidebar multiselect to filter all visualizations by category

## Requirements

- Python 3.9+
- pandas, matplotlib, seaborn, plotly, numpy, openpyxl, streamlit (see `requirements.txt`)
