// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { Citation } from "@/components/citation"
import type { Entry } from "@/lib/map"

/** The written column: what the programme has put into the record.
 *
 * One row per study that has a paper. Today that is one study of twelve,
 * which is the true state of the programme rather than a rendering fault.
 * It uses the same Citation component the detail sheet does, so there is one
 * place that decides whether a DOI is safe to link. */
export function Publications({ entries }: { entries: Entry[] }) {
  const papers = entries.filter((entry) => entry.paper)
  // The written column is not a study, so it is not part of the denominator.
  const studies = entries.filter((entry) => entry.card)

  return (
    <section id="publications" className="scroll-mt-4 border-t border-border py-10">
      <div className="mb-5 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-foreground">
          Publications
        </h2>
        <p className="text-xs text-muted-foreground">
          {papers.length} of {studies.length} studies have entered the record.
        </p>
      </div>

      {papers.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          Nothing published yet.
        </p>
      ) : (
        <ul className="grid gap-4 lg:grid-cols-2">
          {papers.map((entry) => (
            <li key={entry.key}>
              <p className="mb-1.5 font-mono text-[11px] text-muted-foreground">
                {entry.key}
              </p>
              <Citation paper={entry.paper!} entryKey={entry.key} />
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
