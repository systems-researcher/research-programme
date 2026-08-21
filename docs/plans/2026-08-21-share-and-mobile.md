<!--
Copyright (c) 2026 Jason D. Gower
SPDX-License-Identifier: CC-BY-4.0
-->

# Social Preview and Mobile Overflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the programme map shareable — a real preview card when the link is pasted, and a page that does not slide sideways on a phone.

**Architecture:** Two independent defects in the published site. The preview card is static metadata in `app/index.html` plus a generated PNG in `app/public/`, so it needs no React change. The overflow is a CSS containment bug: `matrix.tsx` and `graph.tsx` both wrap wide content in `-mx-4 overflow-x-auto px-4`, which makes the wrapper *wider* than its parent, so `overflow-x-auto` has nothing to clip against and the child escapes to the document. Both are fixed by containing the scroller within the padded column instead of fighting it.

**Tech Stack:** Vite 8, React 19, Tailwind v4, TypeScript 6, Playwright (dev-only, for verification), Python 3.13 + pytest for the data/link guards.

**Spec:** No separate spec document. This plan is the specification; the two defects were established empirically and the evidence is recorded in each task's "Why" block.

## Global Constraints

- **Do not add runtime dependencies.** The page currently contacts no host but `github.com`. `tests/check_external_links.py` enforces this and must keep passing.
- **Playwright is dev-only and must not be committed.** Install it for verification, then `npm --prefix app uninstall playwright` and `git checkout -- app/package-lock.json` before committing. It has leaked into `package.json` before.
- **Every file carries an SPDX header** matching its neighbours (`// SPDX-License-Identifier: MIT` for code, `CC-BY-4.0` for prose).
- **`repos.yml` and `data/map.json` are owned by another agent in this repo.** Do not stage them. Commit only the files each task names.
- **Verify on the built output, not the dev server**, wherever a task's check concerns metadata or layout. `npm --prefix app run build` writes to `site/`.
- **Branch:** work on `main`. Rebase before pushing (`git pull --rebase origin main`), and push as the `systems-researcher` account (`gh auth switch --user systems-researcher`) — the git credential helper intermittently reverts to `jgsystemsconsulting`, which is denied.
- **The site auto-deploys** from `main` via `.github/workflows/pages.yml`. A push is a publish.

---

### Task 1: Contain the horizontal scroll on mobile

**Files:**
- Modify: `app/src/components/matrix.tsx:155`
- Modify: `app/src/components/graph.tsx:146`
- Test: `app/tests/layout.spec.mjs` (create)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `app/tests/layout.spec.mjs`, a standalone Node script run as `node tests/layout.spec.mjs <url>`. Task 2 does not depend on it.

**Why:** Measured on the live site at a 390px viewport: `document.documentElement.scrollWidth` is 787 against a `clientWidth` of 390. Walking the DOM for elements whose right edge exceeds the viewport, and keeping only those whose parent does *not* overflow, isolates two culprits — the matrix `<table>` (right edge 912) and the graph `<svg>` (right edge 1816). Both sit inside `<div className="-mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0">`. The negative margin pulls the wrapper 1rem wider than `<main>` on each side and the padding restores the visual inset, so the wrapper itself is wider than the viewport. `overflow-x-auto` clips a child against its own box, and that box already extends past the screen — so nothing is clipped and the child pushes the document wide.

- [ ] **Step 1: Write the failing test**

Create `app/tests/layout.spec.mjs`:

```javascript
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
```

- [ ] **Step 2: Run it to make sure it fails**

```bash
cd app && npm install -D playwright && npx playwright install chromium
npm run dev &
node tests/layout.spec.mjs http://localhost:5173/
```

Expected: FAIL — `390px: scrollWidth 787 vs 390 — FAIL`, listing `TABLE.w-full min-w-[56rem]…` and `svg…` as escaping.

- [ ] **Step 3: Contain the matrix scroller**

In `app/src/components/matrix.tsx`, replace the wrapper `<div>` on line 155:

```tsx
    // The scroller must be no wider than the column that holds it, or
    // overflow-x-auto has nothing to clip against and the table escapes to
    // the document. Bleeding to the screen edge is done with padding inside
    // the scroller rather than a negative margin outside it.
    <div className="overflow-x-auto">
```

- [ ] **Step 4: Contain the graph scroller**

In `app/src/components/graph.tsx`, replace the wrapper `<div>` on line 146 with the identical containment (the SVG is rendered at natural size and must scroll, not shrink):

