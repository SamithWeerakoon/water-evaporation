"""HydroScope — light water-analytics dashboard with waves, gradients,
and analytical colors.

Usage: python3 dashboard.py
Then open http://localhost:8050/dashboard.html
"""
import json
import os
import webbrowser

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression

from analyze import (FORECAST_YEARS, MONTH_NAMES, fit_forecast,
                     load_evaporation, load_rainfall, seasonal_forecast)

BASE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(BASE, "dashboard.html")
PORT = 8050

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

BG = "#F3F7FC"
BLUE, CYAN, TEAL = "#3182CE", "#18A8D1", "#2CB6A0"
GREEN, GOLD = "#43A66B", "#E6AD35"
CORAL, PURPLE = "#E87568", "#8B78D8"
TEXT, MUTED = "#24344D", "#65758B"
GRID, BORDER = "#E6EDF5", "#DFE8F2"

LIGHT = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(color=TEXT, family="Inter, Segoe UI, sans-serif", size=13),
    margin=dict(l=52, r=24, t=64, b=44),
    height=400,
    legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.14,
                font=dict(size=12)),
    xaxis=dict(gridcolor=GRID, zeroline=False, linecolor=BORDER,
               tickfont=dict(color=MUTED), title_font=dict(color=MUTED)),
    yaxis=dict(gridcolor=GRID, zeroline=False, linecolor=BORDER,
               tickfont=dict(color=MUTED), title_font=dict(color=MUTED)),
    hoverlabel=dict(bgcolor="#FFFFFF", font_size=13, font_color=TEXT,
                    bordercolor=BORDER),
    hovermode="closest",
    dragmode="pan",
)

TITLE_FONT = dict(font=dict(size=16, color=TEXT), x=0.01, xanchor="left")


def themed(title):
    return {**LIGHT, "title": {**TITLE_FONT, "text": title}}


evap_ts = evap.sort_values("date").copy()
evap_ts["t"] = (evap_ts["year"] - evap_ts["year"].min()) + (evap_ts["month"] - 1) / 12
month_model = LinearRegression().fit(evap_ts[["t"]], evap_ts["evap_mm"])
monthly_trend = month_model.predict(evap_ts[["t"]])

fc_ts = fc_monthly.copy()
fc_ts["date"] = pd.to_datetime(dict(year=fc_ts.year, month=fc_ts.month, day=1))
monthly_band = band / np.sqrt(12)

y_max = max(evap_ts["evap_mm"].max(), (fc_ts["evap_mm"] + monthly_band).max()) * 1.08

f1 = go.Figure()
f1.add_trace(go.Bar(x=evap_ts["date"], y=evap_ts["evap_mm"], name="Historical",
                    marker=dict(color=BLUE, opacity=0.88, cornerradius=4),
                    hovertemplate="%{x|%b %Y}: %{y:.1f} mm<extra></extra>"))
f1.add_trace(go.Scatter(x=evap_ts["date"], y=monthly_trend, name="Trend",
                        mode="lines",
                        line=dict(color=GREEN, width=2, dash="dash")))
f1.update_layout(**{**themed("Evaporation Trend — Historical 2004–2024 (mm)"),
                    "yaxis": dict(LIGHT["yaxis"], range=[0, y_max], title="mm")})
f1.update_xaxes(title_text="Month", tickformat="%b %Y", dtick="M3",
                range=[evap_ts["date"].min(), evap_ts["date"].max()],
                gridcolor=GRID, zeroline=False)

f1b = go.Figure()
f1b.add_trace(go.Bar(x=fc_ts["date"], y=fc_ts["evap_mm"], name="Forecast",
                     marker=dict(color=GOLD, opacity=0.9, cornerradius=6),
                     hovertemplate="%{x|%b %Y}: %{y:.1f} mm<extra></extra>"))
f1b.add_trace(go.Scatter(x=fc_ts["date"], y=fc_ts["evap_mm"], name="Forecast line",
                         mode="lines",
                         line=dict(color=CORAL, width=2.5, dash="dot")))
