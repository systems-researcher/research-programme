// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import path from "node:path"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // GitHub Pages serves a project site from /<repo>/, not from the domain
  // root, and Vite writes absolute asset URLs — so a root-relative build
  // 404s there. The workflow sets BASE_PATH; local dev and any root-served
  // deployment leave it unset and keep "/".
  base: process.env.BASE_PATH ?? "/",
  build: { outDir: "../site", emptyOutDir: true },
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
      // The generated payload is imported from its canonical location so
      // there is exactly one map.json in the repository. Copying it into
      // src/ would let the app drift from what `python -m scripts.build`
      // last wrote.
      "@data": path.resolve(import.meta.dirname, "../data"),
    },
  },
})
