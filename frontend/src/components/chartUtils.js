export const tooltipProps = (c) => ({
  contentStyle: {
    background: c.card,
    border: `1px solid ${c.border}`,
    borderRadius: 10,
    color: c.text,
    fontSize: 12,
    boxShadow: "0 6px 20px rgba(0,0,0,.14)",
  },
  labelStyle: { color: c.muted, fontSize: 11, marginBottom: 2 },
  itemStyle: { color: c.text, fontSize: 12 },
});

export const axisProps = (c) => ({
  tick: { fill: c.muted, fontSize: 11 },
  tickLine: false,
  axisLine: { stroke: c.border },
});

export const fmtMY = (d) => {
  const dt = new Date(d);
  return `${dt.toLocaleString("en-US", { month: "short" })} ${String(
    dt.getUTCFullYear()
  ).slice(2)}`;
};

export const fmtMYFull = (d) => {
  const dt = new Date(d);
  return `${dt.toLocaleString("en-US", { month: "short" })} ${dt.getUTCFullYear()}`;
};

export const everyNth = (arr, n) => arr.filter((_, i) => i % n === 0);

export const lerp = (a, b, t) => {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  const p = pa.map((v, i) => Math.round(v + (pb[i] - v) * t));
  return `#${p.map((v) => v.toString(16).padStart(2, "0")).join("")}`;
};

export const heatColor = (v, min, max) => {
  const t = max === min ? 0 : (v - min) / (max - min);
  return t < 0.5
    ? lerp("#EAF6FB", "#7CC4E4", t * 2)
    : lerp("#7CC4E4", "#244F88", (t - 0.5) * 2);
};
