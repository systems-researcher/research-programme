// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// A study's detail panel must be reachable by URL: opening a cell writes
// #study=<key>, reloading with that hash reopens the panel, and Back closes
// it. Run against a built preview or the dev server:
//   node tests/deep-link.spec.mjs http://localhost:4173/
import { chromium } from "playwright"

const url = process.argv[2] ?? "http://localhost:4173/"
const origin = new URL(url).origin
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

const sheet = page.getByRole("dialog")
const title = sheet.locator("h2").first()
check("a private title is not a link", (await title.locator("a").count()) === 0)
check("a private sheet offers the request", (await sheet.getByRole("link", { name: "Request access to this study" }).count()) === 1)
check("a private sheet does not claim to open GitHub", (await sheet.getByText("(opens GitHub)").count()) === 0)

const requestHref = await sheet.getByRole("link", { name: "Request access to this study" }).getAttribute("href")
const requestUrl = new URL(requestHref)
// URLSearchParams values are already decoded; do not decode again.
const body = requestUrl.searchParams.get("body")
check("a private sheet shows the lock", (await sheet.locator("svg.lucide-lock").count()) === 1)
check("a private sheet says it is private", (await sheet.getByText("This study is private.").count()) === 1)
check("the request goes to the research address", requestHref.startsWith("mailto:J.Gower@lboro.ac.uk"))
check("the request subject matches the access route", requestUrl.searchParams.get("subject") === "Research programme: access request")
check("the request names the study", body.includes("Study: sysml2-bench"))
check("the request names the repository", body.includes("Repository: https://github.com/systems-researcher/sysml2-bench"))
check("the request page line carries the study hash", body.includes("Page:") && body.includes("#study=sysml2-bench"))
check("the request never uses the company address", !requestHref.includes("support@jgsystemsconsulting.com"))
// The prefix is only present when the served page itself carries it, so a
// plain dev-server run of this spec stays honest.
if (new URL(url).pathname.includes("/research-programme/")) {
  check("the request page line carries the deploy prefix", body.includes("/research-programme/#study=sysml2-bench"))
}

// Copy control. Spy the write; do not read the clipboard and do not grant
// permissions. data-copy-url is the same string the click writes, so a stub
// drift cannot hide a wrong URL.
const copyButton = sheet.getByRole("button", { name: "Copy link to this study" })
check("the sheet has one copy control", (await copyButton.count()) === 1)
const copyUrl = await copyButton.getAttribute("data-copy-url")
const servedPath = new URL(page.url()).pathname.endsWith("/")
  ? new URL(page.url()).pathname
  : new URL(page.url()).pathname + "/"
const expectedCopy = origin + servedPath + "#study=sysml2-bench"
check("data-copy-url is origin, base, and the study hash", copyUrl === expectedCopy)
if (new URL(url).pathname.includes("/research-programme/")) {
  check("data-copy-url carries the deploy prefix", copyUrl.includes("/research-programme/#study=sysml2-bench"))
} else {
  check("data-copy-url does not invent the deploy prefix", !copyUrl.includes("/research-programme/"))
}

await page.evaluate(() => {
  const calls = []
  window.__copyCalls = calls
  const stub = (text) => {
    calls.push(text)
    return Promise.resolve()
  }
  if (!navigator.clipboard) {
    Object.defineProperty(navigator, "clipboard", { value: { writeText: stub }, configurable: true })
  } else {
    navigator.clipboard.writeText = stub
  }
})
await copyButton.click()
await page.waitForTimeout(300)
const copyCalls = await page.evaluate(() => window.__copyCalls)
check("writeText was called once", copyCalls.length === 1)
check("writeText received data-copy-url", copyCalls[0] === copyUrl)
check("the copy confirms in the accessible name", (await sheet.getByRole("button", { name: "Copied link to this study" }).count()) === 1)
check("the copy does not change the hash", page.url().includes("#study=sysml2-bench"))
check("the copy leaves the sheet open", await page.getByRole("dialog").isVisible())
await page.waitForTimeout(2600)
check("the copy label reverts", (await sheet.getByRole("button", { name: "Copy link to this study" }).count()) === 1)

