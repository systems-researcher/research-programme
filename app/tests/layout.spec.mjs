// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// The page must never scroll sideways. Wide content — the matrix table, the
// dependency graph — scrolls inside its own container instead. Run against a
// built preview or the dev server:
//   node tests/layout.spec.mjs http://localhost:5173/
import { chromium } from "playwright"

const url = process.argv[2] ?? "http://localhost:5173/"
const WIDTHS = [390, 768, 1440]

const browser = await chromium.launch()
let failures = 0

for (const width of WIDTHS) {
  const page = await browser.newPage({ viewport: { width, height: 900 } })
  await page.goto(url, { waitUntil: "networkidle", timeout: 45000 })
  await page.waitForTimeout(800)

  const result = await page.evaluate(() => {
    const clientWidth = document.documentElement.clientWidth
    const escaping = []
    for (const el of document.querySelectorAll("body *")) {
      const box = el.getBoundingClientRect()
      if (box.right <= clientWidth + 1) continue
      // Report only the outermost offender in a chain: a child of an
      // already-overflowing element is a symptom, not the cause.
      const parent = el.parentElement
      if (parent && parent.getBoundingClientRect().right > clientWidth + 1) continue
      escaping.push(`${el.tagName}.${String(el.className).slice(0, 40)}`)
    }
    return { scrollWidth: document.documentElement.scrollWidth, clientWidth, escaping }
  })

  const overflows = result.scrollWidth > result.clientWidth + 1
  console.log(
    `${width}px: scrollWidth ${result.scrollWidth} vs ${result.clientWidth} — ${overflows ? "FAIL" : "ok"}`,
  )
  if (overflows) {
    failures += 1
    result.escaping.forEach((e) => console.log(`    escaping: ${e}`))
  }
  await page.close()
}

await browser.close()
if (failures) {
  console.error(`\n${failures} viewport(s) scroll sideways`)
  process.exit(1)
}
console.log("\nno viewport scrolls sideways")
