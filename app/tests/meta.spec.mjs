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

// A malformed ld+json block is silently ignored by every crawler, which is
// worse than none: it advertises structure it does not have.
const ldMatch = html.match(/<script type="application\/ld\+json">\s*([\s\S]*?)\s*<\/script>/)
if (!ldMatch) {
  console.log("  MISS application/ld+json block")
  failures += 1
} else {
  try {
    const ld = JSON.parse(ldMatch[1])
    const okType = ld["@type"] === "ResearchProject"
    console.log(`  ${okType ? "ok  " : "MISS"} ld+json @type ResearchProject`)
    if (!okType) failures += 1
  } catch (error) {
    console.log(`  MISS ld+json does not parse: ${error.message}`)
    failures += 1
  }
}

if (failures) {
  console.error(`\n${failures} preview tag(s) missing or malformed`)
  process.exit(1)
}
console.log("\npreview card metadata complete")
