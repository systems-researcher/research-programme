<!--
Copyright (c) 2026 Jason D. Gower
SPDX-License-Identifier: CC-BY-4.0
-->

# Design: research-programme — the front door to the research

**Date:** 2026-08-19
**Repo:** `systems-researcher/research-programme` (private)
**Account:** `systems-researcher` is a second **personal GitHub account**, not an
organisation (`gh api user` returns it as the authenticated login, type `User`).
Create the repository while authenticated as that account.
**Status:** design approved, not yet implemented

---

## 1. Purpose

A single entry point that explains what every repository in the doctoral research
programme is for, what question it answers, and how it links to the others.

Primary reader: the supervisor, or anyone told "look at my research" who needs to
understand the shape of it in ten minutes without opening thirteen
repositories.

Two deliverables from one source of truth:

1. A repository whose `README.md` carries the narrative and the repo table.
2. A one-page public website carrying the same content plus a generated
   dependency diagram.

The map is expected to change for the life of the programme. Cheap, correct
updating is a first-class requirement, not an afterthought.

## 2. Scope

**In scope.** The ten `systems-researcher` repositories and the three
local-only research repositories that have no remote yet
(`ahp-framing-fragility-probe`, `dsm-sequencing-probe`,
`epistemic-adequacy-metamodel`). Thirteen repositories, and `Thesis-Work-Area`
is one of the ten, so `repos.yml` holds thirteen entries in total. The count of
ten was verified against `gh repo list systems-researcher` on 2026-08-19; it
includes `sysml2-bench` and `model-vs-document-defect-probe`, which resolve under
the old `jgsystemsconsulting` paths only as redirects.

**Out of scope.** The `jgsystemsconsulting` tooling repositories (MCP bridges,
skill packs), thesis-writing *infrastructure* (`LboroPhdRepo`, the Loughborough
thesis LaTeX template), and commercial work. `Thesis-Work-Area` is in scope and
distinct from those: it is where the programme's findings are written up, so it
is the terminus the map needs, whereas the excluded repositories are build
machinery for the document. A tooling repository may be *named* in a card where a study
depends on it, but gets no card of its own.

**Explicitly not built** (YAGNI, revisit only on evidence):

- A docs-site generator (MkDocs, Astro Starlight). Twelve cards and one terminus node fit on one page.
- Scheduled CI refresh. Manual refresh first; automate when it demonstrably rots.
- Per-repo detail pages. The card is the unit.
- Search. One page, `Ctrl-F`.

## 3. The argument the map presents

Everything hangs off one methodological move: **an AI agent stands in as a
consistent practitioner**, which converts method and representation into
manipulable experimental factors and makes replicated designs affordable that
human-subject systems-engineering research could never run.

That move branches into two strands.

### Strand 1 — epistemic adequacy (thesis spine)

Thesis framing: *Architecting Trustworthy AI Integration in MBSE*; the MODELS
2026 NIER paper's two sides are read-side adequacy and write-side admissibility.

| Stage | Repositories | Role |
|---|---|---|
| Define | `epistemic-adequacy-spec`, `epistemic-adequacy-metamodel` | States what a record must expose; binds it to SysML v2 as metamodel, data model, and ontology |
| Measure | `epistemic-adequacy-toolkit`, `sysml2-bench` | Instruments. The toolkit scores a substrate against the clauses and joins that score to consumer behaviour; the bench measures baseline LLM competence on SysML v2 and acts as the capability control |
| Evidence (read-side) | `epistemic-adequacy-probe`, `pressure-susceptibility-probe` | Does exposing epistemic metadata change how an AI answers, and does that hold under pressure |
| Architecture (write-side) | `SysML-v2-API-Services-Arch-A`, `sysml-v2-metadata-graph-Arch-B`, `sysml-v2-governed-substrate-Arch-C` | Three candidate substrates implementing the admissibility gate, compared |

