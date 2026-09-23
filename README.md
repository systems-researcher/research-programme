<!--
Copyright (c) 2026 Jason D. Gower
SPDX-License-Identifier: CC-BY-4.0
-->

# Research programme

![Architecting Trustworthy AI Integration in MBSE — three strands: epistemic adequacy, do classic SE methods survive an AI practitioner, and formalisation](app/public/banner.png)

**Architecting Trustworthy AI Integration in MBSE** — Loughborough University
doctoral research. This repository is the front door: what each repository in the
programme is for, what question it answers, and how they link.

The same content, with a dependency diagram, is published as a single page:
https://systems-researcher.github.io/research-programme/

## The argument

Everything hangs off one methodological move: an AI agent stands in as a
consistent practitioner, which turns method and representation into manipulable
experimental factors and makes replicated designs affordable that human-subject
systems-engineering research could never run.

That move branches into two strands. **Epistemic adequacy** asks what an
engineering record must expose for an AI to tell a grounded claim from an
ungrounded one — defined as a specification, measured by an instrument, tested by
probes, and enforced by three candidate architectures. **Method validation**
turns the same instrument on the methods themselves: does a model really beat a
document, does a trade study survive cosmetic perturbation, does DSM produce the
optimal order.

## The repositories

<!-- BEGIN:repos -->

| Repository | Stage | Status | What it is for |
|---|---|---|---|
| `epistemic-adequacy-ontology` | define | built-runs-pending | The vocabulary both specifications quantify over: thirteen entities and nine enumerations describing what an engineering record must carry for a machine consumer to decide whether a value is grounded. Split out of the SysML v2 realisation so the entity model can be stated and bound to other languages without carrying SysML v2 assumptions. |
| `epistemic-adequacy-spec` | define | released | A conformance specification stating, in eighteen testable clauses, what an engineering record must expose so that an AI consumer can decide whether a claim the record holds is grounded. |
| `admissibility-spec` | define | design | The write-side counterpart to the epistemic adequacy specification: what an AI-authored contribution must carry, and what conditions a substrate must check, before that contribution may enter the authoritative engineering record. |
| `machine-actionable-requirements` | define | design | The requirement-side artefact that sits upstream of the record: what a requirement representation must expose so that an AI participant can tell how satisfaction is to be established, where the requirement came from, how far it is supported, what it applies to, and what may be done with it. |
| `epistemic-adequacy-sysml-v2-binding` | define | design | Maps the specification's clause metadata into SysML v2, so the eighteen clauses become mechanically checkable on a real model. The entity model and its schema live in epistemic-adequacy-ontology; this repository owns neither. |
| `epistemic-adequacy-testing-toolkit` | measure | built-runs-pending | The instrument: it scores a substrate against the eighteen clauses and joins that score to how an AI consumer then behaves, so that adequacy is the independent variable and consumer behaviour the dependent one. |
| `sysml2-bench` | measure | built-runs-pending | A public, versioned, contamination-resistant benchmark of how well language models read, reason over, critique, and write SysML v2 — the capability baseline every adequacy result has to be read against. |
| `governed-interaction-cost-probe` | measure | design | The practitioner-viability study: what governed interaction with an engineering record actually costs to use, in latency, tokens, money, and the failure modes that only appear under load. |
| `epistemic-adequacy-probe` | evidence | published | The first measured test of whether epistemic metadata, beyond structured model access alone, changes how an AI consumer answers derivation-style questions over an MBSE model. |
| `pressure-susceptibility-probe` | evidence | retired | Retiring. It produced no results: the only runs it reached were pipeline validation. Its remaining value transfers into epistemic-adequacy-under-pressure-probe at pin 2c030ca, and the GitHub repository is archived once that extraction lands. |
| `epistemic-adequacy-under-pressure-probe` | evidence | design | Widens the one governed-and-pressed cell the adequacy probe already ran into a designed two-by-two. That cell — 5 of 15 ungrounded, 33%, against 60% bare — was a completion run over five questions at one pressure lever, and it is the whole of what the programme knows about metadata under pressure. |
| `SysML-v2-API-Services-Arch-A` | architecture | design | Candidate A: epistemic metadata carried inline on model elements through project-local SysML v2 metadata definitions, with an admissibility gate as the sole write path. |
| `sysml-v2-metadata-graph-Arch-B` | architecture | design | Candidate B: the SysML v2 model stays completely untouched and the epistemic metadata lives beside it in a Neo4j graph keyed by programme-level stable identifiers. |
| `sysml-v2-governed-substrate-Arch-C` | architecture | design | Candidate C: one ArcadeDB engine holds model topology, governance metadata and provenance, and retrieval embeddings, with SysML treated as a projection over the store rather than the store itself. |
| `model-vs-document-defect-probe` | evidence | design | Measures MBSE's flagship claim head-on: does a single connected system model let a reviewer catch more defects than an information-equivalent set of documents? |
| `ahp-framing-fragility-probe` | evidence | design | Tests whether a structured trade study gives a stable answer, or whether the winner silently depends on things that should not matter: the order the criteria were listed in, how they were worded, or the presence of irrelevant decoy options. |
| `dsm-sequencing-probe` | evidence | design | Tests whether the Design Structure Matrix actually produces the best task order, measured against a mathematically optimal answer a computer can calculate exactly. |
| `publications` | release | not-applicable | The written column of the programme: one frozen report per study, and the author's copy of every paper. Venues hold the public copy. |

