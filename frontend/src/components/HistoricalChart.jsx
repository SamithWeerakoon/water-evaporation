import {
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

export default function HistoricalChart({ historical, trend }) {
  const { c } = useTheme();
  const data = historical.map((h, i) => ({
    date: h.date,
    value: h.value,
    trend: trend[i]?.value,
  }));
  const ticks = everyNth(data, 3).map((d) => d.date);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart data={data} margin={{ top: 30, right: 16, left: 6, bottom: 20 }}>
        <CartesianGrid stroke={c.grid} vertical={false} />
        <XAxis dataKey="date" ticks={ticks} tickFormatter={fmtMY} {...axisProps(c)}
          label={{ value: "Year", position: "insideBottom", offset: -12,
                   fill: c.muted, fontSize: 11 }} />
        <YAxis width={58} domain={[0, "auto"]} {...axisProps(c)} axisLine={false}
          label={{ value: "Evaporation (mm)", angle: -90, position: "insideLeft",
                   fill: c.muted, fontSize: 11, dx: 4 }} />
        <Tooltip {...tooltipProps(c)} labelFormatter={fmtMYFull}
          formatter={(v, n) => [`${v} mm`, n]} />
        <Legend verticalAlign="top" align="right" height={26}
          wrapperStyle={{ fontSize: 12, color: c.text, paddingBottom: 4 }} />
        <Bar dataKey="value" name="Monthly evaporation" fill={accents.blue}
          radius={[3, 3, 0, 0]} />
        <Line type="linear" dataKey="trend" name="Trend line" stroke={accents.green}
          strokeWidth={2.2} strokeDasharray="6 4" dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
