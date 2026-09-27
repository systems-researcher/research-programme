// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import type { Status } from "@/lib/map"

/** What the status badges mean, in the order a study moves through them.
 *
 * Generated from the same enum the validator uses, so the key on the page
 * cannot document a vocabulary the data does not have. A state with no study
 * in it is still shown — that a stage is defined and unoccupied is itself
 * worth reading. */
export function Legend({
  statuses,
  counts,
  selectedStatusId,
  onSelectStatus,
}: {
  statuses: Status[]
  counts: Record<string, number>
  selectedStatusId: string | null
  onSelectStatus: (id: string | null) => void
}) {
  return (
    <section className="border-t border-border py-8">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-foreground">
          How a study progresses
        </h2>
        {selectedStatusId !== null && (
          <button
            type="button"
            onClick={() => onSelectStatus(null)}
            className="text-[11px] font-medium text-muted-foreground underline decoration-border underline-offset-4 hover:text-foreground hover:decoration-foreground"
          >
            Show all
          </button>
        )}
      </div>
      <p className="mt-1.5 max-w-3xl text-xs text-muted-foreground">
        Every repository carries one of these. They run in order: a study is
        designed, built, released for others to depend on, run for record, and
        written up.
      </p>

      <ol className="mt-5 grid gap-px overflow-hidden rounded-md border border-border bg-border sm:grid-cols-2 lg:grid-cols-5">
        {statuses.map((status, index) => {
          const count = counts[status.id] ?? 0
          return (
            <li key={status.id} className="flex flex-col bg-card">
              <button
                type="button"
                aria-pressed={selectedStatusId === status.id}
                aria-label={`${status.label}, ${count}`}
                onClick={() =>
                  onSelectStatus(selectedStatusId === status.id ? null : status.id)
                }
                className={
                  selectedStatusId === status.id
                    ? "flex h-full flex-col p-3 text-left ring-2 ring-ring ring-inset"
                    : "flex h-full flex-col p-3 text-left"
                }
              >
                <div className="flex items-baseline justify-between gap-2">
                  <span className="font-mono text-[10px] text-muted-foreground">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span
                    className={
                      count
                        ? "font-mono text-xs tabular-nums text-foreground"
                        : "font-mono text-xs tabular-nums text-muted-foreground/50"
                    }
                  >
                    {count}
                  </span>
                </div>
                <span className="mt-1.5 text-xs font-semibold capitalize text-foreground">
                  {status.label}
                </span>
                <span className="mt-1 text-[11px] leading-snug text-muted-foreground">
                  {status.note}
                </span>
                {count === 0 && (
                  <span className="mt-2 text-[10px] uppercase tracking-wider text-muted-foreground/70">
                    No study here yet
                  </span>
                )}
              </button>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
