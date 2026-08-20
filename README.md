<!--
Copyright (c) 2026 Jason D. Gower
SPDX-License-Identifier: CC-BY-4.0
-->

# Research programme

**Architecting Trustworthy AI Integration in MBSE** — Loughborough University
doctoral research. This repository is the front door: what each repository in the
programme is for, what question it answers, and how they link.

The same content, with a dependency diagram, is published as a single page:
<!-- SITE-URL -->

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
| `epistemic-adequacy-spec` | define | released | A conformance specification stating, in eighteen testable clauses, what an engineering record must expose so that an AI consumer can decide whether a claim the record holds is grounded. |
| `epistemic-adequacy-metamodel` | define | design | Owns the metadata model itself — a conceptual ontology, a logical data model, and a generated SysML v2 library, kept in sync — so that the specification's non-normative binding becomes something a tool can mechanically check. |
| `epistemic-adequacy-testing-toolkit` | measure | built-runs-pending | The instrument: it scores a substrate against the eighteen clauses and joins that score to how an AI consumer then behaves, so that adequacy is the independent variable and consumer behaviour the dependent one. |
| `sysml2-bench` | measure | built-runs-pending | A public, versioned, contamination-resistant benchmark of how well language models read, reason over, critique, and write SysML v2 — the capability baseline every adequacy result has to be read against. |
| `epistemic-adequacy-probe` | evidence | published | The first measured test of whether epistemic metadata, beyond structured model access alone, changes how an AI consumer answers derivation-style questions over an MBSE model. |
| `pressure-susceptibility-probe` | evidence | built-runs-pending | Measures how susceptible an AI assistant is to producing unauthorised engineering answers when the work itself pushes on it: a deadline, a senior engineer's stated conclusion, a board that has already agreed, or a question with a false premise baked in. |
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

`data/map.json` is generated and committed. It holds the page already resolved:
entries in render order, badges composed, dependencies inverted. The app reads
it and derives nothing, so those rules stay in Python where the tests are, and
the deployment build needs Node only.

## The site

The page is a small React app (Vite + Tailwind + [shadcn/ui](https://ui.shadcn.com)),
built from the committed `data/map.json`. See [DESIGN.md](DESIGN.md).

```bash
cd app
npm install
npm run dev      # local preview on :5173
npm run build    # writes ../site, which Vercel serves
```

Run `python -m scripts.build` before `npm run build`: the app renders whatever
`data/map.json` last held.

Two checks worth running after a build:

```bash
python -m pytest                    # 49 tests: data rules, diagram, payload
python tests/check_external_links.py  # the built page must fetch nothing off-origin
```

## Licence

Prose and data CC-BY-4.0; code MIT. See [LICENSE.md](LICENSE.md).
