// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { Mail, Lock } from "lucide-react"

/** How to make contact.
 *
 * The page tells a reader that private repositories are readable on request
 * and, until this section existed, gave them no way to make one. Two routes,
 * because that is what a reader actually wants: to read a study that is
 * closed, or to work on the research together.
 *
 * A third route inviting pull requests on this map was removed at the
 * author's request — someone reading a research programme is not here to
 * patch its website, and it read oddly beside two routes about the research
 * itself. Do not restore it without asking.
 *
 * One address, deliberately: this is the programme's first point of contact,
 * not a directory of everyone connected to the work. */

// The university address is the one the routes above write to: this is
// doctoral research, and an academic enquiry belongs there. The company
// address is offered alongside it for anyone whose interest is commercial
// rather than academic, so they do not have to guess which is right.
const EMAIL = "J.Gower@lboro.ac.uk"
const COMPANY_EMAIL = "support@jgsystemsconsulting.com"

/** The two GitHub accounts the work is published from. The research account
 *  carries the programme; the company account carries the consulting work the
 *  methods come out of. Both are listed because a reader following one may
 *  well want the other. */
const ACCOUNTS = [
  {
    handle: "systems-researcher",
    label: "The research",
    detail: "This programme, and the studies as they become public.",
    cue: "Follow for new studies",
  },
  {
    handle: "jgsystemsconsulting",
    label: "JG Systems Consulting",
    detail: "MBSE and AI-in-engineering work outside the doctorate.",
    cue: "Follow the practice",
  },
]

/** The GitHub mark, inline.
 *
 * Lucide dropped brand icons, and a generic substitute would not be
 * recognisable at 16px — the logo is what makes these links readable at a
 * glance. Drawn from the official mark, which GitHub permits for linking to
 * GitHub. */
function GithubMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" fill="currentColor" className={className}>
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
    </svg>
  )
}

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

      {/* Following is a smaller commitment than asking for access, so it sits
          apart from the routes rather than competing with them. The ask is
          stated: a reader who would happily follow will not think to unless
          invited. */}
      <p className="mt-8 text-[13px] text-muted-foreground">
        <span className="font-medium text-foreground">Follow the work.</span>{" "}
        Following either account, or{" "}
        <a
          href="https://github.com/systems-researcher/research-programme"
          rel="noopener"
          className="underline decoration-border underline-offset-4 hover:decoration-foreground"
        >
          starring this map
        </a>
        , is the easiest way to see studies as they are published — and it
        tells me the work is worth continuing to publish.
      </p>
      <div className="mt-3 grid gap-px overflow-hidden rounded-md border border-border bg-border sm:grid-cols-2">
        {ACCOUNTS.map((account) => (
          <a
            key={account.handle}
            href={`https://github.com/${account.handle}`}
            rel="noopener"
            className="group flex items-start gap-3 bg-card p-4 transition-colors hover:bg-muted/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-inset"
          >
            <GithubMark className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
            <span>
              <span className="block text-sm font-medium text-foreground">
                {account.label}
              </span>
              <span className="mt-0.5 block font-mono text-[11px] text-muted-foreground underline decoration-border underline-offset-4 group-hover:decoration-foreground">
                github.com/{account.handle}
              </span>
              <span className="mt-1.5 block text-[13px] leading-relaxed text-muted-foreground">
                {account.detail}
              </span>
              <span className="mt-2 block text-[11px] font-medium text-foreground underline decoration-border underline-offset-4 group-hover:decoration-foreground">
                {account.cue} →
              </span>
            </span>
            <span className="sr-only">(opens GitHub)</span>
          </a>
        ))}
      </div>

      <p className="mt-4 flex flex-wrap gap-x-6 gap-y-1 text-xs text-muted-foreground">
        <span>
          Research:{" "}
          <a
            href={`mailto:${EMAIL}`}
            className="font-mono underline decoration-border underline-offset-4 hover:decoration-foreground"
          >
            {EMAIL}
          </a>
        </span>
        <span>
          Commercial:{" "}
          <a
            href={`mailto:${COMPANY_EMAIL}`}
            className="font-mono underline decoration-border underline-offset-4 hover:decoration-foreground"
          >
            {COMPANY_EMAIL}
          </a>
        </span>
      </p>
    </section>
  )
}
