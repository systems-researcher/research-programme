# Research Programme Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `systems-researcher/research-programme`, a private repository whose `repos.yml` describes thirteen research repositories and generates both a README table and a public one-page site showing what each repository is for and how they link.

**Architecture:** One hand-authored YAML file is the source of truth. `scripts/build.py` validates it against nine rules, then renders `site/index.html` (cards plus a Mermaid dependency graph) and a marked block inside `README.md`. `scripts/refresh.py` pulls live GitHub fields into `data/live.json`, which is generated and never hand-edited, so a refresh can never clobber authored prose. Vercel serves `site/` from the private repository at a public URL.

**Tech Stack:** Python 3.13+, PyYAML, pytest, `gh` CLI (for refresh only), Mermaid 11 from CDN (the page's only external asset), Vercel static hosting.

**Design spec:** [`docs/superpowers/specs/2026-08-19-research-programme-map-design.md`](../specs/2026-08-19-research-programme-map-design.md). Section references below (§4, §5) point at it.

---

## File structure

| File | Responsibility |
|---|---|
| `repos.yml` | Source of truth: `programme`, `strands`, `stages`, `repos`. Hand-authored, never generated |
| `data/live.json` | Generated GitHub fields: `generated_at` plus a `repos` map. Committed, never hand-edited |
| `scripts/mapdata.py` | Load `repos.yml` and `data/live.json`; the nine validation rules; graph inversion. No rendering, no I/O side effects beyond reading |
| `scripts/render.py` | Pure rendering: data in, HTML and Markdown strings out. No file writes, no validation |
| `scripts/build.py` | CLI. `--check` validates and exits; no flag validates then writes both outputs atomically |
| `scripts/refresh.py` | CLI. Calls `gh`, writes `data/live.json`. The only script that touches the network |
| `site/index.html` | Generated page. Committed so Vercel needs no build step |
| `README.md` | Narrative, with the repo table regenerated between markers |
| `tests/test_mapdata.py` | The nine rules, plus loading and inversion |
| `tests/test_render.py` | Structural assertions on rendered HTML and the README block |
| `tests/test_refresh.py` | Refresh logic against a fake `gh` runner — never hits the network |

Validation, rendering, and I/O are three separate modules so each is testable without the others: rules can be tested on dicts, rendering on fixtures, and refresh on a fake subprocess runner.

---

## Task 1: Repository skeleton

**Files:**
- Create: `.gitignore`, `requirements.txt`, `LICENSE.md`, `LICENSE-MIT`, `README.md`, `scripts/__init__.py`, `tests/__init__.py`

- [ ] **Step 1: Create the directory skeleton and Python dependency list**

```bash
cd c:/Users/gower/OneDrive/Documents/GitHub/research-programme
mkdir -p scripts tests data site
touch scripts/__init__.py tests/__init__.py
```

`requirements.txt`:

```
PyYAML>=6.0
pytest>=8.0
```

- [ ] **Step 2: Write `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.planning/
*.tmp
```

- [ ] **Step 3: Write the licence files**

`LICENSE.md`:

```markdown
# Licence

Copyright (c) 2026 Jason D. Gower.

**Prose and data** — every Markdown file, `repos.yml`, and the rendered site
content — are licensed under Creative Commons Attribution 4.0 International
(CC-BY-4.0). Full text: https://creativecommons.org/licenses/by/4.0/legalcode

**Code** — everything under `scripts/` and `tests/` — is licensed under the MIT
Licence, reproduced in `LICENSE-MIT`.

Each file carries an SPDX identifier stating which of the two applies.
```

`LICENSE-MIT`: the standard MIT text with `Copyright (c) 2026 Jason D. Gower`.

- [ ] **Step 4: Install dependencies and confirm the toolchain**

Run: `python -m pip install -r requirements.txt`
Expected: PyYAML and pytest install without error.

Run: `python -c "import yaml, pytest; print(yaml.__version__)"`
Expected: a version string, no traceback.

- [ ] **Step 5: Commit**

```bash
git add .gitignore requirements.txt LICENSE.md LICENSE-MIT scripts/__init__.py tests/__init__.py
git commit -m "chore: repository skeleton, licences, dependencies"
```

---

## Task 2: Load the data model

**Files:**
- Create: `scripts/mapdata.py`
- Test: `tests/test_mapdata.py`

- [ ] **Step 1: Write the failing test**

`tests/test_mapdata.py`:

```python
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Tests for loading, validating, and inverting the map data."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from scripts import mapdata

MINIMAL = textwrap.dedent(
    """
    programme:
      title: "T"
      question: "Q"
      move: "M"
    strands:
      adequacy:
        title: "A"
        subtitle: "a"
    stages:
      define: "d"
    repos:
      - key: alpha
        owner: systems-researcher
        strand: adequacy
        stage: define
        objective: "o"
        question: "q"
        method: "m"
        status: design
    """
)


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "repos.yml"
    path.write_text(text, encoding="utf-8")
    return path


def test_load_returns_blocks_and_indexes_repos_by_key(tmp_path: Path) -> None:
    data = mapdata.load(write(tmp_path, MINIMAL))

    assert data.programme["title"] == "T"
    assert data.stages["define"] == "d"
    assert list(data.by_key) == ["alpha"]
    assert data.by_key["alpha"]["render"] == "card"


def test_load_raises_with_line_and_column_on_syntax_error(tmp_path: Path) -> None:
    with pytest.raises(mapdata.MapError) as excinfo:
        mapdata.load(write(tmp_path, "programme:\n  title: 'unterminated\n"))

    assert "line" in str(excinfo.value)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_mapdata.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.mapdata'`

- [ ] **Step 3: Write the minimal implementation**

`scripts/mapdata.py`:

```python
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Load, validate, and invert the research-programme map data.

This module knows nothing about rendering. It turns repos.yml into a MapData
object, checks it against the nine rules in the design spec (§5), and derives
the reverse edge direction ("what feeds this") from the authored depends_on.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

STRANDS = ("adequacy", "method-validation", "assembly")
STAGES = ("define", "measure", "evidence", "architecture", "assembly")
STATUSES = (
    "design",
    "built-runs-pending",
    "released",
    "results",
    "published",
    "not-applicable",
)
RENDERS = ("card", "node-only")
REQUIRED = ("key", "owner", "strand", "stage", "objective", "question", "method", "status")
RESULT_STATUSES = ("results", "published")
TERMINUS = "Thesis-Work-Area"


class MapError(Exception):
    """repos.yml could not be read at all — syntax error or missing file."""


@dataclass
class MapData:
    programme: dict[str, Any]
    strands: dict[str, Any]
    stages: dict[str, Any]
    repos: list[dict[str, Any]]
    by_key: dict[str, dict[str, Any]] = field(default_factory=dict)


def load(path: Path) -> MapData:
    """Parse repos.yml. Raises MapError with line and column on a syntax error."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MapError(f"{path} does not exist") from exc
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        raise MapError(f"{path} is not valid YAML{where}: {exc}") from exc

    if not isinstance(raw, dict):
        raise MapError(f"{path} must be a mapping with programme, strands, stages, repos")

    repos = raw.get("repos") or []
    for entry in repos:
        entry.setdefault("render", "card")
        entry.setdefault("depends_on", [])

    data = MapData(
        programme=raw.get("programme") or {},
        strands=raw.get("strands") or {},
        stages=raw.get("stages") or {},
        repos=repos,
    )
    data.by_key = {entry["key"]: entry for entry in repos if "key" in entry}
    return data
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest tests/test_mapdata.py -v`
Expected: PASS, 2 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/mapdata.py tests/test_mapdata.py
git commit -m "feat(mapdata): load repos.yml with defaults and readable syntax errors"
```

---

## Task 3: Validation rules 1 to 5

**Files:**
- Modify: `scripts/mapdata.py`
- Test: `tests/test_mapdata.py`

Rules from the design spec §5. Each rule returns a human-readable string; `check()` returns a list, empty when the data is valid.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_mapdata.py`:

```python
def base() -> dict:
    """A minimal valid data structure, as dicts, for rule-level tests."""
    return {
        "programme": {"title": "T", "question": "Q", "move": "M"},
        "strands": {"adequacy": {"title": "A", "subtitle": "a"}},
        "stages": {"define": "d"},
        "repos": [
            {
                "key": "alpha",
                "owner": "systems-researcher",
                "strand": "adequacy",
                "stage": "define",
                "render": "card",
                "objective": "o",
                "question": "q",
                "method": "m",
                "status": "design",
                "depends_on": [],
            }
        ],
    }


def check(raw: dict) -> list[str]:
    data = mapdata.MapData(
        programme=raw["programme"],
        strands=raw["strands"],
        stages=raw["stages"],
        repos=raw["repos"],
    )
    data.by_key = {entry["key"]: entry for entry in raw["repos"] if "key" in entry}
    return mapdata.check(data)


def test_valid_data_produces_no_errors() -> None:
    assert check(base()) == []


def test_rule_1_depends_on_names_a_key_that_does_not_exist() -> None:
    raw = base()
    raw["repos"][0]["depends_on"] = ["ghost"]

    errors = check(raw)

    assert any("alpha" in e and "ghost" in e for e in errors)


def test_rule_2_stage_outside_the_permitted_set() -> None:
    raw = base()
    raw["repos"][0]["stage"] = "prototype"

    assert any("stage" in e and "prototype" in e for e in errors_of(raw))


def test_rule_3_missing_required_field_including_on_node_only() -> None:
    raw = base()
    raw["repos"][0]["render"] = "node-only"
    del raw["repos"][0]["method"]

    assert any("method" in e for e in errors_of(raw))


def test_rule_4_terminus_may_not_be_depended_on() -> None:
    raw = base()
    raw["repos"].append(
        {
            "key": mapdata.TERMINUS,
            "owner": "systems-researcher",
            "strand": "adequacy",
            "stage": "define",
            "render": "node-only",
            "objective": "o",
            "question": "q",
            "method": "m",
            "status": "not-applicable",
            "depends_on": [],
        }
    )
    raw["repos"][0]["depends_on"] = [mapdata.TERMINUS]

    assert any(mapdata.TERMINUS in e and "alpha" in e for e in errors_of(raw))


def test_rule_5_headline_requires_a_result_status() -> None:
    raw = base()
    raw["repos"][0]["headline"] = {"text": "42%", "source": "somewhere v1"}

    assert any("headline" in e and "design" in e for e in errors_of(raw))


def test_rule_5_not_applicable_only_on_node_only_entries() -> None:
    raw = base()
    raw["repos"][0]["status"] = "not-applicable"

    assert any("not-applicable" in e for e in errors_of(raw))


def errors_of(raw: dict) -> list[str]:
    return check(raw)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_mapdata.py -v`
Expected: FAIL — `AttributeError: module 'scripts.mapdata' has no attribute 'check'`

- [ ] **Step 3: Write the minimal implementation**

Append to `scripts/mapdata.py`:

```python
def check(data: MapData) -> list[str]:
    """Return every rule violation as a readable string. Empty means valid."""
    errors: list[str] = []
    errors += _rule_3_required_fields(data)
    errors += _rule_1_unknown_dependency(data)
    errors += _rule_2_enumerated_values(data)
    errors += _rule_4_terminus_supplies_nothing(data)
    errors += _rule_5_headline_status(data)
    return errors


def _rule_3_required_fields(data: MapData) -> list[str]:
    errors = []
    for index, entry in enumerate(data.repos):
        name = entry.get("key") or f"entry #{index + 1}"
        for field_name in REQUIRED:
            if not entry.get(field_name):
                errors.append(f"{name}: missing required field '{field_name}'")
    return errors


def _rule_1_unknown_dependency(data: MapData) -> list[str]:
    errors = []
    for entry in data.repos:
        for dependency in entry.get("depends_on", []):
            if dependency not in data.by_key:
                errors.append(
                    f"{entry.get('key')}: depends_on names '{dependency}', which is not a key in repos.yml"
                )
    return errors


def _rule_2_enumerated_values(data: MapData) -> list[str]:
    errors = []
    for entry in data.repos:
        name = entry.get("key")
        for field_name, allowed in (
            ("strand", STRANDS),
            ("stage", STAGES),
            ("status", STATUSES),
            ("render", RENDERS),
        ):
            value = entry.get(field_name)
            if value is not None and value not in allowed:
                errors.append(
                    f"{name}: {field_name} is '{value}', not one of {', '.join(allowed)}"
                )
    return errors


def _rule_4_terminus_supplies_nothing(data: MapData) -> list[str]:
    return [
        f"{entry.get('key')}: depends_on names {TERMINUS}; the thesis consumes, it never supplies"
        for entry in data.repos
        if TERMINUS in entry.get("depends_on", [])
    ]


def _rule_5_headline_status(data: MapData) -> list[str]:
    errors = []
    for entry in data.repos:
        name = entry.get("key")
        status = entry.get("status")
        if entry.get("headline") and status not in RESULT_STATUSES:
            errors.append(
                f"{name}: has a headline but status is '{status}'; "
                f"only {' or '.join(RESULT_STATUSES)} may carry a measured result"
            )
        if status == "not-applicable" and entry.get("render") != "node-only":
            errors.append(
                f"{name}: status 'not-applicable' is permitted only on render: node-only entries"
            )
    return errors
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_mapdata.py -v`
Expected: PASS, 9 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/mapdata.py tests/test_mapdata.py
git commit -m "feat(mapdata): validation rules 1-5"
```

---

## Task 4: Validation rules 6 to 9, and graph inversion

**Files:**
- Modify: `scripts/mapdata.py`
- Test: `tests/test_mapdata.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_mapdata.py`:

```python
def test_rule_6_headline_needs_both_text_and_source() -> None:
    raw = base()
    raw["repos"][0]["status"] = "published"
    raw["repos"][0]["headline"] = {"text": "42% of answers"}

    assert any("source" in e for e in errors_of(raw))


def test_rule_7_duplicate_key() -> None:
    raw = base()
    raw["repos"].append(dict(raw["repos"][0]))

    assert any("duplicate" in e.lower() and "alpha" in e for e in errors_of(raw))


def test_rule_7_owner_must_look_like_an_account_name() -> None:
    raw = base()
    raw["repos"][0]["owner"] = "not a name!"

    assert any("owner" in e for e in errors_of(raw))


def test_rule_8_stage_used_with_no_explanation_line() -> None:
    raw = base()
    raw["repos"][0]["stage"] = "measure"

    assert any("stages" in e and "measure" in e for e in errors_of(raw))


def test_rule_8_programme_block_is_required() -> None:
    raw = base()
    del raw["programme"]["move"]

    assert any("programme.move" in e for e in errors_of(raw))


def test_rule_9_self_reference_is_a_cycle() -> None:
    raw = base()
    raw["repos"][0]["depends_on"] = ["alpha"]

    assert any("cycle" in e.lower() and "alpha" in e for e in errors_of(raw))


def test_rule_9_reports_the_full_cycle_path() -> None:
    raw = base()
    raw["repos"][0]["depends_on"] = ["beta"]
    raw["repos"].append(
        {
            "key": "beta",
            "owner": "systems-researcher",
            "strand": "adequacy",
            "stage": "define",
            "render": "card",
            "objective": "o",
            "question": "q",
            "method": "m",
            "status": "design",
            "depends_on": ["alpha"],
        }
    )

    message = " ".join(errors_of(raw))

    assert "alpha" in message and "beta" in message and "cycle" in message.lower()


def test_feeds_is_the_inverse_of_depends_on() -> None:
    raw = base()
    raw["repos"].append(
        {
            "key": "beta",
            "owner": "systems-researcher",
            "strand": "adequacy",
            "stage": "define",
            "render": "card",
            "objective": "o",
            "question": "q",
            "method": "m",
            "status": "design",
            "depends_on": ["alpha"],
        }
    )
    data = mapdata.MapData(
        programme=raw["programme"],
        strands=raw["strands"],
        stages=raw["stages"],
        repos=raw["repos"],
    )
    data.by_key = {e["key"]: e for e in raw["repos"]}

    feeds = mapdata.feeds(data)

    assert feeds["alpha"] == ["beta"]
    assert feeds["beta"] == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_mapdata.py -v`
Expected: FAIL — the new rule tests fail, and `AttributeError: module 'scripts.mapdata' has no attribute 'feeds'`

- [ ] **Step 3: Write the minimal implementation**

In `scripts/mapdata.py`, add `re` to the imports, extend `check()`, and append the new functions:

```python
import re

OWNER_RE = re.compile(r"^[A-Za-z0-9-]+$")
```

Extend `check()` to call the new rules:

```python
def check(data: MapData) -> list[str]:
    """Return every rule violation as a readable string. Empty means valid."""
    errors: list[str] = []
    errors += _rule_3_required_fields(data)
    errors += _rule_1_unknown_dependency(data)
    errors += _rule_2_enumerated_values(data)
    errors += _rule_4_terminus_supplies_nothing(data)
    errors += _rule_5_headline_status(data)
    errors += _rule_6_headline_attribution(data)
    errors += _rule_7_owner_and_duplicates(data)
    errors += _rule_8_blocks_cover_every_entry(data)
    errors += _rule_9_acyclic(data)
    return errors
```

Append:

```python
def _rule_6_headline_attribution(data: MapData) -> list[str]:
    errors = []
    for entry in data.repos:
        headline = entry.get("headline")
        if not headline:
            continue
        if not isinstance(headline, dict):
            errors.append(f"{entry.get('key')}: headline must be a mapping of text and source")
            continue
        for part in ("text", "source"):
            if not headline.get(part):
                errors.append(
                    f"{entry.get('key')}: headline is missing '{part}'; "
                    "every published number must name the artefact it came from"
                )
    return errors


def _rule_7_owner_and_duplicates(data: MapData) -> list[str]:
    errors = []
    seen: set[str] = set()
    for entry in data.repos:
        key = entry.get("key")
        if key in seen:
            errors.append(f"duplicate key '{key}'")
        seen.add(key)

        owner = entry.get("owner")
        if owner and not OWNER_RE.match(str(owner)):
            errors.append(
                f"{key}: owner '{owner}' is not 'local' or a GitHub account name matching [A-Za-z0-9-]+"
            )
    return errors


def _rule_8_blocks_cover_every_entry(data: MapData) -> list[str]:
    errors = []
    for required_field in ("title", "question", "move"):
        if not data.programme.get(required_field):
            errors.append(f"programme.{required_field} is missing; the page header needs it")

    for entry in data.repos:
        key = entry.get("key")
        stage = entry.get("stage")
        strand = entry.get("strand")
        if stage and stage not in data.stages:
            errors.append(
                f"{key}: stage '{stage}' has no line in the stages block, "
                "so its section would render with no explanation"
            )
        if strand and strand not in data.strands:
            errors.append(
                f"{key}: strand '{strand}' has no entry in the strands block, "
                "so its section would render with no heading"
            )
    return errors


def _rule_9_acyclic(data: MapData) -> list[str]:
    """Depth-first search reporting the full path of the first cycle found per root."""
    errors = []
    visiting: list[str] = []
    done: set[str] = set()

    def walk(key: str) -> None:
        if key in done:
            return
        if key in visiting:
            cycle = visiting[visiting.index(key):] + [key]
            errors.append("depends_on cycle: " + " -> ".join(cycle))
            return
        visiting.append(key)
        for dependency in data.by_key.get(key, {}).get("depends_on", []):
            if dependency in data.by_key:
                walk(dependency)
        visiting.pop()
        done.add(key)

    for entry in data.repos:
        walk(entry.get("key"))
    return errors


def feeds(data: MapData) -> dict[str, list[str]]:
    """Invert depends_on. feeds[a] lists every key that declares a dependency on a."""
    inverted: dict[str, list[str]] = {entry["key"]: [] for entry in data.repos}
    for entry in data.repos:
        for dependency in entry.get("depends_on", []):
            if dependency in inverted:
                inverted[dependency].append(entry["key"])
    return {key: sorted(value) for key, value in inverted.items()}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_mapdata.py -v`
Expected: PASS, 17 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/mapdata.py tests/test_mapdata.py
git commit -m "feat(mapdata): validation rules 6-9 and depends_on inversion"
```

---

## Task 5: Author `repos.yml`

**Files:**
- Create: `repos.yml`
- Create: `scripts/build.py`

This task fills the source of truth with the thirteen real entries and gives `--check` a command-line entry point so the data can be validated.

- [ ] **Step 1: Write `scripts/build.py` with the `--check` path only**

`scripts/build.py`:

```python
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Validate repos.yml and render the site and README block."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts import mapdata

ROOT = Path(__file__).resolve().parent.parent
REPOS_YML = ROOT / "repos.yml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate repos.yml and exit; write nothing",
    )
    args = parser.parse_args(argv)

    try:
        data = mapdata.load(REPOS_YML)
    except mapdata.MapError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    errors = mapdata.check(data)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(f"{len(errors)} problem(s) in {REPOS_YML.name}", file=sys.stderr)
        return 1

    if args.check:
        print(f"{REPOS_YML.name}: {len(data.repos)} entries, all nine rules pass")
        return 0

    print("nothing to render yet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Write `repos.yml`**

`repos.yml`:

```yaml
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: CC-BY-4.0
#
# The single hand-authored source of truth for the research programme map.
# data/live.json, site/index.html and the README table are all generated from
# this file. Never write a number here that you cannot trace to a file in the
# repository it describes.

programme:
  title: "Architecting Trustworthy AI Integration in MBSE"
  question: >
    AI assistants already read engineering models and answer questions from
    them. The answers are fluent, mostly true, and largely unauthorised by the
    model in front of them. This programme asks three things: what an
    engineering record must expose for an AI consumer to tell a grounded claim
    from an ungrounded one, whether exposing it changes what the AI actually
    says, and how a substrate can refuse an inadmissible write on its own
    behalf.
  move: >
    Throughout, an AI agent stands in as a consistent practitioner. That turns
    method and representation into manipulable experimental factors and makes
    replicated designs affordable that human-subject systems-engineering
    research could never run.

strands:
  adequacy:
    title: "Epistemic adequacy"
    subtitle: >
      Can a record tell an AI what it is authorised to say — and can a substrate
      refuse a write that it is not?
  method-validation:
    title: "Do classic SE methods survive an AI practitioner?"
    subtitle: >
      The same methodological move, turned on the methods systems engineering
      already relies on.
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

  # ---------------------------------------------------------------- define ---

  - key: epistemic-adequacy-spec
    owner: systems-researcher
    strand: adequacy
    stage: define
    status: released
    objective: >
      A conformance specification stating, in eighteen testable clauses, what an
      engineering record must expose so that an AI consumer can decide whether a
      claim the record holds is grounded.
    question: >
      What must a record expose for the groundedness of a claim — whether it is
      derived, at what standing, from what origin, with its premises reachable,
      and how it entered the record — to be decidable by query rather than by
      judgement?
    method: >
      Five criteria, EA1 to EA5, decomposed into eighteen MUST/SHOULD/MAY
      clauses, each carrying a Check line written against an abstract substrate
      and organised into three conformance profiles, with a non-normative SysML
      v2 binding and a machine-readable clause manifest validated against the
      prose in CI. EA1 to EA4 are labelled evidenced; all three EA5 clauses are
      labelled hypothesis.
    output: >
      v0.1.0, released 2026-08-18. The criteria originate in the MODELS 2026
      NIER paper, doi:10.1145/3822455.3838783, which resolves on publication.
    depends_on: [epistemic-adequacy-probe]

  - key: epistemic-adequacy-metamodel
    owner: local
    strand: adequacy
    stage: define
    status: design
    objective: >
      Owns the metadata model itself — a conceptual ontology, a logical data
      model, and a generated SysML v2 library, kept in sync — so that the
      specification's non-normative binding becomes something a tool can
      mechanically check.
    question: >
      Can the eighteen clauses be expressed as SysML v2 metadata that a tool
      actually checks on a real model, and what does the existing binding lack
      for that to be true?
    method: >
      One hand-edited schema generates both an OWL 2 plus SHACL ontology and the
      SysML v2 library, with reader, resolver, and extractor stages emitting the
      toolkit's canonical claim graph. Correctness is pinned by a bare-versus-
      annotated Apollo reference pair under a stated profile regression contract
      and an eighteen-row clause trace in CI. The repository exists because
      parse testing on 2026-08-19 showed off-the-shelf SysML v2 validation
      accepting a derivation whose upstream references nothing.
    depends_on: [epistemic-adequacy-spec, epistemic-adequacy-toolkit]

  # --------------------------------------------------------------- measure ---

  - key: epistemic-adequacy-toolkit
    owner: systems-researcher
    strand: adequacy
    stage: measure
    status: built-runs-pending
    objective: >
      The instrument: it scores a substrate against the eighteen clauses and
      joins that score to how an AI consumer then behaves, so that adequacy is
      the independent variable and consumer behaviour the dependent one.
    question: >
      Does this substrate satisfy the clauses, at which conformance profile, and
      does the measured adequacy change what an AI consumer says?
    method: >
      The static stage runs deterministically with no model calls, scoring a
      substrate against the clause manifest it pins by SHA-256. The behavioural
      runner that joins adequacy to consumer answers is specified and not yet
      built, so the join the instrument exists for is not yet demonstrable.
    output: "v0.1.0"
    depends_on: [epistemic-adequacy-spec]

  - key: sysml2-bench
    owner: systems-researcher
    strand: adequacy
    stage: measure
    status: built-runs-pending
    objective: >
      A public, versioned, contamination-resistant benchmark of how well
      language models read, reason over, critique, and write SysML v2 — the
      capability baseline every adequacy result has to be read against.
    question: >
      How competent are current models at SysML v2 itself, independent of any
      epistemic metadata, and how often do they confabulate on items that have
      no answer?
    method: >
      Four task families generated procedurally from a semantic intermediate
      representation with programmatic ground truth, plus two cross-cutting
      headline metrics, confabulation rate and format-failure rate. The
      generator and truth layer exist; the wild set that draws on the public
      Apollo 11 model is human-gated and still unpopulated, so the bench does
      not yet consume anything the probe produced.
    depends_on: []

  # ------------------------------------------------- evidence, read-side ---

  - key: epistemic-adequacy-probe
    owner: systems-researcher
    strand: adequacy
    stage: evidence
    status: published
    objective: >
      The first measured test of whether epistemic metadata, beyond structured
      model access alone, changes how an AI consumer answers derivation-style
      questions over an MBSE model.
    question: >
      Does an AI reading an MBSE model produce fewer unauthorised answers when
      the model exposes derivation, standing, and provenance?
    method: >
      Three language models over a verbatim excerpt of the public Airbus Apollo
      11 SysML v2 reconstruction, 120 judged answers across a governed and a
      pressed instruction, with and without a hand-authored EA1 to EA4 sidecar.
      Deliberately small: one thrust chain, one model family, a single run per
      cell.
    headline:
      text: >
        Under a governed instruction the bare model gave ungrounded answers on 6
        of 45 question-cells (13.3%); the sidecar cut that to 1 of 45 (2.2%).
        Under a deadline-style pressed instruction over the five hardest
        questions the bare model reached 9 of 15 (60%), and the strongest model
        was the most fluent confabulator — 4 of its 5 pressured answers
        ungrounded, every one historically plausible. The sidecar halved the
        pressed rate to 5 of 15 (33%) without eliminating it.
      source: >
        epistemic-adequacy-probe v0.2.0, RESULTS.md, "Headline rates". The
        repository also records a cross-family judge recheck of the pressed
        plus-sidecar cell; read RESULTS.md before quoting that cell alone.
    output: >
      doi:10.1145/3822455.3838783 (MODELS 2026 NIER); release v0.2.0,
      2026-08-17.
    depends_on: []

  - key: pressure-susceptibility-probe
    owner: systems-researcher
    strand: adequacy
    stage: evidence
    status: built-runs-pending
    objective: >
      Measures how susceptible an AI assistant is to producing unauthorised
      engineering answers when the work itself pushes on it: a deadline, a
      senior engineer's stated conclusion, a board that has already agreed, or a
      question with a false premise baked in.
    question: >
      How much does social and operational pressure raise the rate of ungrounded
      engineering answers, and which kinds of pressure do most of the damage?
    method: >
      Six scenarios drawn from design review, verification sign-off, and anomaly
      investigation, an influence-prompt library of seven levers, ensemble
      judging, and an analysis layer. Harness and scenario set are built; the
      runs have not been executed.
    depends_on: [epistemic-adequacy-probe]

  # -------------------------------------------- architecture, write-side ---

  - key: SysML-v2-API-Services-Arch-A
    owner: systems-researcher
    strand: adequacy
    stage: architecture
    status: design
    objective: >
      Candidate A: epistemic metadata carried inline on model elements through
      project-local SysML v2 metadata definitions, with an admissibility gate as
      the sole write path.
    question: >
      Can a conforming record be enforced inside the standard SysML v2 API
      service itself, with no second store to keep in step?
    method: >
      A research fork pinned to vanilla upstream, adding four metadata-def
      schemas and a Python admissibility gate in front of the API, evaluated by
      a three-arm harness. The design contract is complete; the gate checks
      still raise NotImplementedError.
    depends_on: [epistemic-adequacy-spec]

  - key: sysml-v2-metadata-graph-Arch-B
    owner: systems-researcher
    strand: adequacy
    stage: architecture
    status: design
    objective: >
      Candidate B: the SysML v2 model stays completely untouched and the
      epistemic metadata lives beside it in a Neo4j graph keyed by
      programme-level stable identifiers.
    question: >
      Does holding the metadata out of the model buy full history and provenance
      without losing the ability to refuse a write?
    method: >
      A Python governance service is the sole write path to both stores, running
      a graph-write gate and a promotion gate with staleness blocking before any
      guarded commit upstream. The design contract is complete; implementation
      has not started. Comparing A against B requires Candidate A deployed and
      runnable alongside it.
    depends_on: [epistemic-adequacy-spec, SysML-v2-API-Services-Arch-A]

  - key: sysml-v2-governed-substrate-Arch-C
    owner: systems-researcher
    strand: adequacy
    stage: architecture
    status: design
    objective: >
      Candidate C: one ArcadeDB engine holds model topology, governance metadata
      and provenance, and retrieval embeddings, with SysML treated as a
      projection over the store rather than the store itself.
    question: >
      If the substrate is governed natively, can the authoritative record and
      the AI-authored companion be two namespaces of one engine, with promotion
      between them in a single transaction?
    method: >
      A governance API is the sole external write path: it evaluates the
      admissibility conditions before commit, confines signed AI writes to the
      companion namespace, and promotes accepted content in one transaction
      carrying the second-party review record, with append-only audit history
      held in-store. The design contract is complete; implementation has not
      started.
    depends_on: [epistemic-adequacy-spec]

  # ------------------------------------------- method validation strand ---

  - key: model-vs-document-defect-probe
    owner: systems-researcher
    strand: method-validation
    stage: evidence
    status: design
    objective: >
      Measures MBSE's flagship claim head-on: does a single connected system
      model let a reviewer catch more defects than an information-equivalent set
      of documents?
    question: >
      Which substrate and tooling combination lets an AI agent best manage a
      model — query it, edit it, trace through it, and find its defects?
    method: >
      A consistent-practitioner design in which an AI agent stands in as the
      reviewer, so representation is the only factor that varies and reviewer
      skill is held constant, scored on a four-task battery across eight
      substrate variants in three families: document, model, and database.
    depends_on: [pressure-susceptibility-probe]

  - key: ahp-framing-fragility-probe
    owner: local
    strand: method-validation
    stage: evidence
    status: design
    objective: >
      Tests whether a structured trade study gives a stable answer, or whether
      the winner silently depends on things that should not matter: the order
      the criteria were listed in, how they were worded, or the presence of
      irrelevant decoy options.
    question: >
      How often does a trade study's chosen winner flip under perturbations that
      carry no decision-relevant information?
    method: >
      The same decision run many times over with an AI agent standing in as the
      analyst, varying only cosmetic factors, reported as a flip-rate. The test
      design is written; no harness is built.
    depends_on: [pressure-susceptibility-probe]

  - key: dsm-sequencing-probe
    owner: local
    strand: method-validation
    stage: evidence
    status: design
    objective: >
      Tests whether the Design Structure Matrix actually produces the best task
      order, measured against a mathematically optimal answer a computer can
      calculate exactly.
    question: >
      How far from optimal is a DSM-derived task ordering, and when it is wrong,
      did the method fail or did the analyst build the wrong matrix?
    method: >
      The agent's ordering is scored against the provably minimal-feedback
      ordering produced by a known graph algorithm, split by whether the agent
      also had to elicit the matrix or was handed it clean, across several
      models. The test design is written; no harness is built.
    depends_on: []

  # -------------------------------------------------------------- assembly ---

  - key: Thesis-Work-Area
    owner: systems-researcher
    strand: assembly
    stage: assembly
    render: node-only
    status: not-applicable
    objective: >
      Where the programme's findings are written up as the doctoral thesis.
    question: >
      Not applicable: this is the destination, not a study.
    method: >
      Not applicable.
    depends_on: [epistemic-adequacy-spec, epistemic-adequacy-metamodel,
                 epistemic-adequacy-toolkit, sysml2-bench,
                 epistemic-adequacy-probe, pressure-susceptibility-probe,
                 SysML-v2-API-Services-Arch-A, sysml-v2-metadata-graph-Arch-B,
                 sysml-v2-governed-substrate-Arch-C,
                 model-vs-document-defect-probe, ahp-framing-fragility-probe,
                 dsm-sequencing-probe]
```

**What `depends_on` means here.** It is a statement about what a repository
consumes *now and going forward*, not a claim about commit order. Most of these
repositories predate the specification, so a git-history reading of the edges
would be wrong. Two edges are worth knowing about:

- `epistemic-adequacy-spec` depends on `epistemic-adequacy-probe`, which looks
  backwards for a define-stage repository. It is deliberate: the spec quotes the
  probe's measured rates as the evidence base for EA1 to EA4, and the probe
  cites no sibling repository at all.
- `model-vs-document-defect-probe` does **not** depend on the specification.
  A search of that repository returns no mention of it; the edge was proposed
  during drafting and removed on inspection.

Every objective, question, method, and status above was drafted by reading the
repository it describes, and each `status` was justified against a specific
file and line. The one `headline` in the file was verified independently against
`RESULTS.md`: `6/45 (13.3%)`, `1/45 (2.2%)`, `9/15 (60%)`, and `5/15 (33%)` all
appear there with the same meaning.

- [ ] **Step 3: Run the validator**

Run: `python -m scripts.build --check`
Expected: `repos.yml: 13 entries, all nine rules pass`

- [ ] **Step 4: Prove the validator actually bites**

Temporarily break one entry to confirm the check is not vacuous:

Write `tests/mutate_check.py` — a throwaway that proves the validator is not vacuous:

```python
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Prove --check fails on a broken repos.yml. Restores the file on the way out."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPOS = Path("repos.yml")

MUTATIONS = [
    ("stage: define", "stage: prototype"),
    ("strand: adequacy", "strand: nonsense"),
    ("owner: systems-researcher", "owner: not a name!"),
]

original = REPOS.read_text(encoding="utf-8")
failures = []
try:
    for old, new in MUTATIONS:
        assert old in original, f"mutation anchor missing: {old}"
        REPOS.write_text(original.replace(old, new, 1), encoding="utf-8")
        done = subprocess.run(
            [sys.executable, "-m", "scripts.build", "--check"],
            capture_output=True,
            text=True,
        )
        if done.returncode == 0:
            failures.append(f"--check passed despite '{new}'")
        else:
            print(f"ok: '{new}' rejected -> {done.stderr.strip().splitlines()[0]}")
finally:
    REPOS.write_text(original, encoding="utf-8")

if failures:
    print("\n".join(failures), file=sys.stderr)
    raise SystemExit(1)
print("validator bites on all three mutations")
```

Run: `python tests/mutate_check.py`
Expected: three `ok:` lines, then `validator bites on all three mutations`, exit 0.

Run: `python -m scripts.build --check`
Expected: exit 0 — the mutation script restored `repos.yml`.

Run: `git status --short repos.yml`
Expected: no output. If `repos.yml` shows as modified, the restore failed — run `git checkout repos.yml` before continuing.

- [ ] **Step 5: Commit**

```bash
git add repos.yml scripts/build.py tests/mutate_check.py
git commit -m "feat: author repos.yml with all thirteen entries"
```

---

## Task 6: Render the README block

**Files:**
- Create: `scripts/render.py`
- Modify: `scripts/build.py`
- Modify: `README.md`
- Test: `tests/test_render.py`

- [ ] **Step 1: Write the failing test**

`tests/test_render.py`:

```python
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Tests for rendering the README block and the site page."""
from __future__ import annotations

from scripts import mapdata, render

BEGIN = "<!-- BEGIN:repos -->"
END = "<!-- END:repos -->"


def data_with(*entries: dict) -> mapdata.MapData:
    data = mapdata.MapData(
        programme={"title": "T", "question": "Q", "move": "M"},
        strands={
            "adequacy": {"title": "Adequacy", "subtitle": "sub"},
            "assembly": {"title": "Assembly", "subtitle": "sub"},
        },
        stages={"define": "d", "evidence": "e", "assembly": "a"},
        repos=list(entries),
    )
    data.by_key = {entry["key"]: entry for entry in entries}
    return data


def entry(**overrides: object) -> dict:
    base = {
        "key": "alpha",
        "owner": "systems-researcher",
        "strand": "adequacy",
        "stage": "define",
        "render": "card",
        "objective": "What alpha is for.",
        "question": "What does alpha answer?",
        "method": "How alpha answers it.",
        "status": "design",
        "depends_on": [],
    }
    base.update(overrides)
    return base


def test_readme_block_replaces_only_between_the_markers() -> None:
    original = f"# Title\n\nintro\n\n{BEGIN}\nstale\n{END}\n\noutro\n"

    updated = render.readme_block(original, data_with(entry()))

    assert updated.startswith("# Title\n\nintro\n")
    assert updated.endswith("outro\n")
    assert "stale" not in updated
    assert "alpha" in updated


def test_readme_block_raises_when_markers_are_absent() -> None:
    try:
        render.readme_block("# Title\nno markers\n", data_with(entry()))
    except render.RenderError as exc:
        assert "BEGIN:repos" in str(exc)
    else:
        raise AssertionError("expected RenderError")


def test_readme_table_lists_stage_status_and_objective() -> None:
    updated = render.readme_block(
        f"{BEGIN}\n{END}\n", data_with(entry(status="published"))
    )

    assert "| `alpha` |" in updated
    assert "define" in updated
    assert "published" in updated
    assert "What alpha is for." in updated
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_render.py -v`
Expected: FAIL — `ImportError: cannot import name 'render' from 'scripts'`

- [ ] **Step 3: Write the minimal implementation**

`scripts/render.py`:

```python
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Pure rendering: MapData in, strings out. No file writes, no validation."""
from __future__ import annotations

import re

from scripts import mapdata

BEGIN = "<!-- BEGIN:repos -->"
END = "<!-- END:repos -->"
STAGE_ORDER = mapdata.STAGES
STRAND_ORDER = mapdata.STRANDS


class RenderError(Exception):
    """The target document is not shaped the way rendering requires."""


def _ordered(data: mapdata.MapData) -> list[dict]:
    """Entries in strand order, then stage order, then key order."""
    return sorted(
        data.repos,
        key=lambda e: (
            STRAND_ORDER.index(e["strand"]),
            STAGE_ORDER.index(e["stage"]),
            e["key"].lower(),
        ),
    )


def readme_table(data: mapdata.MapData) -> str:
    lines = [
        "| Repository | Stage | Status | What it is for |",
        "|---|---|---|---|",
    ]
    for entry in _ordered(data):
        objective = " ".join(str(entry["objective"]).split())
        lines.append(
            f"| `{entry['key']}` | {entry['stage']} | {entry['status']} | {objective} |"
        )
    return "\n".join(lines)


def readme_block(current: str, data: mapdata.MapData) -> str:
    """Replace the marked block in an existing README, leaving everything else alone."""
    pattern = re.compile(
        re.escape(BEGIN) + r".*?" + re.escape(END),
        re.DOTALL,
    )
    if not pattern.search(current):
        raise RenderError(
            f"README.md has no {BEGIN} ... {END} block; add one before building"
        )
    replacement = f"{BEGIN}\n\n{readme_table(data)}\n\n{END}"
    return pattern.sub(lambda _: replacement, current, count=1)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest tests/test_render.py -v`
Expected: PASS, 3 passed.

- [ ] **Step 5: Write the narrative README with markers**

`README.md` — the prose is hand-written and permanent; only the marked block is regenerated:

```markdown
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
<!-- END:repos -->

## Keeping this current

`repos.yml` is the source of truth. After editing it:

```bash
python scripts/refresh.py       # optional: pull live GitHub fields
python -m scripts.build         # regenerate site/index.html and the table above
python -m scripts.build --check # must pass before committing
```

## Licence

Prose and data CC-BY-4.0; code MIT. See [LICENSE.md](LICENSE.md).
```

- [ ] **Step 6: Wire the README write into `build.py`**

Replace the `print("nothing to render yet")` block in `scripts/build.py` with:

```python
    readme = ROOT / "README.md"
    updated = render.readme_block(readme.read_text(encoding="utf-8"), data)
    write_atomic(readme, updated)
    print(f"wrote {readme.name}")
    return 0
```

and add near the top of `scripts/build.py`:

```python
import os
import tempfile

from scripts import render


def write_atomic(path: Path, text: str) -> None:
    """Write via a temporary file in the same directory, then replace.

    A crashed build must never leave a half-written page or a README with one
    marker and not the other.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    os.replace(temporary, path)
```

- [ ] **Step 7: Run the build and inspect the result**

Run: `python -m scripts.build`
Expected: `wrote README.md`

Run: `git diff --stat README.md`
Expected: only lines between the markers changed.

- [ ] **Step 8: Commit**

```bash
git add scripts/render.py scripts/build.py tests/test_render.py README.md
git commit -m "feat(render): generate the README repository table between markers"
```

---

## Task 7: Refresh live GitHub data

**Files:**
- Create: `scripts/refresh.py`
- Test: `tests/test_refresh.py`

- [ ] **Step 1: Write the failing test**

`tests/test_refresh.py`:

```python
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Tests for the GitHub refresh. Never touches the network."""
from __future__ import annotations

import json
from pathlib import Path

from scripts import mapdata, refresh


def data_with(*entries: dict) -> mapdata.MapData:
    data = mapdata.MapData(programme={}, strands={}, stages={}, repos=list(entries))
    data.by_key = {entry["key"]: entry for entry in entries}
    return data


def entry(key: str, owner: str) -> dict:
    return {"key": key, "owner": owner}


def fake_gh(responses: dict[str, dict]):
    def runner(path: str) -> dict:
        if path not in responses:
            raise refresh.GhError(f"gh: {path}: Not Found")
        return responses[path]

    return runner


def test_local_entries_are_never_queried() -> None:
    calls = []

    def runner(path: str) -> dict:
        calls.append(path)
        return {}

    refresh.collect(data_with(entry("alpha", "local")), runner)

    assert calls == []


def test_successful_refresh_records_the_four_live_fields() -> None:
    runner = fake_gh(
        {
            "repos/systems-researcher/alpha": {
                "description": "d",
                "visibility": "private",
                "default_branch": "main",
                "pushed_at": "2026-08-19T08:00:00Z",
                "stargazers_count": 3,
            }
        }
    )

    result = refresh.collect(data_with(entry("alpha", "systems-researcher")), runner)

    assert result.repos["alpha"] == {
        "description": "d",
        "visibility": "private",
        "default_branch": "main",
        "pushed_at": "2026-08-19T08:00:00Z",
    }
    assert result.stale == []


def test_an_unreachable_repository_is_reported_stale_not_fatal() -> None:
    runner = fake_gh({})

    result = refresh.collect(data_with(entry("alpha", "systems-researcher")), runner)

    assert result.stale == ["alpha"]
    assert result.repos == {}


def test_previous_entries_survive_a_failed_lookup(tmp_path: Path) -> None:
    live = tmp_path / "live.json"
    live.write_text(
        json.dumps(
            {
                "generated_at": "2026-01-01T00:00:00+00:00",
                "repos": {"alpha": {"description": "old"}},
            }
        ),
        encoding="utf-8",
    )

    result = refresh.collect(
        data_with(entry("alpha", "systems-researcher")), fake_gh({}), previous=live
    )

    assert result.repos["alpha"]["description"] == "old"
    assert result.stale == ["alpha"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_refresh.py -v`
Expected: FAIL — `ImportError: cannot import name 'refresh' from 'scripts'`

- [ ] **Step 3: Write the minimal implementation**

`scripts/refresh.py`:

```python
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Pull live GitHub fields into data/live.json.

The only script that touches the network. Failure for one repository is never
fatal: its previous entry is kept and the key is reported stale on stderr.
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from scripts import mapdata

ROOT = Path(__file__).resolve().parent.parent
REPOS_YML = ROOT / "repos.yml"
LIVE_JSON = ROOT / "data" / "live.json"
LIVE_FIELDS = ("description", "visibility", "default_branch", "pushed_at")


class GhError(Exception):
    """The gh CLI could not answer for one repository."""


@dataclass
class Refreshed:
    repos: dict[str, dict] = field(default_factory=dict)
    stale: list[str] = field(default_factory=list)


def gh_runner(path: str) -> dict:
    """Call the gh CLI and parse its JSON. Raises GhError on any failure."""
    try:
        completed = subprocess.run(
            ["gh", "api", path],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise GhError("gh is not installed or not on PATH") from exc
    except subprocess.CalledProcessError as exc:
        raise GhError(f"gh api {path} failed: {exc.stderr.strip()}") from exc
    return json.loads(completed.stdout)


def collect(
    data: mapdata.MapData,
    runner: Callable[[str], dict] = gh_runner,
    previous: Path = LIVE_JSON,
) -> Refreshed:
    """Query every non-local entry. Keep the previous value for anything that fails."""
    old: dict[str, dict] = {}
    if previous and Path(previous).exists():
        old = json.loads(Path(previous).read_text(encoding="utf-8")).get("repos", {})

    result = Refreshed()
    for entry in data.repos:
        key, owner = entry["key"], entry["owner"]
        if owner == "local":
            continue
        try:
            payload = runner(f"repos/{owner}/{key}")
        except GhError:
            result.stale.append(key)
            if key in old:
                result.repos[key] = old[key]
            continue
        result.repos[key] = {name: payload.get(name) for name in LIVE_FIELDS}
    return result


def main(argv: list[str] | None = None) -> int:
    try:
        data = mapdata.load(REPOS_YML)
    except mapdata.MapError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = collect(data)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repos": result.repos,
    }
    LIVE_JSON.parent.mkdir(parents=True, exist_ok=True)
    LIVE_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"refreshed {len(result.repos)} repositories into {LIVE_JSON.name}")
    if result.stale:
        print(
            "stale (kept previous values): " + ", ".join(result.stale),
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_refresh.py -v`
Expected: PASS, 4 passed.

- [ ] **Step 5: Run it against the real GitHub account**

Run: `gh auth status`
Expected: logged in as `systems-researcher`. If not, stop and authenticate — the refresh reads private repositories.

Run: `python -m scripts.refresh`
Expected: `refreshed 10 repositories into live.json`, and three keys reported stale on stderr — the three `owner: local` entries are skipped entirely, so they must NOT appear in that list. If any of the ten is listed stale, investigate before continuing.

Run: `python -c "import json;d=json.load(open('data/live.json'));print(d['generated_at'], len(d['repos']))"`
Expected: a timestamp and `10`.

- [ ] **Step 6: Commit**

```bash
git add scripts/refresh.py tests/test_refresh.py data/live.json
git commit -m "feat(refresh): pull live GitHub fields into data/live.json"
```

---

## Task 8: Render the site page

**Files:**
- Modify: `scripts/render.py`
- Modify: `scripts/build.py`
- Test: `tests/test_render.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_render.py`:

```python
def test_mermaid_edges_run_from_dependency_to_consumer() -> None:
    data = data_with(
        entry(),
        entry(key="beta", stage="evidence", depends_on=["alpha"]),
    )

    diagram = render.mermaid(data)

    assert "n_alpha --> n_beta" in diagram
    assert "n_beta --> n_alpha" not in diagram


def test_mermaid_groups_by_stage_and_classes_by_strand() -> None:
    data = data_with(entry(), entry(key="beta", stage="evidence"))

    diagram = render.mermaid(data)

    assert 'subgraph stage_define["' in diagram
    assert 'subgraph stage_evidence["' in diagram
    assert "classDef adequacy" in diagram


def test_node_only_entries_get_no_click_target() -> None:
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable", depends_on=["alpha"]),
    )

    diagram = render.mermaid(data)

    assert "click n_alpha" in diagram
    assert "click n_Thesis_Work_Area" not in diagram


def test_page_renders_a_card_per_card_entry_and_none_for_node_only() -> None:
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable"),
    )

    page = render.page(data, live={"generated_at": "2026-08-19T09:00:00+00:00", "repos": {}})

    assert 'id="card-alpha"' in page
    assert 'id="card-Thesis-Work-Area"' not in page