f1b.add_trace(go.Scatter(
    x=list(fc_ts["date"]) + list(fc_ts["date"])[::-1],
    y=list(fc_ts["evap_mm"] + monthly_band) + list((fc_ts["evap_mm"] - monthly_band))[::-1],
    fill="toself", fillcolor="rgba(232,117,104,0.16)",
    line=dict(width=0), name="95% range", hoverinfo="skip", showlegend=True))
f1b.update_layout(**{**themed(
    f"Evaporation Forecast {fc_ts['year'].min()}–{fc_ts['year'].max()} (mm)"),
    "yaxis": dict(LIGHT["yaxis"], range=[0, y_max], title="mm")})
f1b.update_xaxes(title_text="Month", tickformat="%b %Y", dtick="M1",
                 range=[fc_ts["date"].min(), fc_ts["date"].max()],
                 gridcolor=GRID, zeroline=False)

f2 = make_subplots(rows=1, cols=2, subplot_titles=("Total mm / month",
                                                   "Daily rate mm/day"))
f2.add_trace(go.Bar(x=MONTH_NAMES, y=evap_monthly_avg.values, name="mm/month",
                    marker=dict(color=CYAN, cornerradius=6),
                    hovertemplate="%{x}: %{y:.1f} mm<extra></extra>"),
             row=1, col=1)
f2.add_trace(go.Bar(x=MONTH_NAMES, y=rate_monthly_avg.values, name="mm/day",
                    marker=dict(color=TEAL, cornerradius=6),
                    hovertemplate="%{x}: %{y:.2f} mm/day<extra></extra>"),
             row=1, col=2)
f2.update_layout(title="Monthly Evaporation Pattern", **LIGHT)
for c in (1, 2):
    f2.update_xaxes(gridcolor=GRID, zeroline=False, row=1, col=c)
    f2.update_yaxes(gridcolor=GRID, zeroline=False, row=1, col=c)

ANALYTICAL = [BLUE, CYAN, TEAL, GREEN, "#66B96B", GOLD, "#E4A93F",
              "#E58A52", CORAL, PURPLE, "#A08BE0", "#5B9BD5"]
peak_i = int(evap_monthly_avg.values.argmax())
f3 = go.Figure(go.Pie(
    labels=MONTH_NAMES, values=evap_monthly_avg.values,
    hole=0.64, sort=False,
    pull=[0.06 if i == peak_i else 0.02 for i in range(12)],
    textinfo="percent", textposition="inside",
    textfont=dict(size=11, color="#FFFFFF", family="Inter"),
    marker=dict(colors=ANALYTICAL,
                line=dict(color="#FFFFFF", width=3)),
    hovertemplate="%{label}<br>%{value:.1f} mm (%{percent})<extra></extra>",
    legendgroup="months", showlegend=True))
avg_annual = evap_yearly.mean()
PIE_PULLS = json.dumps([0.06 if i == peak_i else 0.02 for i in range(12)])
f3.add_annotation(
    text=f"<b>{avg_annual:,.0f}</b><br><span style='font-size:11px;color:#65758B'>mm / year avg</span>",
    x=0.5, y=0.5, showarrow=False, font=dict(size=24, color=TEXT))
f3.update_layout(title="Evaporation Share by Month", **LIGHT)

pivot = evap.pivot_table(index="year", columns="month", values="evap_mm")
f4 = go.Figure(go.Heatmap(
    z=pivot.values, x=MONTH_NAMES, y=pivot.index,
    colorscale=[[0, "#EAF6FB"], [0.35, "#9CD8EC"],
                [0.7, "#37A6D1"], [1, "#244F88"]],
    colorbar=dict(title="mm", thickness=14, tickfont=dict(color=MUTED)),
    xgap=2, ygap=2,
    hovertemplate="Year %{y}<br>%{x}: %{z:.1f} mm<extra></extra>"))
f4.update_layout(title="Monthly Evaporation Heatmap (mm)",
                 **{**LIGHT, "height": 480})
f4.update_xaxes(gridcolor="#FFFFFF", zeroline=False)
f4.update_yaxes(gridcolor="#FFFFFF", zeroline=False, dtick=1)

