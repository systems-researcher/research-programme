// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { Mail, Lock } from "lucide-react"

/** How to make contact.
 *
 * The page tells a reader that private repositories are readable on request
 * and, until this section existed, gave them no way to make one. Three routes
 * because "collaborate" means three different things: read a study that is
 * closed, work on the research together, or contribute to this map.
 *
 * One address, deliberately: this is the programme's first point of contact,
 * not a directory of everyone connected to the work. */

const EMAIL = "J.Gower@lboro.ac.uk"

function mailto(subject: string, body: string): string {
  return `mailto:${EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
}

const ROUTES = [
  {
    icon: Lock,
    title: "Read a study",
    body: "Most of these repositories stay private while the work is in progress. If you are a researcher working in this area, tell me which one interests you and why, and I will usually share it.",
    action: "Ask for access",
    href: mailto(
      "Research programme: access request",
      "Which repository, and what you are working on:\n\n",
    ),
  },
  {
    icon: Mail,
    title: "Work on it together",
    body: "If one of these questions overlaps something you are working on, or you think a study is asking the wrong thing, I would like to hear from you.",
    action: "Start a conversation",
    href: mailto(
      "Research programme: collaboration",
      "What you are working on, and where it overlaps:\n\n",
    ),
  },
]

export function GetInvolved() {
  return (
    <section id="involved" className="scroll-mt-4 border-t border-border py-10">
      <div className="mb-5 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-foreground">
          Get involved
        </h2>
        <p className="text-xs text-muted-foreground">
          Jason D. Gower, Loughborough University.
        </p>
      </div>

      <ul className="grid gap-px overflow-hidden rounded-md border border-border bg-border sm:grid-cols-2">
        {ROUTES.map((route) => (
          <li key={route.title} className="flex flex-col bg-card p-4">
            <route.icon
              aria-hidden="true"
              className="size-4 shrink-0 text-muted-foreground"
            />
            <h3 className="mt-3 text-sm font-semibold text-foreground">{route.title}</h3>
            <p className="mt-1.5 flex-1 text-[13px] leading-relaxed text-muted-foreground">
              {route.body}
            </p>
            <a
              href={route.href}
              rel="noopener"
              className="mt-4 inline-flex w-fit items-center rounded border border-border bg-background px-2.5 py-1 text-xs transition-colors hover:border-foreground/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {route.action}
            </a>
          </li>
        ))}
      </ul>

      <p className="mt-4 text-xs text-muted-foreground">
        Direct email:{" "}
        <a
          href={`mailto:${EMAIL}`}
          className="font-mono underline decoration-border underline-offset-4 hover:decoration-foreground"
        >
          {EMAIL}
        </a>
      </p>
    </section>
  )
}