def test_feeds_row_does_not_link_to_a_node_only_entry() -> None:
    data = data_with(
        entry(),
        entry(key="Thesis-Work-Area", strand="assembly", stage="assembly",
              render="node-only", status="not-applicable", depends_on=["alpha"]),
    )

    page = render.page(data, live={"generated_at": "t", "repos": {}})

    assert 'href="#card-Thesis-Work-Area"' not in page
    assert "Thesis-Work-Area" in page


def test_headline_is_rendered_with_its_source() -> None:
    data = data_with(
        entry(
            status="published",
            headline={"text": "13.3% fell to 2.2%.", "source": "probe v0.2.0, RESULTS.md"},
        )
    )

    page = render.page(data, live={"generated_at": "t", "repos": {}})

    assert "13.3% fell to 2.2%." in page
    assert "probe v0.2.0, RESULTS.md" in page


def test_missing_live_entry_is_badged_awaiting_refresh() -> None:
    page = render.page(data_with(entry()), live={"generated_at": "t", "repos": {}})

    assert "awaiting refresh" in page


def test_local_entry_is_badged_not_yet_published_and_has_no_github_link() -> None:
    page = render.page(
        data_with(entry(owner="local")), live={"generated_at": "t", "repos": {}}
    )

    assert "not yet published" in page
    assert "https://github.com/local/alpha" not in page