f5 = go.Figure()
f5.add_trace(go.Bar(x=MONTH_NAMES, y=evap_monthly_avg.values,
                    name="Evaporation",
                    marker=dict(color=BLUE, cornerradius=6),
                    text=[f"{v:.0f}" for v in evap_monthly_avg.values],
                    textposition="outside", textfont=dict(size=10, color=MUTED),
                    hovertemplate="%{x}: %{y:.1f} mm<extra></extra>"))
f5.add_trace(go.Bar(x=MONTH_NAMES, y=rain_monthly_avg.values, name="Rainfall",
                    marker=dict(color=TEAL, cornerradius=6),
                    text=[f"{v:.0f}" for v in rain_monthly_avg.values],
                    textposition="outside", textfont=dict(size=10, color=MUTED),
                    hovertemplate="%{x}: %{y:.1f} mm<extra></extra>"))
f5.update_layout(**{**themed("Average Monthly Evaporation vs Rainfall (mm)"),
                    "barmode": "group", "bargap": 0.28, "bargroupgap": 0.08,
                    "legend": dict(LIGHT["legend"], y=1.16),
                    "yaxis": dict(LIGHT["yaxis"],
                                  range=[0, max(evap_monthly_avg.max(),
                                                rain_monthly_avg.max()) * 1.16],
                                  title="mm")})


def _lerp(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a[i] + (b[i] - a[i]) * t):02X}" for i in range(3))


rv = rain_monthly_avg.values
rmin, rmax = rv.min(), rv.max()
rain_colors = [_lerp("#BDE7F4", BLUE, (v - rmin) / (rmax - rmin)) for v in rv]
rain_avg = rv.mean()

f6 = go.Figure()
f6.add_trace(go.Bar(
    x=MONTH_NAMES, y=rv, name="Rainfall",
    marker=dict(color=rain_colors, cornerradius=8),
    text=[f"{v:.0f}" for v in rv], textposition="outside",
    textfont=dict(size=11, color=MUTED),
    hovertemplate="%{x}: %{y:.1f} mm<extra></extra>"))
f6.add_trace(go.Scatter(x=[MONTH_NAMES[0], MONTH_NAMES[-1]],
                        y=[rain_avg, rain_avg], name=f"Average {rain_avg:.0f} mm",
                        mode="lines+text",
                        line=dict(color=GOLD, width=2, dash="dash"),
                        text=[f"avg {rain_avg:.0f}", ""],
                        textposition="top right",
                        textfont=dict(size=11, color=GOLD),
                        hoverinfo="skip"))
f6.update_layout(**{**themed("Average Monthly Rainfall (mm)"),
                    "bargap": 0.35, "showlegend": False,
                    "yaxis": dict(LIGHT["yaxis"],
                                  range=[0, rmax * 1.18], title="mm")})
f6.update_xaxes(gridcolor="rgba(0,0,0,0)")


