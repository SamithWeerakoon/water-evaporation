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
      <BarChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}
        barGap={2} barCategoryGap="28%">
        <CartesianGrid stroke={c.grid} vertical={false} />
        <XAxis dataKey="month" {...axisProps(c)} />
        <YAxis width={42} {...axisProps(c)} axisLine={false} />
        <Tooltip {...tooltipProps(c)} formatter={(v, n) => [`${v} mm`, n]} />
        <Legend wrapperStyle={{ fontSize: 12, color: c.text }} />
        <Bar dataKey="evaporation" name="Evaporation" fill={accents.blue}
          radius={[5, 5, 0, 0]} />
        <Bar dataKey="rainfall" name="Rainfall" fill={accents.teal}
          radius={[5, 5, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
