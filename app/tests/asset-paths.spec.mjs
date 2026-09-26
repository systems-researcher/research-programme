// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// A root-absolute public path in JSX (src="/logo.svg") survives a prefixed
// build untouched — Vite rewrites HTML and imported assets, not string
// literals — and 404s on the project site. Source must reach public chrome
// through import.meta.env.BASE_URL instead. Before trusting the detector on
// the current tree, it proves itself against a known-bad revision:
//   node tests/asset-paths.spec.mjs 2d6db60   (control: must flag findings)
//   node tests/asset-paths.spec.mjs           (current: must find none)
import { execFileSync } from "node:child_process"
import { readdirSync, readFileSync } from "node:fs"
import { join } from "node:path"
import { fileURLToPath } from "node:url"

const controlRef = process.argv[2]
const appDir = fileURLToPath(new URL("..", import.meta.url))
const srcDir = join(appDir, "src")
const repoRoot = join(appDir, "..")

// Matches a quoted attribute value that opens with exactly one slash: a
// root-absolute public path. Template literals that start with ${ (the
// BASE_URL pattern) and protocol-relative or https:// values do not match.
const PATTERN = /\b(?:src|href)\s*=\s*(["'`])\/(?!\/)[^"'`]*\1/

function findingsIn(name, text) {
  return text
    .split("\n")
    .map((line, index) => ({ line: index + 1, text: line.trim(), hit: PATTERN.test(line) }))
    .filter((entry) => entry.hit)
    .map((entry) => `${name}:${entry.line}  ${entry.text}`)
}

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name)
    if (entry.isDirectory()) return walk(path)
    return /\.(tsx?|jsx?)$/.test(entry.name) ? [path] : []
  })
}

if (controlRef) {
  const before = execFileSync("git", ["show", `${controlRef}:app/src/App.tsx`], {
    cwd: repoRoot,
  }).toString()
  const findings = findingsIn(`${controlRef}:app/src/App.tsx`, before)
  if (findings.length === 0) {
    console.error(`control revision ${controlRef} produced no findings — the detector is blind`)
    process.exit(1)
  }
  for (const finding of findings) console.log(`  flagged ${finding}`)
  console.log(`asset-paths detector armed against control ${controlRef}`)
  process.exit(0)
}

const findings = walk(srcDir).flatMap((path) =>
  findingsIn(path, readFileSync(path, "utf8")),
)
if (findings.length > 0) {
  for (const finding of findings) console.log(`  root-absolute: ${finding}`)
  console.error(`\n${findings.length} root-absolute asset path(s) in app source`)
  process.exit(1)
}
console.log("asset-paths detector armed and app source clean")