<!-- END:repos -->

## Keeping this current

`repos.yml` is the source of truth. After editing it:

```bash
python -m scripts.refresh       # optional: validates repos.yml, then pulls live fields
python -m scripts.build         # regenerate data/map.json and the table above
python -m scripts.build --check # must pass before committing
```

Every script runs as a module (`python -m scripts.build`), never as a path
(`python scripts/build.py`) — the latter breaks the package imports.

The banner above is generated too. After changing `repos.yml`, regenerate it
alongside the payload:

```bash
npm --prefix app run banner        # the README banner
npm --prefix app run preview:card  # the social preview card
```

CI fails if either image no longer matches the data, so a stale banner cannot
reach the front page unnoticed.

Both images are drawn headlessly, which needs a browser once:
`npx --prefix app playwright install chromium`.

`data/map.json` is generated and committed. It holds the page already resolved:
entries in render order, badges composed, dependencies inverted. The app reads
it and derives nothing, so those rules stay in Python where the tests are, and
the deployment build needs Node only. A scheduled workflow (`refresh.yml`)
refreshes the live fields weekly, so the badges move without anyone
remembering.

## The site

The page is a small React app (Vite + Tailwind + [shadcn/ui](https://ui.shadcn.com)),
built from the committed `data/map.json`. See [DESIGN.md](DESIGN.md).

```bash
cd app
npm install
npm run dev      # local preview on :5173
npm run build    # writes ../site, deployed by pages.yml to GitHub Pages
```

Run `python -m scripts.build` before `npm run build`: the app renders whatever
`data/map.json` last held.

Three checks worth running after a build:

```bash
python -m pytest                    # data rules, diagram, payload
python tests/check_external_links.py  # the built page must fetch nothing off-origin
cd app && npm run test:meta           # og/twitter tags survived the build
```

Two more need a served page and a browser (`npx --prefix app playwright
install chromium` once). CI runs both on every push against the
production build, served under the Pages prefix. To run them the way CI
does:

```bash
cd app
export BASE_PATH=/research-programme/ MSYS_NO_PATHCONV=1  # MSYS_NO_PATHCONV stops Git Bash rewriting the path
npm run build
npm run preview                      # serves ../site on :4173/research-programme/
node tests/layout.spec.mjs http://localhost:4173/research-programme/
node tests/deep-link.spec.mjs http://localhost:4173/research-programme/
```

In a fresh shell, skip the export and drop `research-programme/` from both URLs to test a root build.

pages.yml publishes a commit only after check passes on it, and only while it is still the tip of main. The weekly refresh bot pushes with `GITHUB_TOKEN`, which starts no workflows, so check listens for refresh to finish and tests the bot's commit before pages publishes it. To redeploy by hand, run `gh workflow run check.yml --ref main`.

## Licence

Prose and data CC-BY-4.0; code MIT. See [LICENSE.md](LICENSE.md).
