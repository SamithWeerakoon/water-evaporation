import {
  ArrowDownRight,
  ArrowUpRight,
  Droplets,
  LineChart,
  Scale,
  Target,
} from "lucide-react";
import { accents } from "../theme.jsx";

const ICONS = {
  average: Droplets,
  highest: ArrowUpRight,
  lowest: ArrowDownRight,
  trend: LineChart,
  balance: Scale,
  forecast: Target,
};

export default function KpiCard({ icon, label, value, sub, color }) {
  const Icon = ICONS[icon];
  return (
    <div className="kpi">
      <div className="kpi-top">
        <span
          className="kpi-icon"
          style={{ background: `${accents[color]}1F`, color: accents[color] }}
        >
          <Icon size={16} strokeWidth={2.2} />
        </span>
        <span className="kpi-label">{label}</span>
      </div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-sub">{sub}</div>
    </div>
  );
}
