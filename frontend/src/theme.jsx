import { createContext, useContext, useEffect, useState } from "react";

export const palettes = {
  light: {
    mode: "light",
    bg: "#F3F7FC",
    card: "#FFFFFF",
    text: "#24344D",
    muted: "#65758B",
    border: "#DFE8F2",
    grid: "#E6EDF5",
    headerFrom: "#244F88",
    headerTo: "#18A8D1",
  },
  dark: {
    mode: "dark",
    bg: "#0D1626",
    card: "#152136",
    text: "#E8EEF8",
    muted: "#94A3B8",
    border: "#233249",
    grid: "#22304A",
    headerFrom: "#0B1526",
    headerTo: "#0E6E8E",
  },
};

export const accents = {
  blue: "#3182CE",
  cyan: "#18A8D1",
  teal: "#2CB6A0",
  green: "#43A66B",
  gold: "#E6AD35",
  coral: "#E87568",
  purple: "#8B78D8",
};

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [mode, setMode] = useState(() => {
    try {
      return localStorage.getItem("hydoscope-theme") || "light";
    } catch {
      return "light";
    }
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", mode);
    try {
      localStorage.setItem("hydoscope-theme", mode);
    } catch {}
  }, [mode]);

  const toggle = () => setMode((m) => (m === "dark" ? "light" : "dark"));
  return (
    <ThemeContext.Provider value={{ mode, toggle, c: palettes[mode] }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