### Strand 2 — do classic SE methods survive an AI practitioner

| Repository | Stage | Claim under test |
|---|---|---|
| `model-vs-document-defect-probe` | `evidence` | MBSE's flagship claim: does a connected model beat information-equivalent documents |
| `ahp-framing-fragility-probe` | `evidence` | Does a structured trade study's winner flip under cosmetic perturbation |
| `dsm-sequencing-probe` | `evidence` | Does DSM produce the optimal task order, measured against a provable optimum |

All three sit at `evidence`: each is an instrument that produces a measured
result about a method. `strand` decides which section of the page an entry lands
in; `stage` decides which subgraph it lands in on the diagram. The two are
independent, and every entry carries both.

### Assembly

`Thesis-Work-Area` is the terminus of both strands: a node on the diagram, with
**no card, and no hyperlink on the node**. It is never a dependency of anything —
material moves *into* the thesis, and no repository may depend on it. Its entry
is a full, valid record like any other; only its rendering differs:

```yaml
- key: Thesis-Work-Area
  owner: systems-researcher
  strand: assembly
  stage: assembly
  render: node-only
  objective: >
    Where the programme's findings are written up as the doctoral thesis.
  question: >
    Not applicable: this is the destination, not a study.
  method: >
    Not applicable.
  status: not-applicable
  depends_on: [epistemic-adequacy-probe, pressure-susceptibility-probe,
               SysML-v2-API-Services-Arch-A, sysml-v2-metadata-graph-Arch-B,
               sysml-v2-governed-substrate-Arch-C, model-vs-document-defect-probe,
               ahp-framing-fragility-probe, dsm-sequencing-probe]
```

`render: node-only` changes rendering only. It grants **no exemption** from
`--check`: every required field is still required, so a node-only entry cannot
become a hole in the validation.

## 4. Content model

`repos.yml` is the single hand-authored source of truth, with four top-level
blocks. `programme` carries the page's framing prose, `strands` carries each
section's heading and subtitle, `stages` carries the one-line explanation each
stage sub-section shows, and `repos` carries one entry per repository. Nothing
the page displays is hardcoded in `build.py`:

```yaml
programme:
  title: "Architecting Trustworthy AI Integration in MBSE"
  question: >
    One paragraph stating the research question, rendered in the page header.
  move: >
    The one sentence stating the methodological move (an AI agent standing in as
    a consistent practitioner), rendered under the question.

strands:
  adequacy:
    title: "Epistemic adequacy"
    subtitle: "Can a record tell an AI what it is authorised to say?"
  method-validation:
    title: "Do classic SE methods survive an AI practitioner?"
    subtitle: "The same instrument turned on the methods themselves."
  assembly:
    title: "Assembly"
    subtitle: "Where the findings are written up."

stages:
  define: "What a record must expose, and how that binds to SysML v2."
  measure: "The instruments that turn the definition into a number."
  evidence: "What the instruments have actually measured."
  architecture: "Candidate substrates that enforce it on the write side."
  assembly: "Where it is written up."

repos:
  - key: ...
```

Each entry under `repos`:

```yaml
- key: epistemic-adequacy-probe      # the GitHub repo name, verbatim, casing included
  owner: systems-researcher          # or "local" when there is no remote yet
  strand: adequacy                   # adequacy | method-validation | assembly
  stage: evidence                    # define | measure | evidence | architecture | assembly
  render: card                       # card (default) | node-only
  objective: >
    First measured test of whether epistemic metadata, beyond structured model
    access alone, changes how an AI consumer answers derivation questions.
  question: >
    Does an AI consumer reading an MBSE model produce fewer unauthorised answers
    when the model exposes derivation, status, and provenance?
  method: >
    Three LLMs, 120 judged answers, over a verbatim excerpt of the public
    Airbus Apollo 11 SysML v2 reconstruction, with and without a sidecar.
  status: published                  # see the permitted-values table below
  headline:                          # omit entirely when nothing has been measured
    text: >
      Unauthorised content on 13.3% of governed answers bare, 2.2% with the
      metadata layer; 60% under answer pressure, roughly halved with it.
    source: "epistemic-adequacy-probe v0.2.0, RESULTS.md verdict counts"
  output: "doi:10.1145/3822455.3838783"   # optional: paper, artefact, release
  depends_on: [epistemic-adequacy-spec, epistemic-adequacy-toolkit]
```