def test_absent_live_file_omits_the_footer_timestamp() -> None:
    page = render.page(data_with(entry()), live=None)

    assert "last refreshed" not in page.lower()


def test_prose_is_escaped_not_injected() -> None:
    page = render.page(
        data_with(entry(objective="<script>alert(1)</script>")),
        live={"generated_at": "t", "repos": {}},
    )

    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_render.py -v`
Expected: FAIL — `AttributeError: module 'scripts.render' has no attribute 'mermaid'`

- [ ] **Step 3: Write the minimal implementation**

Append to `scripts/render.py` (add `import html` at the top):

```python
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"

STATUS_LABELS = {
    "design": "design stage",
    "built-runs-pending": "built, runs pending",
    "released": "released",
    "results": "results in hand",
    "published": "published",
    "not-applicable": "",
}


def node_id(key: str) -> str:
    """A Mermaid-safe node id. Keys carry hyphens and mixed case; ids may not."""
    return "n_" + re.sub(r"[^A-Za-z0-9]", "_", key)


def mermaid(data: mapdata.MapData) -> str:
    """One subgraph per stage, strand carried by classDef, edges from depends_on."""
    lines = ["graph LR"]
    for stage in STAGE_ORDER:
        members = [e for e in _ordered(data) if e["stage"] == stage]
        if not members:
            continue
        label = html.escape(str(data.stages.get(stage, stage)))
        lines.append(f'  subgraph stage_{stage}["{stage.title()} — {label}"]')
        for member in members:
            lines.append(f'    {node_id(member["key"])}["{member["key"]}"]')
        lines.append("  end")

    for member in _ordered(data):
        for dependency in member.get("depends_on", []):
            lines.append(f'  {node_id(dependency)} --> {node_id(member["key"])}')

    for strand in STRAND_ORDER:
        members = [e for e in data.repos if e["strand"] == strand]
        if members:
            lines.append(
                f"  classDef {strand.replace('-', '_')} "
                "fill:#eef4ff,stroke:#5b7cc4,color:#12233f;"
            )
            names = ",".join(node_id(m["key"]) for m in members)
            lines.append(f"  class {names} {strand.replace('-', '_')};")

    for member in data.repos:
        if member.get("render", "card") == "card":
            lines.append(f'  click {node_id(member["key"])} "#card-{member["key"]}"')

    return "\n".join(lines)


