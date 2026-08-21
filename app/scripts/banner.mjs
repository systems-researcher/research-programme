// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// Renders the README banner. Same technique as the social preview card:
// drawn with the site's own tokens and type, from data/map.json, so it
// cannot claim a shape the programme does not have. Run:
//   node scripts/banner.mjs
import { chromium } from "playwright"
import { readFileSync, writeFileSync } from "node:fs"
import { resolve } from "node:path"

const SITE = "systems-researcher.github.io/research-programme"

const map = JSON.parse(
  readFileSync(resolve(import.meta.dirname, "../../data/map.json"), "utf8"),
)

// Each strand's colour comes from the same custom properties the site uses,
// transcribed here because a headless page has no stylesheet to read them
// from. A strand whose token is missing would render an invisible rule, so
// the lookup fails loudly instead.
const STRAND_COLOUR = {
  adequacy: "oklch(0.55 0.16 250)",
  method: "oklch(0.55 0.17 305)",
  formalisation: "oklch(0.52 0.12 165)",
}

const strands = map.strands.map((strand) => {
  const colour = STRAND_COLOUR[strand.token]
  if (!colour) {
    throw new Error(
      `strand "${strand.id}" has token "${strand.token}", which has no colour here. ` +
        `Add it to STRAND_COLOUR, matching --strand-${strand.token}-line in app/src/index.css.`,
    )
  }
  const studies = strand.entries.filter((entry) => entry.card).length
  return { title: strand.title, colour, studies }
})

const studies = strands.reduce((total, strand) => total + strand.studies, 0)
const published = map.strands
  .flatMap((strand) => strand.entries)
  .filter((entry) => entry.paper).length

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
  @import url("https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&display=swap");
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
    <h1>${escape(map.programme.title)}</h1>
    <ul>${strands.map(strandRow).join("")}</ul>
  </div>
  <div class="foot">
    <span class="site">${SITE}</span>
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
await browser.close()
console.log(`wrote ${out} (1280x640, ${studies} studies, ${published} in the record)`)
console.log(`Geist webfont: ${geistLoaded ? "loaded" : "fell back to system sans"}`)