**Required on every entry:** `key`, `owner`, `strand`, `stage`, `objective`,
`question`, `method`, `status`.
**Optional:** `render` (defaults to `card`), `headline`, `output`, `depends_on`
(absent means the repository depends on nothing else in the map).

Permitted values, which `--check` enforces:

| Field | Values |
|---|---|
| `strand` | `adequacy`, `method-validation`, `assembly` |
| `stage` | `define`, `measure`, `evidence`, `architecture`, `assembly` |
| `status` | `design`, `built-runs-pending`, `released`, `results`, `published`, `not-applicable` |
| `render` | `card`, `node-only` |
| `owner` | the literal `local`, or a non-empty GitHub account name — `--check` verifies it is non-empty and matches `[A-Za-z0-9-]+`, not that the account exists |

`render: node-only` suppresses card rendering while keeping the diagram node. It
is used by `Thesis-Work-Area` alone.

Rules on the fields:

- `headline` is a mapping of `text` (the result in prose) and `source` (the
  artefact and version the number came from). Both are required whenever
  `headline` is present, which makes "every number is attributed" a mechanically
  checkable rule rather than an authoring habit. A repository whose runs have not
  happened has no `headline` key at all. The map must never imply a result exists
  where none does.
- `status` is the author's judgement, not derived. `built-runs-pending` is a real
  and common state in this programme and must be visible as such.
  `released` is for a versioned artefact that ships without producing a measured
  result — a specification, a library, an instrument release. It exists because
  the enum is otherwise a study lifecycle, and calling a released specification
  "design stage" on a supervisor-facing page understates it. A `released` entry
  carries no `headline`: a release is not a measurement.
  `not-applicable` exists for entries that are not studies and have no run
  lifecycle at all; `--check` permits it only on `render: node-only` entries, and
  permits `render: node-only` only on `Thesis-Work-Area`. The two rules together
  are what stops the pair being used to hide a study: without the second, any
  entry could be marked node-only and not-applicable and vanish from the cards.
- `depends_on` states what a repository consumes **now and going forward**, not
  what existed when it was committed. Most of the programme predates the
  specification, so reading the edges as commit order would be wrong.
- `depends_on` is the **only** authored edge source. The reverse direction
  ("what this feeds") is derived at build time by inverting the graph, so the two
  can never disagree and no edge can be declared twice. Keys are named verbatim,
  so `SysML-v2-API-Services-Arch-A` and `Thesis-Work-Area` keep their upstream
  casing.

Two repositories, `sysml2-bench` and `model-vs-document-defect-probe`, resolve
under both `jgsystemsconsulting/` and `systems-researcher/` with identical push
timestamps: they were transferred, and the old paths are GitHub redirects. The
map names the `systems-researcher` path in both cases. Several local working
copies still carry the pre-transfer remote; that is harmless and out of scope
here.

`data/live.json` holds machine-derived fields only, and only fields the page
actually renders. Its shape is a top-level `generated_at` (ISO-8601 UTC timestamp
of the last successful refresh, which the site footer renders) and a `repos`
object keyed by `key`, each holding `visibility` and `pushed_at`. A field nothing
renders does not belong here: it would be data the map carries but never shows. It is generated,
never edited, and committed so a build works without network access. Keeping it separate from
`repos.yml` is deliberate: a refresh can never clobber authored prose.

