// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
import { useEffect, useRef, useState } from "react"
import { useTheme } from "@/components/theme"

/** The dependency graph, rendered from the Mermaid source Python emits.
 *
 * Mermaid fixes its theme at initialize() time, so a theme flip must
 * re-initialise and re-render or the diagram keeps the palette it was born
 * with. That is why this redraws on `resolved` rather than mounting once.
 *
 * The source carries no classDef and no inline fill, so the strand colours
 * come from index.css and follow the theme for free. */
export function Diagram({ source }: { source: string }) {
  const host = useRef<HTMLDivElement>(null)
  const { resolved } = useTheme()
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let cancelled = false
    // Mermaid is ~250 kB gzipped — far more than the rest of the page put
    // together. The cards are the content and must not wait behind it, so it
    // is fetched only when this component mounts rather than in the entry
    // chunk. `import()` also keeps it out of the modulepreload list.
    import("mermaid").then(({ default: mermaid }) => {
      if (cancelled) return
      mermaid.initialize({
      startOnLoad: false,
      theme: resolved === "dark" ? "dark" : "default",
        securityLevel: "strict",
        flowchart: { curve: "basis", htmlLabels: true },
      })

      // A unique id per render: Mermaid caches by id and would otherwise
      // hand back the previous theme's SVG.
      const id = `graph-${resolved}-${Math.random().toString(36).slice(2)}`
      return mermaid.render(id, source).then(({ svg, bindFunctions }) => {
        if (cancelled || !host.current) return
        host.current.innerHTML = svg
        // Wires the `click n_x "#card-x"` statements to real anchors.
        bindFunctions?.(host.current)
        setFailed(false)
      })
    }).catch(() => {
      if (!cancelled) setFailed(true)
    })

    return () => {
      cancelled = true
    }
  }, [source, resolved])

  return (
    <figure className="my-8">
      <div
        id="diagram"
        ref={host}
        role="img"
        aria-label="Dependency graph of the programme repositories, grouped by stage and coloured by strand. Every repository it shows is also listed as a card below."
        className="overflow-x-auto rounded-lg border bg-card p-4 [&_svg]:mx-auto [&_svg]:h-auto [&_svg]:max-w-none"
      />
      {failed && (
        <figcaption className="mt-2 text-sm text-muted-foreground">
          The diagram could not be drawn. Every repository it would show is
          listed in full below.
        </figcaption>
      )}
    </figure>
  )
}
