import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { accents, useTheme } from "../theme.jsx";
import { MONTHS } from "../api.js";
import { axisProps, lerp, tooltipProps } from "./chartUtils.js";

export default function RainfallChart({ rainfall }) {
  const { c } = useTheme();
  const data = rainfall.map((d) => ({ month: MONTHS[d.month - 1], value: d.value }));
  const vals = data.map((d) => d.value);
  const min = Math.min(...vals);
  const max = Math.max(...vals);
  const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 30, right: 16, left: 6, bottom: 20 }}>
        <CartesianGrid stroke={c.grid} vertical={false} />
        <XAxis dataKey="month" {...axisProps(c)}
          label={{ value: "Month", position: "insideBottom", offset: -12,
                   fill: c.muted, fontSize: 11 }} />
        <YAxis width={58} domain={[0, max * 1.18]} {...axisProps(c)} axisLine={false}
          label={{ value: "Rainfall (mm)", angle: -90, position: "insideLeft",
                   fill: c.muted, fontSize: 11, dx: 4 }} />
        <Tooltip {...tooltipProps(c)} formatter={(v) => [`${v} mm`, "Rainfall"]} />
        <ReferenceLine y={avg} stroke={accents.gold} strokeDasharray="6 4"
          label={{ value: `avg ${avg.toFixed(0)}`, position: "insideTopRight",
                   fill: accents.gold, fontSize: 11 }} />
        <Legend verticalAlign="top" align="right" height={26}
          wrapperStyle={{ fontSize: 12, color: c.text, paddingBottom: 4 }} />
        <Bar dataKey="value" name="Rainfall" radius={[8, 8, 0, 0]}>
          {data.map((d) => (
            <Cell key={d.month}
              fill={lerp("#BDE7F4", accents.blue, (d.value - min) / (max - min || 1))} />
          ))}
          <LabelList dataKey="value" position="top" fill={c.muted} fontSize={10}
            formatter={(v) => v.toFixed(0)} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
