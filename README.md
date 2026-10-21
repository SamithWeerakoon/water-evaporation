# HydroScope – Water Evaporation & Rainfall Analytics

End-to-end analysis of **20 years of monthly evaporation** at Mahailluppallama
(2004–2024) together with **Rajanganaya Scheme rainfall**, visualized in an
interactive dashboard and projected 5 years ahead.

> This README is the project's memory: what it does, how it is built, how to run it,
> and every non-obvious decision/limitation. Read this before making changes.

---

## 1. What this project does

- Loads and cleans the raw Excel records in `data/`.
- Computes annual/monthly evaporation totals, long-term trend, seasonal pattern,
  monthly share, and the annual water balance (evaporation vs rainfall).
- Produces a 5-year monthly forecast with a 95% confidence band.
- Serves an interactive **React + FastAPI** dashboard (light/dark theme).
- Also ships a **legacy Plotly static dashboard** and PNG/CSV report artifacts.

### Headline results (computed from the data)

| Metric | Value |
|--------|-------|
| Mean annual evaporation | **1,263.8 mm/yr** (252 months, 2004–2024) |
| Highest year | **2005 — 1,472.9 mm** |
| Lowest year | **2010 — 1,092.5 mm** |
| Long-term trend | **−0.14 mm/yr** (essentially flat) |
| Peak month | **August — 141.5 mm** (average) |
| Driest month | **December — 61.4 mm** (average) |
| Mean annual rainfall | **1,182.4 mm/yr** (complete years 2004–2018) |
| Water balance | **+81.7 mm/yr** (evaporation − rainfall) |
| Forecast 2025 | **1,262.3 mm ± 101.1 mm** (95% band) |
| Forecast 2025–2029 | ≈ 1,262 mm/yr, stable |

Interpretation: evaporation is high and remarkably stable; rainfall exceeds
evaporation by ~82 mm/yr on average, but rainfall is concentrated in the
Oct–Jan monsoon while evaporation peaks Jun–Sep.

---

## 2. Ports and entry points

| Port | Command | What runs there | Status |
|------|---------|-----------------|--------|
| **8060** | `python3 api.py` | FastAPI API + prebuilt React dashboard | **Current / use this** |
| 8050 | `python3 dashboard.py` | Legacy static Plotly dashboard (`dashboard.html`) | Kept as fallback |
| 5173 | `npm run dev` (in `frontend/`) | Vite dev server with HMR, proxies `/api` → 8060 | Development only |

Key files:

| File | Role |
|------|------|
| `analyze.py` | Single source of truth for data loading, statistics, forecasting, report charts. Import-safe (`main()` guarded). |
| `api.py` | FastAPI app on `0.0.0.0:8060`; builds JSON payloads at startup from `analyze`; serves `frontend/dist`. |
| `dashboard.py` | Legacy Plotly page generator/server on 8050; writes `dashboard.html` (gitignored). |
| `frontend/` | React 18 + Vite + Recharts + lucide-react source and prebuilt `dist/`. |
| `data/*.xlsx` | Raw datasets (committed — do not modify). |
| `output/` | Generated PNG charts and forecast CSVs (gitignored). |

---

## 3. Setup and running

### Local (WSL / Linux)

```bash
git clone https://github.com/SamithWeerakoon/water-evaporation.git
cd water-evaporation
python3 -m pip install --user -r requirements.txt
python3 api.py                 # open http://localhost:8060
```

On Windows, open `http://localhost:8060` in the normal browser;
inside WSL use `explorer.exe 'http://localhost:8060'` (no GUI/browser in WSL).

### VM / server (no Node.js required)

`frontend/dist` is committed, so the VM only needs Python:

```bash
git clone https://github.com/SamithWeerakoon/water-evaporation.git
cd water-evaporation
python3 -m pip install -r requirements.txt
python3 api.py                 # listens on 0.0.0.0:8060
```

Use `setsid nohup python3 api.py < /dev/null > api.log 2>&1 &` to keep it
running after the terminal closes.

### Rebuilding the React frontend

```bash
cd frontend
npm install
npm run build                  # writes frontend/dist  -> commit this
npm run dev                    # optional: HMR on http://localhost:5173
```

> **This machine:** the system Node is v12 (too old for Vite 5). Node 20 lives at
> `~/.local/node/bin`, so prefix commands with
> `export PATH=~/.local/node/bin:$PATH`.
> Python has no venv/pip preinstalled and no sudo; install packages with
> `python3 -m pip install --user`.

### Legacy dashboard

```bash
python3 dashboard.py           # http://localhost:8050/dashboard.html
```

`dashboard.py` regenerates `dashboard.html` on start (auto-refresh every 3 s;
zoom resets after 5 s).

### Report artifacts

```bash
python3 analyze.py             # output/*.png and forecast CSVs
```

---

## 4. Architecture

```
Excel data ──> analyze.py (load, clean, totals, trend, seasonal forecast)
                   │
                   ├──> api.py (FastAPI, :8060)
                   │        └── JSON endpoints ──> frontend/dist (React + Recharts)
                   │
                   ├──> dashboard.py (Plotly, :8050) ──> dashboard.html
                   │
                   └──> analyze.py main() ──> output/*.png, *.csv
```

- The React app has **no build-time data**: everything is fetched from `/api/*`
  on load. `VITE` dev proxies `/api` to `localhost:8060`.
- `api.py` computes payloads once at startup (`lifespan`) into module-level dicts;
  restart it after changing `analyze.py` or `api.py`. Rebuilt static assets are
  picked up without restart.
