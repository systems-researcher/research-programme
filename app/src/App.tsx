// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { useCallback, useEffect, useMemo, useState } from "react"
import { Monitor, Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Detail } from "@/components/detail"
import { DependencyGraph } from "@/components/graph"
import { GetInvolved } from "@/components/involved"
import { Legend } from "@/components/legend"
import { Matrix } from "@/components/matrix"
import { Publications } from "@/components/publications"
import { useTheme } from "@/components/theme"
import type { Entry, MapPayload } from "@/lib/map"
import payload from "@data/map.json"

const map = payload as MapPayload

function ThemeToggle() {
  const { choice, setChoice } = useTheme()
  const order = ["system", "light", "dark"] as const
  const icons = { system: Monitor, light: Sun, dark: Moon }
  const Icon = icons[choice]
  return (
    <Button
      variant="ghost"
      size="sm"
      className="h-8 gap-1.5 px-2 text-muted-foreground hover:text-foreground"
      onClick={() => setChoice(order[(order.indexOf(choice) + 1) % order.length])}
    >
      <Icon className="size-3.5" aria-hidden="true" />
      <span className="sr-only">Colour scheme: {choice}. Activate to change.</span>
      <span aria-hidden="true" className="text-[11px] capitalize">
        {choice}
      </span>
    </Button>
  )
}

/** The hash is the open panel's address: #study=<key>. Parsing lives here so
 *  initial load, popstate and the writers all agree on the format. */
function keyFromHash(): string | null {
  const match = /^#study=([A-Za-z0-9_-]+)$/.exec(window.location.hash)
  return match ? match[1] : null
}

export default function App() {
  const { programme, strands, stages, statuses, graph, refreshedAt } = map
  const [openKey, setOpenKey] = useState<string | null>(() => keyFromHash())

  // Browser navigation owns the hash: Back must close the panel, Forward
  // reopen it, so this listener keeps state in step with either.
  useEffect(() => {
    const sync = () => setOpenKey(keyFromHash())
    window.addEventListener("popstate", sync)
    return () => window.removeEventListener("popstate", sync)
  }, [])

  // State and hash move together. Assigning location.hash pushes a history
  // entry, which is what makes Back mean "close".
  const openByKey = useCallback((key: string) => {
    setOpenKey(key)
    window.location.hash = `study=${key}`
  }, [])

  const openEntry = useCallback((entry: Entry) => openByKey(entry.key), [openByKey])

  // One flat index, so the sheet's own dependency links can open a sibling
  // without the matrix having to hand its position down.
  const index = useMemo(() => {
    const byKey = new Map<string, { entry: Entry; strandId: string }>()
    for (const strand of strands) {
      for (const entry of strand.entries) {
        byKey.set(entry.key, { entry, strandId: strand.id })
      }
    }
    return byKey
  }, [strands])

  const current = openKey ? index.get(openKey) : undefined

  const all = useMemo(() => strands.flatMap((s) => s.entries), [strands])

  const orderedKeys = useMemo(() => all.map((e) => e.key), [all])

  const counts = useMemo(
    () => ({ repos: all.length, published: all.filter((e) => e.paper).length }),
    [all],
  )

  // How many studies sit in each lifecycle state, for the legend. Derived
  // from the badges the payload already resolved rather than re-deriving
  // status here, so the legend counts exactly what the cells display.
  const byStatus = useMemo(() => {
    const tally: Record<string, number> = {}
    for (const status of statuses) {
      tally[status.id] = all.filter((entry) =>
        (entry.badges ?? []).includes(status.label),
      ).length
    }
    return tally
  }, [all, statuses])

  return (
    <div className="min-h-dvh bg-background">
      <a
        href="#matrix"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-background focus:px-4 focus:py-2 focus:ring-2 focus:ring-ring"
      >
        Skip to the map
      </a>

      <header className="border-b border-border">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <span className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground">
            Loughborough University
            <span className="mx-2 text-border">/</span>
            Doctoral research programme
          </span>
          <ThemeToggle />
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 pb-24 sm:px-6">
        <section className="border-b border-border py-9">
          <div className="max-w-3xl">
            <h1 className="text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
              {programme.title}
            </h1>
            <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
              {programme.question}
            </p>
            <p className="mt-4 text-sm leading-relaxed text-foreground">{programme.move}</p>
          </div>
          <dl className="mt-7 flex flex-wrap gap-x-10 gap-y-3">
            {[
              { label: "Repositories", value: counts.repos },
              { label: "In the record", value: counts.published },
              { label: "Strands", value: strands.length },
            ].map((stat) => (
              <div key={stat.label}>
                <dt className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                  {stat.label}
                </dt>
                <dd className="mt-0.5 font-mono text-xl tabular-nums">{stat.value}</dd>
              </div>
            ))}
          </dl>
        </section>

        <section id="matrix" className="scroll-mt-4 py-8">
          <div className="mb-5 flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-xs font-semibold uppercase tracking-widest text-foreground">
              The programme
            </h2>
            <p className="text-xs text-muted-foreground">
              Select a repository for its question, method, and dependencies.
            </p>
          </div>
          <Matrix strands={strands} stages={stages} statuses={statuses} onOpen={openEntry} />
        </section>

        <section id="dependencies" className="scroll-mt-4 border-t border-border py-10">
          <div className="mb-5 flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-xs font-semibold uppercase tracking-widest text-foreground">
              How the studies depend on each other
            </h2>
            <p className="text-xs text-muted-foreground">
              Left to right is dependency order. Hover a study to see what it touches.
            </p>
          </div>
          <DependencyGraph graph={graph} entries={all} onOpen={openEntry} />
        </section>

        <Legend statuses={statuses} counts={byStatus} />

        <Publications entries={all} />

        <GetInvolved />

        <footer className="border-t border-border pt-6 text-xs text-muted-foreground">
          {refreshedAt && <p>Live repository data last refreshed {refreshedAt}.</p>}
          <p className="mt-1">
            Repositories marked private are readable on request — see{" "}
            <a
              href="#involved"
              className="underline decoration-border underline-offset-4 hover:decoration-foreground"
            >
              Get involved
            </a>
            .
          </p>
        </footer>
      </main>

      <Detail
        entry={current?.entry ?? null}
        strand={strands.find((s) => s.id === current?.strandId)}
        orderedKeys={orderedKeys}
        onOpenKey={openByKey}
        onStep={() => {}}
        onClose={() => {
          // Closing via Esc or overlay pops the history entry this open
          // pushed, keeping one Back = one close. Without a hash there is
          // nothing to pop, so clear directly.
          if (/^#study=/.test(window.location.hash)) window.history.back()
          else setOpenKey(null)
        }}
      />
    </div>
  )
}
