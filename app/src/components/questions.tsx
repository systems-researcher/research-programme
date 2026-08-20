// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import type { Entry, Status, Strand } from "@/lib/map"

/** The programme's argument, in words.
 *
 * The matrix says where each study sits; this says what it is for. The
 * question leads because it is the thing being asked, and the objective
 * answers it — what the study establishes if the question resolves.
 *
 * Grouped by strand rather than listed flat, and shown in full rather than
 * truncated: a colleague reading the page should be able to follow the
 * argument without opening twelve detail sheets. */

function cellStatus(entry: Entry, vocabulary: Set<string>): string | null {
  return (entry.badges ?? []).find((badge) => vocabulary.has(badge)) ?? null
}

export function Questions({
  strands,
  statuses,
  onOpen,
}: {
  strands: Strand[]
  statuses: Status[]
  onOpen: (entry: Entry) => void
}) {
  const vocabulary = new Set(statuses.map((status) => status.label))
  const groups = strands
    .map((strand) => ({ strand, studies: strand.entries.filter((e) => e.card) }))
    .filter((group) => group.studies.length)

  return (
    <section id="questions" className="scroll-mt-4 border-t border-border py-10">
      <div className="mb-6 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-foreground">
          What each study asks
        </h2>
        <p className="text-xs text-muted-foreground">
          The question, and what answering it establishes.
        </p>
      </div>

      <div className="space-y-10">
        {groups.map(({ strand, studies }) => (
          <div key={strand.id}>
            <div className="flex items-center gap-2.5">
              <span
                aria-hidden="true"
                className="h-1 w-8 shrink-0 rounded-full"
                style={{ backgroundColor: `var(--strand-${strand.token}-line)` }}
              />
              <h3 className="text-sm font-semibold tracking-tight text-foreground">
                {strand.title}
              </h3>
            </div>
            <p className="mt-1.5 max-w-3xl text-xs leading-snug text-muted-foreground">
              {strand.subtitle}
            </p>

            <ul className="mt-4 border-t border-border">
              {studies.map((entry) => {
                const status = cellStatus(entry, vocabulary)
                return (
                  <li key={entry.key} className="border-b border-border">
                    <button
                      type="button"
                      onClick={() => onOpen(entry)}
                      style={{
                        ["--accent" as string]: `var(--strand-${strand.token}-line)`,
                      }}
                      className="group w-full py-4 pl-4 pr-2 text-left transition-colors hover:bg-muted/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-inset"
                    >
                      {/* The strand's colour, on the same left edge the matrix
                          tiles use, so the two views read as one system. */}
                      <span className="relative block">
                        <span
                          aria-hidden="true"
                          className="absolute -left-4 top-0.5 h-[calc(100%-0.25rem)] w-[3px] rounded-full bg-[--accent] opacity-0 transition-opacity group-hover:opacity-70"
                        />
                        <span className="block max-w-3xl text-[0.9375rem] font-medium leading-snug tracking-tight text-foreground">
                          {entry.question}
                        </span>
                        <span className="mt-2 block max-w-2xl text-[13px] leading-relaxed text-muted-foreground">
                          {entry.objective}
                        </span>
                        <span className="mt-2 flex flex-wrap items-baseline gap-x-3 gap-y-1">
                          <span className="font-mono text-[11px] text-muted-foreground">
                            {entry.key}
                          </span>
                          {status && (
                            <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                              {status}
                            </span>
                          )}
                        </span>
                      </span>
                    </button>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </div>
    </section>
  )
}
