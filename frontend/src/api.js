const get = async (path) => {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
};

export const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export async function fetchAll() {
  const [summary, series, monthly, heatmap, comparison] = await Promise.all([
    get("/api/summary"),
    get("/api/series"),
    get("/api/monthly"),
    get("/api/heatmap"),
    get("/api/comparison"),
  ]);
  return { summary, series, monthly, heatmap, comparison };
}

export const monthName = (m) => MONTHS[m - 1];
