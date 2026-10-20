"""Water evaporation & rainfall analysis for Mahailluppallama / Rajanganaya.

Reads:
  data/Mahailluppallama Monthly Evaporation 2004-2024.xlsx  (EVP = mm/day)
  data/Rainfall - Rajanganaya Scheme.xlsx  (sheet 'MRF & HFR', MRF = mm/month)

Outputs charts and forecasts to output/.
"""
import calendar
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "output")
FORECAST_YEARS = 5
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

os.makedirs(OUT, exist_ok=True)


def clean_number(v):
    if pd.isna(v):
        return np.nan
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[^0-9.\-]", "", str(v))
    try:
        return float(s) if s else np.nan
    except ValueError:
        return np.nan


def load_evaporation():
    path = os.path.join(DATA, "Mahailluppallama Monthly Evaporation 2004-2024.xlsx")
    df = pd.read_excel(path)
    df = df.rename(columns={"YY": "year", "Month": "month", "EVP": "rate_mm_day"})
    df["days"] = [calendar.monthrange(y, m)[1] for y, m in zip(df.year, df.month)]
    df["evap_mm"] = df["rate_mm_day"] * df["days"]
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.month, day=1))
    df = df.sort_values("date").drop_duplicates(["year", "month"])

    idx = pd.MultiIndex.from_product(
        [range(df.year.min(), df.year.max() + 1), range(1, 13)],
        names=["year", "month"])
    missing = idx.difference(pd.MultiIndex.from_frame(df[["year", "month"]]))
    print(f"Evaporation: {len(df)} months, {df.year.min()}-{df.year.max()}")
    if len(missing):
        print(f"  Missing months filled with monthly average: {list(missing)}")
        df = df.set_index(["year", "month"]).reindex(idx).reset_index()
        df["days"] = [calendar.monthrange(y, m)[1]
                      for y, m in zip(df.year, df.month)]
        df["rate_mm_day"] = (df["evap_mm"] / df["days"]).where(df["evap_mm"].notna())
        for mo in range(1, 13):
            fill = df.loc[df.month == mo, "evap_mm"].mean()
            mask = (df.month == mo) & df["evap_mm"].isna()
            df.loc[mask, "evap_mm"] = fill
            df.loc[mask, "rate_mm_day"] = fill / df.loc[mask, "days"]
        df["date"] = pd.to_datetime(dict(year=df.year, month=df.month, day=1))
    return df.dropna(subset=["evap_mm"])


def load_rainfall():
    path = os.path.join(DATA, "Rainfall - Rajanganaya Scheme.xlsx")
    raw = pd.read_excel(path, sheet_name="MRF & HFR", header=None)
    rows = []
    for _, r in raw.iloc[7:].iterrows():
        year = clean_number(r[0])
        if year is None or pd.isna(year):
            continue
        year = int(year)
        for i, mo in enumerate(range(1, 13)):
            rows.append({"year": year, "month": mo,
                         "rain_mm": clean_number(r[1 + 2 * i])})
    df = pd.DataFrame(rows)
    total = df.groupby("year")["rain_mm"].count()
    partial = total[total < 12]
    print(f"Rainfall: {df.year.min()}-{df.year.max()}")
    if len(partial):
        print(f"  Years with missing months (excluded from totals): "
              f"{list(partial.index)}")
    return df


def fit_forecast(yearly, n_years):
    X = yearly.index.values.reshape(-1, 1)
    model = LinearRegression().fit(X, yearly.values)
    if n_years <= 0:
        return model, pd.Series(dtype=float)
    future = pd.Series(
        model.predict(np.arange(yearly.index.max() + 1,
                                yearly.index.max() + n_years + 1).reshape(-1, 1)),
        index=range(yearly.index.max() + 1, yearly.index.max() + n_years + 1))
    return model, future


def seasonal_forecast(df, value_col, n_years):
    X = pd.get_dummies(df["month"], prefix="m").astype(float)
    X["trend"] = (df["year"] - df["year"].min()).astype(float)
    model = LinearRegression().fit(X, df[value_col])
    resid_sd = (df[value_col] - model.predict(X)).std()
    last_year = int(df["year"].max())
    rows = []
    for yr in range(last_year + 1, last_year + n_years + 1):
        for mo in range(1, 13):
            feats = pd.get_dummies(pd.Series([mo]), prefix="m").astype(float)
            for col in X.columns.drop("trend"):
                if col not in feats.columns:
                    feats[col] = 0.0
            feats["trend"] = yr - df["year"].min()
            pred = max(model.predict(feats[X.columns])[0], 0.0)
            rows.append({"year": yr, "month": mo, value_col: pred})
    monthly = pd.DataFrame(rows)
    yearly = monthly.groupby("year")[value_col].sum()
    band = resid_sd * np.sqrt(12) * 1.96
    return monthly, yearly, band




