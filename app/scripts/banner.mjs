// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// Renders the README banner. Same technique as the social preview card:
// drawn with the site's own tokens and type, from data/map.json, so it
// cannot claim a shape the programme does not have. Run:
//   node scripts/banner.mjs
import { chromium } from "playwright"
import { writeFileSync } from "node:fs"
import { resolve } from "node:path"
import { fontFace, imageData, manifest } from "./image-data.mjs"

// Every drawn value comes from here, and the manifest written beside the PNG
// holds the same object. CI recomputes it and diffs the JSON, which is how a
// stale banner is caught without re-rendering across platforms.
const data = imageData()
const { title, site, strands, studies, published } = data

const escape = (text) =>
  String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")

// A strand with no studies of its own is not an empty row to hide: the
// written column is a real part of the programme. Say what it holds.
const strandRow = (strand) => `
  <li>
    <i style="background:${strand.colour}"></i>
    <span class="name">${escape(strand.title)}</span>
    <span class="count">${
      strand.studies ? `${strand.studies} ${strand.studies === 1 ? "study" : "studies"}` : "the written record"
    }</span>
  </li>`

const html = `<!doctype html>
<html><head><meta charset="utf-8">
<style>
  ${fontFace()}
  * { margin: 0; box-sizing: border-box; }
  body {
    width: 1280px; height: 640px; display: flex; flex-direction: column;
    justify-content: space-between; padding: 80px;
    background: #fafafa; color: #0a0a0a;
    font-family: Geist, ui-sans-serif, system-ui, sans-serif;
  }
  .rules { display: flex; gap: 10px; margin-bottom: 30px; }
  .rules i { display: block; width: 80px; height: 6px; border-radius: 3px; }
  .eyebrow { font-size: 19px; font-weight: 600; letter-spacing: .18em;
             text-transform: uppercase; color: #737373; }
  h1 { font-size: 62px; line-height: 1.08; font-weight: 600;
       letter-spacing: -.02em; max-width: 16ch; margin-top: 14px; }
  ul { list-style: none; display: flex; flex-direction: column; gap: 14px;
       margin-top: 46px; }
  li { display: flex; align-items: center; gap: 16px; }
  li i { display: block; width: 42px; height: 4px; border-radius: 2px; flex: none; }
  .name { font-size: 21px; font-weight: 500; }
  .count { font-size: 19px; color: #737373; }
  .foot { display: flex; align-items: flex-end; justify-content: space-between; }
  .site { font-size: 19px; color: #737373; }
  .stat { font-size: 19px; color: #737373; }
  .stat b { font-weight: 600; color: #0a0a0a; font-variant-numeric: tabular-nums; }
</style></head>
<body>
  <div>
    <div class="rules">${strands.map((s) => `<i style="background:${s.colour}"></i>`).join("")}</div>
    <p class="eyebrow">Doctoral research programme</p>
    <h1>${escape(title)}</h1>
    <ul>${strands.map(strandRow).join("")}</ul>
  </div>
  <div class="foot">
    <span class="site">${escape(site)}</span>
    <span class="stat">
      <b>${studies}</b> studies &middot; <b>${published}</b> in the record
    </span>
  </div>
</body></html>`

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 640 } })
await page.setContent(html, { waitUntil: "networkidle" })
// `networkidle` does not reliably wait for an @import-ed webfont to finish
// parsing/applying, so confirm against the Font Loading API before shooting.
await page.evaluate(() => document.fonts.ready)
const geistLoaded = await page.evaluate(() => document.fonts.check("600 62px Geist"))
const out = resolve(import.meta.dirname, "../public/banner.png")
writeFileSync(out, await page.screenshot({ type: "png" }))
// The values the PNG draws, so CI can detect drift without a browser.
writeFileSync(resolve(import.meta.dirname, "../public/images.manifest.json"), manifest(data))
await browser.close()
console.log(`wrote ${out} (1280x640, ${studies} studies, ${published} in the record)`)
console.log(`Geist webfont: ${geistLoaded ? "loaded" : "fell back to system sans"}`)