Local-only repositories (`owner: local`) have no live data. They render with a
"not yet published" badge and no link. A non-`local` entry missing from
`live.json`'s `repos` map — added to `repos.yml` since the last refresh, or
unreachable when `refresh.py` ran — keeps its GitHub link and is badged
"awaiting refresh" instead. See §5 for the two missing-data cases in full.

## 5. Repository layout

```
research-programme/
  README.md              narrative spine + repo table generated between markers
  repos.yml              source of truth (hand-authored)
  data/live.json         generated by refresh.py
  scripts/refresh.py     gh api -> data/live.json
  scripts/build.py       repos.yml + live.json -> site/index.html + README block
  site/index.html        generated, committed
  vercel.json            static output dir = site/
  docs/superpowers/specs/  this document
  LICENSE.md             states the split: CC-BY-4.0 for prose, MIT for scripts
  LICENSE-MIT            the MIT text the code is under
```

### `scripts/refresh.py`

Calls `gh api repos/{owner}/{key}` for every entry with a real owner, writes
`data/live.json`. On the very first run the file does not exist yet; the script
creates it.

Missing live data has exactly two cases, and neither ever blocks a build:

- **The whole file is absent.** `build.py` builds from `repos.yml` alone, omits
  the footer's last-refreshed line entirely, badges every non-`local` entry
  "awaiting refresh", and prints a warning.
- **Every lookup failed.** `refresh.py` exits non-zero and leaves
  `data/live.json` untouched. It must never stamp a fresh `generated_at` over a
  refresh that reached nothing: the footer would then publish a last-refreshed
  date describing no data at all.
- **The file exists but has no entry for a key.** The footer always renders that
  file's `generated_at` — it is the honest timestamp of the last successful
  refresh, whatever it covered — and the individual entry is badged "awaiting
  refresh". Failures are non-fatal per repository: a repo that cannot be
reached keeps its previous live entry and the script reports which ones went
stale on stderr. Requires an authenticated `gh`; no token handling of its own.

### `scripts/build.py`

Pure function of `repos.yml` + `data/live.json`. Emits:

- `site/index.html` — the whole page, CSS inline, one `<script>` tag for Mermaid
  from CDN.
- The Mermaid graph definition, inlined in that page: one subgraph per stage in
  argument order, strand carried by a Mermaid `classDef` per strand rather than
  by layout, and edges taken from `depends_on` alone.
- The README table, written between `<!-- BEGIN:repos -->` and
  `<!-- END:repos -->` markers. Content outside the markers is never touched.

`build.py --check` validates and exits non-zero on:

1. a `depends_on` entry naming a key that does not exist;
2. a `stage` or `strand` outside the permitted sets;
3. a card missing any required field (`key`, `owner`, `strand`, `stage`,
   `objective`, `question`, `method`, `status`) — `render: node-only` is not an
   exemption;
4. `Thesis-Work-Area` appearing in any other card's `depends_on` (the terminus
   rule: the thesis consumes, it never supplies);
5. a `headline` present on a card whose `status` is not `results` or
   `published` — a repository whose runs have not happened cannot carry a number;
   `status: not-applicable` on any entry that is not `render: node-only`; or
   `render: node-only` on any entry other than `Thesis-Work-Area`;
6. a `headline` missing either `text` or `source`, which is what makes every
   published number attributable;
7. a field value outside the permitted sets in the table in §4, or a duplicate
   `key`;
8. a missing `programme` block, a missing `programme.title`, `programme.question`
   or `programme.move`, or a `stage` or `strand` used by some entry with no
   matching line in `stages` or `strands` — a section would otherwise render with
   no heading or no explanation;
9. a `depends_on` cycle, or an entry naming itself. The graph is a DAG: a cycle
   makes "what feeds what" unanswerable and would render an unreadable diagram.
   `--check` reports the full cycle path, not just one edge.

These nine rules are the project's whole test suite. They run as
`python scripts/build.py --check`, and that command is what a future change has
to keep passing.

## 6. The website

