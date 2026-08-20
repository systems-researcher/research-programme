// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { ArrowUpRight } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import type { Entry, LinkRef, Strand } from "@/lib/map"

/** Everything about one repository, in a panel over the matrix.
 *
 * The matrix stays the page; this is what a cell opens. Detail that used to
 * make the page a scrolling wall of cards lives here instead. */

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  if (!children) return null
  return (
    <div>
      <dt className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
        {label}
      </dt>
      <dd className="mt-1 text-sm leading-relaxed text-foreground">{children}</dd>
    </div>
  )
}

function Refs({
  label,
  refs,
  onOpen,
}: {
  label: string
  refs: LinkRef[]
  onOpen: (key: string) => void
}) {
  if (!refs.length) return null
  return (
    <div>
      <dt className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
        {label}
      </dt>
      <dd className="mt-1.5 flex flex-wrap gap-1.5">
        {refs.map((ref) =>
          // A node-only target renders no cell of its own, so there is
          // nothing to navigate to; it stays plain text.
          ref.linkable ? (
            <button
              key={ref.key}
              type="button"
              onClick={() => onOpen(ref.key)}
              className="rounded border border-border bg-muted/40 px-1.5 py-0.5 font-mono text-[11px] text-foreground transition-colors hover:border-foreground/40 hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {ref.key}
            </button>
          ) : (
            <span
              key={ref.key}
              className="rounded border border-dashed border-border px-1.5 py-0.5 font-mono text-[11px] text-muted-foreground"
            >
              {ref.key}
            </span>
          ),
        )}
      </dd>
    </div>
  )
}

export function Detail({
  entry,
  strand,
  onOpenKey,
  onClose,
}: {
  entry: Entry | null
  strand: Strand | undefined
  onOpenKey: (key: string) => void
  onClose: () => void
}) {
  return (
    <Sheet open={!!entry} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full gap-0 overflow-y-auto sm:max-w-lg">
        {entry && (
          <>
            <SheetHeader className="space-y-0 border-b border-border pb-4">
              {strand && (
                <span className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                  <span
                    aria-hidden="true"
                    className="h-0.5 w-4 rounded-full"
                    style={{ backgroundColor: `var(--strand-${strand.token}-line)` }}
                  />
                  {strand.title}
                </span>
              )}
              <SheetTitle className="font-mono text-base leading-tight break-words">
                {entry.url ? (
                  <a
                    href={entry.url}
                    rel="noopener"
                    className="underline decoration-border underline-offset-4 hover:decoration-foreground"
                  >
                    {entry.key}
                    <ArrowUpRight aria-hidden="true" className="ml-0.5 inline size-3.5 align-text-top" />
                    <span className="sr-only">(opens GitHub)</span>
                  </a>
                ) : (
                  entry.key
                )}
              </SheetTitle>
              <SheetDescription asChild>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {(entry.badges ?? []).map((badge) => (
                    <Badge key={badge} variant="secondary" className="font-normal">
                      {badge}
                    </Badge>
                  ))}
                </div>
              </SheetDescription>
            </SheetHeader>

            <dl className="space-y-5 px-4 py-5">
              <Field label="What it is for">{entry.objective}</Field>
              <Field label="Question">{entry.question}</Field>
              <Field label="Method">{entry.method}</Field>

              {entry.headline && (
                <div
                  className="rounded-md border-l-2 bg-muted/40 py-3 pl-3 pr-3"
                  style={{
                    borderLeftColor: strand
                      ? `var(--strand-${strand.token}-line)`
                      : "var(--border)",
                  }}
                >
                  <dt className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                    Result
                  </dt>
                  <dd className="mt-1 text-sm leading-relaxed">
                    {entry.headline.text}
                    <span className="mt-1.5 block text-xs text-muted-foreground">
                      Source: {entry.headline.source}
                    </span>
                  </dd>
                </div>
              )}

              <Field label="Output">{entry.output}</Field>
              <Refs label="Depends on" refs={entry.dependsOn ?? []} onOpen={onOpenKey} />
              <Refs label="Feeds" refs={entry.feeds ?? []} onOpen={onOpenKey} />
            </dl>
          </>
        )}
      </SheetContent>
    </Sheet>
  )
}
