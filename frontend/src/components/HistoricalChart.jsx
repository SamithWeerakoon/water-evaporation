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
      <ComposedChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid stroke={c.grid} vertical={false} />
        <XAxis dataKey="date" ticks={ticks} tickFormatter={fmtMY} {...axisProps(c)} />
        <YAxis width={46} domain={[0, "auto"]} {...axisProps(c)} axisLine={false} />
        <Tooltip {...tooltipProps(c)} labelFormatter={fmtMYFull}
          formatter={(v, n) => [`${v} mm`, n]} />
        <Legend iconType="plainline" wrapperStyle={{ fontSize: 12, color: c.text }} />
        <Bar dataKey="value" name="Historical" fill={accents.blue} radius={[3, 3, 0, 0]} />
        <Line type="linear" dataKey="trend" name="Trend" stroke={accents.green}
          strokeWidth={2.2} strokeDasharray="6 4" dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
