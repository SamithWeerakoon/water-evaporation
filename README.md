# HydroScope – Water Evaporation & Rainfall Analytics

Mahailluppallama monthly evaporation (2004–2024) and Rajanganaya Scheme
rainfall analysis with 5-year forecast.

Two frontends are included:

| App | Stack | Entry |
|-----|-------|-------|
| **React dashboard (current)** | React 18 + Vite + Recharts + FastAPI | `api.py` + `frontend/` |
| Static dashboard | Plotly-generated HTML | `dashboard.py` |

## Quick start (local or VM)

```bash
git clone <repo-url> water-evaporation
cd water-evaporation
python3 -m pip install -r requirements.txt

python3 api.py          # http://localhost:8060
```

The React app is prebuilt in `frontend/dist`, so no Node.js is needed on the VM.

### Rebuilding the frontend (only if you change React code)

```bash
cd frontend
npm install
npm run build           # outputs frontend/dist
```

For development with hot reload: `npm run dev` (http://localhost:5173,
proxying `/api` to port 8060) while `python3 api.py` runs.

## Report charts (PNG/CSV)

```bash
python3 analyze.py      # -> output/
```

## React dashboard features

- Professional light theme + dark mode toggle (sun/moon, remembered in localStorage)
- Wave SVG header, gradient accents, analytical color palette
- KPI cards with Lucide icons: average, highest/lowest year, trend,
  water balance, next-year forecast
- Historical monthly evaporation + trend, separate 5-year forecast with 95% band
- Monthly pattern (mm and mm/day), evaporation-share doughnut, year×month heatmap
- Average monthly evaporation vs rainfall, gradient rainfall chart
- Responsive layout, chart tooltips, drag-to-pan, scroll zoom,
  5-second auto-reset after zoom/pan

## API

| Endpoint | Contents |
|----------|----------|
| `/api/summary` | KPI values, forecast year/band |
| `/api/series` | historical, trend, forecast (monthly) |
| `/api/monthly` | monthly averages, rates, share, rainfall |
| `/api/heatmap` | year × month matrix |
| `/api/comparison` | average monthly evaporation vs rainfall |

## Data (in `data/`)

| File | Contents |
|------|----------|
| `Mahailluppallama Monthly Evaporation 2004-2024.xlsx` | StationID, station_Name, YY, Month, EVP (mm/day) |
| `Rainfall - Rajanganaya Scheme.xlsx` | Sheet `MRF & HFR`: monthly rainfall (MRF, mm) and highest daily rainfall |

**Notes**
- Evaporation EVP is a daily rate (mm/day); converted to monthly totals using
  days in each month.
- 6 months are missing in the evaporation record (2008-12, 2009-01/02/04/07,
  2011-07); filled with the long-term average for that month.
- Rainfall years with any missing month (2012, 2013, 2015, 2019–2024) are
  excluded from annual totals; complete years are 2004–2018.

## Method

- Trend: linear regression on annual totals
- Forecast: linear regression with year trend + monthly seasonal factors
  (scikit-learn); confidence band from residual standard deviation
