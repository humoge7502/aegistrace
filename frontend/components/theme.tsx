"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

export type Theme = "ledger" | "paper";

const ThemeContext = createContext<{ theme: Theme; toggle: () => void }>({
  theme: "ledger",
  toggle: () => {},
});

export const THEME_KEY = "aegistrace-theme";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("ledger");

  useEffect(() => {
    const stored = window.localStorage.getItem(THEME_KEY);
    if (stored === "paper" || stored === "ledger") setTheme(stored);
  }, []);

  const toggle = useCallback(() => {
    setTheme((t) => {
      const next: Theme = t === "ledger" ? "paper" : "ledger";
      window.localStorage.setItem(THEME_KEY, next);
      document.documentElement.dataset.theme = next === "paper" ? "paper" : "";
      return next;
    });
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}

/** Inline script: apply the persisted theme before first paint (no flash). */
export const themeInitScript = `(function(){try{var t=localStorage.getItem("${THEME_KEY}");if(t==="paper"){document.documentElement.dataset.theme="paper";}}catch(e){}})();`;
