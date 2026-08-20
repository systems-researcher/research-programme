// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { ArrowUpRight } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Entry, LinkRef } from "@/lib/map"

/** Dependency references. A node-only target renders no card, so it appears
 *  as plain text rather than a link that would go nowhere. */
function Refs({ label, refs }: { label: string; refs: LinkRef[] }) {
  if (!refs.length) return null
  return (
    <p className="text-sm">
      <span className="font-semibold text-foreground">{label}.</span>{" "}
      {refs.map((ref, index) => (
        <span key={ref.key}>
          {index > 0 && ", "}
          {ref.linkable ? (
            <a href={`#card-${ref.key}`} className="underline underline-offset-4 hover:text-foreground">
              {ref.key}
            </a>
          ) : (
            <span className="text-muted-foreground">{ref.key}</span>
          )}
        </span>
      ))}
    </p>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <p className="text-sm leading-relaxed text-muted-foreground">
      <span className="font-semibold text-foreground">{label}.</span> {children}
    </p>
  )
}

export function RepoCard({ entry, accent }: { entry: Entry; accent: string }) {
  return (
    <Card
      id={`card-${entry.key}`}
      // The strand's colour is carried on the left edge, matching the node
      // colour in the diagram so a reader arriving via a click sees the link.
      // target: makes the card announce itself when the diagram sends you here.
      className="scroll-mt-20 border-l-4 target:ring-2 target:ring-ring target:ring-offset-2 target:ring-offset-background"
      style={{ borderLeftColor: `var(--strand-${accent}-line)` }}
    >
      <CardHeader>
        <CardTitle className="font-mono text-base break-words">
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
        </CardTitle>
        {!!entry.badges?.length && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {entry.badges.map((badge) => (
              <Badge key={badge} variant="secondary" className="font-normal">
                {badge}
              </Badge>
            ))}
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-3">
        <Field label="What it is for">{entry.objective}</Field>
        <Field label="Question">{entry.question}</Field>
        <Field label="Method">{entry.method}</Field>

        {entry.headline && (
          <p className="border-l-2 border-primary py-1 pl-3 text-sm leading-relaxed">
            <span className="font-semibold">Result.</span> {entry.headline.text}{" "}
            <span className="text-muted-foreground">Source: {entry.headline.source}</span>
          </p>
        )}
        {entry.output && (
          <p className="text-sm text-muted-foreground">{entry.output}</p>
        )}

        <Refs label="Depends on" refs={entry.dependsOn ?? []} />
        <Refs label="Feeds" refs={entry.feeds ?? []} />
      </CardContent>
    </Card>
  )
}
