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
  /** The publication's own lifecycle, not the study's. Only "published"
   *  means the DOI resolves, so only then is it rendered as a link. */
  status: "in-preparation" | "submitted" | "in-review" | "accepted" | "published"
}

export type Entry = {
  key: string
  stage: string
  card: boolean
  objective: string
  /** null when the repository is not yet published. */
  url?: string | null
  /** Resolved in Python from the owner and the live row. Only "public" may
   *  render a GitHub link; anything else, including a missing refresh, is
   *  closed. Required so missing cannot be read as public. */
  visibility: "public" | "private" | "local" | "unknown"
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

/** One state in the study lifecycle, in order. Generated from the validator's
 *  own enum so the legend cannot drift from the vocabulary. */
export type Status = { id: string; label: string; note: string }

/** True when entry carries this status's label as a badge.
 *  Same rule as App.byStatus: badges include visibility and
 *  "last commit …" words, so only an exact label hit counts.
 *  Do not match status.id. built-runs-pending never appears in a badge. */
export function entryHasStatus(
  entry: { badges?: string[] },
  status: { label: string },
): boolean {
  return (entry.badges ?? []).includes(status.label)
}

/** A study in the dependency picture, already positioned by Python.
 *  `x` is dependency depth, `y` the slot within that column. */
export type GraphNode = {
  key: string
  x: number
  y: number
  /** How many nodes share this column, so it can be centred vertically. */
  column: number
  strand: string
  token: string
  /** The payload's status label; the diagram draws it as dash, not colour. */
  status?: string
}

export type GraphEdge = { from: string; to: string }

export type Graph = {
  nodes: GraphNode[]
  edges: GraphEdge[]
  columns: number
}

export type MapPayload = {
  statuses: Status[]
  graph: Graph
  programme: { title: string; question: string; move: string }
  stages: Stage[]
  strands: Strand[]
  refreshedAt: string | null
}
