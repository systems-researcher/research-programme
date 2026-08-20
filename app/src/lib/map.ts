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

/** A peer-reviewed paper this repository is the artefact for. Validated in
 *  Python (rule 10): every field present, a bare DOI, and a known status. */
export type Paper = {
  title: string
  authors: string[]
  venue: string
  year: number
  doi: string
  /** "accepted" means the DOI does not resolve yet, so it must not be a link. */
  status: "accepted" | "published"
}

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
  /** The repository's own published result site, when it has one. */
  site?: string | null
  paper?: Paper | null
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