```tsx
    // Same containment as the matrix: the scroller is bounded by its column,
    // so the graph scrolls inside it rather than widening the page.
    <div className="overflow-x-auto">
```

- [ ] **Step 5: Run the test to verify it passes**

```bash
cd app && node tests/layout.spec.mjs http://localhost:5173/
```

Expected: PASS — `390px … ok`, `768px … ok`, `1440px … ok`, then `no viewport scrolls sideways`.

- [ ] **Step 6: Confirm the content still scrolls rather than being cut off**

```bash
cd app && node -e "
import('playwright').then(async ({chromium}) => {
  const b = await chromium.launch()
  const p = await b.newPage({viewport:{width:390,height:844}})
  await p.goto('http://localhost:5173/',{waitUntil:'networkidle'})
  await p.waitForTimeout(600)
  const r = await p.evaluate(() => {
    const s = document.querySelector('table').closest('div')
    return {scrollable: s.scrollWidth > s.clientWidth, tiles: document.querySelectorAll('tbody button').length}
  })
  console.log('matrix scrolls inside its own box:', r.scrollable)
  console.log('tiles still rendered:', r.tiles)
  await b.close()
})"
```

Expected: `matrix scrolls inside its own box: true` and a non-zero tile count matching the payload (16 at time of writing). A `false` on the first line would mean the table was squashed rather than contained.

- [ ] **Step 7: Verify the full suite and build are unaffected**

```bash
cd .. && python -m pytest -q && npm --prefix app run build && python tests/check_external_links.py
```

Expected: `74 passed`, `✓ built in …`, and the link check reporting `14 outbound links across 2 permitted hosts`.

- [ ] **Step 8: Remove Playwright and commit**

```bash
npm --prefix app uninstall playwright
git checkout -- app/package-lock.json
git add app/src/components/matrix.tsx app/src/components/graph.tsx app/tests/layout.spec.mjs
git commit -m "fix(site): stop the page scrolling sideways on a phone

The matrix table and the dependency graph both sat in a
'-mx-4 overflow-x-auto px-4' wrapper. The negative margin makes that wrapper
wider than the viewport, so overflow-x-auto has nothing to clip against and
the child pushes the whole document wide: 787px of scrollWidth against a
390px screen.

Both scrollers are now bounded by the column that holds them, so the wide
content scrolls inside its own box as intended. tests/layout.spec.mjs asserts
no viewport scrolls sideways, and that the matrix still scrolls internally
rather than being squashed."
```

---

### Task 2: Generate the social preview image

**Files:**
- Create: `app/scripts/preview.mjs`
- Create: `app/public/preview.png` (generated, committed)
- Modify: `app/package.json` (add the `preview` script)

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `app/public/preview.png` at exactly 1200×630, served at `/research-programme/preview.png`. Task 3 references that path.

**Why:** Pasting the site link into Slack, Teams, LinkedIn or an email renders a bare URL — the built `site/index.html` contains zero `og:` or `twitter:` tags. The page's stated purpose is being shared with colleagues, so this is the defect that most undercuts it. The image is generated from the page's own tokens rather than hand-drawn, so it cannot drift from the site's typography and palette.

- [ ] **Step 1: Write the generator**

Create `app/scripts/preview.mjs`:

```javascript
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
const out = resolve(import.meta.dirname, "../public/preview.png")
writeFileSync(out, await page.screenshot({ type: "png" }))
await browser.close()
console.log(`wrote ${out} (1200x630, ${studies} studies)`)
```

- [ ] **Step 2: Add the npm script**

In `app/package.json`, add to `"scripts"` (keep the existing entries):

```json
    "preview": "node scripts/preview.mjs"
```

- [ ] **Step 3: Generate the image**

```bash
cd app && npm install -D playwright && npm run preview
```

Expected: `wrote …/app/public/preview.png (1200x630, 15 studies)`. The count is read from the payload at generation time, so a different number simply means the programme has grown — not a failure.

- [ ] **Step 4: Verify the dimensions are exactly 1200×630**

Platforms crop anything else.

```bash
cd app && node -e "
const b=require('fs').readFileSync('public/preview.png')
console.log('PNG:', b.slice(1,4).toString()==='PNG')
console.log('width:', b.readUInt32BE(16), 'height:', b.readUInt32BE(20))
console.log('size:', Math.round(b.length/1024)+'KB')"
```

Expected: `PNG: true`, `width: 1200 height: 630`, and a size under 1MB (platforms reject larger).

