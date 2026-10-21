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

function MiniBar({ data, color, unit, name, c }) {
  const margin = { top: 28, right: 8, left: 4, bottom: 18 };
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={margin}>
        <CartesianGrid stroke={c.grid} vertical={false} />
        <XAxis dataKey="month" tickFormatter={(m) => MONTHS[m - 1]} {...axisProps(c)}
          label={{ value: "Month", position: "insideBottom", offset: -12,
                   fill: c.muted, fontSize: 11 }} />
        <YAxis width={48} {...axisProps(c)} axisLine={false}
          label={{ value: unit === "mm" ? "Monthly total (mm)" : "Daily rate (mm/day)",
                   angle: -90, position: "insideLeft",
                   fill: c.muted, fontSize: 10, dx: 4 }} />
        <Tooltip {...tooltipProps(c)}
          labelFormatter={(m) => MONTHS[m - 1]}
          formatter={(v) => [`${v} ${unit}`, ""]} />
        <Legend verticalAlign="top" align="right" height={22}
          wrapperStyle={{ fontSize: 11, color: c.text, paddingBottom: 2 }} />
        <Bar dataKey="value" name={name} fill={color} radius={[5, 5, 0, 0]} />
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
          <MiniBar data={pattern} color={accents.cyan} unit="mm" name="mm / month" c={c} />
        </div>
      </div>
      <div>
        <p className="mini-title">Daily rate mm/day</p>
        <div className="mini-chart">
          <MiniBar data={rate} color={accents.teal} unit="mm/day" name="mm / day" c={c} />
        </div>
      </div>
    </div>
  );
}
