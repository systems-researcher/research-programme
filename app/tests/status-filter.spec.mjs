// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// Clicking a legend stage dims non-matching tiles and nodes. The filter is
// session-only and must not remove a matrix button: the deep-link walk counts
// those buttons and clicks every one. Run against a built preview:
//   node tests/status-filter.spec.mjs "http://localhost:4173/research-programme/"
import { chromium } from "playwright"

const url = process.argv[2]
if (!url) {
  console.error("usage: node tests/status-filter.spec.mjs <url>")
  process.exit(2)
}

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
let failures = 0
const check = (name, ok) => {
  console.log(`${ok ? "pass" : "FAIL"}  ${name}`)
  if (!ok) failures += 1
}

const near = (value, target) => Math.abs(value - target) < 0.02

await page.goto(url, { waitUntil: "networkidle", timeout: 45000 })

const legendButtons = page.getByRole("button", { name: /^(design|built|released|results|published|retired), / })
const showAll = page.getByRole("button", { name: "Show all" })
const matrixButtons = page.locator("#matrix").getByRole("button")

// 1. On load: legend items are buttons, none pressed, Show all absent.
const legendCount = await legendButtons.count()
check("legend stages are buttons", legendCount >= 1)
let pressedOnLoad = 0
for (let i = 0; i < legendCount; i++) {
  if ((await legendButtons.nth(i).getAttribute("aria-pressed")) === "true") pressedOnLoad += 1
}
check("no legend stage is pressed on load", pressedOnLoad === 0)
check("Show all is absent on load", (await showAll.count()) === 0)

// 2. No filter class: matrix buttons and graph nodes at opacity 1.
const buttonCount = await matrixButtons.count()
const loadMatrix = await matrixButtons.evaluateAll((els) =>
  els.map((el) => Number(getComputedStyle(el).opacity)),
)
check("every matrix button starts at opacity 1", loadMatrix.every((v) => near(v, 1)))
const loadNodes = await page.locator("g.graph-node").evaluateAll((els) =>
  els.map((el) => ({
    name: el.getAttribute("aria-label") ?? "",
    opacity: Number(getComputedStyle(el).opacity),
  })),
)
check("every graph node starts at opacity 1", loadNodes.every((n) => near(n.opacity, 1)))
const nodeCount = loadNodes.length
// Graph edges only. The arrow marker in <defs> is also a path, and its
// computed opacity is 1, which is neither 0.75 nor 0.12.
const edgeCount = await page.locator("svg g.text-muted-foreground > path").count()

const stageButton = (word) =>
  page.getByRole("button", { name: new RegExp(`^${word}, `) })

// Status word is the uppercase tracking line on a card tile. The written
// column has no such line, so it never counts as a match.
async function matrixOpacityByWord(word) {
  return matrixButtons.evaluateAll((els, w) => {
    return els.map((el) => {
      const line = [...el.querySelectorAll("span")].find((span) =>
        span.className.includes("uppercase"),
      )
      const text = (line?.textContent ?? "").trim().toLowerCase()
      return {
        word: text,
        matches: text === w,
        opacity: Number(getComputedStyle(el).opacity),
      }
    })
  }, word)
}

async function graphState() {
  return page.evaluate(() => {
    const nodes = [...document.querySelectorAll("g.graph-node")].map((el) => {
      const name = el.getAttribute("aria-label") ?? ""
      const status = name.match(/\(([^)]+)\)/)?.[1] ?? ""
      const box = el.querySelector("rect")
      return {
        status,
        opacity: Number(getComputedStyle(el).opacity),
        dash: box?.getAttribute("stroke-dasharray") ?? "",
      }
    })
    const edges = [...document.querySelectorAll("svg g.text-muted-foreground > path")].map((el) =>
      Number(getComputedStyle(el).opacity),
    )
    return { nodes, edges }
  })
}

// 3-4. Click design. Only that stage is pressed. Matching tiles stay at 1.
// design, not built: the served payload has edges whose both ends are design,
// and edges with one design end. built has no both-ends edge, so a built click
// cannot satisfy the lit-edge assert below. The accessible name still starts
// with the status word, which is what the spec's step 3 asks for.
await stageButton("design").click()
await page.waitForTimeout(250)
check("design is pressed", (await stageButton("design").getAttribute("aria-pressed")) === "true")
let othersPressed = 0
for (const word of ["built", "released", "results", "published", "retired"]) {
  if ((await stageButton(word).getAttribute("aria-pressed")) === "true") othersPressed += 1
}
check("no other stage is pressed", othersPressed === 0)
check("Show all is present while design is selected", (await showAll.count()) === 1)

const designTiles = await matrixOpacityByWord("design")
const matched = designTiles.filter((t) => t.matches && !/papers? so far|written column/i.test(t.word))
const missed = designTiles.filter((t) => !t.matches && !/papers? so far|written column/i.test(t.word))
const written = designTiles.filter((t) => /papers? so far|written column/i.test(t.word))
check("at least one matrix tile reads design", matched.length >= 1)
check("design tiles stay at opacity 1", matched.every((t) => near(t.opacity, 1)))
check("non-design tiles dim to 0.4", missed.every((t) => near(t.opacity, 0.4)))
check("the written-column button is dimmed", written.length === 1 && near(written[0].opacity, 0.4))
check("matrix button count is unchanged", (await matrixButtons.count()) === buttonCount)