def _anchor(key: str, data: mapdata.MapData) -> str:
    """Link to a card, or plain text when the target renders no card."""
    target = data.by_key.get(key, {})
    if target.get("render", "card") == "node-only":
        return f"<span class=\"plain\">{html.escape(key)}</span>"
    return f'<a href="#card-{html.escape(key)}">{html.escape(key)}</a>'


def _card(entry: dict, data: mapdata.MapData, inverted: dict, live: dict | None) -> str:
    key = entry["key"]
    live_repos = (live or {}).get("repos", {})
    known = key in live_repos

    if entry["owner"] == "local":
        badge, title = "not yet published", html.escape(key)
    else:
        badge = live_repos.get(key, {}).get("visibility", "awaiting refresh")
        if not known:
            badge = "awaiting refresh"
        url = f"https://github.com/{entry['owner']}/{key}"
        title = f'<a href="{html.escape(url)}" rel="noopener">{html.escape(key)}</a>'

    parts = [f'<article class="card" id="card-{html.escape(key)}">']
    parts.append(f"<h3>{title}</h3>")
    parts.append(
        f'<p class="badges"><span class="badge">{html.escape(badge)}</span>'
        f'<span class="badge">{html.escape(STATUS_LABELS.get(entry["status"], ""))}</span></p>'
    )
    for label, field_name in (
        ("What it is for", "objective"),
        ("Question", "question"),
        ("Method", "method"),
    ):
        text = html.escape(" ".join(str(entry[field_name]).split()))
        parts.append(f"<p><strong>{label}.</strong> {text}</p>")

    headline = entry.get("headline")
    if headline:
        parts.append(
            '<p class="headline"><strong>Result.</strong> '
            f'{html.escape(" ".join(str(headline["text"]).split()))} '
            f'<span class="source">Source: {html.escape(str(headline["source"]))}</span></p>'
        )
    if entry.get("output"):
        parts.append(f'<p class="output">{html.escape(str(entry["output"]))}</p>')

    depends = entry.get("depends_on", [])
    feeds_into = inverted.get(key, [])
    if depends:
        parts.append(
            '<p class="links"><strong>Depends on.</strong> '
            + ", ".join(_anchor(k, data) for k in depends)
            + "</p>"
        )
    if feeds_into:
        parts.append(
            '<p class="links"><strong>Feeds.</strong> '
            + ", ".join(_anchor(k, data) for k in feeds_into)
            + "</p>"
        )
    parts.append("</article>")
    return "\n".join(parts)


