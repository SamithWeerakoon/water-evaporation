import {
  Area,
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { accents, useTheme } from "../theme.jsx";
import {
  axisProps,
  everyNth,
  fmtMY,
  fmtMYFull,
  tooltipProps,
} from "./chartUtils.js";

export default function ForecastChart({ forecast }) {
  const { c } = useTheme();
  const data = forecast.map((f) => ({
    date: f.date,
    value: f.value,
    lo: f.lo,
    band: Math.max(f.hi - f.lo, 0),
  }));
  const ticks = everyNth(data, 1).map((d) => d.date);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart data={data} margin={{ top: 30, right: 16, left: 6, bottom: 20 }}>
        <CartesianGrid stroke={c.grid} vertical={false} />
        <XAxis dataKey="date" ticks={ticks} tickFormatter={fmtMY} {...axisProps(c)}
          interval={0} fontSize={10}
          label={{ value: "Forecast month", position: "insideBottom", offset: -12,
                   fill: c.muted, fontSize: 11 }} />
        <YAxis width={58} domain={[0, "auto"]} {...axisProps(c)} axisLine={false}
          label={{ value: "Evaporation (mm)", angle: -90, position: "insideLeft",
                   fill: c.muted, fontSize: 11, dx: 4 }} />
        <Tooltip {...tooltipProps(c)} labelFormatter={fmtMYFull}
          formatter={(v, n) => [`${v} mm`, n]} />
        <Legend verticalAlign="top" align="right" height={26}
          wrapperStyle={{ fontSize: 12, color: c.text, paddingBottom: 4 }} />
        <Area dataKey="lo" stackId="band" stroke="none" fill="transparent" />
        <Area dataKey="band" name="95% range" stackId="band" stroke="none"
          fill={accents.gold} fillOpacity={0.18} />
        <Bar dataKey="value" name="Forecast" fill={accents.gold}
          radius={[4, 4, 0, 0]} />
        <Line type="monotone" dataKey="value" name="Forecast line"
          stroke={accents.coral} strokeWidth={2.4} strokeDasharray="3 3" dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
