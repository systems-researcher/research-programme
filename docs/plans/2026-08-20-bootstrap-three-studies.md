# Bootstrap Three Scoped Studies — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the three GitHub repositories scoped in `repos.yml` on 2026-08-20 — `admissibility-spec`, `epistemic-adequacy-under-pressure-probe`, `governed-interaction-cost-probe` — each carrying the programme's house structure and its own scoped question, so a full research execution can be run against them.

**Architecture:** Each repository is created private under `systems-researcher`, seeded from the structure the existing programme repositories share (dual licence, CITATION.cff, contribution and security policy, a stated question), and given a README that says what it is for. `repos.yml` is then flipped from `owner: local` to `owner: systems-researcher`, and the map regenerated so the study stops being badged "not yet published".

This plan bootstraps the repositories. It does **not** write the admissibility clauses, build the two-by-two harness, or instrument the cost probe — those are the research executions this plan makes possible, and each needs its own plan.

**Tech Stack:** `gh` CLI (authenticated as `systems-researcher`), git, Python 3.13 with PyYAML, GitHub Actions.

**Spec:** The scoped entries in `repos.yml` are the specification. Each carries `objective`, `question`, `method`, and `depends_on`, validated by the ten rules in `scripts/mapdata.py`. Read the entry for a study before bootstrapping it — the README must not say anything the entry does not.

## Global Constraints

- **Visibility:** private at creation. The map badges private repositories "readable on request"; nothing here is ready to publish.
- **Owner:** `systems-researcher`, not `jgsystemsconsulting`. The programme's studies live under one account.
- **Licence:** prose and data CC-BY-4.0, code MIT, as `LICENSE.md` states. Every Markdown and YAML file carries an SPDX identifier in a comment.
- **Copyright:** `Copyright (c) 2026 Jason D. Gower, Michael J. de C. Henshaw, Siyuan Ji` on programme output.
- **Never invent a result, a citation, or a DOI.** These three studies have produced nothing. A README implying otherwise is a false claim about the record.
- **`repos.yml` is the source of truth.** The README restates its `objective` and `question`. If bootstrapping reveals the entry is wrong, change the entry first and regenerate.
- **After any `repos.yml` edit:** run `python -m scripts.build --check`, then `python -m scripts.build`, and commit the regenerated `data/map.json` and `README.md`. CI fails on a stale payload.

---

### Task 1: Bootstrap `admissibility-spec`

Do this one first: it is the study the three architecture candidates already depend on, and its shape is closest to an existing repository, so it establishes the pattern the other two follow.

**Files:**
- Create (in the new repository): `README.md`, `LICENSE.md`, `LICENSE-MIT`, `CITATION.cff`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.gitignore`, `SPEC.md`
- Modify: `repos.yml` — the `admissibility-spec` entry, `owner` field only
- Regenerate: `data/map.json`, `README.md` (this repository's table)

**Interfaces:**
- Consumes: the `admissibility-spec` entry in `repos.yml` — its `objective`, `question` and `method` are the README's only source.
- Produces: a repository at `https://github.com/systems-researcher/admissibility-spec`, and an entry whose `owner` is `systems-researcher`, so `refresh.py` queries it and the map shows real visibility and last commit.

- [ ] **Step 1: Read the scoped entry, so the README cannot contradict it**

```bash
cd /c/Users/gower/OneDrive/Documents/GitHub/research-programme
python -c "
import yaml
d = yaml.safe_load(open('repos.yml', encoding='utf-8'))
e = [x for x in d['repos'] if x['key'] == 'admissibility-spec'][0]
for f in ('objective', 'question', 'method', 'depends_on'):
    print(f.upper(), ':', ' '.join(str(e[f]).split()))
    print()
"
```

Expected: the objective, question and method committed on 2026-08-20. Everything the README says about purpose must trace to this output.

- [ ] **Step 2: Create the repository, private**

```bash
gh repo create systems-researcher/admissibility-spec \
  --private \
  --description "Write-side conformance: what an AI-authored engineering contribution must carry to be admitted to the authoritative record." \
  --clone
cd admissibility-spec
```

Expected: `gh` reports the repository created and clones an empty directory.

- [ ] **Step 3: Copy the licence files verbatim from the programme repository**

One licence split across every repository; retyping invites drift.

