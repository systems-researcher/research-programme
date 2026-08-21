// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// Renders the social preview card. Drawn with the site's own tokens and type
// so the card cannot drift from the page it advertises. Run:
//   node scripts/preview.mjs
import { chromium } from "playwright"
import { readFileSync, writeFileSync } from "node:fs"
import { resolve } from "node:path"

const map = JSON.parse(
  readFileSync(resolve(import.meta.dirname, "../../data/map.json"), "utf8"),
)
const studies = map.strands
  .flatMap((strand) => strand.entries)
  .filter((entry) => entry.card).length

const html = `<!doctype html>
<html><head><meta charset="utf-8">
<style>
  @import url("https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&display=swap");
  * { margin: 0; box-sizing: border-box; }
  body {
    width: 1200px; height: 630px; display: flex; flex-direction: column;
    justify-content: space-between; padding: 72px;
    background: #fafafa; color: #0a0a0a;
    font-family: Geist, ui-sans-serif, system-ui, sans-serif;
  }
  .eyebrow { font-size: 20px; font-weight: 600; letter-spacing: .18em;
             text-transform: uppercase; color: #737373; }
  h1 { font-size: 68px; line-height: 1.08; font-weight: 600;
       letter-spacing: -.02em; max-width: 15ch; }
  .foot { display: flex; align-items: flex-end; justify-content: space-between; }
  .stats { display: flex; gap: 48px; }
  .n { font-size: 40px; font-weight: 600; font-variant-numeric: tabular-nums; }
  .l { font-size: 17px; color: #737373; margin-top: 4px; }
  .rules { display: flex; gap: 10px; margin-bottom: 28px; }
  .rules i { display: block; width: 76px; height: 6px; border-radius: 3px; }
</style></head>
<body>
  <div>
    <div class="rules">
      <i style="background:oklch(0.55 0.16 250)"></i>
      <i style="background:oklch(0.55 0.17 305)"></i>
      <i style="background:oklch(0.52 0.12 165)"></i>
    </div>
    <p class="eyebrow">Doctoral research programme</p>
    <h1>${map.programme.title}</h1>
  </div>
  <div class="foot">
    <div class="stats">
      <div><div class="n">${studies}</div><div class="l">studies</div></div>
      <div><div class="n">${map.strands.length}</div><div class="l">strands</div></div>
    </div>
    <div class="l">Loughborough University</div>
  </div>
</body></html>`

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } })
await page.setContent(html, { waitUntil: "networkidle" })
// `networkidle` does not reliably wait for an @import-ed webfont to finish
// parsing/applying, so confirm against the Font Loading API before shooting.
await page.evaluate(() => document.fonts.ready)
const geistLoaded = await page.evaluate(() => document.fonts.check("600 68px Geist"))
const out = resolve(import.meta.dirname, "../public/preview.png")
writeFileSync(out, await page.screenshot({ type: "png" }))
await browser.close()
console.log(`wrote ${out} (1200x630, ${studies} studies)`)
console.log(`Geist webfont: ${geistLoaded ? "loaded" : "fell back to system sans"}`)
