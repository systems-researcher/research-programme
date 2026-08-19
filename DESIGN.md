<!--
Copyright (c) 2026 Jason D. Gower
SPDX-License-Identifier: CC-BY-4.0
-->

# Design System — Research programme

Shared look for every repository in this doctoral programme. Source of the
rules: the [GOV.UK Design System](https://design-system.service.gov.uk/),
chosen from [alexpate/awesome-design-systems](https://github.com/alexpate/awesome-design-systems).

This is **not** a GOV.UK service. Do not use the crown, the GDS Transport
typeface, or the GOV.UK wordmark. Use the tokens and patterns below.

## Product Context

- **What this is:** The front door and the house style for a Loughborough
  University doctoral programme on trustworthy AI in MBSE.
- **Who it's for:** Supervisor first. Then any reader sent "look at my research".
- **Space/industry:** Academic systems engineering. Peers are university
  research groups and UK public technical services, not SaaS landing pages.
- **Project type:** One-page generated map here; later repos reuse the same
  tokens on their own pages.

## Why GOV.UK

The awesome list is mostly React/npm libraries (Chakra, Fluent, Ant, Carbon)
or brand kits we cannot ship. This programme's sites are static HTML, one
stylesheet, no framework.

| Candidate | Why not / why |
|---|---|
| GOV.UK Design System | **Pick.** Public source, WCAG AA by default, CSS tokens, UK public-sector literacy. Fits a UK university reader. |
| NHS.UK Service Manual | Same family, health-branded. Wrong domain. |
| BBC GEL | Guidelines, no coded tokens we can copy. |
| IBM Carbon / Primer / Polaris | Component runtimes. Too much for a map page. |
| USWDS / France DSFR | Same idea as GOV.UK, wrong country. |

Local folder `AppData\Local\Temp\awesome-design-md` is empty brand stubs, not
this list. The list itself was fetched from
https://github.com/alexpate/awesome-design-systems.

## Aesthetic Direction

- **Direction:** Industrial / utilitarian, GOV.UK service-page grammar.
- **Decoration level:** Minimal. Type, hairlines, and the black masthead do
  the work.
- **Mood:** Official, readable, a bit severe. A controlled record, not a
  product launch.
- **Reference:** https://design-system.service.gov.uk/ and any GOV.UK start
  page.

## Typography

- **Display / body / UI:** Helvetica Neue, Helvetica, Arial, sans-serif —
  the GOV.UK fallback. GDS Transport is not licensed for this site.
- **Data / code:** ui-monospace / SF Mono / Consolas.
- **Loading:** System fonts only. No CDN fonts.
- **Scale** (GOV.UK): 80 / 48 / 36 / 27 / 24 / 19 / 16 / 14. Body is 19px /
  25px (`1.1875rem` / `1.315`). Headings are 700.

## Colour

- **Approach:** Restrained. Colour means something (link, focus, strand).
- **Ink:** `#0b0c0c` — text.
- **Canvas:** `#f3f2f1` — page. **Surface:** `#ffffff` — cards.
- **Link:** `#1d70b8`, hover `#003078`, visited `#4c2c92`.
- **Focus:** `#ffdd00` on ink. Never remove the focus ring.
- **Success / error:** `#00703c` / `#d4351c`.
- **Strands:** adequacy blue, method-validation purple (GOV.UK visited),
  assembly green.
- **Dark mode:** Unofficial extension. Invert canvas/ink, keep focus yellow,
  lighten links. GOV.UK has no public dark theme; this one exists so the
  existing `prefers-color-scheme` contract does not vanish.

## Spacing

- **Base unit:** 5px (GOV.UK).
- **Density:** Comfortable. Body stays 19px.
- **Scale:** 5 10 15 20 25 30 40 50 60.

## Layout

- **Approach:** Grid-disciplined. Header full bleed, content `max-width: 62rem`.
- **Signature chrome:** Black masthead, blue phase banner that says this is
  research and not a GOV.UK service, white cards on grey canvas, square
  corners, underlined links.
- **Border radius:** 0.
- **Diagram:** Mermaid may scroll horizontally; the page itself does not.

## Motion

- **Approach:** Minimal-functional. No entrance choreography.
- **Focus and hover only.** Honour `prefers-reduced-motion`.

## How later repos use this

1. Copy `design/tokens.css`.
2. Read this file before any visual decision.
3. Keep the masthead + phase banner + tokens. Do not invent a second palette.
4. No third-party fonts, no rounded-pill SaaS chrome, no purple gradients.

## Decisions Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-08-19 | Adopt GOV.UK Design System tokens/patterns, not the npm runtime | Awesome-list pick that fits static HTML and a UK academic reader |
| 2026-08-19 | Helvetica/Arial fallback, not GDS Transport | Transport is crown-use; GOV.UK documents this fallback |
| 2026-08-19 | Phase banner states "not a GOV.UK service" | Avoid impersonating a government site |
