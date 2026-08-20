// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { useState } from "react"
import { Check, Copy, ExternalLink } from "lucide-react"
import type { Paper } from "@/lib/map"

/** A paper, cited as the published record actually has it.
 *
 * Two rules this component exists to keep:
 *
 * 1. Every author is named. Exporting a co-authored paper's citation with no
 *    author list credits nobody.
 * 2. An accepted paper's DOI is shown as text, not as a link. It does not
 *    resolve until the venue posts the proceedings, and a citation block that
 *    links to a 404 is worse than one that says "not yet". */

function bibtex(paper: Paper, key: string): string {
  const id = key.replace(/[^A-Za-z0-9]/g, "") + paper.year
  // Fields are assembled without trailing commas, then joined with them, so
  // an optional field can never leave the entry unparseable.
  const fields = [
    `  title     = {${paper.title}}`,
    `  author    = {${paper.authors.join(" and ")}}`,
    `  booktitle = {${paper.venue}}`,
    `  year      = {${paper.year}}`,
    `  doi       = {${paper.doi}}`,
  ]
  // Say so in the export too: a reference manager should not silently
  // imply the proceedings are out.
  const state = paper.status.replace(/-/g, " ").replace(/^./, (c) => c.toUpperCase())
  if (paper.status !== "published") {
    fields.push(`  note      = {${state}; DOI resolves on publication}`)
  }
  return `@inproceedings{${id},\n${fields.join(",\n")}\n}`
}

export function Citation({ paper, entryKey }: { paper: Paper; entryKey: string }) {
  const [copied, setCopied] = useState(false)
  const live = paper.status === "published"

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(bibtex(paper, entryKey))
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard is unavailable over plain http or without permission. The
      // citation is still readable on the page, so this stays quiet.
    }
  }

  return (
    <div className="rounded-md border border-border bg-muted/40 p-3">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
        {paper.status.replace(/-/g, " ")}
      </p>
      <p className="mt-1.5 text-sm font-medium leading-snug text-foreground">{paper.title}</p>
      <p className="mt-1 text-xs leading-snug text-muted-foreground">
        {paper.authors.join("; ")}
      </p>
      <p className="mt-1 text-xs leading-snug text-muted-foreground">
        {paper.venue} · {paper.year}
      </p>

      <div className="mt-2.5 flex flex-wrap items-center gap-2">
        {live ? (
          <a
            href={`https://doi.org/${paper.doi}`}
            rel="noopener"
            className="inline-flex items-center gap-1 rounded border border-border bg-background px-2 py-1 font-mono text-[11px] transition-colors hover:border-foreground/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {paper.doi}
            <ExternalLink aria-hidden="true" className="size-3" />
            <span className="sr-only">(resolves the DOI)</span>
          </a>
        ) : (
          <span className="inline-flex items-center gap-1.5 rounded border border-dashed border-border px-2 py-1 font-mono text-[11px] text-muted-foreground">
            {paper.doi}
            <span className="font-sans not-italic">— resolves on publication</span>
          </span>
        )}
        <button
          type="button"
          onClick={copy}
          className="inline-flex items-center gap-1 rounded border border-border bg-background px-2 py-1 text-[11px] transition-colors hover:border-foreground/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          {copied ? (
            <Check aria-hidden="true" className="size-3" />
          ) : (
            <Copy aria-hidden="true" className="size-3" />
          )}
          {copied ? "Copied" : "BibTeX"}
        </button>
      </div>
    </div>
  )
}
