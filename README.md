# E-Commerce Sales & Customer Analysis Dashboard

An interactive, four-page analytics dashboard built with **Python, Streamlit and Plotly** for the
industrial training project **E-commerce Sales and Customer Analysis**. Every number is computed
from `data/Ecommerce_sales.csv`; no categories, currencies or business results are invented.

## Pages

| Page | What it covers |
| --- | --- |
| **Sales Performance** | Revenue, purchases, sessions, conversion rate, AOV, monthly trend, category revenue, payment-method analysis |
| **Customer Analysis** | Unique/buying/repeat customers, repeat rate, top 10 customers, purchase-frequency segments, ratings (purchasers only) |
| **Customer Behaviour** | Add-to-cart sessions, cart abandonment, shopping funnel, device performance, time on site, pages viewed |
| **Marketing & Product** | Channel revenue and purchases, category performance, discount analysis, product ratings, units sold by category |

All four pages share the same global filters, dark navy theme, KPI cards and chart styling.

## Project structure

```
dashboard/
├── app.py                  # Entry point, sidebar navigation, global filters
├── data_loader.py          # Loading, validation, filtering, KPI and chart-data helpers
├── theme.py                # Navy Plotly template and palette
├── components.py           # KPI cards, page headers, insight boxes, icons
├── assets/
│   ├── styles.css          # Premium dark UI styling
│   └── favicon.svg         # Browser favicon
├── views/
│   ├── sales.py
│   ├── customers.py
│   ├── behaviour.py
│   └── marketing.py
├── requirements.txt
└── README.md
```

The notebook and SQL files outside this folder are not modified.

## Run the dashboard

From the **project root** (`Ecommerce_sales_customer_analysis`):

```powershell
# 1. Create and activate a virtual environment (skip if it already exists)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
python -m pip install -r dashboard\requirements.txt

# 3. Launch the dashboard
python -m streamlit run dashboard\app.py
```

Streamlit opens `http://localhost:8501` automatically. To use a specific port:

```powershell
python -m streamlit run dashboard\app.py --server.port 8501
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Alternatively, call the virtual environment Python directly without activating:

```powershell
.\venv\Scripts\python.exe -m streamlit run dashboard\app.py
```

The dataset path is resolved automatically as `<project>/data/Ecommerce_sales.csv`.
If the file is missing, the app shows a clear error instead of failing silently.

## KPI definitions

| KPI | Formula |
| --- | --- |
| Total Revenue | `SUM(revenue)` |
| Total Purchases | `SUM(purchased = 1)` — one row is one purchase session |
| Total Sessions | row count |
| Conversion Rate | `purchases / sessions × 100` |
| Average Order Value | `revenue / purchases` |
| Buying Customers | distinct `customer_id` with at least one purchase |
| Repeat Customers | buying customers with `>= 2` purchase sessions |
| Repeat Customer Rate | `repeat customers / buying customers × 100` |
| Cart Abandonment Rate | `cart_abandoned / added_to_cart × 100` |
| Average Time on Site | mean `time_on_site_sec`, displayed in minutes |
| Average Pages Viewed | mean `pages_viewed` |

All divisions are guarded against zero. Invalid dates are excluded from time-based views and the
count is reported in the sidebar under **Data quality notes**.

## Data notes

- **One row = one website session**, not one order line.
- Numeric code columns (`device_type`, `user_type`, `marketing_channel`, `product_category`,
  `payment_method`, `location`, `visit_season`) have **no data dictionary**. For the five
  business columns the dashboard shows readable names (e.g. "Mobile*", "Email*") that are
  **inferred from common e-commerce conventions**, marked with a trailing `*`. They are not
  official values. `location` and `visit_season` remain as raw codes. To use real names,
  replace `INFERRED_CODE_LABELS` in `dashboard/data_loader.py`.
- Revenue is displayed in the dataset's native units because no currency is declared.
- Non-purchasing sessions all have `rating = 4`, so rating analysis uses purchasing sessions only.
- `review_text` is a numeric value (0–10), not real review text, and is not presented as text.
- Results show **associations**, not proof of cause and effect.
- The dataset covers **1 January 2024 to 30 December 2024**.

## Filters

The sidebar contains:

- Start and end date
- Product category
- Marketing channel
- Device type
- User type
- Payment method
- **Reset filters** and **Download filtered data**

Empty multi-select values mean "all". Every KPI, chart and table recalculates on the filtered data.

## Testing performed

- `python -m compileall dashboard`
- Streamlit `AppTest` rendered all four pages with no exceptions
- Filter interaction test (category filter) passed
- Headless server health check returned HTTP `200 ok`

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError: streamlit` | Run `python -m pip install -r dashboard\requirements.txt` in the active environment |
| Dataset not found | Keep `Ecommerce_sales.csv` inside `data/` at the project root |
| Port already in use | Add `--server.port 8502` |
| Blank charts after filtering | Widen the date range or clear the code filters; the sidebar shows the selected row count |