- SPA fallback: unknown non-API paths return `index.html`; missing `/assets` files 404.

### API reference

| Endpoint | Returns |
|----------|---------|
| `GET /api/summary` | `avg_yearly`, `highest_year`, `highest_val`, `lowest_year`, `lowest_val`, `trend_per_year`, `water_balance`, `forecast_year`, `forecast_val`, `forecast_band`, `months`, `start_year`, `end_year`, `rain_avg` |
| `GET /api/series` | `historical` (252 monthly points `{date, value}`), `trend` (252 fitted points), `forecast` (60 points `{date, value, lo, hi}`) |
| `GET /api/monthly` | `pattern` (12 × `{month, value}` mm totals), `rate` (mm/day), `share` (`{month, value}`), `rainfall` (12 averages) |
| `GET /api/heatmap` | `years` (21), `months` (`Jan`…`Dec`), `values` (21×12, `null` = no data) |
| `GET /api/comparison` | 12 × `{month, evaporation, rainfall}` averages |
| `GET /` and SPA routes | React app |

---

## 5. Data rules (important)

Files in `data/` (names contain spaces — keep them):

1. `Mahailluppallama Monthly Evaporation 2004-2024.xlsx`
   Columns: `StationID`, `station_Name`, `YY`, `Month`, `EVP` (**mm/day**).
2. `Rainfall - Rajanganaya Scheme.xlsx`
   Sheet `MRF & HFR`. Columns 1/3/5/…/23 repeat ID/name/MRF pairs.
   `MRF` = monthly rainfall in **mm**; other columns are highest daily rainfall.
   Some cells are dirty strings such as `".11.5"`; `clean_number()` strips
   non-numeric characters.

Transformations:

- **EVP is a daily rate**, not a monthly total. Monthly total =
  `EVP × days_in_month` (leap years handled with `calendar.monthrange`).
- **6 missing evaporation months** — 2008-12, 2009-01/02/04/07, 2011-07 — are
  filled with that month's long-term average (counts stay at 252 months).
- **Rainfall years with any missing month are excluded** from annual totals:
  2012, 2013, 2015, 2019–2024. Complete years: 2004–2018.
- Dates are normalized to the 1st of each month; duplicate year/month rows dropped.

Never replace real observations with synthetic data. Do not change the
calculation/forecast logic unless explicitly asked — the README results depend on it.

---

## 6. Methods

- **Trend:** linear regression of annual evaporation totals on year
  (`scikit-learn`), reported as mm/yr.
- **Forecast (`fit_forecast`):** linear year trend + additive monthly seasonal
  factors, fitted on monthly totals; 5-year horizon (`FORECAST_YEARS = 5`).
- **Confidence band:** ±1.96 × residual standard deviation (`forecast_band`).
- **Heatmap:** original monthly totals, `null` where missing.
- **Water balance:** mean annual evaporation − mean annual rainfall.

---

## 7. Dashboard design

- Light theme: bg `#F3F7FC`, card `#FFFFFF`, text `#24344D`, muted `#65758B`,
  border `#DFE8F2`, grid `#E6EDF5`.
- Dark theme: bg `#0D1626`, card `#152136`, text `#E8EEF8`, muted `#94A3B8`,
  border `#233249`, grid `#22304A`.
- Accents: blue `#3182CE`, cyan `#18A8D1`, teal `#2CB6A0`, green `#43A66B`,
  gold `#E6AD35`, coral `#E87568`, purple `#8B78D8`.
- Theme is applied as `data-theme` on `<html>` by `src/theme.jsx`, persisted in
  `localStorage` (`hydoscope-theme`); charts read colors via `useTheme()` and
  `chartUtils.js` so both themes stay legible.
- Wave SVG header, gradient card top-borders, Lucide icons, rounded bars,
  tooltips, Legends on every chart, drag-to-pan, scroll zoom, and a 5-second
  auto-reset after zoom/pan.
- Layout: 6 KPI cards (2 rows on desktop), then 7 chart cards; `full` cards span
  both columns. Responsive single column below 1000 px.
- Charts: historical trend, forecast with band, monthly pattern (mm and mm/day),
  share doughnut, year×month heatmap, evaporation-vs-rainfall bars, gradient
  rainfall bars with average reference line.

### Deliberately not implemented

The reference mockup (`data/ight-dashboard-reference.png`, untracked) shows
reservoir storage and rainfall-vs-inflow panels. **No storage/inflow data was
provided**, so those panels are intentionally omitted rather than mocked with
invented numbers.

---

## 8. Repository and workflow

- Remote: <https://github.com/SamithWeerakoon/water-evaporation> (branch `main`).
- Committed: source, `data/*.xlsx`, `frontend/dist`, `requirements.txt`, docs.
- Ignored: `__pycache__/`, `*.pyc`, `dashboard.html`, `output/`, `nohup.out`,
  `frontend/node_modules/`, `frontend/.vite/`.
- `data/ight-dashboard-reference.png` is untracked on purpose (design reference) —
  in `git add -A` workflows, unstage it.
- Only commit/push when asked. Push with a transient token URL, then clean it:
  `git remote set-url origin https://github.com/SamithWeerakoon/water-evaporation.git`.
- No automated tests, linter, or typechecker. Verification = frontend build
  succeeds + API endpoints return 200 + `http://localhost:8060` loads.

See `AGENTS.md` for the condensed agent-facing version of these rules.
