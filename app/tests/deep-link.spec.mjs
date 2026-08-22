// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// A study's detail panel must be reachable by URL: opening a cell writes
// #study=<key>, reloading with that hash reopens the panel, and Back closes
// it. Run against a built preview or the dev server:
//   node tests/deep-link.spec.mjs http://localhost:4173/
import { chromium } from "playwright"

const url = process.argv[2] ?? "http://localhost:4173/"
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
let failures = 0
const check = (name, ok) => {
  console.log(`${ok ? "pass" : "FAIL"}  ${name}`)
  if (!ok) failures += 1
}

await page.goto(url, { waitUntil: "networkidle", timeout: 45000 })

await page.locator("#matrix").getByRole("button").filter({ hasText: "sysml2-bench" }).click()
await page.waitForTimeout(300)
check("opening a cell writes the hash", page.url().includes("#study=sysml2-bench"))
check("the sheet opens", await page.getByRole("dialog").isVisible())

await page.reload({ waitUntil: "networkidle" })
await page.waitForTimeout(500)
check("reloading the hash reopens the sheet", await page.getByRole("dialog").isVisible())

await page.goBack()
await page.waitForTimeout(500)
check("Back closes the sheet", !(await page.getByRole("dialog").isVisible()))

// A pasted deep link inherits its hash rather than pushing it, so Escape
// must clear the hash in place instead of walking back off the site.
const origin = new URL(url).origin
await page.goto(`${url}#study=sysml2-bench`, { waitUntil: "networkidle", timeout: 45000 })
await page.waitForTimeout(300)
check("a pasted deep link opens the sheet", await page.getByRole("dialog").isVisible())
await page.keyboard.press("Escape")
await page.waitForTimeout(300)
check("Escape strips an inherited hash", !page.url().includes("#study="))
check("closing an inherited deep link shuts the sheet", !(await page.getByRole("dialog").isVisible()))
check("closing an inherited deep link stays on the page", page.url().startsWith(origin))

// Regression: any traversal retires the session's pushed flag, because the
// entry we landed on was not pushed here. Stepping from an inherited deep
// link to another study pushes onto the inherited entry; one Escape steps
// back to the inherited study, and only then does the hash get cleared —
// never a walk off the page. The sheet's own next-study button drives the
// same openByKey push as a matrix cell, without fighting the overlay.
await page.goto(`${url}#study=sysml2-bench`, { waitUntil: "networkidle", timeout: 45000 })
await page.waitForTimeout(300)
await page.getByRole("button", { name: /governed-interaction-cost-probe →/ }).click()
await page.waitForTimeout(300)
check("stepping from an inherited deep link pushes a new entry", page.url().includes("#study=governed-interaction-cost-probe"))
await page.keyboard.press("Escape")
await page.waitForTimeout(500)
check("one Escape steps back to the inherited study", page.url().includes("#study=sysml2-bench"))
check("the sheet is still open on the inherited study", await page.getByRole("dialog").isVisible())
await page.keyboard.press("Escape")
await page.waitForTimeout(500)
check("a second Escape clears the hash", !page.url().includes("#study="))
check("a second Escape stays on the app origin", page.url().startsWith(origin))
check("a second Escape closes the sheet", !(await page.getByRole("dialog").isVisible()))

await browser.close()
process.exit(failures ? 1 : 0)