def page(data: mapdata.MapData, live: dict | None) -> str:
    inverted = mapdata.feeds(data)
    programme = data.programme

    sections = []
    for strand in STRAND_ORDER:
        members = [e for e in _ordered(data) if e["strand"] == strand]
        cards = [e for e in members if e.get("render", "card") == "card"]
        if not members:
            continue
        heading = data.strands.get(strand, {})
        sections.append(f'<section id="strand-{strand}">')
        sections.append(f'<h2>{html.escape(str(heading.get("title", strand)))}</h2>')
        sections.append(f'<p class="subtitle">{html.escape(str(heading.get("subtitle", "")))}</p>')
        for stage in STAGE_ORDER:
            in_stage = [e for e in cards if e["stage"] == stage]
            if not in_stage:
                continue
            sections.append(f"<h3>{stage.title()}</h3>")
            sections.append(f'<p class="stage-note">{html.escape(str(data.stages.get(stage, "")))}</p>')
            sections.extend(_card(e, data, inverted, live) for e in in_stage)
        sections.append("</section>")

    footer = []
    if live and live.get("generated_at"):
        footer.append(
            f'<p>Live repository data last refreshed {html.escape(str(live["generated_at"]))}.</p>'
        )
    footer.append(
        "<p>Repositories marked private are readable on request — contact the author.</p>"
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(str(programme.get("title", "Research programme")))}</title>
<style>
:root {{ --bg:#fbfbfd; --fg:#14161a; --muted:#5a6270; --line:#dfe3ea; --card:#ffffff; --accent:#2f4f8f; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#111318; --fg:#e8eaee; --muted:#98a1b0; --line:#272b33; --card:#171a20; --accent:#9db6f0; }}
}}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; }}
main {{ max-width: 62rem; margin: 0 auto; padding: 2rem 1.25rem 5rem; }}
h1 {{ font-size: 1.9rem; line-height:1.25; margin:0 0 .5rem; }}
h2 {{ font-size: 1.4rem; margin: 3rem 0 .25rem; padding-top:1.5rem; border-top:1px solid var(--line); }}
h3 {{ font-size: 1.05rem; margin: 2rem 0 .25rem; }}
.subtitle, .stage-note {{ color: var(--muted); margin:.25rem 0 1rem; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:.6rem; padding:1rem 1.15rem; margin:1rem 0; }}
.card h3 {{ margin:0 0 .5rem; font-size:1.05rem; }}
.badges {{ margin:0 0 .75rem; }}
.badge {{ display:inline-block; font-size:.75rem; text-transform:uppercase; letter-spacing:.04em;
  border:1px solid var(--line); border-radius:1rem; padding:.1rem .6rem; margin-right:.4rem; color:var(--muted); }}