- [ ] **Step 5: Look at it**

Open `app/public/preview.png` and confirm the title is legible, nothing is clipped at the edges, and the three strand rules are visible. If the font failed to load the type will fall back to system sans — acceptable, but re-run once with a network connection if so.

- [ ] **Step 6: Commit**

```bash
npm --prefix app uninstall playwright
git checkout -- app/package-lock.json
git add app/scripts/preview.mjs app/public/preview.png app/package.json
git commit -m "feat(site): generate the social preview card

Drawn from data/map.json with the site's own tokens and type, so the card
cannot drift from the page it advertises: same Geist, same neutral ground,
same three strand colours, and a study count read from the payload rather
than typed in.

Exactly 1200x630, which is what every platform crops to."
```

---

### Task 3: Serve the preview card metadata

**Files:**
- Modify: `app/index.html:3-11`
- Test: `app/tests/meta.spec.mjs` (create)

**Interfaces:**
- Consumes: `app/public/preview.png` from Task 2, served at `/research-programme/preview.png`.
- Produces: nothing later tasks rely on.

**Why:** The image alone does nothing — a platform reads `og:image`. Absolute URLs are required: Slack, LinkedIn and Twitter all reject a relative `og:image`. The canonical URL is `https://systems-researcher.github.io/research-programme/`, confirmed live and returning HTTP 200.

- [ ] **Step 1: Write the failing test**

Create `app/tests/meta.spec.mjs`:

```javascript
// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// A pasted link must render as a card, not a bare URL. Checks the built page,
// because these tags are static and only the build output is published:
//   node tests/meta.spec.mjs ../site/index.html
import { readFileSync } from "node:fs"

const file = process.argv[2] ?? "../site/index.html"
const html = readFileSync(file, "utf8")

const REQUIRED = [
  ["og:title", /property="og:title" content="[^"]{10,}"/],
  ["og:description", /property="og:description" content="[^"]{40,}"/],
  ["og:image", /property="og:image" content="https:\/\/[^"]+\.png"/],
  ["og:url", /property="og:url" content="https:\/\/[^"]+"/],
  ["og:type", /property="og:type" content="website"/],
  ["twitter:card", /name="twitter:card" content="summary_large_image"/],
  ["twitter:image", /name="twitter:image" content="https:\/\/[^"]+\.png"/],
]

let failures = 0
for (const [name, pattern] of REQUIRED) {
  const ok = pattern.test(html)
  console.log(`  ${ok ? "ok  " : "MISS"} ${name}`)
  if (!ok) failures += 1
}

// A relative og:image is silently dropped by every major platform.
if (/property="og:image" content="\//.test(html)) {
  console.log("  MISS og:image is relative; it must be an absolute https URL")
  failures += 1
}

if (failures) {
  console.error(`\n${failures} preview tag(s) missing or malformed`)
  process.exit(1)
}
console.log("\npreview card metadata complete")
```

- [ ] **Step 2: Run it to make sure it fails**

```bash
cd app && npm run build && node tests/meta.spec.mjs ../site/index.html
```

Expected: FAIL — every tag reported `MISS`, then `7 preview tag(s) missing or malformed`.

- [ ] **Step 3: Add the tags**

In `app/index.html`, insert immediately after the existing `<meta name="description" …>` block:

```html
    <!-- Preview card. Absolute URLs: Slack, LinkedIn and Twitter all drop a
         relative og:image. The path carries the /research-programme/ prefix
         because this is a GitHub Pages project site, not a domain root. -->
    <meta property="og:type" content="website" />
    <meta
      property="og:url"
      content="https://systems-researcher.github.io/research-programme/"
    />
    <meta
      property="og:title"
      content="Architecting Trustworthy AI Integration in MBSE"
    />
    <meta
      property="og:description"
      content="A doctoral research programme mapped: what each study asks, how they depend on each other, and what has entered the written record."
    />
    <meta
      property="og:image"
      content="https://systems-researcher.github.io/research-programme/preview.png"
    />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:site_name" content="Loughborough University" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta
      name="twitter:title"
      content="Architecting Trustworthy AI Integration in MBSE"
    />
    <meta
      name="twitter:description"
      content="A doctoral research programme mapped: what each study asks, how they depend on each other, and what has entered the written record."
    />
    <meta
      name="twitter:image"
      content="https://systems-researcher.github.io/research-programme/preview.png"
    />
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
cd app && npm run build && node tests/meta.spec.mjs ../site/index.html
```

