export default function ChartCard({ title, children, className = "", tall }) {
  return (
    <div className={`card ${className}`}>
      <h3 className="chart-title">{title}</h3>
      <div className={tall ? "chart tall" : "chart"}>{children}</div>
    </div>
  );
}