await page.reload({ waitUntil: "networkidle" })
await page.waitForTimeout(500)
check("reloading the hash reopens the sheet", await page.getByRole("dialog").isVisible())

await page.goBack()
await page.waitForTimeout(500)
check("Back closes the sheet", !(await page.getByRole("dialog").isVisible()))

// A pasted deep link inherits its hash rather than pushing it, so Escape
// must clear the hash in place instead of walking back off the site.
await page.goto(`${url}#study=sysml2-bench`, { waitUntil: "networkidle", timeout: 45000 })
await page.waitForTimeout(300)
check("a pasted deep link opens the sheet", await page.getByRole("dialog").isVisible())
await page.keyboard.press("Escape")
await page.waitForTimeout(300)
check("Escape strips an inherited hash", !page.url().includes("#study="))
check("closing an inherited deep link shuts the sheet", !(await page.getByRole("dialog").isVisible()))
check("closing an inherited deep link stays on the page", page.url().startsWith(origin))

// Mount-time strip. A hash-only goto from the same page is a same-document
// navigation and would exercise popstate instead. about:blank forces a real
// document load so the mount effect is what runs.
await page.goto("about:blank")
await page.goto(`${url}#study=not-a-study`, { waitUntil: "networkidle", timeout: 45000 })
await page.waitForTimeout(300)
check("an unknown key is stripped on load", !page.url().includes("#study="))
check("an unknown key does not open a sheet", !(await page.getByRole("dialog").isVisible()))
check("an unknown-key load stays on the origin", page.url().startsWith(origin))
await page.keyboard.press("Escape")
await page.waitForTimeout(300)
check("Escape after a strip stays on the origin", page.url().startsWith(origin))

// Popstate strip. Plant the bad entry with pushState so the traversal is
// guaranteed same-document: a fragment-only goto can full-load, which would
// run the mount strip instead and make this check pass vacuously. Back lands
// on the entry behind the planted hash; Forward lands on the planted bad
// hash and the listener must strip it.
await page.evaluate(() => window.history.pushState(null, "", "#study=not-a-study"))
await page.waitForTimeout(300)
check("the planted bad hash is in the address bar", page.url().includes("#study=not-a-study"))
await page.goBack()
await page.waitForTimeout(300)
check("Back off a planted bad hash leaves no study hash", !page.url().includes("#study="))
await page.goForward()
await page.waitForTimeout(500)
check("Forward onto a planted bad hash strips it", !page.url().includes("#study="))
check("Forward onto a planted bad hash leaves the sheet closed", !(await page.getByRole("dialog").isVisible()))

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

await page.goto(url, { waitUntil: "networkidle", timeout: 45000 })
const buttons = page.locator("#matrix").getByRole("button")
const count = await buttons.count()
check("the matrix has studies to walk", count > 0)
for (let i = 0; i < count; i++) {
  await buttons.nth(i).click()
  await page.waitForTimeout(300)
  const open = page.getByRole("dialog")
  const heading = open.locator("h2").first()
  const linked = (await heading.locator("a").count()) === 1
  const requested = (await open.getByRole("link", { name: "Request access to this study" }).count()) === 1
  const claimsGitHub = (await open.getByText("(opens GitHub)").count()) > 0
  const key = (await heading.innerText()).replace(/\s*\(opens GitHub\)\s*$/, "").trim()
  if (linked) {
    const href = await heading.locator("a").getAttribute("href")
    check(`${key} links its own repository`, href !== null && (href === `https://github.com/systems-researcher/${key}` || href === `https://github.com/jgsystemsconsulting/${key}`))
    check(`${key} says it opens GitHub`, claimsGitHub)
    check(`${key} offers no request link`, !requested)
  } else {
    check(`${key} is closed text`, !claimsGitHub && requested)
  }
  await page.keyboard.press("Escape")
  await page.waitForTimeout(300)
}

await browser.close()
process.exit(failures ? 1 : 0)
