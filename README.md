# Water Evaporation & Rainfall Analysis

Mahailluppallama monthly evaporation (2004–2024) and Rajanganaya Scheme
rainfall analysis with 5-year forecast.

## Data (in `data/`)

| File | Contents |
|------|----------|
| `Mahailluppallama Monthly Evaporation 2004-2024.xlsx` | StationID, station_Name, YY, Month, EVP (mm/day) |
| `Rainfall - Rajanganaya Scheme.xlsx` | Sheet `MRF & HFR`: monthly rainfall (MRF, mm) and highest daily rainfall per month |

**Notes**
- Evaporation EVP is a daily rate (mm/day); the analysis converts it to
  monthly totals using days in each month.
- 6 months are missing in the evaporation record (2008-12, 2009-01/02/04/07,
  2011-07); they are filled with the long-term average for that month.
- Rainfall years with any missing month (2012, 2013, 2015, 2019–2024) are
  excluded from annual totals; complete years are 2004–2018.

## Quick start (local or VM)

```bash
git clone <repo-url> water-evaporation
cd water-evaporation
pip install -r requirements.txt

python3 analyze.py      # report charts + forecast CSVs -> output/
python3 dashboard.py    # generates dashboard.html and serves
                        # http://localhost:8050/dashboard.html
```

Requirements: Python 3.10+. The dashboard page auto-reloads when regenerated.

## Dashboard (`dashboard.py`)

Interactive light-theme web dashboard:
- KPI cards, monthly evaporation trend & 5-year forecast (separate charts)
- Monthly pattern, evaporation-share doughnut, year×month heatmap
- Average monthly evaporation vs rainfall, average monthly rainfall
- Pan by drag, scroll zoom, tooltips follow the cursor,
  charts auto-reset 5 s after interaction stops
- Page auto-refreshes every 3 s when `dashboard.html` is regenerated

## Run (report PNGs)

```bash
python3 analyze.py
```

## Outputs (in `output/`)

| File | Description |
|------|-------------|
| `yearly_totals.png` | Annual evaporation with trend line |
| `monthly_pattern.png` | Monthly totals (mm) and daily rate (mm/day) |
| `monthly_share_pie.png` | Pie chart of each month's share of annual evaporation |
| `yearly_rainfall.png` | Annual rainfall totals |
| `evap_vs_rainfall.png` | Evaporation vs rainfall by year |
| `prediction.png` | Evaporation history + 5-year forecast with 95% range |
| `forecast_monthly.csv` | Month-by-month forecast (2025–2029) |
| `forecast_yearly.csv` | Annual forecast totals |

## Method

- Trend: linear regression on annual totals
- Forecast: linear regression with year trend + monthly seasonal factors
  (scikit-learn); confidence band from residual standard deviation
