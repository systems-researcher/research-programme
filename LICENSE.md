# Licence

Copyright (c) 2026 Jason D. Gower.

**Prose and data** — every Markdown file, `repos.yml`, and the rendered site
content — are licensed under Creative Commons Attribution 4.0 International
(CC-BY-4.0). Full text: https://creativecommons.org/licenses/by/4.0/legalcode

**Code** — everything under `scripts/`, `tests/`, and the first-party sources
under `app/src/` — is licensed under the MIT Licence, reproduced in
`LICENSE-MIT`.

Every Markdown, YAML, Python, and TypeScript file that carries content states
which of the two applies with an SPDX identifier. Empty package markers
(`__init__.py`) and generated files (`data/map.json`, `data/live.json`, and
everything under `site/`) do not.

## Third-party components

The site bundles work by others, under their own licences and with their
copyright notices retained:

| Component | Where | Licence | Copyright |
|---|---|---|---|
| [shadcn/ui](https://ui.shadcn.com) | `app/src/components/ui/`, `app/src/lib/utils.ts` — vendored source, modified | MIT | shadcn |
| [Radix UI](https://www.radix-ui.com) | npm dependency of the above | MIT | WorkOS |
| [Geist](https://github.com/vercel/geist-font) | bundled into `site/assets/` via `@fontsource-variable/geist` | SIL OFL 1.1 | The Geist Project Authors |
| [Lucide](https://lucide.dev) | icons, npm dependency | ISC | Lucide Contributors |
| [Mermaid](https://mermaid.js.org) | diagram rendering, npm dependency | MIT | Knut Sveidqvist |
| [tw-animate-css](https://github.com/Wombosvideo/tw-animate-css) | npm dependency | MIT | Wombosvideo |

Full licence texts ship inside each package under `app/node_modules/`. The
Geist fonts are served from this origin rather than a font CDN; OFL 1.1 permits
this, and the reserved-name and bundling conditions are unchanged by it.
