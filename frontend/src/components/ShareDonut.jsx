import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { accents, useTheme } from "../theme.jsx";
import { MONTHS } from "../api.js";
import { tooltipProps } from "./chartUtils.js";

const COLORS = [
  accents.blue, accents.cyan, accents.teal, accents.green, "#66B96B",
  accents.gold, "#E4A93F", "#E58A52", accents.coral, accents.purple,
  "#A08BE0", "#5B9BD5",
];

export default function ShareDonut({ share, avgYearly }) {
  const { c } = useTheme();
  const data = share.map((d) => ({ name: MONTHS[d.month - 1], value: d.value }));
  return (
    <div className="donut-wrap">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Tooltip {...tooltipProps(c)}
            formatter={(v, n, p) => [`${v} mm (${(p.percent * 100).toFixed(1)}%)`, n]} />
          <Pie data={data} dataKey="value" nameKey="name" innerRadius="58%"
            outerRadius="84%" paddingAngle={2} stroke={c.card} strokeWidth={2}>
            {data.map((d, i) => (
              <Cell key={d.name} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="donut-center">
        <b>{avgYearly.toLocaleString()}</b>
        <span>mm / year avg</span>
      </div>
    </div>
  );
}
