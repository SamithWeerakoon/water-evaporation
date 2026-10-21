"""FastAPI backend for the HydroScope React dashboard.

Usage: python3 api.py   ->  http://localhost:8060
"""
import os
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from analyze import (FORECAST_YEARS, MONTH_NAMES, fit_forecast,
                     load_evaporation, load_rainfall, seasonal_forecast)

BASE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(BASE, "frontend", "dist")

store = {}


def build_payload():
    evap = load_evaporation()
    rain = load_rainfall()

    evap_yearly = evap.groupby("year")["evap_mm"].sum()
    evap_monthly_avg = evap.groupby("month")["evap_mm"].mean()
    rate_monthly_avg = evap.groupby("month")["rate_mm_day"].mean()
    rain_yearly = rain.groupby("year")["rain_mm"].sum(min_count=12)
    rain_monthly_avg = rain.groupby("month")["rain_mm"].mean()

    model, _ = fit_forecast(evap_yearly, 0)
    fc_monthly, fc_yearly, band = seasonal_forecast(evap, "evap_mm", FORECAST_YEARS)

    common = evap_yearly.index.intersection(rain_yearly.dropna().index)
    balance = (evap_yearly[common] - rain_yearly[common]).mean()

    evap_ts = evap.sort_values("date").copy()
    evap_ts["t"] = (evap_ts["year"] - evap_ts["year"].min()) + (evap_ts["month"] - 1) / 12
    from sklearn.linear_model import LinearRegression
    month_model = LinearRegression().fit(evap_ts[["t"]], evap_ts["evap_mm"])
    monthly_trend = month_model.predict(evap_ts[["t"]])
    monthly_band = band / np.sqrt(12)

    fc_ts = fc_monthly.copy()
    fc_ts["date"] = pd.to_datetime(dict(year=fc_ts.year, month=fc_ts.month, day=1))

    history = [
        {"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 2)}
        for d, v in zip(evap_ts["date"], evap_ts["evap_mm"])
    ]
    trend = [
        {"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 2)}
        for d, v in zip(evap_ts["date"], monthly_trend)
    ]
    forecast = [
        {"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 2),
         "lo": round(float(v - monthly_band), 2),
         "hi": round(float(v + monthly_band), 2)}
        for d, v in zip(fc_ts["date"], fc_ts["evap_mm"])
    ]

    pivot = evap.pivot_table(index="year", columns="month", values="evap_mm")

    store["summary"] = {
        "avg_yearly": round(float(evap_yearly.mean()), 1),
        "highest_year": int(evap_yearly.idxmax()),
        "highest_val": round(float(evap_yearly.max()), 1),
        "lowest_year": int(evap_yearly.idxmin()),
        "lowest_val": round(float(evap_yearly.min()), 1),
        "trend_per_year": round(float(model.coef_[0]), 2),
        "water_balance": round(float(balance), 1),
        "forecast_year": int(fc_yearly.index.min()),
        "forecast_val": round(float(fc_yearly.iloc[0]), 1),
        "forecast_band": round(float(band), 1),
        "months": int(len(evap)),
        "start_year": int(evap.year.min()),
        "end_year": int(evap.year.max()),
        "rain_avg": round(float(rain_yearly.dropna().mean()), 1),
    }
    store["series"] = {"historical": history, "trend": trend,
                       "forecast": forecast}
    store["monthly"] = {
        "pattern": [{"month": int(m), "value": round(float(v), 2)}
                    for m, v in evap_monthly_avg.items()],
        "rate": [{"month": int(m), "value": round(float(v), 3)}
                 for m, v in rate_monthly_avg.items()],
        "share": [{"month": int(m), "value": round(float(v), 2)}
                  for m, v in evap_monthly_avg.items()],
        "rainfall": [{"month": int(m), "value": round(float(v), 2)}
                     for m, v in rain_monthly_avg.items()],
    }
    store["heatmap"] = {
        "years": [int(y) for y in pivot.index],
        "months": MONTH_NAMES,
        "values": [[None if pd.isna(v) else round(float(v), 1) for v in row]
                   for row in pivot.values],
    }
    store["comparison"] = [
        {"month": int(m),
         "evaporation": round(float(evap_monthly_avg[m]), 2),
         "rainfall": round(float(rain_monthly_avg.get(m, 0)), 2)}
        for m in range(1, 13)
    ]


@asynccontextmanager
async def lifespan(app):
    build_payload()
    yield


app = FastAPI(title="HydroScope API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/api/summary")
def summary():
    return store["summary"]


@app.get("/api/series")
def series():
    return store["series"]


@app.get("/api/monthly")
def monthly():
    return store["monthly"]


@app.get("/api/heatmap")
def heatmap():
    return store["heatmap"]


@app.get("/api/comparison")
def comparison():
    return store["comparison"]


if os.path.isdir(DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST, "assets")),
              name="assets")

    @app.get("/")
    def index():
        return FileResponse(os.path.join(DIST, "index.html"))

    @app.get("/{path:path}")
    def spa(path: str):
        candidate = os.path.join(DIST, path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(DIST, "index.html"))


if __name__ == "__main__":
    import uvicorn
    print("HydroScope API -> http://localhost:8060")
    uvicorn.run(app, host="0.0.0.0", port=8060, log_level="warning")
