import { Moon, Sun } from "lucide-react";
import { useTheme } from "../theme.jsx";

export default function Header() {
  const { mode, toggle, c } = useTheme();
  return (
    <header
      style={{
        background: `linear-gradient(115deg, ${c.headerFrom} 0%, ${
          mode === "dark" ? "#123B66" : "#3182CE"
        } 50%, ${c.headerTo} 100%)`,
      }}
    >
      <div className="logo">≈</div>
      <div>
        <h1>HydroScope – Water Analytics</h1>
        <p className="sub">
          Mahailluppallama evaporation · 2004–2024 historical analysis ·
          Rajanganaya rainfall · 5-year forecast
        </p>
      </div>
      <button
        className="theme-btn"
        onClick={toggle}
        aria-label="Toggle dark or light mode"
        title="Toggle dark / light mode"
      >
        {mode === "dark" ? <Sun size={20} /> : <Moon size={20} />}
      </button>
      <svg className="waves" viewBox="0 0 1440 70" preserveAspectRatio="none">
        <path className="w1" d="M0,32 C240,64 480,0 720,20 C960,40 1200,64 1440,28 L1440,70 L0,70 Z" />
        <path className="w2" d="M0,44 C240,20 480,64 720,44 C960,24 1200,12 1440,44 L1440,70 L0,70 Z" />
        <path className="w3" d="M0,58 C300,42 600,70 900,56 C1140,46 1320,60 1440,52 L1440,70 L0,70 Z" />
      </svg>
    </header>
  );
}