One page, no framework, no build step at deploy time.

Structure, top to bottom:

1. **Header** — thesis title, one-paragraph statement of the research question,
   and the single sentence that states the methodological move.
2. **Diagram** — the generated Mermaid graph, stages left to right. Every node
   whose entry renders a card is hyperlinked to that card's anchor; a
   `render: node-only` node carries no link, because there is no anchor to
   point at.
3. **Strand 1**, stage by stage. Each stage gets a one-line explanation of why
   the stage exists, then its cards.
4. **Strand 2**, same treatment.
5. **Assembly** — the thesis terminus.
6. **Footer** — how to request access to a private repository, last-refreshed
   date from `data/live.json`.

Card rendering: title (links to GitHub), visibility badge, status badge,
objective, question, method, headline result when present, and two rows —
"depends on" (authored) and "feeds" (derived by inversion). Each entry in those
rows is an internal anchor to the named card, except where the named key is
`render: node-only`, which renders as plain text. No row ever emits an anchor to
an element the page does not contain.

Design constraints: readable at 400px wide, works in light and dark, no
horizontal page scroll, external links marked. No client-side JavaScript beyond
Mermaid.

### Hosting

Vercel project connected to the private GitHub repository, static output
directory `site/`, public URL. The repository stays private; the built page is
public. Every repository gets a full card, design-stage ones included: the AHP
flip-rate and DSM sequencing probes publish their objective, question, and method
before they have been run, which stakes the ground and is a deliberate choice.
What must never appear is a **result** that has not been produced — that is what
`--check` rule 5 enforces. The page is world-readable and `repos.yml` is authored
on that assumption.

Private repository links are rendered with a "private" badge and still point at
GitHub, so a reader with access lands correctly and a reader without one sees
immediately why they cannot.

## 7. Workflow for keeping it current

```
# after anything changes in the programme
edit repos.yml
python -m scripts.refresh      # optional; pulls live GitHub fields
python -m scripts.build        # regenerates site/index.html and the README block
python -m scripts.build --check   # must pass; a non-zero exit stops here, nothing is committed
git commit -am "map: <what changed>"
git push                       # Vercel redeploys
```

No CI. If the committed site is ever found stale against `repos.yml`, add a
GitHub Action running `build.py` and failing on a dirty tree — at that point the
drift is evidenced and the automation is earned.

## 8. Error handling

| Failure | Behaviour |
|---|---|
| `gh` unauthenticated or offline | `refresh.py` exits non-zero, prints the reason, leaves `data/live.json` untouched. `build.py` still works from the committed file |
| A repository is renamed or deleted | `refresh.py` reports it as stale; `--check` still passes, because the graph is authored not derived. The author fixes `repos.yml` |
| `repos.yml` has a YAML syntax error | `build.py` fails with the parser's line and column; no partial write to `site/index.html` |
| `repos.yml` parses but an entry is invalid | `build.py` fails naming the offending `key` and field; no partial write |
| A card references a missing key | `--check` fails with both keys named |

`build.py` writes both of its outputs — `site/index.html` and the rewritten
`README.md` — to temporary files and moves each into place, so a crashed build
leaves neither a half-written page nor a README with one marker and no other.

## 9. Success criteria

1. A reader who has never seen the programme can name, after ten minutes on the
   page, what each repository is for and which repository feeds which.
2. Every claim on the page that carries a number also carries the artefact and
   version that number came from.
3. Adding a new repository to the programme costs one `repos.yml` entry and one
   command.
4. `python scripts/build.py --check` passes, and fails when an edge is broken.
5. The diagram and the cards cannot disagree, because both are generated from
   one authored edge list, and the reverse direction is derived rather than
   written twice.

## 10. Open questions

None blocking. Deferred by choice: whether the site eventually needs per-repo
pages (only if a card stops fitting one screen), and whether to publish the map
itself as a public repository once enough of the programme is public.