```bash
PROG=/c/Users/gower/OneDrive/Documents/GitHub/research-programme
cp "$PROG/LICENSE.md" "$PROG/LICENSE-MIT" .
```

Then delete the "Third-party components" section from the copied `LICENSE.md` — it describes the map site's vendored shadcn/ui and Geist, which this repository does not contain. Keep the prose/code split and the SPDX paragraph.

- [ ] **Step 4: Write `.gitignore`**

```gitignore
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.venv/
*.tmp
```

- [ ] **Step 5: Write `CITATION.cff`**

No `preferred-citation` block: this study has no paper, and adding one would claim a publication that does not exist.

```yaml
cff-version: 1.2.0
message: "If you use this specification, cite it as below."
title: "Admissibility Specification — conformance requirements for AI participation in the authoritative engineering record"
abstract: >
  Conformance requirements stating what an AI-authored engineering
  contribution must carry, and what conditions a substrate must check,
  before that contribution may enter the authoritative record.
authors:
  - given-names: "Jason D."
    family-names: "Gower"
    orcid: "https://orcid.org/0009-0001-5945-6294"
    affiliation: "Loughborough University, Loughborough, United Kingdom"
  - given-names: "Michael J. de C."
    family-names: "Henshaw"
    orcid: "https://orcid.org/0000-0003-0511-179X"
    affiliation: "Loughborough University, Loughborough, United Kingdom"
  - given-names: "Siyuan"
    family-names: "Ji"
    orcid: "https://orcid.org/0000-0001-6139-3539"
    affiliation: "Loughborough University, Loughborough, United Kingdom"
license: CC-BY-4.0
repository-code: "https://github.com/systems-researcher/admissibility-spec"
```

- [ ] **Step 6: Write `README.md`**

State the question and the gap. State no result; there is none. The status badge says `scoping`, not `working draft`, because no clause is written.

~~~markdown
<!--
Copyright (c) 2026 Jason D. Gower, Michael J. de C. Henshaw, Siyuan Ji
SPDX-License-Identifier: CC-BY-4.0
-->

# Admissibility Specification

**What an AI-authored engineering contribution must carry before it may enter the authoritative record.**

