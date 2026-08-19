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
understand the shape of it in ten minutes without opening twelve repositories.

Two deliverables from one source of truth:

1. A repository whose `README.md` carries the narrative and the repo table.
2. A one-page public website carrying the same content plus a generated
   dependency diagram.

The map is expected to change for the life of the programme. Cheap, correct
updating is a first-class requirement, not an afterthought.

## 2. Scope

**In scope.** The nine `systems-researcher` repositories and the three
local-only research repositories that have no remote yet
(`ahp-framing-fragility-probe`, `dsm-sequencing-probe`,
`epistemic-adequacy-metamodel`).

**Out of scope.** The `jgsystemsconsulting` tooling repositories (MCP bridges,
skill packs), thesis-writing infrastructure (`LboroPhdRepo`, thesis template),
and commercial work. A tooling repository may be *named* in a card where a study
depends on it, but gets no card of its own.

**Explicitly not built** (YAGNI, revisit only on evidence):

- A docs-site generator (MkDocs, Astro Starlight). Twelve cards fit one page.
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

| Repository | Claim under test |
|---|---|
| `model-vs-document-defect-probe` | MBSE's flagship claim: does a connected model beat information-equivalent documents |
| `ahp-framing-fragility-probe` | Does a structured trade study's winner flip under cosmetic perturbation |
| `dsm-sequencing-probe` | Does DSM produce the optimal task order, measured against a provable optimum |

### Assembly

`Thesis-Work-Area` is shown as the terminus of both strands. It is a node on the
diagram and never a dependency of anything: material moves *into* the thesis, and
no repository is permitted to link back to it or depend on it.

## 4. Content model

`repos.yml` is the single hand-authored source of truth. One entry per
repository:

```yaml
- key: epistemic-adequacy-probe      # the GitHub repo name, verbatim, casing included
  owner: systems-researcher          # or "local" when there is no remote yet
  strand: adequacy                   # adequacy | method-validation | assembly
  stage: evidence                    # define | measure | evidence | architecture | assembly
  objective: >                       # one sentence: what the repo is for
    ...
  question: >                        # the question it answers
    ...
  method: >                          # how it answers it
    ...
  status: published                  # design | built-runs-pending | results | published
  headline: >                        # measured result, with its source and version;
    ...                              # omit entirely when there is nothing measured
  output: "doi:10.1145/3822455.3838783"   # optional: paper, artefact, release
  depends_on: [epistemic-adequacy-spec, epistemic-adequacy-toolkit]
```

Rules on the fields:

- `headline` carries a number **only** when a run produced it, and always names
  the artefact and version it came from. A repository at design stage has no
  `headline` key. The map must never imply a result exists where none does.
- `status` is the author's judgement, not derived. `built-runs-pending` is a real
  and common state in this programme and must be visible as such.
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

`data/live.json` holds machine-derived fields only — description, visibility,
default branch, last push date — keyed by `key`. It is generated, never edited,
and committed so a build works without network access. Keeping it separate from
`repos.yml` is deliberate: a refresh can never clobber authored prose.

Local-only repositories (`owner: local`) have no live data. They render with a
"not yet published" badge and no link.

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
  LICENSE                CC-BY-4.0 for prose, MIT for scripts
```

### `scripts/refresh.py`

Calls `gh api repos/{owner}/{key}` for every entry with a real owner, writes
`data/live.json`. Failures are non-fatal per repository: a repo that cannot be
reached keeps its previous live entry and the script reports which ones went
stale on stderr. Requires an authenticated `gh`; no token handling of its own.

### `scripts/build.py`

Pure function of `repos.yml` + `data/live.json`. Emits:

- `site/index.html` — the whole page, CSS inline, one `<script>` tag for Mermaid
  from CDN.
- The Mermaid graph definition, inlined in that page, with nodes grouped into
  subgraphs by stage and edges taken from `depends_on` alone.
- The README table, written between `<!-- BEGIN:repos -->` and
  `<!-- END:repos -->` markers. Content outside the markers is never touched.

`build.py --check` validates and exits non-zero on:

1. a `depends_on` or `feeds` entry naming a key that does not exist;
2. a `stage` or `strand` outside the permitted sets;
3. a card missing a required field (`key`, `owner`, `strand`, `stage`,
   `objective`, `question`, `status`);
4. `Thesis-Work-Area` appearing in any other card's `depends_on` (the terminus
   rule: the thesis consumes, it never supplies);
5. a `headline` present on a card whose `status` is not `results` or
   `published` — a repository whose runs have not happened cannot carry a number.

This is the project's one test. It runs as `python scripts/build.py --check` and
is the check a future change has to keep passing.

## 6. The website

One page, no framework, no build step at deploy time.

Structure, top to bottom:

1. **Header** — thesis title, one-paragraph statement of the research question,
   and the single sentence that states the methodological move.
2. **Diagram** — the generated Mermaid graph, stages left to right, strands as
   rows. Nodes link to their card.
3. **Strand 1**, stage by stage. Each stage gets a one-line explanation of why
   the stage exists, then its cards.
4. **Strand 2**, same treatment.
5. **Assembly** — the thesis terminus.
6. **Footer** — how to request access to a private repository, last-refreshed
   date from `data/live.json`.

Card rendering: title (links to GitHub), visibility badge, status badge,
objective, question, method, headline result when present, and two link rows —
"depends on" (authored) and "feeds" (derived by inversion) — as internal anchors
to the other cards on the page.

Design constraints: readable at 400px wide, works in light and dark, no
horizontal page scroll, external links marked. No client-side JavaScript beyond
Mermaid.

### Hosting

Vercel project connected to the private GitHub repository, static output
directory `site/`, public URL. The repository stays private; the built page is
public. Nothing in `repos.yml` may contain unpublished results the programme is
not ready to disclose — the page is world-readable and should be authored on that
assumption.

Private repository links are rendered with a "private" badge and still point at
GitHub, so a reader with access lands correctly and a reader without one sees
immediately why they cannot.

## 7. Workflow for keeping it current

```
# after anything changes in the programme
edit repos.yml
python scripts/refresh.py      # optional; pulls live GitHub fields
python scripts/build.py        # regenerates site/index.html and the README block
python scripts/build.py --check
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
| `repos.yml` malformed | `build.py` fails with the YAML error and the offending key; no partial write to `site/index.html` |
| A card references a missing key | `--check` fails with both keys named |

`build.py` writes to a temporary file and moves it into place, so a crashed build
never leaves a half-written page.

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
