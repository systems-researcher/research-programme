// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import path from "node:path"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // The page is served from the domain root and holds no routes of its own.
  base: "/",
  build: { outDir: "../site", emptyOutDir: true },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      // The generated payload is imported from its canonical location so
      // there is exactly one map.json in the repository. Copying it into
      // src/ would let the app drift from what `python -m scripts.build`
      // last wrote.
      "@data": path.resolve(__dirname, "../data"),
    },
  },
})
