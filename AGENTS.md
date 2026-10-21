# AGENTS.md

HydroScope: evaporation/rainfall analysis (Python) with two dashboards. WSL repo at
`/mnt/d/water-evaporation` (Windows `D:\water-evaporation`).

## Apps and ports

- `api.py` — FastAPI + prebuilt React app, **port 8060** (current/main dashboard).
- `dashboard.py` — legacy static Plotly page, **port 8050**; regenerates `dashboard.html`.
- `analyze.py` — data loaders, stats, forecasts; also writes PNG/CSV reports to `output/`.
  Import-safe (`main()` runs only under `__main__`); `api.py` imports its functions.

## Environment quirks (this machine)

- System `python3` has **no pip/venv**; install with `python3 -m pip install --user ...`.
  Do not assume `sudo` (requires password).
- System Node is v12 (too old for Vite 5). Node 20 is at `~/.local/node/bin`:
  `export PATH=~/.local/node/bin:$PATH` before any `npm` command.
- Background servers must use `setsid nohup ... < /dev/null &`; plain `nohup` dies when
  the shell call times out.
- No browser in WSL: open URLs with `explorer.exe 'http://localhost:PORT/...'`
  (`xdg-open`/`webbrowser` fail).

## Commands

```bash
python3 api.py                       # serve API + React dist on :8060 (no Node needed)
cd frontend && npm run build         # rebuild React (needed after editing frontend/src)
cd frontend && npm run dev           # Vite dev on :5173, proxies /api -> :8060
python3 analyze.py                   # regenerate output/*.png and forecast CSVs
python3 dashboard.py                 # regenerate legacy dashboard.html and serve :8050
```

- FastAPI mounts `frontend/dist/assets` at startup; rebuilt assets/index are served
  without restarting, but **restart `api.py` after editing `api.py`**.
- `frontend/dist` is committed on purpose so a VM only needs `pip install -r
  requirements.txt` + `python3 api.py`. Rebuild before committing frontend changes.
- No test/lint/typecheck suite exists; verification = build succeeds + endpoints return
  200 (`/api/summary`, `/api/series`, `/api/monthly`, `/api/heatmap`, `/api/comparison`)
  + page loads at `/`.

## Data rules

- Files are Excel with spaces in names under `data/`; do not rename.
- Evaporation `EVP` is **mm/day**; monthly totals = rate × days in month (`analyze.load_evaporation`).
- 6 missing evaporation months are filled with that month's long-term average.
- Rainfall sheet `MRF & HFR`: MRF = monthly mm; dirty values like `".11.5"` are cleaned;
  years with <12 months are excluded from annual totals (complete: 2004–2018).
- Never replace real data with synthetic values. Keep calculations/forecasting unchanged
  unless explicitly asked.

## Frontend conventions

- React 18 + Vite + Recharts + `lucide-react`; no Tailwind, plain CSS in
  `src/styles.css` driven by CSS vars on `:root` / `[data-theme="dark"]`.
- Theme state lives in `src/theme.jsx`; charts read colors via `useTheme()` and
  `chartUtils.js` helpers. Keep both themes working when changing colors.
- `to_html`/`dashboard.html` is gitignored generated output. `output/` too.
- `data/ight-dashboard-reference.png` is an untracked design reference — after
  `git add -A`, unstage it (don't commit it).

## Git

- Remote: `github.com/SamithWeerakoon/water-evaporation` (branch `main`).
- Only commit/push when the user asks. Push with a transient token URL, then reset:
  `git remote set-url origin https://github.com/SamithWeerakoon/water-evaporation.git`.
