// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { createContext, useCallback, useContext, useEffect, useState } from "react"

/** shadcn themes on a `.dark` class, so a media query alone cannot drive it.
 *
 * The page still honours the reader's system setting by default; an explicit
 * choice is remembered. `resolved` is what is actually painted, which is what
 * the diagram needs, since Mermaid fixes its theme at render time. */

type Choice = "light" | "dark" | "system"
type Resolved = "light" | "dark"

const KEY = "rp-theme"

const ThemeContext = createContext<{
  choice: Choice
  resolved: Resolved
  setChoice: (c: Choice) => void
}>({ choice: "system", resolved: "light", setChoice: () => {} })

const systemPrefersDark = () =>
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-color-scheme: dark)").matches

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [choice, setStored] = useState<Choice>(() => {
    const saved = localStorage.getItem(KEY)
    return saved === "light" || saved === "dark" ? saved : "system"
  })
  const [resolved, setResolved] = useState<Resolved>(() =>
    (localStorage.getItem(KEY) as Resolved | null) ??
    (systemPrefersDark() ? "dark" : "light"),
  )

  useEffect(() => {
    const apply = () => {
      const next: Resolved =
        choice === "system" ? (systemPrefersDark() ? "dark" : "light") : choice
      document.documentElement.classList.toggle("dark", next === "dark")
      document.documentElement.style.colorScheme = next
      setResolved(next)
    }
    apply()

    // Only track the system while the reader has not chosen for themselves.
    if (choice !== "system") return
    const query = window.matchMedia("(prefers-color-scheme: dark)")
    query.addEventListener("change", apply)
    return () => query.removeEventListener("change", apply)
  }, [choice])

  const setChoice = useCallback((next: Choice) => {
    if (next === "system") localStorage.removeItem(KEY)
    else localStorage.setItem(KEY, next)
    setStored(next)
  }, [])

  return (
    <ThemeContext.Provider value={{ choice, resolved, setChoice }}>
      {children}
    </ThemeContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useTheme = () => useContext(ThemeContext)