// 5. A dimmed card button still opens its sheet. Skip the written column:
// it is dimmed (no lifecycle badge) but it is not a study tile, and the
// canary the spec asks for is a study sheet.
const dimmedIndex = designTiles.findIndex((t) => !t.matches && !/papers? so far|written column/i.test(t.word))
check("a dimmed study tile exists", dimmedIndex >= 0)
await matrixButtons.nth(dimmedIndex).click()
await page.waitForTimeout(300)
check("a dimmed tile opens the sheet", await page.getByRole("dialog").isVisible())
await page.keyboard.press("Escape")
await page.waitForTimeout(300)
check("Escape closes the sheet", !(await page.getByRole("dialog").isVisible()))
check("Escape clears the hash", !page.url().includes("#study="))
check("the filter survives the sheet", (await stageButton("design").getAttribute("aria-pressed")) === "true")

// 6. Graph: design nodes lit, others at 0.25. Design dash stays on the lit
// nodes. A non-design node does not gain a dash.
const filtered = await graphState()
const designNodes = filtered.nodes.filter((n) => n.status === "design")
const otherNodes = filtered.nodes.filter((n) => n.status !== "design")
check("a design graph node exists", designNodes.length >= 1)
check("design nodes stay at opacity 1", designNodes.every((n) => near(n.opacity, 1)))
check("other nodes dim to 0.25", otherNodes.every((n) => near(n.opacity, 0.25)))
check("node count is unchanged", filtered.nodes.length === nodeCount)
check("edge count is unchanged", filtered.edges.length === edgeCount)
check("a lit design node keeps its dash", designNodes.every((n) => n.dash.includes("4")))
check("a non-design node does not gain a dash", otherNodes.every((n) => n.dash === ""))
// Dash is a design mark, not a filter mark: it survives dimming too. This is
// checked on the built selection in step 8, where design nodes are dimmed.
const litEdges = filtered.edges.filter((v) => near(v, 0.75))
const dimEdges = filtered.edges.filter((v) => near(v, 0.12))
check("some edge is lit at 0.75", litEdges.length >= 1)
check("some edge is dimmed at 0.12", dimEdges.length >= 1)
check("every edge is 0.75 or 0.12", litEdges.length + dimEdges.length === filtered.edges.length)

// 7. Click the pressed design button again. Reset.
await stageButton("design").click()
await page.waitForTimeout(250)
check("second click clears aria-pressed", (await stageButton("design").getAttribute("aria-pressed")) === "false")
check("Show all is absent after toggle off", (await showAll.count()) === 0)
const resetMatrix = await matrixButtons.evaluateAll((els) =>
  els.map((el) => Number(getComputedStyle(el).opacity)),
)
check("matrix opacities return to 1", resetMatrix.every((v) => near(v, 1)))
const resetGraph = await graphState()
check("graph nodes return to opacity 1", resetGraph.nodes.every((n) => near(n.opacity, 1)))

// 8. Click built, then Show all. Same reset. built is the second stage, so
// this is not a replay of the design click above.
await stageButton("built").click()
await page.waitForTimeout(250)
check("built is pressed", (await stageButton("built").getAttribute("aria-pressed")) === "true")
// The dash is a design mark, not a filter mark: a design node dimmed by the
// built selection keeps its stroke-dasharray.
const builtGraph = await graphState()
const dimmedDesign = builtGraph.nodes.filter((n) => n.status === "design")
check("a dimmed design node keeps its dash", dimmedDesign.length >= 1 && dimmedDesign.every((n) => n.dash.includes("4")))
await showAll.click()
await page.waitForTimeout(250)
check("Show all clears aria-pressed", (await stageButton("built").getAttribute("aria-pressed")) === "false")
check("Show all is absent after clear", (await showAll.count()) === 0)
const cleared = await graphState()
check("Show all restores node opacity", cleared.nodes.every((n) => near(n.opacity, 1)))

// 9. built then design: only design stays pressed. Single-select.
await stageButton("built").click()
await page.waitForTimeout(250)
await stageButton("design").click()
await page.waitForTimeout(250)
check("design replaces built", (await stageButton("design").getAttribute("aria-pressed")) === "true")
check("built is not pressed after design", (await stageButton("built").getAttribute("aria-pressed")) === "false")
const swapTiles = await matrixOpacityByWord("design")
const swapMatched = swapTiles.filter((t) => t.matches)
const swapMissed = swapTiles.filter((t) => !t.matches)
check("design tiles stay at opacity 1", swapMatched.length >= 1 && swapMatched.every((t) => near(t.opacity, 1)))
check("non-design tiles dim, so built did not stay lit", swapMissed.every((t) => near(t.opacity, 0.4)))
await showAll.click()
await page.waitForTimeout(250)

// 10. Keyboard: Enter presses, Enter again resets.
await stageButton("built").focus()
await page.keyboard.press("Enter")
await page.waitForTimeout(250)
check("Enter presses built", (await stageButton("built").getAttribute("aria-pressed")) === "true")
await page.keyboard.press("Enter")
await page.waitForTimeout(250)
check("Enter again resets built", (await stageButton("built").getAttribute("aria-pressed")) === "false")

// 11. Filter writes nothing to the URL.
const address = new URL(page.url())
check("no hash after filter clicks", address.hash === "")
check("no query after filter clicks", address.search === "")

await browser.close()
if (failures) {
  console.error(`\n${failures} status-filter check(s) failed`)
  process.exit(1)
}
console.log("\nstatus filter holds")