def to_html(fig, div_id=None):
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id=div_id,
                       config={"displayModeBar": True, "displaylogo": False,
                               "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                               "scrollZoom": True, "responsive": True})


def kpi(icon, label, value, sub, color):
    return f"""
    <div class="kpi">
      <div class="kpi-top">
        <span class="kpi-icon" style="background:{color}1F;color:{color};">{icon}</span>
        <span class="kpi-label">{label}</span>
      </div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""


kpis = "".join([
    kpi("◔", "Average Evaporation", f"{evap_yearly.mean():,.0f} mm/yr",
        f"{len(evap)} months · 2004–2024", BLUE),
    kpi("▲", "Highest Year", f"{evap_yearly.idxmax()}",
        f"{evap_yearly.max():,.0f} mm", GREEN),
    kpi("▼", "Lowest Year", f"{evap_yearly.idxmin()}",
        f"{evap_yearly.min():,.0f} mm", CORAL),
    kpi("~", "Long-term Trend", f"{model.coef_[0]:+.1f} mm/yr",
        "linear regression", PURPLE),
    kpi("⚖", "Water Balance", f"{balance:+,.0f} mm/yr",
        "evaporation − rainfall", GOLD),
    kpi("◎", f"Forecast {fc_yearly.index.min()}", f"{fc_yearly.iloc[0]:,.0f} mm",
        f"±{band:,.0f} mm (95% range)", TEAL),
])

WAVES = """
<svg class="waves" viewBox="0 0 1440 70" preserveAspectRatio="none">
  <path class="w1" d="M0,32 C240,64 480,0 720,20 C960,40 1200,64 1440,28 L1440,70 L0,70 Z"/>
  <path class="w2" d="M0,44 C240,20 480,64 720,44 C960,24 1200,12 1440,44 L1440,70 L0,70 Z"/>
  <path class="w3" d="M0,58 C300,42 600,70 900,56 C1140,46 1320,60 1440,52 L1440,70 L0,70 Z"/>
</svg>"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HydroScope – Water Analytics</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  :root {{
    --bg: {BG}; --card: #FFFFFF;
    --blue: {BLUE}; --cyan: {CYAN}; --teal: {TEAL};
    --green: {GREEN}; --gold: {GOLD}; --coral: {CORAL}; --purple: {PURPLE};
    --text: {TEXT}; --muted: {MUTED};
    --border: {BORDER}; --grid: {GRID};
    --shadow: rgba(36,52,77,.06);
  }}
  [data-theme="dark"] {{
    --bg: #0D1626; --card: #152136;
    --text: #E8EEF8; --muted: #94A3B8;
    --border: #233249; --grid: #22304A;
    --shadow: rgba(0,0,0,.35);
  }}
  * {{ box-sizing:border-box; margin:0; }}
  body {{
    font-family:'Inter',system-ui,sans-serif; color:var(--text);
    background:var(--bg); min-height:100vh;
  }}
  header {{
    position:relative; overflow:hidden;
    background:linear-gradient(115deg,#244F88 0%,#3182CE 45%,#18A8D1 100%);
    color:#fff; padding:20px 32px 34px;
    display:flex; align-items:center; gap:14px;
    transition:background .35s ease;
  }}
  [data-theme="dark"] header {{
    background:linear-gradient(115deg,#0B1526 0%,#123B66 55%,#0E6E8E 100%);
  }}
  .logo {{
    width:44px; height:44px; border-radius:12px; flex:none;
    background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.30);
    display:flex; align-items:center; justify-content:center;
    font-size:21px; font-weight:600;
    box-shadow:0 4px 18px rgba(0,0,0,.15);
  }}
  header h1 {{ font-size:21px; font-weight:700; letter-spacing:.2px; }}
  header .sub {{ font-size:12.5px; opacity:.9; margin-top:3px; }}
  .waves {{ position:absolute; left:0; right:0; bottom:-1px; width:100%;
            height:56px; pointer-events:none; }}
  .waves .w1 {{ fill:rgba(255,255,255,0.10); }}
  .waves .w2 {{ fill:rgba(24,168,209,0.28); }}
  .waves .w3 {{ fill:rgba(243,247,252,0.85); }}
  [data-theme="dark"] .waves .w1 {{ fill:rgba(255,255,255,0.05); }}
  [data-theme="dark"] .waves .w2 {{ fill:rgba(24,168,209,0.20); }}
  [data-theme="dark"] .waves .w3 {{ fill:rgba(13,22,38,0.92); }}
  .theme-btn {{
    margin-left:auto; width:40px; height:40px; border-radius:11px;
    background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.30);
    color:#fff; cursor:pointer; display:flex; align-items:center;
    justify-content:center; flex:none; transition:background .2s, transform .2s;
  }}
  .theme-btn:hover {{ background:rgba(255,255,255,.28); transform:rotate(12deg); }}
  .theme-btn svg {{ width:20px; height:20px; }}
  .content {{ max-width:1500px; margin:0 auto; padding:22px 32px 36px; }}
  .kpi-grid {{
    display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
    gap:14px; margin-bottom:18px;
  }}
  .kpi, .card {{
    background:var(--card); border:1px solid var(--border);
    border-radius:14px;
    box-shadow:0 2px 10px var(--shadow);
  }}
  .kpi {{ padding:14px 16px; transition:transform .2s, box-shadow .2s;
          position:relative; overflow:hidden; }}
  .kpi::before {{
    content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,var(--blue),var(--cyan),var(--teal));
    opacity:.85;
  }}
  .kpi:hover {{ transform:translateY(-2px);
    box-shadow:0 8px 22px rgba(49,130,206,.16); }}
  .kpi-top {{ display:flex; align-items:center; gap:8px; }}
  .kpi-icon {{
    width:28px; height:28px; border-radius:8px; flex:none;
    display:flex; align-items:center; justify-content:center; font-size:14px;
  }}
  .kpi-label {{ font-size:12px; font-weight:600; color:var(--muted);
                text-transform:uppercase; letter-spacing:.4px; }}
  .kpi-value {{ font-size:22px; font-weight:700; color:var(--text);
                margin-top:8px; }}
  .kpi-sub {{ font-size:11.5px; color:var(--muted); margin-top:3px; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  .card {{ padding:14px 12px 4px; position:relative; overflow:hidden; }}
  .card::after {{
    content:""; position:absolute; top:0; left:0; width:100%; height:3px;
    background:linear-gradient(90deg,var(--cyan),var(--teal),var(--green));
    opacity:.7;
  }}
  .full {{ grid-column:1 / -1; }}
  .card:hover {{ box-shadow:0 10px 28px rgba(49,130,206,.16);
                 border-color:#CFE1F5; }}
  .pie-card {{ transition:transform .2s, box-shadow .2s; }}
  .pie-card:hover {{ transform:translateY(-4px); }}
  footer {{ text-align:center; color:var(--muted); font-size:12px;
            padding:22px 0 8px; }}
  @media (max-width:1000px) {{
    .grid {{ grid-template-columns:1fr; }}
    .content {{ padding:16px; }}
    header {{ padding:16px 16px 30px; }}
  }}
</style>
<script>
(function () {{
  var stamp = null;
  setInterval(function () {{
    fetch(window.location.pathname, {{ method: "HEAD", cache: "no-store" }})
      .then(function (r) {{ return r.headers.get("last-modified"); }})
      .then(function (lm) {{
        if (lm && stamp && lm !== stamp) location.reload();
        if (lm && !stamp) stamp = lm;
      }})
      .catch(function () {{}});
  }}, 3000);
}})();
</script>
</head>
<body>
<header>
  <div class="logo">≈</div>
  <div>
    <h1>HydroScope – Water Analytics</h1>
    <div class="sub">Mahailluppallama evaporation · 2004–2024 historical analysis ·
      Rajanganaya rainfall · {FORECAST_YEARS}-year forecast</div>
  </div>
  <button id="themeToggle" class="theme-btn" title="Toggle dark / light mode"
          aria-label="Toggle dark or light mode">
    <svg id="iconMoon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
         stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
    <svg id="iconSun" viewBox="0 0 24 24" fill="none" stroke="currentColor"
         stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
         style="display:none">
      <circle cx="12" cy="12" r="4"/>
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
    </svg>
  </button>
  {WAVES}
</header>
<div class="content">
  <div class="kpi-grid">{kpis}</div>
  <div class="grid">
    <div class="card full">{to_html(f1)}</div>
    <div class="card full">{to_html(f1b)}</div>
    <div class="card">{to_html(f2)}</div>
    <div class="card pie-card">{to_html(f3, div_id="pieChart")}</div>
    <div class="card full">{to_html(f4)}</div>
    <div class="card">{to_html(f5)}</div>
    <div class="card">{to_html(f6)}</div>
  </div>
  <footer>HydroScope · generated by dashboard.py · data: data/*.xlsx</footer>
</div>
<script>
(function () {{
  var LIGHT_C = {{card:"#FFFFFF", text:"{TEXT}", muted:"{MUTED}",
                  grid:"{GRID}", border:"{BORDER}"}};
  var DARK_C  = {{card:"#152136", text:"#E8EEF8", muted:"#94A3B8",
                  grid:"#22304A", border:"#2A3B55"}};
  function applyChartTheme(isDark) {{
    var c = isDark ? DARK_C : LIGHT_C;
    document.querySelectorAll(".js-plotly-plot").forEach(function (fig) {{
      var upd = {{
        "paper_bgcolor": c.card, "plot_bgcolor": c.card,
        "font.color": c.text,
        "legend.font.color": c.muted,
        "hoverlabel.bgcolor": c.card,
        "hoverlabel.font.color": c.text,
        "hoverlabel.bordercolor": c.border,
        "title.font.color": c.text
      }};
      Object.keys(fig.layout).forEach(function (k) {{
        if (/^(x|y)axis\d*$/.test(k)) {{
          upd[k + ".gridcolor"] = c.grid;
          upd[k + ".linecolor"] = c.border;
          upd[k + ".zerolinecolor"] = c.border;
          upd[k + ".tickfont.color"] = c.muted;
          upd[k + ".title.font.color"] = c.muted;
        }}
      }});
      var anns = (fig.layout.annotations || []);
      for (var i = 0; i < anns.length; i++) {{
        upd["annotations[" + i + "].font.color"] = c.text;
      }}
      Plotly.relayout(fig, upd);
    }});
  }}
  function applyTheme(isDark) {{
    document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
    try {{ localStorage.setItem("hydoscope-theme", isDark ? "dark" : "light"); }} catch (e) {{}}
    document.getElementById("iconMoon").style.display = isDark ? "none" : "block";
    document.getElementById("iconSun").style.display = isDark ? "block" : "none";
    applyChartTheme(isDark);
  }}
  var saved = "light";
  try {{ saved = localStorage.getItem("hydoscope-theme") || "light"; }} catch (e) {{}}
  applyTheme(saved === "dark");
  document.getElementById("themeToggle").addEventListener("click", function () {{
    applyTheme(document.documentElement.getAttribute("data-theme") !== "dark");
  }});
}})();
</script>
<script>
(function () {{
  function armReset(fig) {{
    fig._zoomed = true;
    if (fig._resetTimer) clearTimeout(fig._resetTimer);
    fig._resetTimer = setTimeout(function () {{
      fig._resetTimer = null;
      fig._zoomed = false;
      fig._resetting = true;
      var upd = {{}};
      Object.keys(fig.layout).forEach(function (k) {{
        if (/^(x|y)axis\d*$/.test(k)) upd[k + ".autorange"] = true;
      }});
      Plotly.relayout(fig, upd).then(function () {{ fig._resetting = false; }},
                                      function () {{ fig._resetting = false; }});
    }}, 5000);
  }}
  document.querySelectorAll(".js-plotly-plot").forEach(function (fig) {{
    fig.on("plotly_relayout", function (ev) {{
      if (fig._resetting) return;
      var keys = Object.keys(ev || {{}});
      if (keys.some(function (k) {{ return k.indexOf(".range") !== -1; }})) {{
        armReset(fig);
      }}
    }});
    var mv = null;
    fig.addEventListener("mousemove", function () {{
      if (!fig._zoomed) return;
      if (mv) clearTimeout(mv);
      mv = setTimeout(function () {{ armReset(fig); }}, 300);
    }});
  }});
  var pie = document.getElementById("pieChart");
  var basePulls = {PIE_PULLS};
  if (pie) {{
    pie.on("plotly_hover", function (d) {{
      if (!d.points || !d.points.length) return;
      var hi = d.points[0].pointNumber;
      var pulls = basePulls.map(function (v, i) {{ return i === hi ? 0.10 : 0.02; }});
      Plotly.restyle(pie, {{ pull: [pulls] }}, [0]);
    }});
    pie.on("plotly_unhover", function () {{
      Plotly.restyle(pie, {{ pull: [basePulls] }}, [0]);
    }});
  }}
}})();
</script>
</body>
</html>
"""

with open(PAGE, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Dashboard written to {PAGE}")
print(f"Serving at http://localhost:{PORT}/dashboard.html")

import http.server  # noqa: E402
import socketserver  # noqa: E402

os.chdir(BASE)
handler = http.server.SimpleHTTPRequestHandler
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), handler) as httpd:
    webbrowser.open(f"http://localhost:{PORT}/dashboard.html")
    httpd.serve_forever()