Expected: PASS — every tag `ok`, then `preview card metadata complete`.

- [ ] **Step 5: Confirm the image ships in the build**

```bash
cd .. && ls -la site/preview.png && python tests/check_external_links.py
```

Expected: the file exists at ~50–200KB, and the link check still reports `14 outbound links across 2 permitted hosts` — the `og:` URLs point at this same origin, so the permitted-host set does not change. If the count rises, a tag has the wrong host.

- [ ] **Step 6: Commit**

```bash
git add app/index.html app/tests/meta.spec.mjs
git commit -m "feat(site): render a preview card when the link is shared

Pasting the URL into Slack, Teams, LinkedIn or an email produced a bare
string: the built page carried no og: or twitter: tags at all. For a page
whose whole job is being sent to colleagues, that was the defect most
undercutting it.

Absolute URLs throughout — every major platform silently drops a relative
og:image — and the /research-programme/ prefix because this is a project
Pages site rather than a domain root. tests/meta.spec.mjs asserts the tags
exist in the built output and that og:image is absolute."
```

---

### Task 4: Publish and verify against the live site

**Files:**
- Modify: none (verification and deployment only)

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: nothing.

**Why:** Every check so far ran locally. The site is served from GitHub Pages under a `/research-programme/` path prefix, and the preview image is fetched by third-party crawlers over the public internet — neither is exercised by a local build. A tag that resolves locally can still 404 in production.

- [ ] **Step 1: Push**

```bash
gh auth switch --user systems-researcher
git pull --rebase origin main
git push origin main
```

Expected: the push succeeds. If it is denied for `jgsystemsconsulting`, re-run the `gh auth switch` and push again — the credential helper reverts intermittently.

- [ ] **Step 2: Wait for the deploy**

```bash
sleep 12
RID=$(gh run list --repo systems-researcher/research-programme --workflow pages.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RID" --repo systems-researcher/research-programme --exit-status --interval 10
gh run view "$RID" --repo systems-researcher/research-programme --json conclusion,headSha --jq '"\(.conclusion) @ \(.headSha[0:7])"'
```

Expected: `success @ <the sha you just pushed>`. A success against an *older* sha means you are reading the previous run — re-query.

- [ ] **Step 3: Verify the preview image is publicly fetchable**

```bash
curl -s -o /dev/null -w "preview.png: HTTP %{http_code}  %{content_type}  %{size_download} bytes\n" \
  -L --max-time 30 "https://systems-researcher.github.io/research-programme/preview.png"
```

Expected: `HTTP 200  image/png` and a non-zero size. A 404 means the file did not ship in `app/public/`.

- [ ] **Step 4: Verify the tags as a crawler sees them**

Crawlers read the raw HTML without executing JavaScript, so `curl` is the honest check.

```bash
curl -s -L --max-time 30 "https://systems-researcher.github.io/research-programme/" \
  | grep -oE '<meta (property|name)="(og|twitter):[^"]*" content="[^"]*"'
```

Expected: all twelve tags, with both image URLs absolute and beginning `https://systems-researcher.github.io/research-programme/`.

- [ ] **Step 5: Verify the live site does not scroll sideways**

```bash
cd app && npm install -D playwright
node tests/layout.spec.mjs https://systems-researcher.github.io/research-programme/
npm uninstall playwright && git checkout -- ../app/package-lock.json
```

Expected: `no viewport scrolls sideways` across all three widths.

- [ ] **Step 6: Confirm nothing regressed**

```bash
cd .. && python -m pytest -q && python -m scripts.build --check && python tests/mutate_check.py
```

Expected: `74 passed`, `all ten rules pass`, `validator bites on all 4 mutations`. Do not stage `repos.yml` or `data/map.json` if `--check` regenerates them — they belong to another agent.

---

## Notes for the executor

- **The dev server may already be running** on port 5173 from an earlier session. `curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/` before starting another.
- **Two agents share this repository.** Run `git status --short` before every commit and stage only the files the task names. `repos.yml`, `data/map.json` and `README.md` are frequently modified by the other agent mid-task.
- **`docs/superpowers/` is gitignored**; `docs/plans/` is tracked. This plan lives in the tracked directory deliberately.
- **If Task 1's fix squashes the table rather than containing it** — Step 6 reports `matrix scrolls inside its own box: false` — the cause is a parent with `min-width` rather than the wrapper. Check `<main>` in `app/src/App.tsx:98` before changing the table's own `min-w-[56rem]`, which is load-bearing for column widths.
