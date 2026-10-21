import { Fragment } from "react";
import { useTheme } from "../theme.jsx";
import { heatColor } from "./chartUtils.js";

export default function Heatmap({ heatmap }) {
  const { c } = useTheme();
  const { years, months, values } = heatmap;
  const flat = values.flat().filter((v) => v != null);
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  return (
    <div className="heatmap-block">
      <div className="heatmap" style={{ color: c.muted }}>
        <div className="hm-corner" />
        {months.map((m) => (
          <div key={m} className="hm-month">{m}</div>
        ))}
        {years.map((y, r) => (
          <Fragment key={y}>
            <div className="hm-year">{y}</div>
            {values[r].map((v, ci) => (
              <div
                key={ci}
                className="hm-cell"
                style={{
                  background: v == null ? "transparent" : heatColor(v, min, max),
                  border: `1px solid ${c.card}`,
                }}
                title={v == null ? `${months[ci]} ${y}: no data` : `${months[ci]} ${y}: ${v} mm`}
              />
            ))}
          </Fragment>
        ))}
      </div>
      <div className="hm-legend">
        <span>{min.toFixed(0)} mm</span>
        <div className="hm-scale" />
        <span>{max.toFixed(0)} mm</span>
      </div>
    </div>
  );
}