![status](https://img.shields.io/badge/status-scoping-lightgrey)
![licence](https://img.shields.io/badge/docs-CC--BY--4.0-green)
![licence](https://img.shields.io/badge/code-MIT-green)

---

## The question

What must an AI-generated engineering contribution expose — its author, its
warrant, the standing of its review, and its effect on claims already in the
record — for a substrate to decide admissibility by rule rather than by
reviewer judgement?

## Why this repository exists

[`epistemic-adequacy-spec`](https://github.com/systems-researcher/epistemic-adequacy-spec)
covers the read side: what a record must expose so an AI consumer can tell a
grounded claim from an ungrounded one. It says nothing about writes.

Three architecture candidates already implement admissibility gates — Arch-A in
front of the SysML v2 API, Arch-B as a promotion gate, Arch-C as a governance
API confining signed AI writes to a companion namespace. Each invents its
admission conditions independently, because no specification states them. This
repository is that specification.

## Scope

In scope: the admission decision. What a contribution must carry, what a
substrate must check, and what it must record about the decision.

Out of scope: how a substrate stores or enforces it. That is what the
architecture candidates are for, and keeping it out is what lets them be
compared.

## Status

Scoping. No clauses are written yet. Part of a doctoral research programme; see
the [programme map](https://systems-researcher.github.io/research-programme/).

## Licence

Prose and data CC-BY-4.0; code MIT. See [LICENSE.md](LICENSE.md).
~~~

- [ ] **Step 7: Write `SPEC.md` as an empty structure, not a placeholder**

The file exists so the shape of the work is visible. It states what is absent rather than pretending to content.

~~~markdown
<!--
Copyright (c) 2026 Jason D. Gower, Michael J. de C. Henshaw, Siyuan Ji
SPDX-License-Identifier: CC-BY-4.0
-->

# Admissibility Specification

**Version 0.0.0 — scoping. No clause below is written.**

## 1. Scope

The admission decision for AI-authored contributions to an authoritative
engineering record.

## 2. Terms

To be defined: contribution, author, warrant, review standing, admission,
companion namespace, promotion.

## 3. Criteria

The read-side specification decomposes into five criteria, EA1 to EA5. The
write-side decomposition is not yet decided. Candidate axes, to be settled
before any clause is written:

- Attribution — who or what authored the contribution, and how that is proven.
- Warrant — what the contribution claims as its basis, and whether that basis
  is reachable in the record.
- Review — what human or automated review it has passed, and at what standing.
- Effect — what existing claims it changes, contradicts, or supersedes.
- Record — what the substrate must retain about the admission decision itself.

## 4. Conformance profiles

Not yet defined. The read-side specification uses three; whether the same
division suits the write side is an open question.

## 5. Clause manifest

Not yet written. When clauses exist, this section carries the machine-readable
manifest and CI validates it against the prose, as the read-side specification
does.
~~~

- [ ] **Step 8: Copy the community health files**

```bash
gh api repos/systems-researcher/epistemic-adequacy-spec/contents/CONTRIBUTING.md --jq '.content' | base64 -d > CONTRIBUTING.md
gh api repos/systems-researcher/epistemic-adequacy-spec/contents/SECURITY.md --jq '.content' | base64 -d > SECURITY.md
gh api repos/systems-researcher/epistemic-adequacy-spec/contents/CODE_OF_CONDUCT.md --jq '.content' | base64 -d > CODE_OF_CONDUCT.md
```

Then read each one and correct every reference to the repository it came from. `CONTRIBUTING.md` in particular names clause numbers and a repository name; a contribution guide describing another repository's clauses is worse than none.

- [ ] **Step 9: Verify nothing claims a result that does not exist**

```bash
grep -rniE "13\.3|2\.2%|60%|doi:|10\.1145|results in hand|published" . --include="*.md" --include="*.cff" || echo "clean: no borrowed results or citations"
```

Expected: `clean`. Any hit is a number or citation copied from another repository and must be removed. This is the check that would have caught the fabricated citation corrected in `ad21973`.

- [ ] **Step 10: Commit and push**

```bash
git add -A
git commit -m "chore: scope the admissibility specification

The write-side counterpart to epistemic-adequacy-spec. States the question and
the gap; no clause is written yet, and SPEC.md says so rather than carrying
placeholder content.

Three architecture candidates already implement admissibility gates with no
specification above them. This repository is that specification."
git push -u origin main
```

- [ ] **Step 11: Set topics**

```bash
gh repo edit systems-researcher/admissibility-spec \
  --add-topic ai-governance,admissibility,epistemic-adequacy,mbse,provenance,specification,sysml-v2,systems-engineering
```

- [ ] **Step 12: Flip the entry to its real owner**

```bash
cd /c/Users/gower/OneDrive/Documents/GitHub/research-programme
python - <<'EOF'
import re
from pathlib import Path
p = Path("repos.yml")
s = p.read_text(encoding="utf-8")
s = re.sub(r"(- key: admissibility-spec\n    owner: )local", r"\1systems-researcher", s, count=1)
p.write_text(s, encoding="utf-8")
EOF
python -m scripts.build --check
```

Expected: `repos.yml: 16 entries, all ten rules pass`

- [ ] **Step 13: Refresh live data, rebuild, and verify the map shows it**

```bash
python -m scripts.refresh
python -m scripts.build
python -c "
import json
d = json.load(open('data/map.json', encoding='utf-8'))
e = [x for s in d['strands'] for x in s['entries'] if x['key'] == 'admissibility-spec'][0]
print('url    :', e['url'])
print('badges :', e['badges'])
"
```

Expected: a `github.com/systems-researcher/admissibility-spec` URL, and badges reading `private`, `design`, and a last-commit date — not `not yet published`.

- [ ] **Step 14: Run the full check and commit**

```bash
python -m pytest -q
python tests/mutate_check.py
npm --prefix app run build
python tests/check_external_links.py
git add -A
git commit -m "feat(data): publish admissibility-spec as a real repository

Owner flips from local to systems-researcher, so refresh.py queries it and the
map shows its visibility and last commit rather than badging it not yet
published."
git push origin main
```

Expected: tests pass, the validator bites on all four mutations, the build succeeds, and the link check reports one more outbound link than before.

---

### Task 2: Bootstrap `epistemic-adequacy-under-pressure-probe`

A study rather than a specification, so it carries a `PROTOCOL.md` describing the
design instead of a `SPEC.md`.

**Files:**
- Create (in the new repository): `README.md`, `LICENSE.md`, `LICENSE-MIT`, `CITATION.cff`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.gitignore`, `PROTOCOL.md`
- Modify: `repos.yml` - the `epistemic-adequacy-under-pressure-probe` entry, `owner` field only
- Regenerate: `data/map.json`, `README.md`

**Interfaces:**
- Consumes: the scoped entry in `repos.yml`; the influence-prompt library in `pressure-susceptibility-probe`; the annotated sidecar from `epistemic-adequacy-metamodel`. Neither is copied here - `PROTOCOL.md` names them as inputs.
- Produces: a repository at `https://github.com/systems-researcher/epistemic-adequacy-under-pressure-probe`, owned and queried.

- [ ] **Step 1: Read the scoped entry**

```bash
cd /c/Users/gower/OneDrive/Documents/GitHub/research-programme
python -c "
import yaml
d = yaml.safe_load(open('repos.yml', encoding='utf-8'))
e = [x for x in d['repos'] if x['key'] == 'epistemic-adequacy-under-pressure-probe'][0]
for f in ('objective', 'question', 'method', 'depends_on'):
    print(f.upper(), ':', ' '.join(str(e[f]).split()))
    print()
"
```

- [ ] **Step 2: Create the repository, private**

```bash
gh repo create systems-researcher/epistemic-adequacy-under-pressure-probe \
  --private \
  --description "Does epistemic metadata still protect an AI consumer under deadline, seniority, and false-premise pressure? A two-by-two." \
  --clone
cd epistemic-adequacy-under-pressure-probe
```

- [ ] **Step 3: Copy licences and community files**

```bash
PROG=/c/Users/gower/OneDrive/Documents/GitHub/research-programme
cp "$PROG/LICENSE.md" "$PROG/LICENSE-MIT" .
gh api repos/systems-researcher/epistemic-adequacy-spec/contents/CONTRIBUTING.md --jq '.content' | base64 -d > CONTRIBUTING.md
gh api repos/systems-researcher/epistemic-adequacy-spec/contents/SECURITY.md --jq '.content' | base64 -d > SECURITY.md
gh api repos/systems-researcher/epistemic-adequacy-spec/contents/CODE_OF_CONDUCT.md --jq '.content' | base64 -d > CODE_OF_CONDUCT.md
```

Strip the third-party section from `LICENSE.md` and correct `CONTRIBUTING.md`'s
references, as in Task 1 Steps 3 and 8.

- [ ] **Step 4: Write `.gitignore`**

`runs/` and `.env` matter here and did not in Task 1: this study calls model
APIs, and neither raw run output nor a key belongs in the repository.

```gitignore
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.venv/
*.tmp
runs/
.env
```

- [ ] **Step 5: Write `CITATION.cff`**

```yaml
cff-version: 1.2.0
message: "If you use this study, cite it as below."
title: "Epistemic Adequacy Under Pressure - does metadata protection survive answer pressure?"
abstract: >
  A two-by-two study crossing epistemic metadata against answer pressure,
  measuring how much of the metadata's protection against ungrounded
  engineering answers remains when the work pushes on the AI consumer.
authors:
  - given-names: "Jason D."
    family-names: "Gower"
    orcid: "https://orcid.org/0009-0001-5945-6294"
    affiliation: "Loughborough University, Loughborough, United Kingdom"
  - given-names: "Michael J. de C."
    family-names: "Henshaw"
    orcid: "https://orcid.org/0000-0003-0511-179X"
    affiliation: "Loughborough University, Loughborough, United Kingdom"
  - given-names: "Siyuan"
    family-names: "Ji"
    orcid: "https://orcid.org/0000-0001-6139-3539"
    affiliation: "Loughborough University, Loughborough, United Kingdom"
license: CC-BY-4.0
repository-code: "https://github.com/systems-researcher/epistemic-adequacy-under-pressure-probe"
```

- [ ] **Step 6: Write `README.md`**

The two prior rates may be cited here, because they are published in
`epistemic-adequacy-probe` v0.2.0 and this study exists because of them. Cite
them with their source. Claim nothing for this study.

~~~markdown
<!--
Copyright (c) 2026 Jason D. Gower, Michael J. de C. Henshaw, Siyuan Ji
SPDX-License-Identifier: CC-BY-4.0
-->

# Epistemic Adequacy Under Pressure

**Does the protection epistemic metadata gives against ungrounded answers survive answer pressure?**

![status](https://img.shields.io/badge/status-scoping-lightgrey)
![licence](https://img.shields.io/badge/docs-CC--BY--4.0-green)
![licence](https://img.shields.io/badge/code-MIT-green)

---

## The question

Does the protection epistemic metadata gives against ungrounded engineering
answers hold when the work pushes on the AI consumer, and by how much is it
eroded under deadline, seniority, and false-premise pressure?

## Why this repository exists

Two effects are established separately in this programme:

- Epistemic metadata reduces ungrounded answers. Under a governed instruction
  the bare model was ungrounded on 6 of 45 question-cells (13.3%); a sidecar
  cut that to 1 of 45 (2.2%). Source:
  [`epistemic-adequacy-probe`](https://github.com/systems-researcher/epistemic-adequacy-probe)
  v0.2.0, `RESULTS.md`.
- Pressure increases them. Under a deadline-style pressed instruction the bare
  model reached 9 of 15 (60%) on the five hardest questions. Same source.

Nothing crosses the two. The pressed figures above are bare-substrate; whether
the sidecar's protection holds under the same pressure is measured here and
nowhere else.

## Design

A two-by-two: governed against ungoverned record, calm against pressed
instruction. Neither factor is invented here - the influence-prompt library
comes from
[`pressure-susceptibility-probe`](https://github.com/systems-researcher/pressure-susceptibility-probe)
and the annotated sidecar from
[`epistemic-adequacy-metamodel`](https://github.com/systems-researcher/epistemic-adequacy-metamodel),
so this study varies only the crossing.

See [PROTOCOL.md](PROTOCOL.md).

## Status

Scoping. No runs have been executed and no result is claimed. Part of a
doctoral research programme; see the
[programme map](https://systems-researcher.github.io/research-programme/).

## Licence

Prose and data CC-BY-4.0; code MIT. See [LICENSE.md](LICENSE.md).
~~~

- [ ] **Step 7: Write `PROTOCOL.md`**

Pre-registering the design before any run is what keeps the result honest: the
analysis cannot be chosen after seeing the numbers.

~~~markdown
<!--
Copyright (c) 2026 Jason D. Gower, Michael J. de C. Henshaw, Siyuan Ji
SPDX-License-Identifier: CC-BY-4.0
-->

# Protocol

**Version 0.0.0 - scoping. Written before any run, and to be frozen before the first.**

## Factors

| Factor | Levels |
|---|---|
| Record | ungoverned (bare model) / governed (model plus EA1-EA4 sidecar) |
| Instruction | calm / pressed |

Four cells. The bare-calm and bare-pressed cells replicate published conditions
and act as the check that this harness reproduces them.

## Materials

- **Model excerpt.** The same verbatim excerpt of the public Airbus Apollo 11
  SysML v2 reconstruction used by `epistemic-adequacy-probe`, so the record is
  not a new variable.
- **Sidecar.** The annotated EA1-EA4 pair from `epistemic-adequacy-metamodel`,
  not hand-authored here.
- **Pressure levers.** The influence-prompt library from
  `pressure-susceptibility-probe`. Which levers, and how many, is settled
  before the first run and recorded here.

## Measure

Ungrounded-answer rate per cell, judged by the same rubric
`epistemic-adequacy-probe` used, so the numbers are comparable to the published
ones.

**Headline.** How much of the metadata's benefit remains under pressure,
reported as the governed-versus-ungoverned difference in the pressed condition
against the same difference in the calm condition.

## To settle before the first run

Each of these would change the result if decided after seeing the data, so each
is fixed here first:

- Number of questions per cell, and whether they are the full set or the five
  hardest.
- Which models, and how many runs per cell.
- Judging: single judge, ensemble, or the published rubric applied by hand.
- What counts as a failed run, and how one is retried.

## Analysis

Stated before the runs: the comparison is the difference-in-differences above.
No subgroup analysis is reported unless it appears in this section first.
~~~

- [ ] **Step 8: Verify no result is claimed for this study**

```bash
grep -rniE "we (found|show|demonstrate)|our results|the study found" . --include="*.md" || echo "clean: no unearned findings"
grep -c "epistemic-adequacy-probe" README.md
```

Expected: `clean`, and at least one citation of the source repository - the
prior rates must never appear unattributed.

- [ ] **Step 9: Commit, push, set topics**

```bash
git add -A
git commit -m "chore: scope the epistemic adequacy under pressure probe"
git push -u origin main
gh repo edit systems-researcher/epistemic-adequacy-under-pressure-probe \
  --add-topic ai-safety,confabulation,epistemic-adequacy,llm-evaluation,mbse,sysml-v2,systems-engineering
```

- [ ] **Step 10: Flip the owner, regenerate, verify, commit**

```bash
cd /c/Users/gower/OneDrive/Documents/GitHub/research-programme
python - <<'EOF'
import re
from pathlib import Path
p = Path("repos.yml")
s = p.read_text(encoding="utf-8")
s = re.sub(r"(- key: epistemic-adequacy-under-pressure-probe\n    owner: )local",
           r"\1systems-researcher", s, count=1)
p.write_text(s, encoding="utf-8")
EOF
python -m scripts.build --check
python -m scripts.refresh
python -m scripts.build
python -m pytest -q
npm --prefix app run build
python tests/check_external_links.py
git add -A
git commit -m "feat(data): publish epistemic-adequacy-under-pressure-probe as a real repository"
git push origin main
```

Expected: sixteen entries pass, and the study's badges show `private` and a
last-commit date.

---

### Task 3: Bootstrap `governed-interaction-cost-probe`

The practitioner-viability study. Its README must be explicit that it is
blocked: a repository that looks ready but cannot start is worse than one that
says why.

**Files:**
- Create (in the new repository): `README.md`, `LICENSE.md`, `LICENSE-MIT`, `CITATION.cff`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.gitignore`, `PROTOCOL.md`
- Modify: `repos.yml` - the `governed-interaction-cost-probe` entry, `owner` field only
- Regenerate: `data/map.json`, `README.md`

**Interfaces:**
- Consumes: the scoped entry in `repos.yml`; the harness from `epistemic-adequacy-testing-toolkit`; a running Arch-A, which does not exist yet.
- Produces: a repository at `https://github.com/systems-researcher/governed-interaction-cost-probe`, owned and queried.

- [ ] **Step 1: Read the scoped entry**

```bash
cd /c/Users/gower/OneDrive/Documents/GitHub/research-programme
python -c "
import yaml
d = yaml.safe_load(open('repos.yml', encoding='utf-8'))
e = [x for x in d['repos'] if x['key'] == 'governed-interaction-cost-probe'][0]
for f in ('objective', 'question', 'method', 'depends_on'):
    print(f.upper(), ':', ' '.join(str(e[f]).split()))
    print()
"
```

- [ ] **Step 2: Create the repository, private**

```bash
gh repo create systems-researcher/governed-interaction-cost-probe \
  --private \
  --description "What does an engineer pay - in latency, tokens, money, and failure modes - for interacting with a governed record rather than an ungoverned one?" \
  --clone
cd governed-interaction-cost-probe
```

- [ ] **Step 3: Copy licences and community files, and write `.gitignore`**

```bash
PROG=/c/Users/gower/OneDrive/Documents/GitHub/research-programme
cp "$PROG/LICENSE.md" "$PROG/LICENSE-MIT" .
gh api repos/systems-researcher/epistemic-adequacy-spec/contents/CONTRIBUTING.md --jq '.content' | base64 -d > CONTRIBUTING.md
gh api repos/systems-researcher/epistemic-adequacy-spec/contents/SECURITY.md --jq '.content' | base64 -d > SECURITY.md
gh api repos/systems-researcher/epistemic-adequacy-spec/contents/CODE_OF_CONDUCT.md --jq '.content' | base64 -d > CODE_OF_CONDUCT.md
printf '%s\n' '__pycache__/' '*.pyc' '.pytest_cache/' '.ruff_cache/' '.venv/' '*.tmp' 'runs/' '.env' > .gitignore
```

Strip the third-party section from `LICENSE.md` and correct `CONTRIBUTING.md`,
as in Task 1.

- [ ] **Step 4: Write `CITATION.cff`**

```yaml
cff-version: 1.2.0
message: "If you use this study, cite it as below."
title: "Governed Interaction Cost - the practitioner cost of governed AI-model interaction"
abstract: >
  Measures what an engineer pays for interacting with a governed engineering
  record rather than an ungoverned one: latency, token consumption, monetary
  cost, retrieval depth, and the failure modes that appear under load.
authors:
  - given-names: "Jason D."
    family-names: "Gower"
    orcid: "https://orcid.org/0009-0001-5945-6294"
    affiliation: "Loughborough University, Loughborough, United Kingdom"
  - given-names: "Michael J. de C."
    family-names: "Henshaw"
    orcid: "https://orcid.org/0000-0003-0511-179X"
    affiliation: "Loughborough University, Loughborough, United Kingdom"
  - given-names: "Siyuan"
    family-names: "Ji"
    orcid: "https://orcid.org/0000-0001-6139-3539"
    affiliation: "Loughborough University, Loughborough, United Kingdom"
license: CC-BY-4.0
repository-code: "https://github.com/systems-researcher/governed-interaction-cost-probe"
```

- [ ] **Step 5: Write `README.md`, stating the blocker plainly**

~~~markdown
<!--
Copyright (c) 2026 Jason D. Gower, Michael J. de C. Henshaw, Siyuan Ji
SPDX-License-Identifier: CC-BY-4.0
-->

# Governed Interaction Cost

**What does governance cost the engineer who has to use it?**

![status](https://img.shields.io/badge/status-blocked-red)
![blocked%20on](https://img.shields.io/badge/blocked%20on-Arch--A-lightgrey)
![licence](https://img.shields.io/badge/docs-CC--BY--4.0-green)
![licence](https://img.shields.io/badge/code-MIT-green)

---

## The question

What does an engineer pay - in latency, token consumption, monetary cost, and
additional failure modes - for interacting with a governed record rather than
an ungoverned one, and at what pattern of usage does that cost stop being worth
paying?

## Why this repository exists

The programme measures whether governance works. It does not yet measure what
governance costs, and that is the first objection a practitioner raises: a
governed record that triples latency or token spend will not be adopted
whatever it does for groundedness.

Scoped as viability rather than cost alone. Money is one column; latency,
retrieval depth, and the failure modes that only appear under load are the
others.

## Blocked

This study cannot produce a number until at least one architecture candidate
runs. It depends on
[`SysML-v2-API-Services-Arch-A`](https://github.com/systems-researcher/SysML-v2-API-Services-Arch-A),
whose admissibility gate checks currently raise `NotImplementedError`.

The protocol is written now so that the instrumentation is designed before the
architecture is built, rather than bolted on afterwards when the measurement
points are already fixed.

## Status

Blocked, by design. Part of a doctoral research programme; see the
[programme map](https://systems-researcher.github.io/research-programme/).

## Licence

Prose and data CC-BY-4.0; code MIT. See [LICENSE.md](LICENSE.md).
~~~

- [ ] **Step 6: Write `PROTOCOL.md`**

~~~markdown
<!--
Copyright (c) 2026 Jason D. Gower, Michael J. de C. Henshaw, Siyuan Ji
SPDX-License-Identifier: CC-BY-4.0
-->

# Protocol

**Version 0.0.0 - scoping. Written before the architecture it measures, deliberately.**

## Comparison

The same question set, run against a governed and an ungoverned substrate
through the harness in `epistemic-adequacy-testing-toolkit`. The question set is
held constant; the substrate is what varies.

## Instrumented per request

| Measure | Unit | Why |
|---|---|---|
| Wall-clock latency | ms | What the engineer waits |
| Prompt tokens | count | The governed path sends more context |
| Completion tokens | count | Governance may lengthen or shorten answers |
| Retrieval depth | count | How many record traversals an answer needed |
| Cost | currency at published rates | The number a budget holder reads |
| Outcome | ok / refused / error / timeout | Refusal is a governed-path outcome, not a failure |

## Reporting

**As a distribution, not a mean.** A governed path with an acceptable median
and an unusable tail is unusable; a mean hides that. Report median, 90th and
99th percentile per measure.

**Saturation point.** The concurrency or request rate at which the governed
path degrades relative to the ungoverned one, stated as a number rather than a
claim that it scales.

## To settle before the first run

- The question set, and whether it is the toolkit's or a new one.
- Published rates used for the cost column, and the date they were read - rates
  change, and a cost figure without a date is unreadable later.
- Concurrency levels tested.
- How a refusal is counted: it is a correct governed outcome, and counting it as
  a failure would make governance look worse than it is.

## Blocked on

Arch-A running. Until then this protocol is a design, and no measurement in it
has been taken.
~~~

- [ ] **Step 7: Verify nothing claims a measurement**

```bash
grep -rniE "we measured|our results|median|% (slower|faster)" . --include="*.md" | grep -v "Report median" || echo "clean: no unearned measurements"
```

Expected: `clean`. The one permitted use of "median" is the reporting
instruction in `PROTOCOL.md`, which describes what will be reported rather than
reporting it.

- [ ] **Step 8: Commit, push, set topics**

```bash
git add -A
git commit -m "chore: scope the governed interaction cost probe

Blocked on Arch-A running, and the README says so. The protocol is written now
so instrumentation is designed before the architecture rather than bolted on
once the measurement points are fixed."
git push -u origin main
gh repo edit systems-researcher/governed-interaction-cost-probe \
  --add-topic ai-governance,benchmarking,cost-analysis,mbse,performance,sysml-v2,systems-engineering
```

- [ ] **Step 9: Flip the owner, regenerate, verify, commit**

```bash
cd /c/Users/gower/OneDrive/Documents/GitHub/research-programme
python - <<'EOF'
import re
from pathlib import Path
p = Path("repos.yml")
s = p.read_text(encoding="utf-8")
s = re.sub(r"(- key: governed-interaction-cost-probe\n    owner: )local",
           r"\1systems-researcher", s, count=1)
p.write_text(s, encoding="utf-8")
EOF
python -m scripts.build --check
python -m scripts.refresh
python -m scripts.build
python -m pytest -q
python tests/mutate_check.py
npm --prefix app run build
python tests/check_external_links.py
git add -A
git commit -m "feat(data): publish governed-interaction-cost-probe as a real repository"
git push origin main
```

---

### Task 4: Verify the programme map reflects all three

**Files:**
- Verify only: `data/map.json`, the deployed site

- [ ] **Step 1: Confirm no study is still badged "not yet published"**

```bash
cd /c/Users/gower/OneDrive/Documents/GitHub/research-programme
python -c "
import json
d = json.load(open('data/map.json', encoding='utf-8'))
unpublished = [e['key'] for s in d['strands'] for e in s['entries']
               if 'not yet published' in (e.get('badges') or [])]
print('still local:', unpublished or 'none')
"
```

Expected: `none`. Every study now has a repository.

- [ ] **Step 2: Confirm the graph still resolves**

```bash
python -c "
import json
d = json.load(open('data/map.json', encoding='utf-8'))
g = d['graph']
pos = {n['key']: n['x'] for n in g['nodes']}
print('nodes:', len(g['nodes']), 'edges:', len(g['edges']), 'columns:', g['columns'])
print('all forward:', all(pos[e['from']] < pos[e['to']] for e in g['edges']))
"
```

Expected: fifteen nodes, fourteen edges, all forward. A non-forward edge means a
dependency added during bootstrapping created a cycle; rule 9 would have caught
it at `--check`, so this is a second check on the same property.

- [ ] **Step 3: Confirm the deployed site matches**

```bash
gh run list --repo systems-researcher/research-programme --workflow pages.yml --limit 1 \
  --json headSha,status,conclusion --jq '.[0]'
curl -s -o /dev/null -w "site: HTTP %{http_code}\n" -L \
  https://systems-researcher.github.io/research-programme/
```

Expected: the most recent run succeeded on the current `main` SHA, and the site
returns 200.

---

## Notes for the executor

**What this plan does not do.** It creates three repositories with a stated
question and an honest empty structure. It does not write admissibility clauses,
build the two-by-two harness, or instrument the cost probe. Each of those is a
research execution needing its own plan, and attempting one here would produce
placeholder content - which is what the verification steps in Tasks 1, 2 and 3
exist to prevent.

**Why the grep checks matter.** This programme has already shipped a fabricated
paper title behind a Copy BibTeX button, corrected in commit `ad21973`. It
happened because plausible-sounding text was written from memory rather than
transcribed from a source. Copying a README between repositories is the same
failure waiting to happen: the borrowed file carries the source repository's
numbers, and they are false in the new one.

**If a scoped entry turns out to be wrong.** Change `repos.yml` first, run
`--check`, regenerate, then write the README from the corrected entry. The entry
is the specification; the README restates it. Never let the two disagree.

**Order matters.** Task 1 first: it establishes the file pattern the other two
copy, and it is the study three architecture candidates already depend on.
Tasks 2 and 3 are independent of each other.
