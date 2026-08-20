// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { Monitor, Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Diagram } from "@/components/diagram"
import { RepoCard } from "@/components/repo-card"
import { useTheme } from "@/components/theme"
import type { MapPayload, Stage, Strand } from "@/lib/map"
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
      className="text-neutral-50 hover:bg-white/10 hover:text-neutral-50"
      onClick={() => setChoice(order[(order.indexOf(choice) + 1) % order.length])}
    >
      <Icon className="size-4" aria-hidden="true" />
      <span className="sr-only">
        Colour scheme: {choice}. Activate to change.
      </span>
      <span aria-hidden="true" className="ml-1.5 text-xs capitalize">{choice}</span>
    </Button>
  )
}

/** A strand: its heading, then its entries grouped under the stages that
 *  actually contain one. Stage order comes from the payload, so a stage
 *  cannot appear here in an order the programme did not author. */
function StrandSection({ strand, stages }: { strand: Strand; stages: Stage[] }) {
  const cards = strand.entries.filter((entry) => entry.card)

  return (
    <section id={`strand-${strand.id}`} className="scroll-mt-20 pt-14">
      <div className="flex items-center gap-3">
        <span
          aria-hidden="true"
          className="size-3 shrink-0 rounded-full"
          style={{ backgroundColor: `var(--strand-${strand.token}-line)` }}
        />
        <h2 className="text-2xl font-semibold tracking-tight">{strand.title}</h2>
      </div>
      <p className="mt-2 max-w-3xl text-muted-foreground">{strand.subtitle}</p>
      <Separator className="mt-5" />

      {/* Every member is node-only (the thesis terminus). The section still
          belongs on the page, but an empty one reads as a rendering fault,
          so the entries are named in a line instead. */}
      {cards.length === 0 &&
        strand.entries.map((entry) => (
          <p key={entry.key} className="mt-5 text-sm text-muted-foreground">
            <span className="font-mono font-semibold text-foreground">{entry.key}.</span>{" "}
            {entry.objective}
          </p>
        ))}

      {stages.map((stage) => {
        const inStage = cards.filter((entry) => entry.stage === stage.id)
        if (!inStage.length) return null
        return (
          <div key={stage.id} className="mt-8">
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              {stage.title}
            </h3>
            <p className="mt-1 max-w-3xl text-sm text-muted-foreground">{stage.note}</p>
            <div className="mt-4 grid gap-4">
              {inStage.map((entry) => (
                <RepoCard key={entry.key} entry={entry} accent={strand.token} />
              ))}
            </div>
          </div>
        )
      })}
    </section>
  )
}

export default function App() {
  const { programme, strands, stages, diagram, refreshedAt } = map

  return (
    <div className="min-h-dvh bg-background">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-background focus:px-4 focus:py-2 focus:ring-2 focus:ring-ring"
      >
        Skip to content
      </a>

      <header className="sticky top-0 z-40 border-b border-white/10 bg-neutral-950 text-neutral-50 supports-[backdrop-filter]:bg-neutral-950/90 supports-[backdrop-filter]:backdrop-blur">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-2 px-6 py-3">
          <a href="#main" className="text-sm font-semibold tracking-tight">
            Loughborough University
            <span className="ml-2 font-normal opacity-70">Doctoral research programme</span>
          </a>
          <ThemeToggle />
        </div>
      </header>

      <main id="main" className="mx-auto max-w-5xl px-6 pb-24">
        <section className="pt-14">
          <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
            Programme map
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
            {programme.title}
          </h1>
          <p className="mt-6 max-w-3xl leading-relaxed text-muted-foreground">
            {programme.question}
          </p>
          <p className="mt-4 max-w-3xl leading-relaxed font-medium">{programme.move}</p>
        </section>

        <Diagram source={diagram} />

        {strands.map((strand) => (
          <StrandSection key={strand.id} strand={strand} stages={stages} />
        ))}

        <footer className="mt-20 border-t pt-6 text-sm text-muted-foreground">
          {refreshedAt && <p>Live repository data last refreshed {refreshedAt}.</p>}
          <p className="mt-1">
            Repositories marked private are readable on request: contact the author.
          </p>
        </footer>
      </main>
    </div>
  )
}
