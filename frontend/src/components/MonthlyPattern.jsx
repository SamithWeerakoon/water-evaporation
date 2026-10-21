import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { accents, useTheme } from "../theme.jsx";
import { MONTHS } from "../api.js";
import { axisProps, tooltipProps } from "./chartUtils.js";

function MiniBar({ data, color, unit, c }) {
  const margin = { top: 16, right: 8, left: 0, bottom: 0 };
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={margin}>
        <CartesianGrid stroke={c.grid} vertical={false} />
        <XAxis dataKey="month" tickFormatter={(m) => MONTHS[m - 1]} {...axisProps(c)} />
        <YAxis width={40} {...axisProps(c)} axisLine={false} />
        <Tooltip {...tooltipProps(c)}
          labelFormatter={(m) => MONTHS[m - 1]}
          formatter={(v) => [`${v} ${unit}`, ""]} />
        <Bar dataKey="value" fill={color} radius={[5, 5, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default function MonthlyPattern({ pattern, rate }) {
  const { c } = useTheme();
  return (
    <div className="split">
      <div>
        <p className="mini-title">Total mm / month</p>
        <div className="mini-chart">
          <MiniBar data={pattern} color={accents.cyan} unit="mm" c={c} />
        </div>
      </div>
      <div>
        <p className="mini-title">Daily rate mm/day</p>
        <div className="mini-chart">
          <MiniBar data={rate} color={accents.teal} unit="mm/day" c={c} />
        </div>
      </div>
    </div>
  );
}