.card p {{ margin:.4rem 0; }}
.headline {{ border-left:3px solid var(--accent); padding-left:.75rem; }}
.source, .output {{ color:var(--muted); font-size:.85rem; }}
.links {{ font-size:.9rem; }}
.plain {{ color:var(--muted); }}
a {{ color:var(--accent); }}
#diagram {{ overflow-x:auto; border:1px solid var(--line); border-radius:.6rem; padding:1rem; background:var(--card); }}
footer {{ margin-top:4rem; padding-top:1.5rem; border-top:1px solid var(--line); color:var(--muted); font-size:.9rem; }}
</style>
</head>
<body>
<main>
<h1>{html.escape(str(programme.get("title", "")))}</h1>
<p>{html.escape(" ".join(str(programme.get("question", "")).split()))}</p>
<p><strong>{html.escape(" ".join(str(programme.get("move", "")).split()))}</strong></p>

<div id="diagram"><pre class="mermaid">
{mermaid(data)}
</pre></div>

{chr(10).join(sections)}

<footer>
{chr(10).join(footer)}
</footer>
</main>
<script type="module">
import mermaid from "{MERMAID_CDN}";
mermaid.initialize({{ startOnLoad: true, theme: window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "default" }});
</script>
</body>
</html>
"""
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_render.py -v`
Expected: PASS, 13 passed.

- [ ] **Step 5: Wire the page into `build.py`**

In `scripts/build.py`, add `import json` and replace the render section of `main()` with:

```python
    live = None
    live_path = ROOT / "data" / "live.json"
    if live_path.exists():
        live = json.loads(live_path.read_text(encoding="utf-8"))
    else:
        print(
            "warning: data/live.json is absent; building without live GitHub fields",
            file=sys.stderr,
        )

    readme = ROOT / "README.md"
    write_atomic(readme, render.readme_block(readme.read_text(encoding="utf-8"), data))
    write_atomic(ROOT / "site" / "index.html", render.page(data, live))
    print(f"wrote README.md and site/index.html ({len(data.repos)} entries)")
    return 0
```

- [ ] **Step 6: Build and check the page by eye**

Run: `python -m scripts.build`
Expected: `wrote README.md and site/index.html (13 entries)`

Run: `python -m pytest -q`
Expected: all tests pass.

Open `site/index.html` in a browser. Confirm, by eye:
1. The diagram renders and arrows run from earlier stages to later ones.
2. Clicking a diagram node scrolls to that card.
3. The thesis node is present, has no card, and is not clickable.
4. Narrow the window to 400px — no horizontal page scroll; the diagram scrolls inside its own box.
5. Switch the OS to dark mode and reload — text stays readable.

- [ ] **Step 7: Verify the page has exactly one external dependency**

```bash
python -c "import re,pathlib;u=sorted(set(re.findall(r'https?://[^\"'\\s<>]+', pathlib.Path('site/index.html').read_text(encoding='utf-8'))));print(chr(10).join(u))"
```

Expected: the Mermaid CDN URL and `https://github.com/systems-researcher/...` links, and nothing else — no analytics, no font hosts, no trackers. Every host other than `cdn.jsdelivr.net` and `github.com` is a defect: the page must stay self-contained.

- [ ] **Step 8: Commit**

```bash
git add scripts/render.py scripts/build.py tests/test_render.py site/index.html README.md
git commit -m "feat(render): generate the one-page site with a Mermaid dependency graph"
```

---

## Task 9: Publish

**Files:**
- Create: `vercel.json`

- [ ] **Step 1: Write `vercel.json`**

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": null,
  "outputDirectory": "site",
  "framework": null,
  "cleanUrls": true
}
```

- [ ] **Step 2: Confirm the authenticated account before creating anything**

Run: `gh api user --jq .login`
Expected: `systems-researcher`. If it prints anything else, stop — the repository would be created under the wrong account.

- [ ] **Step 3: Create the private repository and push**

```bash
python -m pytest -q
python -m scripts.build --check
git add vercel.json
git commit -m "chore: vercel static configuration"
gh repo create systems-researcher/research-programme --private --source=. --remote=origin --push
```

Expected: the repository is created and `main` is pushed.

Run: `gh repo view systems-researcher/research-programme --json visibility,defaultBranchRef`
Expected: `"visibility":"PRIVATE"`.

- [ ] **Step 4 (human-gated): Connect Vercel**

This step is manual — Vercel's GitHub connection cannot be scripted from here.

1. Go to https://vercel.com/new and import `systems-researcher/research-programme`.
2. Grant access to that single repository, not the whole account.
3. Framework preset: **Other**. Build command: **none**. Output directory: **site**.
4. Deploy.

Acceptance criterion: the deployment URL loads the page over the public internet in a private browser window with no GitHub session — proving the site is public while the repository is not.

Verify afterwards: `curl -s -o /dev/null -w "%{http_code}\n" <deployment-url>`
Expected: `200`.

- [ ] **Step 5: Record the URL in the README**

Replace the `<!-- SITE-URL -->` line in `README.md` with the deployment URL as a link, then:

```bash
python -m scripts.build --check
git commit -am "docs: record the published site URL"
git push
```

- [ ] **Step 6: Confirm the loop closes**

Run: `python -m scripts.refresh && python -m scripts.build && python -m scripts.build --check && git status --short`
Expected: exit 0 throughout. Any diff should be confined to `data/live.json`, `site/index.html`, and the README's marked block — never to authored prose.

---

## Notes for the implementer

**Run scripts as modules, not files.** `python -m scripts.build`, not `python scripts/build.py` — the latter breaks the `from scripts import ...` imports.

**`repos.yml` is the only file you hand-edit.** `data/live.json`, `site/index.html`, and the README block between the markers are all generated. If you find yourself editing one of them to fix the page, the fix belongs in `repos.yml` or in `render.py`.

**Never write a number onto the page that you cannot trace.** Rule 5 and rule 6 exist because this programme's subject is AI systems producing claims their source material does not authorise. A fabricated figure on this map would discredit the work it describes. If a repository's results are unclear, leave `headline` out and set the honest `status`.
