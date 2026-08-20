// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { useState } from "react"
import { Check, Copy, ExternalLink } from "lucide-react"
import type { Paper } from "@/lib/map"

/** A paper, cited properly.
 *
 * The DOI is the strongest claim on this page: it says the work is in the
 * published record. It used to sit mid-sentence inside a prose field, which
 * is not something a reader can act on. Here it resolves, and the BibTeX is
 * one click from a reference manager. */

function bibtex(paper: Paper, key: string): string {
  return [
    `@inproceedings{${key.replace(/[^A-Za-z0-9]/g, "")}${paper.year},`,
    `  title     = {${paper.title}},`,
    `  booktitle = {${paper.venue}},`,
    `  year      = {${paper.year}},`,
    `  doi       = {${paper.doi}}`,
    `}`,
  ].join("\n")
}

export function Citation({ paper, entryKey }: { paper: Paper; entryKey: string }) {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(bibtex(paper, entryKey))
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard is unavailable over plain http or without permission. The
      // DOI link still works, so this stays quiet rather than alarming.
    }
  }

  return (
    <div className="rounded-md border border-border bg-muted/40 p-3">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
        Published
      </p>
      <p className="mt-1.5 text-sm font-medium leading-snug text-foreground">{paper.title}</p>
      <p className="mt-1 text-xs text-muted-foreground">
        {paper.venue} · {paper.year}
      </p>
      <div className="mt-2.5 flex flex-wrap items-center gap-2">
        <a
          href={`https://doi.org/${paper.doi}`}
          rel="noopener"
          className="inline-flex items-center gap-1 rounded border border-border bg-background px-2 py-1 font-mono text-[11px] transition-colors hover:border-foreground/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          {paper.doi}
          <ExternalLink aria-hidden="true" className="size-3" />
          <span className="sr-only">(resolves the DOI)</span>
        </a>
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
