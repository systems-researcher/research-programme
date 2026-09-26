// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// Every <img> the app renders must actually decode, and the favicon link must
// fetch, under whatever base serves the page: a root-absolute path in JSX
// survives a prefixed build untouched and 404s on the project site. Run
// against an already-served preview, or with no argument to boot one:
//   node tests/assets.spec.mjs "http://localhost:4173/research-programme/"
//   npm run test:assets
import { chromium } from "playwright"

let closeServer = null
let servedUrl = process.argv[2]

if (!servedUrl) {
  // Same mechanism CI uses (vite preview reads vite.config.ts, so the served
  // base comes from the environment), on a private port so it can run beside
  // a manually started preview.
  const { preview } = await import("vite")
  const server = await preview({ preview: { port: 4174, strictPort: true } })
  closeServer = () => new Promise((resolve) => server.httpServer.close(resolve))
  servedUrl = `http://localhost:4174${process.env.BASE_PATH ?? "/"}`
}

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
let failures = 0
const check = (name, ok) => {
  console.log(`${ok ? "pass" : "FAIL"}  ${name}`)
  if (!ok) failures += 1
}

await page.goto(servedUrl, { waitUntil: "networkidle", timeout: 45000 })

const images = await page.evaluate(() =>
  Array.from(document.querySelectorAll("img")).map((img) => ({
    src: img.getAttribute("src"),
    ok: img.complete && img.naturalWidth > 0,
  })),
)
if (images.length === 0) check("the page renders an image", false)
for (const image of images) check(`image decodes: ${image.src}`, image.ok)

const favicon = await page.evaluate(
  () => document.querySelector('link[rel="icon"]')?.href ?? null,
)
check("a favicon link is present", favicon !== null)
if (favicon) {
  const response = await page.request.get(favicon)
  check(`favicon fetches: ${favicon}`, response.ok())
}

await browser.close()
await closeServer?.()

if (failures) {
  console.error(`\n${failures} chrome asset(s) missing under the served base`)
  process.exit(1)
}
console.log("\nall chrome assets load under the served base")