def main():
    evap = load_evaporation()
    rain = load_rainfall()

    evap_yearly = evap.groupby("year")["evap_mm"].sum()
    evap_monthly_avg = evap.groupby("month")["evap_mm"].mean()
    rate_monthly_avg = evap.groupby("month")["rate_mm_day"].mean()
    rain_yearly = rain.groupby("year")["rain_mm"].sum(min_count=12)
    rain_monthly_avg = rain.groupby("month")["rain_mm"].mean()

    # Chart 1: yearly evaporation totals
    _, ax = plt.subplots(figsize=(12, 5))
    ax.bar(evap_yearly.index, evap_yearly.values, color="#4C9BE8", label="Actual")
    m, _ = fit_forecast(evap_yearly, 0)
    ax.plot(evap_yearly.index, m.predict(evap_yearly.index.values.reshape(-1, 1)),
            "r--", lw=2, label=f"Trend ({m.coef_[0]:+.1f} mm/year)")
    ax.set_title("Annual Water Evaporation — Mahailluppallama")
    ax.set_xlabel("Year")
    ax.set_ylabel("Evaporation (mm/year)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "yearly_totals.png"), dpi=130)
    plt.close()

    # Chart 2: monthly pattern (mm and mm/day)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].bar(MONTH_NAMES, evap_monthly_avg.values, color="#F2A93B")
    axes[0].set_title("Average Monthly Evaporation (total mm)")
    axes[0].set_ylabel("mm per month")
    axes[0].grid(axis="y", alpha=0.3)
    axes[1].bar(MONTH_NAMES, rate_monthly_avg.values, color="#6BCB77")
    axes[1].set_title("Average Daily Evaporation Rate")
    axes[1].set_ylabel("mm per day")
    axes[1].grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "monthly_pattern.png"), dpi=130)
    plt.close()

    # Chart 3: pie of monthly share
    plt.figure(figsize=(8, 8))
    plt.pie(evap_monthly_avg.values, labels=MONTH_NAMES, autopct="%1.1f%%",
            startangle=90, colors=plt.cm.Set3.colors)
    plt.title("Share of Annual Evaporation by Month")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "monthly_share_pie.png"), dpi=130)
    plt.close()

    # Chart 4: yearly rainfall
    plt.figure(figsize=(12, 5))
    plt.bar(rain_yearly.index, rain_yearly.values, color="#7EB6D9")
    plt.title("Annual Rainfall — Rajanganaya Scheme")
    plt.xlabel("Year")
    plt.ylabel("Rainfall (mm/year)")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "yearly_rainfall.png"), dpi=130)
    plt.close()

    # Chart 5: evaporation vs rainfall
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(evap_yearly.index, evap_yearly.values, color="#4C9BE8",
           label="Evaporation")
    ax.plot(rain_yearly.index, rain_yearly.values, "o-", color="#2E7D32",
            lw=2, label="Rainfall")
    ax.set_title("Evaporation vs Rainfall (annual)")
    ax.set_xlabel("Year")
    ax.set_ylabel("mm")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "evap_vs_rainfall.png"), dpi=130)
    plt.close()

    # Chart 6: evaporation forecast
    model, _ = fit_forecast(evap_yearly, 0)
    fc_monthly, fc_yearly, band = seasonal_forecast(evap, "evap_mm", FORECAST_YEARS)

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(evap_yearly.index, evap_yearly.values, "o-", color="#4C9BE8",
            label="Historical")
    ax.plot(fc_yearly.index, fc_yearly.values, "s--", color="#E05555",
            label=f"Forecast ({FORECAST_YEARS} yr)")
    ax.fill_between(fc_yearly.index, fc_yearly.values - band,
                    fc_yearly.values + band, color="#E05555", alpha=0.15,
                    label="95% range (approx)")
    ax.set_title("Annual Evaporation: History and Forecast")
    ax.set_xlabel("Year")
    ax.set_ylabel("Evaporation (mm/year)")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "prediction.png"), dpi=130)
    plt.close()

    fc_monthly.to_csv(os.path.join(OUT, "forecast_monthly.csv"), index=False)
    fc_yearly.rename("evap_mm").to_csv(os.path.join(OUT, "forecast_yearly.csv"))

    # Summary
    peak = MONTH_NAMES[int(evap_monthly_avg.idxmax()) - 1]
    low = MONTH_NAMES[int(evap_monthly_avg.idxmin()) - 1]
    print("=" * 58)
    print("MAHAILLUPPALLAMA EVAPORATION / RAJANGANAYA RAINFALL SUMMARY")
    print("=" * 58)
    print(f"Evaporation period : {evap.year.min()}-{evap.year.max()} "
          f"(EVP is mm/day, converted to monthly totals)")
    print(f"Yearly average     : {evap_yearly.mean():,.0f} mm")
    print(f"Highest year       : {evap_yearly.idxmax()} ({evap_yearly.max():,.0f} mm)")
    print(f"Lowest year        : {evap_yearly.idxmin()} ({evap_yearly.min():,.0f} mm)")
    print(f"Trend              : {model.coef_[0]:+.1f} mm per year")
    print(f"Peak month         : {peak} ({evap_monthly_avg.max():.1f} mm avg)")
    print(f"Lowest month       : {low} ({evap_monthly_avg.min():.1f} mm avg)")
    print("-" * 58)
    print("EVAPORATION FORECAST (annual totals)")
    for yr, val in fc_yearly.items():
        print(f"  {yr}: {val:,.0f} mm")
    print("-" * 58)
    rw = rain_yearly.dropna()
    print(f"Rainfall period    : {rw.index.min()}-{rw.index.max()} (complete years)")
    print(f"Rainfall average   : {rw.mean():,.0f} mm/year")
    common = evap_yearly.index.intersection(rw.index)
    balance = (evap_yearly[common] - rw[common]).mean()
    print(f"Mean water balance : {balance:+,.0f} mm/year (evap - rain)")
    print("-" * 58)
    print(f"Files written to {OUT}:")
    for f in sorted(os.listdir(OUT)):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
