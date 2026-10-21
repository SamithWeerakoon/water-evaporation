import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { accents, useTheme } from "../theme.jsx";
import { MONTHS } from "../api.js";
import { axisProps, tooltipProps } from "./chartUtils.js";

export default function ComparisonChart({ comparison }) {
  const { c } = useTheme();
  const data = comparison.map((d) => ({
    ...d,
    month: MONTHS[d.month - 1],
  }));
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 30, right: 16, left: 6, bottom: 20 }}
        barGap={2} barCategoryGap="28%">
        <CartesianGrid stroke={c.grid} vertical={false} />
        <XAxis dataKey="month" {...axisProps(c)}
          label={{ value: "Month", position: "insideBottom", offset: -12,
                   fill: c.muted, fontSize: 11 }} />
        <YAxis width={58} {...axisProps(c)} axisLine={false}
          label={{ value: "Water depth (mm)", angle: -90, position: "insideLeft",
                   fill: c.muted, fontSize: 11, dx: 4 }} />
        <Tooltip {...tooltipProps(c)} formatter={(v, n) => [`${v} mm`, n]} />
        <Legend verticalAlign="top" align="right" height={26}
          wrapperStyle={{ fontSize: 12, color: c.text, paddingBottom: 4 }} />
        <Bar dataKey="evaporation" name="Evaporation" fill={accents.blue}
          radius={[5, 5, 0, 0]} />
        <Bar dataKey="rainfall" name="Rainfall" fill={accents.teal}
          radius={[5, 5, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
