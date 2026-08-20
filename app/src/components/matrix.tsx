// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { Fragment } from "react"
import { BookOpen, ExternalLink } from "lucide-react"
import { cn } from "@/lib/utils"
import type { Entry, Stage, Status, Strand } from "@/lib/map"

/** The programme as a stage x strand matrix.
 *
 * This is a real <table>: five stages across, three strands down, with proper
 * scope="col" / scope="row" headers. It is a grid with headers on two axes,
 * which is what a table is for, and it is how a screen reader announces
 * "epistemic-adequacy-spec, Define, Epistemic adequacy" in one move.
 *
 * Only seven of the fifteen cells hold anything, and the empty ones are the
 * point: "method-validation has nothing at architecture yet" is a finding a
 * supervisor reads this page to get. Empty cells are rendered, never
 * collapsed, or the finding disappears. */

/** The one badge a cell has room for. Visibility and commit date are detail,
 *  and live in the sheet; status is what a reader scans the grid for.
 *
 *  The label is whatever the payload's status vocabulary calls it, so the
 *  cell and the legend below always read the same word. */
function cellStatus(entry: Entry, vocabulary: Set<string>): string | null {
  return (entry.badges ?? []).find((badge) => vocabulary.has(badge)) ?? null
}

function Cell({
  entries,
  strand,
  vocabulary,
  onOpen,
}: {
  entries: Entry[]
  strand: Strand
  vocabulary: Set<string>
  onOpen: (entry: Entry) => void
}) {
  if (!entries.length) {
    return (
      <td className="cell-empty border-b border-l border-border align-top">
        <span className="sr-only">Nothing at this stage</span>
      </td>
    )
  }

  return (
    <td className="border-b border-l border-border p-1.5 align-top">
      <div className="flex flex-col gap-1.5">
        {entries.map((entry) => {
          const status = cellStatus(entry, vocabulary)
          return (
            <button
              key={entry.key}
              type="button"
              onClick={() => onOpen(entry)}
              style={{ ["--accent" as string]: `var(--strand-${strand.token}-line)` }}
              className={cn(
                "cell-card group relative w-full rounded-md border p-2 text-left",
                "transition-colors focus-visible:outline-none",
              )}
            >
              {/* The strand's colour, as a spine rather than a whole-cell
                  wash: enough to group the row, quiet enough to read over. */}
              <span
                aria-hidden="true"
                className="cell-spine absolute inset-y-1 left-0 w-[3px] rounded-full opacity-80 group-hover:opacity-100"
              />
              <span className="block pl-2 font-mono text-[11px] leading-tight break-words text-foreground">
                {entry.key}
              </span>
              {/* Which cells have more than a repository behind them: a
                  published paper, or a result site to read. */}
              {(entry.paper || entry.site) && (
                <span className="mt-1 flex items-center gap-1 pl-2 text-muted-foreground">
                  {entry.paper && (
                    <>
                      <BookOpen aria-hidden="true" className="size-3" />
                      <span className="sr-only">Has a published paper.</span>
                    </>
                  )}
                  {entry.site && (
                    <>
                      <ExternalLink aria-hidden="true" className="size-3" />
                      <span className="sr-only">Has a published result site.</span>
                    </>
                  )}
                </span>
              )}
              {status && (
                <span className="mt-1 block pl-2 text-[10px] uppercase tracking-wider text-muted-foreground">
                  {status}
                </span>
              )}
            </button>
          )
        })}
      </div>
    </td>
  )
}

export function Matrix({
  strands,
  stages,
  statuses,
  onOpen,
}: {
  strands: Strand[]
  stages: Stage[]
  statuses: Status[]
  onOpen: (entry: Entry) => void
}) {
  const vocabulary = new Set(statuses.map((status) => status.label))

  return (
    // Five columns cannot fit a phone. Rather than inventing a second layout,
    // the table scrolls sideways with the strand column pinned, so the matrix
    // reading survives at any width.
    <div className="-mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0">
      <table className="w-full min-w-[56rem] border-separate border-spacing-0 text-sm">
        <caption className="sr-only">
          Research repositories by stage and strand. Stages run left to right;
          strands run top to bottom.
        </caption>
        <thead>
          <tr>
            <th
              scope="col"
              className="sticky left-0 z-20 w-56 border-b border-border bg-background pb-2 pr-4 text-left align-bottom"
            >
              <span className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
                Strand
              </span>
            </th>
            {stages.map((stage) => (
              <th
                key={stage.id}
                scope="col"
                className="border-b border-l border-border bg-background px-2 pb-2 text-left align-bottom"
              >
                <span className="block text-[10px] font-semibold uppercase tracking-widest text-foreground">
                  {stage.title}
                </span>
                <span className="mt-0.5 block text-[11px] font-normal leading-snug text-muted-foreground">
                  {stage.note}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {strands.map((strand) => (
            <Fragment key={strand.id}>
              <tr>
                <th
                  scope="row"
                  className="sticky left-0 z-10 border-b border-border bg-background py-3 pr-4 text-left align-top"
                >
                  <span
                    aria-hidden="true"
                    className="strand-rule mb-2 block h-1 w-8 rounded-full"
                    style={{ ["--accent" as string]: `var(--strand-${strand.token}-line)` }}
                  />
                  <span className="block text-xs font-semibold leading-tight text-foreground">
                    {strand.title}
                  </span>
                  {/* The strand's own question, hand-authored in repos.yml.
                      It is the reason the row exists, so it belongs beside
                      the name rather than only in the data. */}
                  <span className="mt-1.5 block text-[11px] font-normal leading-snug text-muted-foreground">
                    {strand.subtitle}
                  </span>
                </th>
                {stages.map((stage) => (
                  <Cell
                    key={stage.id}
                    strand={strand}
                    vocabulary={vocabulary}
                    entries={strand.entries.filter((e) => e.stage === stage.id)}
                    onOpen={onOpen}
                  />
                ))}
              </tr>
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  )
}
