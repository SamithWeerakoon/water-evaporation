import { useEffect, useState } from "react";
import { fetchAll } from "./api.js";
import Header from "./components/Header.jsx";
import KpiCard from "./components/KpiCard.jsx";
import ChartCard from "./components/ChartCard.jsx";
import HistoricalChart from "./components/HistoricalChart.jsx";
import ForecastChart from "./components/ForecastChart.jsx";
import MonthlyPattern from "./components/MonthlyPattern.jsx";
import ShareDonut from "./components/ShareDonut.jsx";
import Heatmap from "./components/Heatmap.jsx";
import ComparisonChart from "./components/ComparisonChart.jsx";
import RainfallChart from "./components/RainfallChart.jsx";

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAll().then(setData).catch((e) => setError(e.message));
  }, []);

  return (
    <>
      <Header />
      <main className="content">
        {error && <div className="state error">Could not load data: {error}</div>}
        {!data && !error && <div className="state">Loading analytics…</div>}
        {data && <Dashboard data={data} />}
        <footer>HydroScope · React + FastAPI · data: data/*.xlsx</footer>
      </main>
    </>
  );
}

function Dashboard({ data }) {
  const { summary: s, series, monthly, heatmap, comparison } = data;
  return (
    <>
      <section className="kpi-grid">
        <KpiCard icon="average" label="Average Evaporation"
          value={`${s.avg_yearly.toLocaleString()} mm/yr`}
          sub={`${s.months} months · ${s.start_year}–${s.end_year}`} color="blue" />
        <KpiCard icon="highest" label="Highest Year" value={s.highest_year}
          sub={`${s.highest_val.toLocaleString()} mm`} color="green" />
        <KpiCard icon="lowest" label="Lowest Year" value={s.lowest_year}
          sub={`${s.lowest_val.toLocaleString()} mm`} color="coral" />
        <KpiCard icon="trend" label="Long-term Trend"
          value={`${s.trend_per_year > 0 ? "+" : ""}${s.trend_per_year} mm/yr`}
          sub="linear regression" color="purple" />
        <KpiCard icon="balance" label="Water Balance"
          value={`${s.water_balance > 0 ? "+" : ""}${s.water_balance.toLocaleString()} mm/yr`}
          sub="evaporation − rainfall" color="gold" />
        <KpiCard icon="forecast" label={`Forecast ${s.forecast_year}`}
          value={`${s.forecast_val.toLocaleString()} mm`}
          sub={`±${s.forecast_band.toLocaleString()} mm (95% range)`} color="teal" />
      </section>

      <section className="grid">
        <ChartCard className="full"
          title="Evaporation Trend — Historical 2004–2024 (monthly, mm)">
          <HistoricalChart historical={series.historical} trend={series.trend} />
        </ChartCard>

        <ChartCard className="full"
          title={`Evaporation Forecast ${series.forecast[0].date.slice(0, 4)}–${series.forecast.at(-1).date.slice(0, 4)} (monthly, mm)`}>
          <ForecastChart forecast={series.forecast} />
        </ChartCard>

        <ChartCard title="Monthly Evaporation Pattern">
          <MonthlyPattern pattern={monthly.pattern} rate={monthly.rate} />
        </ChartCard>

        <ChartCard title="Evaporation Share by Month">
          <ShareDonut share={monthly.share} avgYearly={s.avg_yearly} />
        </ChartCard>

        <ChartCard className="full" title="Monthly Evaporation Heatmap (mm)" tall>
          <Heatmap heatmap={heatmap} />
        </ChartCard>

        <ChartCard title="Average Monthly Evaporation vs Rainfall (mm)">
          <ComparisonChart comparison={comparison} />
        </ChartCard>

        <ChartCard title="Average Monthly Rainfall (mm)">
          <RainfallChart rainfall={monthly.rainfall} />
        </ChartCard>
      </section>
    </>
  );
}
