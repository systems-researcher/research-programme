// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT

/** The shape of data/map.json, written by scripts/render.py `payload()`.
 *
 * Everything here is already resolved: entries arrive in final render order,
 * badges are composed, and dependency references already know whether they
 * can be linked. The app derives nothing — if a rule needs to change, it
 * changes in the Python, where the tests are. */

export type LinkRef = {
  key: string
  /** node-only entries render no card, so there is nothing to anchor to. */
  linkable: boolean
}

export type Headline = { text: string; source: string }

export type Entry = {
  key: string
  stage: string
  card: boolean
  objective: string
  /** null when the repository is not yet published. */
  url?: string | null
  badges?: string[]
  question?: string
  method?: string
  headline?: Headline | null
  output?: string | null
  dependsOn?: LinkRef[]
  feeds?: LinkRef[]
}

export type Strand = {
  id: string
  token: string
  title: string
  subtitle: string
  entries: Entry[]
}

export type Stage = { id: string; title: string; note: string }

export type MapPayload = {
  programme: { title: string; question: string; move: string }
  stages: Stage[]
  strands: Strand[]
  refreshedAt: string | null
}
