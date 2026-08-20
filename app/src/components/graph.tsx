// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { useMemo, useState } from "react"
import type { Entry, Graph, GraphNode } from "@/lib/map"

/** How the studies depend on each other.
 *
 * Hand-drawn SVG rather than a layout library. Python has already decided
 * where every node sits (longest-path layering, so every edge flows left to
 * right); this only turns those integer coordinates into pixels. That split
 * is the reason the picture looks composed rather than generated.
 *
 * The one interaction: focusing a study dims everything it is not connected
 * to. With eleven edges the whole graph is legible at rest, so the
 * interaction answers "what does THIS one touch" rather than making an
 * unreadable picture readable. */

// Wide enough for the longest repository key at 10.5px mono
// (epistemic-adequacy-testing-toolkit, 34 characters). A key is an
// identifier a reader may need to go and find, so it is never truncated.
const NODE_W = 242
const NODE_H = 44
const GAP_X = 64
const GAP_Y = 14
const PAD = 14

const columnX = (x: number) => PAD + x * (NODE_W + GAP_X)

/** Columns are centred against the tallest, so the picture has a spine
 *  rather than hanging off the top edge. */
const nodeY = (node: GraphNode, tallest: number) =>
  PAD + (tallest - node.column) * ((NODE_H + GAP_Y) / 2) + node.y * (NODE_H + GAP_Y)

export function DependencyGraph({
  graph,
  entries,
  onOpen,
}: {
  graph: Graph
  entries: Entry[]
  onOpen: (entry: Entry) => void
}) {
  const [active, setActive] = useState<string | null>(null)

  const byKey = useMemo(
    () => new Map(entries.map((entry) => [entry.key, entry])),
    [entries],
  )

  const tallest = useMemo(
    () => Math.max(...graph.nodes.map((n) => n.column)),
    [graph.nodes],
  )

  const placed = useMemo(() => {
    const map = new Map<string, { node: GraphNode; cx: number; cy: number }>()
    for (const node of graph.nodes) {
      map.set(node.key, {
        node,
        cx: columnX(node.x),
        cy: nodeY(node, tallest),
      })
    }
    return map
  }, [graph.nodes, tallest])

  // Everything the active node touches, in either direction, so hovering a
  // study shows its whole neighbourhood rather than only what it feeds.
  const related = useMemo(() => {
    if (!active) return null
    const keep = new Set<string>([active])
    for (const edge of graph.edges) {
      if (edge.from === active) keep.add(edge.to)
      if (edge.to === active) keep.add(edge.from)
    }
    return keep
  }, [active, graph.edges])

  const width = PAD * 2 + graph.columns * NODE_W + (graph.columns - 1) * GAP_X
  const height = PAD * 2 + tallest * NODE_H + (tallest - 1) * GAP_Y

  return (
    <div className="-mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width={width}
        height={height}
        role="img"
        aria-label="Dependency graph of the twelve studies. Every study it shows is also a tile in the matrix above."
        className="h-auto w-full min-w-[52rem] max-w-none"
        onMouseLeave={() => setActive(null)}
      >
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 8 8"
            refX="7"
            refY="4"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            {/* A marker is rendered outside the referencing element's
                context, so currentColor resolves against <defs>, not the
                edge — which drew the arrowheads invisible. */}
            <path d="M 0 1 L 7 4 L 0 7 z" className="fill-muted-foreground" />
          </marker>
        </defs>

        <g className="text-muted-foreground">
          {graph.edges.map((edge) => {
            const a = placed.get(edge.from)
            const b = placed.get(edge.to)
            if (!a || !b) return null

            const x1 = a.cx + NODE_W
            const y1 = a.cy + NODE_H / 2
            const x2 = b.cx
            const y2 = b.cy + NODE_H / 2
            // A horizontal-tangent cubic: edges leave and enter side-on, so
            // they never appear to clip the boxes they connect.
            const bend = Math.max(28, (x2 - x1) * 0.45)
            const lit = !related || (related.has(edge.from) && related.has(edge.to))

            return (
              <path
                key={`${edge.from}->${edge.to}`}
                d={`M ${x1} ${y1} C ${x1 + bend} ${y1}, ${x2 - bend} ${y2}, ${x2} ${y2}`}
                fill="none"
                stroke="currentColor"
                strokeWidth={related && lit ? 1.75 : 1.25}
                markerEnd="url(#arrow)"
                className="transition-opacity duration-150 motion-reduce:transition-none"
                opacity={lit ? 0.75 : 0.12}
              />
            )
          })}
        </g>

        {graph.nodes.map((node) => {
          const spot = placed.get(node.key)!
          const entry = byKey.get(node.key)
          const lit = !related || related.has(node.key)
          const isActive = active === node.key

          return (
            <g
              key={node.key}
              transform={`translate(${spot.cx} ${spot.cy})`}
              tabIndex={0}
              role="button"
              aria-label={`${node.key}. Show its dependencies, or open its detail.`}
              onMouseEnter={() => setActive(node.key)}
              onFocus={() => setActive(node.key)}
              onBlur={() => setActive(null)}
              onClick={() => entry && onOpen(entry)}
              onKeyDown={(event) => {
                if (entry && (event.key === "Enter" || event.key === " ")) {
                  event.preventDefault()
                  onOpen(entry)
                }
              }}
              style={{ ["--accent" as string]: `var(--strand-${node.token}-line)` }}
              className="graph-node cursor-pointer transition-opacity duration-150 focus:outline-none motion-reduce:transition-none"
              opacity={lit ? 1 : 0.25}
            >
              <rect
                width={NODE_W}
                height={NODE_H}
                rx="6"
                className="graph-node-box"
                strokeWidth={isActive ? 1.5 : 1}
              />
              {/* The strand's colour on the left edge, matching its tile. */}
              <rect x="0" y="8" width="3" height={NODE_H - 16} rx="1.5" fill="var(--accent)" />
              <text
                x="14"
                y={NODE_H / 2 + 1}
                dominantBaseline="middle"
                className="fill-foreground font-mono"
                fontSize="10.5"
              >
                {node.key}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
