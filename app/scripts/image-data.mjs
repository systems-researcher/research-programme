// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// Every value the generated images draw, derived from data/map.json.
//
// The generators render these into PNGs; CI recomputes them and diffs the
// result against the committed manifests. That is why this lives apart from
// the generators: the check must run without a browser, because a rendered
// PNG is not reproducible across platforms — Windows and Linux rasterise the
// same text to different bytes, so comparing pixels reports drift that is not
// there. Comparing the values instead is text derived from text, identical
// everywhere.
//
// Anything an image displays belongs in here. A field the image draws but the
// manifest omits can drift without the check noticing.
import { readFileSync } from "node:fs"
import { resolve } from "node:path"

export const SITE = "systems-researcher.github.io/research-programme"

// The strand colours the site defines as --strand-<token>-line. Transcribed
// because a headless page has no stylesheet to read them from.
const STRAND_COLOUR = {
  adequacy: "oklch(0.55 0.16 250)",
  method: "oklch(0.55 0.17 305)",
  formalisation: "oklch(0.52 0.12 165)",
}

export function readMap() {
  return JSON.parse(
    readFileSync(resolve(import.meta.dirname, "../../data/map.json"), "utf8"),
  )
}

/** Everything the banner and the preview card draw.
 *
 * A strand whose token has no colour here throws rather than rendering an
 * invisible rule — silence would be the failure nobody notices. */
export function imageData(map = readMap()) {
  const strands = map.strands.map((strand) => {
    const colour = STRAND_COLOUR[strand.token]
    if (!colour) {
      throw new Error(
        `strand "${strand.id}" has token "${strand.token}", which has no colour here. ` +
          `Add it to STRAND_COLOUR in scripts/image-data.mjs, matching ` +
          `--strand-${strand.token}-line in app/src/index.css.`,
      )
    }
    return {
      title: strand.title,
      colour,
      studies: strand.entries.filter((entry) => entry.card).length,
    }
  })

  return {
    title: map.programme.title,
    site: SITE,
    strands,
    studies: strands.reduce((total, strand) => total + strand.studies, 0),
    published: map.strands
      .flatMap((strand) => strand.entries)
      .filter((entry) => entry.paper).length,
  }
}

/** The manifest text, so the generators and the check produce it identically. */
export function manifest(data = imageData()) {
  return JSON.stringify(data, null, 2) + "\n"
}

// `node scripts/image-data.mjs --check` — used by CI. Recomputes the manifest
// from data/map.json and compares it against the committed one, so a data
// change that was not followed by regenerating the images fails the build.
if (process.argv.includes("--check")) {
  const { readFileSync: read } = await import("node:fs")
  const path = resolve(import.meta.dirname, "../public/images.manifest.json")
  const expected = manifest()

  let committed
  try {
    committed = read(path, "utf8")
  } catch {
    console.error("::error::app/public/images.manifest.json is missing.")
    console.error("Run 'npm --prefix app run banner' and commit the result.")
    process.exit(1)
  }

  if (committed !== expected) {
    console.error("::error::The generated images are stale.")
    console.error(
      "Run 'npm --prefix app run banner' and 'npm --prefix app run preview:card', then commit the result.",
    )
    console.error("\nCommitted:\n" + committed + "\nFrom data/map.json:\n" + expected)
    process.exit(1)
  }
  console.log("generated images match data/map.json")
}
