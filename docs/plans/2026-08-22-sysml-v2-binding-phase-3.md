<!--
Copyright (c) 2026 Jason D. Gower
SPDX-License-Identifier: CC-BY-4.0
-->

# SysML v2 Binding — Phase 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `epistemic-adequacy-metamodel` a *binding* — one that consumes the published ontology at a pinned version, supplies the four concrete types the binding contract asks for, and generates its SysML v2 library from that rather than from a schema of its own — then rename it.

**Architecture:** The ontology repository now owns the schema. This repository stops owning one. It gains `type-map.yaml`, which answers the binding contract's four obligations; its SysML generator is rewritten to render from `(eaont model + type map)`; and its own `metamodel/metamodel.yaml`, `load.py` and `model.py` retire, superseded by `eaont`. The library must come out **structurally identical** to the one committed today — same definitions, same parameters, same multiplicities — with doc text differing only where the ontology deliberately rewrote it. The full Apollo regression is the proof the refactor preserved behaviour.

**Tech Stack:** Python ≥ 3.14 in the repository's own `.venv`, JDK 21, Node 24, the OMG SysML v2 pilot, and the private `epistemic-adequacy-testing-toolkit`.

**Spec:** [`2026-08-21-epistemic-adequacy-ontology-split-design.md`](2026-08-21-epistemic-adequacy-ontology-split-design.md) §5.2, §9 (Phase 3). Phases 1 and 2 are complete — see [`2026-08-21-ontology-repo-phase-1-2.md`](2026-08-21-ontology-repo-phase-1-2.md) and its [execution log](2026-08-21-ontology-repo-phase-1-2-execution-log.md).

**Scope:** Phase 3 only. Phase 4 (spec v0.2.0), Phase 5 (write-side entities) and Phase 6 (programme bookkeeping) are separate plans.

---

## Three corrections to the design, made before planning

The design's Phase 3 is wrong in three places. Each was found by checking the repositories rather than reading the design, and each is corrected here rather than discovered mid-execution.

### C1. "Generated `.sysml` byte-matches" is unachievable

Design §9 states the exit criterion as a byte-match. It cannot hold, for two reasons that are both *intended* consequences of Phase 1:

- **Doc text deliberately differs.** Phase 1 Task 6 moved clause consequences out of enumeration member documentation, and the final fix wave neutralised SysML v2 prose in entity docs. `UnresolvedFieldKind::evidence` reads `"Fails EA-REQ-10 — declaring evidence unreachable is not evidence."` in the committed library and `"A declared gap where a retrievable source for the claim would sit."` in the ontology.
- **The enumeration counts differ by three.** Committed library: 13 metadata defs, **12** enum defs. Ontology: 13 defs, **9** enums. The gap is exactly `RevisionSchemeKind`, `ProfileKind` and `CriticalityPolicyKind`.

**Replaced by: structural equivalence with an enumerated allowed-diff.** Task 4 defines it precisely and makes it a test.

### C2. The binding must *extend* the ontology's schema, not merely render it

`models/apollo-annotated.sysml:29-34` sets `revisionScheme`, `criticalityPolicy` and `profileClaimed` on its `@SubstrateDeclaration`. All three parameters were removed from the ontology in Phase 1 — correctly: `RevisionSchemeKind`'s member `apiCommit` is a SysML v2 API concept, and the other two duplicate `conformance/profiles.md` and `clauses.yaml`.

They are read by `src/eamm/resolve/rules.py`, `scripts/check_profile_claim.py`, `scripts/apollo_delta.py`, `tests/test_apollo_annotated.py` and `tests/test_conformance_claim.py`. Deleting them breaks the Apollo regression, which is this phase's exit criterion.

ADR-012 already anticipated this and the plan follows it verbatim:

> A substrate still declares a claimed profile — but it does so in the binding, against the specification's vocabulary, with no second definition here.

So `type-map.yaml` carries three kinds of thing, not one: type mappings, binding-owned enumerations, and binding-owned parameter extensions.

### C3. The order in §9 puts the rename first; it goes last

§9 lists Phase 3 as "Rename … Add `type-map.yaml`, regenerate `library/`". Inverted here. A rename is ten files plus a GitHub redirect and is trivially reversible; a half-regenerated library inside a freshly renamed repository is the state in which a failure cannot be attributed to either cause. Get the regeneration green under the old name, then rename.

This is the same discipline Phase 1 Task 2 used when it ordered the provenance edit before the byte-compare.

---

## Global Constraints

- **Use `.venv/Scripts/python.exe`, never bare `python`.** The ambient interpreter has an editable `eamm` install pointing at a dead scratchpad from an earlier session (`AppData/Local/Temp/claude/…/p2-r8/src/eamm`), so `import eamm` there resolves to a partial copy and the suite fails to collect with `ModuleNotFoundError: No module named 'eamm.generate.owl'`. **Every command in this plan uses the venv interpreter explicitly.**
- **`JAVA_HOME` must point at JDK 21.** `java` on `PATH` is JRE 1.8, which cannot run tiers 2 or 3. JDK 21 is installed at `C:\Program Files\Microsoft\jdk-21.0.10.7-hotspot`. Export it and prepend its `bin`.
- **`EAMM_PILOT_HOME=.pilot`**, which is already provisioned (`kernel.conda`, `share/…/jupyter-sysml-kernel-0.60.1-all.jar`) and whose exporter is already compiled (`java/classes/ModelExport.class`).
- **Toolkit pin:** `6374b6715aca8d206003919e3824f9d41915fc89`, recorded in `docs/conformance-claim.md`. Do not change it in this phase — a claim scored against a different instrument version is a different claim.
- **Baseline to preserve: `294 passed`**, all three tiers, measured 2026-08-22. Any number below that is a regression.
- Python ≥ 3.14; all file writes `newline="\n"`; `.py` carries `# SPDX-License-Identifier: MIT`; `.md` an HTML-comment CC-BY-4.0 header; **never SPDX in `.ttl` or `.sysml`**.
- **`library/EpistemicAdequacy.sysml` is generated.** `Derivations.sysml`, `Constraints.sysml` and `Queries.sysml` are hand-written behaviour and no generator touches them.
- The ontology is consumed **at a pin**. Never edit anything under the installed `eaont`.

---

### Task 1: Lock the baseline and the environment

Nothing in this phase means anything measured against an unknown starting point, and two environment defects will silently produce a false red.

**Files:**
- Create: `scripts/env.sh`
- Create: `docs/phase-3-baseline.md`

**Interfaces:**
- Produces: `scripts/env.sh`, sourced by every later task to set `JAVA_HOME`, `PATH` and `EAMM_PILOT_HOME`. Later tasks assume `PY=.venv/Scripts/python.exe`.

- [ ] **Step 1: Confirm the two environment defects for yourself**

```bash
python -c "import eamm; print(eamm.__file__)"          # ambient: a dead scratchpad path
.venv/Scripts/python.exe -c "import eamm; print(eamm.__file__)"   # venv: this repo's src/eamm
java -version 2>&1 | head -1                            # 1.8 - cannot run tiers 2-3
"/c/Program Files/Microsoft/jdk-21.0.10.7-hotspot/bin/java" -version 2>&1 | head -1   # 21
```

Expected: the first two disagree, and the last two disagree. If the ambient `eamm` now resolves into this repository, say so in your report — it means someone reinstalled it and the hazard has changed shape, not gone.

- [ ] **Step 2: Write `scripts/env.sh`**

```bash
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
#
# Source this before any command in Phase 3: `. scripts/env.sh`
#
# Two defects this guards against, both observed on 2026-08-22:
#   - the ambient Python carries an editable `eamm` install pointing at a
#     deleted scratchpad, so `import eamm` there resolves to a partial copy
#   - `java` on PATH is JRE 1.8; tiers 2 and 3 need JDK 21
export JAVA_HOME="/c/Program Files/Microsoft/jdk-21.0.10.7-hotspot"
export PATH="$JAVA_HOME/bin:$PATH"
export EAMM_PILOT_HOME="$(git rev-parse --show-toplevel)/.pilot"
PY="$(git rev-parse --show-toplevel)/.venv/Scripts/python.exe"
export PY
echo "java: $(java -version 2>&1 | head -1)"
echo "PY:   $PY"
```

- [ ] **Step 3: Record the baseline**

```bash
. scripts/env.sh
"$PY" -m pytest -q 2>&1 | tail -3
```

Expected: `294 passed`, roughly two minutes. **If it is not 294 passed, stop and report.** A regression that predates this phase is a precondition to fix, not something this plan absorbs — and every later exit criterion is measured against this number.

Write `docs/phase-3-baseline.md` with the CC-BY-4.0 header recording: the date, the count, the three environment settings, the toolkit pin, and the commit (`git rev-parse HEAD`).

- [ ] **Step 4: Commit**

```bash
git add scripts/env.sh docs/phase-3-baseline.md
git commit -m "chore(phase-3): pin the interpreter and the JDK, and record the baseline

294 passed across all three tiers. The ambient Python resolves eamm to a
deleted scratchpad and PATH java is 1.8; both silently produce a false red."
```

---

### Task 2: Depend on the ontology, at a pin

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/test_ontology_pin.py`

**Interfaces:**
- Consumes: the ontology repository at `../epistemic-adequacy-ontology`.
- Produces: `eaont` importable in the venv; `ONTOLOGY_PIN` recorded in `pyproject.toml`'s `[tool.eamm]` table and asserted by `tests/test_ontology_pin.py`.

- [ ] **Step 1: Record the pin and install**

Take the ontology's current commit:

```bash
ONTOLOGY_PIN=$(git -C ../epistemic-adequacy-ontology rev-parse HEAD)
echo "$ONTOLOGY_PIN"
```

Add to `pyproject.toml` (a new table; do not disturb `[project]`):

```toml
[tool.eamm]
# The ontology this binding renders. A library generated against a different
# version is a library generated against a contract that moved.
ontology_pin = "<the 40-char sha>"
ontology_version = "0.1.0"
```

Install it editable, into the venv only:

```bash
. scripts/env.sh
"$PY" -m pip install -e ../epistemic-adequacy-ontology
"$PY" -c "import eaont, eamm; print('eaont', eaont.__file__); print('eamm ', eamm.__file__)"
```

Expected: two distinct paths, `eaont` in the ontology repo and `eamm` in this one. They are different top-level packages and do not shadow each other.

- [ ] **Step 2: Write the failing test**

Create `tests/test_ontology_pin.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""The binding renders one version of the ontology, and says which.

A library generated against an unrecorded ontology version is not
reproducible, and the two repositories move independently.
"""

from __future__ import annotations

import pathlib
import subprocess
import tomllib

import pytest

ROOT = pathlib.Path(__file__).parents[1]
CONFIG = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
PIN = CONFIG["tool"]["eamm"]["ontology_pin"]


def test_pin_is_a_full_sha():
    assert len(PIN) == 40 and all(c in "0123456789abcdef" for c in PIN)


def test_the_installed_ontology_is_the_pinned_commit():
    """Editable installs track a working tree, so the tree must be AT the pin.

    Skipped rather than failed when the ontology repo is absent: tier 1 of this
    repository must stay runnable without it.
    """
    import eaont

    repo = pathlib.Path(eaont.__file__).parents[2]
    if not (repo / ".git").exists():
        pytest.skip("ontology installed from a wheel, not a checkout")
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert head == PIN, (
        f"ontology checkout is at {head[:7]}, pinned at {PIN[:7]}; either "
        f"update tool.eamm.ontology_pin deliberately or check the tree out at the pin"
    )


def test_the_two_loaders_refuse_each_other():
    """The reason this binding cannot simply reuse its own loader.

    `eamm.load` does not know the abstract reference types; `eaont.load`
    refuses language types by construction. Neither can read the other's
    schema, which is why Task 4 renders through `eaont` and applies a type map.
    """
    import eaont.load
    import eamm.load

    ontology_schema = pathlib.Path(eaont.load.__file__).parents[2] / "model" / "ontology.yaml"
    with pytest.raises(eamm.load.MetamodelError, match="unknown type"):
        eamm.load.load_metamodel(ontology_schema)
```

- [ ] **Step 3: Run it**

```bash
. scripts/env.sh
"$PY" -m pytest tests/test_ontology_pin.py -v
```

Expected: PASS, 3 tests. If `test_the_two_loaders_refuse_each_other` fails, the binding's loader has changed and Task 4's design premise needs re-checking before you continue.

- [ ] **Step 4: Full suite, then commit**

```bash
"$PY" -m pytest -q 2>&1 | tail -2     # expect 297 passed
git add pyproject.toml tests/test_ontology_pin.py
git commit -m "feat: consume the ontology at a pin, and prove why a type map is needed

The two loaders refuse each other's schemas by construction - eamm.load does
not know ElementRef, eaont.load refuses SysML::EnumerationDefinition. That
mutual refusal is the reason this binding renders through eaont rather than
reusing its own loader, and it is now a test."
```

---

### Task 3: `type-map.yaml` — the binding's answer to the contract

**Files:**
- Create: `type-map.yaml`
- Create: `tests/test_type_map.py`

**Interfaces:**
- Consumes: `eaont.load.ABSTRACT_REFS` (exactly `ElementRef`, `ExpressionRef`, `PredicateRef`, `VocabularyRef`).
- Produces: `type-map.yaml` with top-level keys `ontology_version`, `types`, `enumerations`, `extends`. Task 4's generator reads all four.

- [ ] **Step 1: Write the failing test**

Create `tests/test_type_map.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""The binding supplies what the contract asks for, and nothing it does not."""

from __future__ import annotations

import pathlib

import yaml
from eaont.load import ABSTRACT_REFS

ROOT = pathlib.Path(__file__).parents[1]
MAP = yaml.safe_load((ROOT / "type-map.yaml").read_text(encoding="utf-8"))


def test_every_abstract_ref_is_mapped_and_nothing_else():
    assert set(MAP["types"]) == ABSTRACT_REFS


def test_every_mapping_names_a_language_type():
    """This is a SysML v2 binding; a mapping to a bare string would mean the
    binding had not bound anything."""
    for name, target in MAP["types"].items():
        assert target.startswith(("KerML::", "SysML::")), f"{name} -> {target!r}"


def test_every_binding_enumeration_names_an_anchor_and_members():
    for name, body in MAP["enumerations"].items():
        assert body["after"], f"{name} has no `after:` anchor"
        assert body["members"], f"{name} declares no members"


def test_binding_owned_enumerations_are_the_three_the_ontology_dropped():
    """RevisionSchemeKind left because apiCommit is a SysML v2 API concept.
    ProfileKind and CriticalityPolicyKind left because they duplicate the
    specification. All three are still needed HERE - see ADR-012."""
    assert set(MAP["enumerations"]) == {
        "RevisionSchemeKind", "ProfileKind", "CriticalityPolicyKind"
    }


def test_substrate_declaration_regains_exactly_three_parameters():
    assert set(MAP["extends"]["SubstrateDeclaration"]) == {
        "revisionScheme", "criticalityPolicy", "profileClaimed"
    }


def test_the_apollo_model_can_still_be_satisfied():
    """The three extension parameters exist because models/apollo-annotated.sysml
    sets them. If that stops being true, the extensions are dead weight."""
    model = (ROOT / "models" / "apollo-annotated.sysml").read_text(encoding="utf-8")
    for param in MAP["extends"]["SubstrateDeclaration"]:
        assert f"{param} =" in model, f"{param} is mapped but the model does not set it"


def test_ontology_version_agrees_with_pyproject():
    import tomllib
    cfg = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert MAP["ontology_version"] == cfg["tool"]["eamm"]["ontology_version"]
```

- [ ] **Step 2: Run it to see it fail**

```bash
. scripts/env.sh
"$PY" -m pytest tests/test_type_map.py -v
```

Expected: FAIL, `FileNotFoundError` on `type-map.yaml`.

- [ ] **Step 3: Write `type-map.yaml`**

```yaml
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
#
# This binding's answer to docs/binding-contract.md in the ontology repository.
#
# Three kinds of thing live here, and the difference matters:
#   types        - what the four abstract reference types resolve to in SysML v2
#   enumerations - vocabularies the ontology does not own, but this binding needs
#   extends      - parameters this binding adds to an ontology entity
#
# The second and third exist because the ontology deliberately gave three things
# up in the split, and a SysML v2 substrate still needs them. ADR-012: "A
# substrate still declares a claimed profile - but it does so in the binding,
# against the specification's vocabulary, with no second definition here."

ontology_version: "0.1.0"

# Obligation 2: map every abstract reference type, and no others.
types:
  ElementRef:    "KerML::Element"
  ExpressionRef: "KerML::Function"
  PredicateRef:  "KerML::Predicate"
  VocabularyRef: "SysML::EnumerationDefinition"

# Vocabularies this binding owns. None is ontology: `apiCommit` is a SysML v2
# API service commit identity, and the other two restate conformance packaging
# that epistemic-adequacy-spec's profiles.md and clauses.yaml already own.
# `after:` fixes each one's position among the ontology's, so the rendered
# library keeps the order the committed one has.
enumerations:
  RevisionSchemeKind:
    after: BoundaryKind
    members:
      gitCommit: The commit hash of the model tree at extraction time.
      apiCommit: A SysML v2 API service commit identity.
      tag: >-
        An annotated git tag, for substrates publishing at release
        granularity. A working tree differing from the named tag fails
        extraction.
  CriticalityPolicyKind:
    after: RevisionSchemeKind
    members:
      declaredPerClaim: >-
        EA-REQ-10 reaches MUST only for claims declaring safetyCritical. This
        is the Governed profile's behaviour.
      allCritical: >-
        EA-REQ-10 is MUST for every governed claim, which is what the
        Safety-critical profile requires.
  ProfileKind:
    after: UnresolvedFieldKind
    members:
      minimal: EA-REQ-01, 02, 03, 05, 06.
      governed: Minimal plus EA-REQ-04, 07, 08, 09, 10, 11, 12, 13, 14, 15.
      safetyCritical: >-
        Governed, EA-REQ-10 at MUST for all claims, plus EA-REQ-16, 17, 18.

# Parameters this binding adds to an ontology entity. models/apollo-annotated.sysml
# sets all three, and resolve/rules.py, scripts/check_profile_claim.py and
# scripts/apollo_delta.py read them.
extends:
  SubstrateDeclaration:
    revisionScheme:
      kind: attribute
      type: RevisionSchemeKind
      multiplicity: "1"
      after: lifecycleStages
    criticalityPolicy:
      kind: attribute
      type: CriticalityPolicyKind
      multiplicity: "1"
      after: revisionScheme
    profileClaimed:
      kind: attribute
      type: ProfileKind
      multiplicity: "1"
      after: specVersion

defaults:
  revision_scheme: gitCommit
```

`after:` fixes each extension's position in the rendered `metadata def`, so the generated library keeps the parameter order the committed one has. Task 4's structural comparison depends on it.

- [ ] **Step 4: Run the tests, then the suite**

```bash
"$PY" -m pytest tests/test_type_map.py -v      # expect PASS, 7 tests
"$PY" -m pytest -q 2>&1 | tail -2              # expect 304 passed
```

- [ ] **Step 5: Commit**

```bash
git add type-map.yaml tests/test_type_map.py
git commit -m "feat: type-map.yaml - four mappings, three vocabularies, three extensions

The ontology gave up RevisionSchemeKind (apiCommit is a SysML v2 API concept)
and ProfileKind/CriticalityPolicyKind (they duplicate the specification). A
SysML v2 substrate still needs all three, and models/apollo-annotated.sysml
sets all three on its @SubstrateDeclaration. ADR-012 anticipated this: the
substrate declares its profile in the binding, against the spec's vocabulary."
```

---

### Task 4: Render the library from the ontology, and prove it is the same library

The heart of the phase. The generator stops reading a local schema and starts rendering `(eaont model + type map)`.

**Files:**
- Modify: `src/eamm/generate/sysml.py`
- Create: `tests/fixtures/library-before.sysml`
- Create: `tests/test_library_equivalence.py`

**Interfaces:**
- Consumes: `eaont.load.load_metamodel`, `eaont.model.{Metamodel,MetadataDef,Parameter,Enumeration,Member}`, `type-map.yaml`.
- Produces: `render_library(ontology_model, type_map) -> str`. Task 5 calls it through the CLI.

- [ ] **Step 1: Capture the before-library as a fixture**

```bash
mkdir -p tests/fixtures
cp library/EpistemicAdequacy.sysml tests/fixtures/library-before.sysml
grep -c "^    metadata def " tests/fixtures/library-before.sysml   # 13
grep -c "^    enum def " tests/fixtures/library-before.sysml        # 12
```

This is the artefact the refactor must reproduce. Commit it — a baseline that is not committed is not a baseline.

- [ ] **Step 2: Write the equivalence test**

**Byte-identity is not the criterion and cannot be** — Phase 1 deliberately rewrote doc text, and the enumeration counts differ by the three the binding now supplies. What must hold is structure.

Create `tests/test_library_equivalence.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""The regenerated library is the same library, structurally.

Byte-identity is impossible on purpose: Phase 1 moved clause consequences out
of enumeration member docs and neutralised SysML v2 prose in entity docs, so
doc text differs by design. What must not differ is the shape - every
definition, every parameter, every type, every multiplicity, every enumeration
member.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).parents[1]
BEFORE = (ROOT / "tests" / "fixtures" / "library-before.sysml").read_text(encoding="utf-8")
AFTER = (ROOT / "library" / "EpistemicAdequacy.sysml").read_text(encoding="utf-8")

DEF = re.compile(r"^    metadata def (\w+) \{", re.M)
ENUM = re.compile(r"^    enum def (\w+) \{", re.M)
MEMBER = re.compile(r"^        enum (\w+)", re.M)
# `attribute foo : Bar;` / `attribute foo[1..*] : Bar;` / `ref foo : Bar;`
PARAM = re.compile(r"^        (attribute|ref) (\w+)(\[[^\]]+\])? : ([\w:]+);", re.M)


def _params(text: str, name: str) -> set[tuple[str, ...]]:
    block = text.split(f"metadata def {name} {{", 1)[1].split("\n    }", 1)[0]
    return {(k, n, m or "", t) for k, n, m, t in PARAM.findall(block)}


def test_the_same_definitions_exist():
    assert set(DEF.findall(AFTER)) == set(DEF.findall(BEFORE))


def test_the_same_enumerations_exist():
    assert set(ENUM.findall(AFTER)) == set(ENUM.findall(BEFORE))


def test_the_same_enumeration_members_exist():
    assert set(MEMBER.findall(AFTER)) == set(MEMBER.findall(BEFORE))


def test_every_definition_has_the_same_parameters():
    for name in DEF.findall(BEFORE):
        assert _params(AFTER, name) == _params(BEFORE, name), name


def test_parameter_order_is_preserved():
    """`after:` in type-map.yaml exists to hold this. Order is not cosmetic:
    a reader comparing the two libraries side by side is the check of last
    resort, and reordering defeats it."""
    for name in DEF.findall(BEFORE):
        b = _params_ordered(BEFORE, name)
        a = _params_ordered(AFTER, name)
        assert a == b, f"{name}: {a} != {b}"


def _params_ordered(text: str, name: str) -> list[str]:
    block = text.split(f"metadata def {name} {{", 1)[1].split("\n    }", 1)[0]
    return [n for _, n, _, _ in PARAM.findall(block)]


def test_doc_text_is_allowed_to_differ_and_does():
    """Guards the claim above. If docs stopped differing, either Phase 1's
    rewrites were lost or this test is comparing a file to itself."""
    assert "Fails EA-REQ-10" in BEFORE
    assert "Fails EA-REQ-10" not in AFTER
```

- [ ] **Step 3: Run it to see it fail**

```bash
. scripts/env.sh
"$PY" -m pytest tests/test_library_equivalence.py -v
```

Expected: `test_doc_text_is_allowed_to_differ_and_does` FAILS — `library/` is still the old file, so `BEFORE == AFTER`. That failure is the proof the test is comparing two real things.

- [ ] **Step 4: Rewrite the generator**

`src/eamm/generate/sysml.py` is 106 lines and its rendering primitives stay exactly as they are. **Do not touch `RESERVED`, `_identifier`, `_doc`, `_multiplicity`, `render_enum` or `render_metadata_def`'s formatting** — `RESERVED` in particular was determined empirically against `sysml-validate` 0.15.7 by probing 47 enum members and 48 parameter names, and `entry` unquoted makes the resource stop indexing silently.

Four changes. Add these helpers:

```python
def _type_name(raw: str, type_map: dict) -> str:
    """Primitive, mapped abstract reference, or a name that stands as written."""
    if raw in PRIMITIVE_TYPES:
        return PRIMITIVE_TYPES[raw]
    return type_map["types"].get(raw, raw)


def _ordered_merge(base: dict, additions: dict, anchors: dict) -> dict:
    """Insert each addition immediately after the key its anchor names.

    Dicts keep insertion order, so rebuilding is how position is set. An
    addition whose anchor is itself an addition is handled, because each
    inserted key is offered as an anchor in turn.
    """
    out: dict = {}
    pending = dict(additions)

    def _emit(anchor: str) -> None:
        for name, after in list(anchors.items()):
            if after == anchor and name in pending:
                out[name] = pending.pop(name)
                _emit(name)

    for key, value in base.items():
        out[key] = value
        _emit(key)
    if pending:
        raise ValueError(
            f"type map anchors to names that do not exist: {sorted(pending)}"
        )
    return out


def _binding_enums(type_map: dict) -> dict:
    """Enumerations this binding owns, shaped like the ontology's.

    Rendered by the same `render_enum` the ontology's go through, so the two
    are indistinguishable in the output. That is deliberate: a reader of the
    library should not have to know which vocabulary came from where.
    """
    from eaont.model import Enumeration, Member

    return {
        name: Enumeration(
            name=name,
            enforcement="binding",
            members=[
                Member(name=k, doc=" ".join(v.split()))
                for k, v in body["members"].items()
            ],
        )
        for name, body in type_map.get("enumerations", {}).items()
    }


def _extended_parameters(d, type_map: dict) -> list:
    """This definition's parameters, plus any this binding adds to it."""
    from eaont.model import Parameter

    ext = type_map.get("extends", {}).get(d.name, {})
    if not ext:
        return list(d.parameters)
    base = {p.name: p for p in d.parameters}
    additions = {
        name: Parameter(
            name=name,
            kind=spec["kind"],
            type=spec["type"],
            multiplicity=spec["multiplicity"],
        )
        for name, spec in ext.items()
    }
    anchors = {name: spec["after"] for name, spec in ext.items()}
    return list(_ordered_merge(base, additions, anchors).values())
```

Then thread the map through the two renderers and the entry point:

```python
def render_metadata_def(d, type_map) -> str:
    lines = [f"{INDENT}metadata def {d.name} {{"]
    if d.doc:
        lines.append(f"{INDENT * 2}doc /* {_doc(d.doc)} */")
    for p in _extended_parameters(d, type_map):
        keyword = "ref" if p.is_reference else "attribute"
        lines.append(
            f"{INDENT * 2}{keyword} {_identifier(p.name)}"
            f"{_multiplicity(p.multiplicity)} : {_type_name(p.type, type_map)};"
        )
    lines.append(f"{INDENT}}}")
    return "\n".join(lines) + "\n"


def render_library(m, type_map) -> str:
    """Render the library from the ontology model plus this binding's type map.

    `m` is an `eaont.model.Metamodel`, loaded by `eaont.load`. This binding's
    own loader cannot read the ontology's schema - it does not know the
    abstract reference types and refuses them as unknown - which is why the
    model arrives from `eaont` and the concrete types arrive from here.
    Asserted in tests/test_ontology_pin.py.
    """
    enums = _ordered_merge(
        m.enumerations,
        _binding_enums(type_map),
        {n: b["after"] for n, b in type_map.get("enumerations", {}).items()},
    )
    parts = [HEADER, "\npackage EpistemicAdequacy {\n"]
    parts.append(f"{INDENT}private import ScalarValues::*;\n\n")
    for enum in enums.values():
        parts.append(render_enum(enum))
        parts.append("\n")
    for d in m.metadata_definitions.values():
        parts.append(render_metadata_def(d, type_map))
        parts.append("\n")
    body = "".join(parts).rstrip("\n")
    return body + "\n}\n"
```

And correct the header, which names a file this repository will no longer have:

```python
HEADER = """// Copyright (c) 2026 Jason D. Gower.
// SPDX-License-Identifier: MIT
//
// GENERATED - DO NOT EDIT
// Rendered from the epistemic-adequacy-ontology schema at the pin recorded in
// pyproject.toml [tool.eamm], plus this repository's type-map.yaml.
// Regenerate with: eamm generate
// CI byte-compares this file against a fresh run; hand edits fail the build.
"""
```

`_ordered_merge` raising on an unknown anchor is not defensive clutter: a typo in an `after:` would otherwise drop a parameter or a vocabulary silently, and the structural test would then be comparing against a library that had quietly lost something.

- [ ] **Step 5: Regenerate and compare**

```bash
"$PY" -m eamm.cli generate      # or `eamm generate` if the console script is on PATH
"$PY" -m pytest tests/test_library_equivalence.py -v
```

Expected: PASS, 6 tests.

**If a structural test fails, read the diff before changing anything.** `git diff library/` shows exactly what moved. A missing parameter means the type map is short an extension; a missing enumeration means it is short a vocabulary; a changed type means a mapping is wrong. Do not relax the test — it is the only thing standing between this refactor and a silently different library.

- [ ] **Step 6: Parse gate and full suite**

```bash
npx sysml-validate library/ --format compact --strict
"$PY" -m pytest -q 2>&1 | tail -2
```

Expected: the parse gate clean, and `309 passed`. The parse gate covers `library/` and not `models/` — that is deliberate and pre-existing.

- [ ] **Step 7: Commit**

```bash
git add src/eamm/generate/sysml.py library/ tests/fixtures/library-before.sysml \
        tests/test_library_equivalence.py
git commit -m "feat(generate): render the library from the pinned ontology and the type map

The generator no longer reads a schema of its own. It renders eaont's model,
resolving the four abstract reference types through type-map.yaml and adding
the three parameters this binding owns.

Byte-identity was never achievable - Phase 1 rewrote doc text deliberately and
the enumeration counts differ by the three the binding supplies. The criterion
is structural: same definitions, same parameters, same types, same
multiplicities, same order. Six tests hold it."
```

---

### Task 5: Retire this repository's schema and loader

**Files:**
- Delete: `metamodel/metamodel.yaml`, `src/eamm/load.py`, `src/eamm/model.py`, `tests/test_load.py`, `tests/test_model.py`
- Modify: `src/eamm/cli.py`, and every module importing `eamm.load` or `eamm.model`

**Interfaces:**
- Consumes: `eaont.load.load_metamodel`, `eaont.model`.
- Produces: `eamm.cli.SOURCE` now points at the installed ontology's `model/ontology.yaml`.

- [ ] **Step 1: Find every consumer**

```bash
. scripts/env.sh
grep -rn "from eamm.load\|from eamm.model\|eamm\.load\|eamm\.model" src/ scripts/ tests/ --include=*.py
```

Every hit is either repointed to `eaont` or deleted. Record the list in your report — it is the blast radius, and a later reader needs it.

- [ ] **Step 2: Repoint the CLI**

`src/eamm/cli.py` currently sets `SOURCE = ROOT / "metamodel" / "metamodel.yaml"`. The schema is no longer here. Resolve it from the installed package instead:

```python
import eaont

from eaont.load import load_metamodel

ONTOLOGY_ROOT = pathlib.Path(eaont.__file__).parents[2]
SOURCE = ONTOLOGY_ROOT / "model" / "ontology.yaml"
TYPE_MAP = ROOT / "type-map.yaml"
```

and load the type map beside the model wherever `render_library` is called.

- [ ] **Step 3: Delete, and run**

```bash
git rm --quiet metamodel/metamodel.yaml src/eamm/load.py src/eamm/model.py \
               tests/test_load.py tests/test_model.py
rmdir metamodel 2>/dev/null || true
"$PY" -m pytest -q 2>&1 | tail -3
```

`tests/test_load.py` and `tests/test_model.py` go because their subject went — the same rule Phase 1 Task 1 used. **`tests/test_ontology_pin.py::test_the_two_loaders_refuse_each_other` imports `eamm.load` and must be updated in this step**, since the module it asserts against no longer exists. Replace that test with one asserting the schema is *not* present in this repository:

```python
def test_this_repository_no_longer_owns_a_schema():
    """The ontology owns it. A second copy here would be the drift the split
    exists to end."""
    assert not (ROOT / "metamodel").exists()
    assert not (ROOT / "src" / "eamm" / "load.py").exists()
```

- [ ] **Step 4: Regenerate, verify, commit**

```bash
"$PY" -m eamm.cli generate
"$PY" -m pytest tests/test_library_equivalence.py -q
"$PY" -m pytest -q 2>&1 | tail -2
git add -A
git commit -m "refactor: retire this repository's schema and loader

The ontology owns the schema; keeping a second copy here would be exactly the
drift the split exists to end. eamm.load and eamm.model are superseded by
eaont's, which is why the CLI now resolves SOURCE from the installed package."
```

---

### Task 6: The full Apollo regression, and the findings that rest on it

This is the phase's real exit criterion. Everything so far could pass while the substance moved.

**Files:**
- Modify: `docs/conformance-claim.md`, `docs/round-trip-loss.md`, `docs/annotation-burden.md` (only if their numbers changed)
- Modify: `README.md`

- [ ] **Step 1: Run everything**

```bash
. scripts/env.sh
"$PY" -m pytest -q 2>&1 | tail -3
"$PY" scripts/check_trace.py
"$PY" scripts/check_profile_claim.py
npx sysml-validate library/ --format compact --strict
"$PY" scripts/check_release.py
```

Expected: **at least 294 passed** (309 with this phase's additions), `clause trace clean: 18 clauses, pin intact, targets resolve`, `every model earns the profile it claims`, parse gate clean, release gate passed.

- [ ] **Step 2: Confirm the findings did not move**

The three findings documents carry measured numbers. The refactor changed how the library is produced, not what it says, so they must be unchanged:

```bash
git diff --stat docs/conformance-claim.md docs/annotation-burden.md docs/round-trip-loss.md
```

Expected: no changes. **If a number moved, stop and report it.** A refactor that alters a published finding is not a refactor, and `docs/conformance-claim.md` is scored against a pinned toolkit — a different number means either the instrument or the substrate changed, and this phase changed neither deliberately.

- [ ] **Step 3: Update the README's prerequisites**

The README's tier table now needs `eaont` and the pin, and its "Expected: `178 passed, 4 skipped`" numbers are stale — the tier-1 suite is 196 passed, 4 skipped, and the full suite is 309. Record the ontology dependency in the tier-1 row, and correct every count.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "test(phase-3): the Apollo regression is green against the pinned ontology

309 passed across all three tiers, up from a 294 baseline by this phase's own
additions. conformance-claim.md, annotation-burden.md and round-trip-loss.md
are byte-unchanged: the refactor changed how the library is produced, not what
it says."
```

---

### Task 7: Rename, and only now

Deliberately last. A rename is ten files and a GitHub redirect; a half-regenerated library inside a renamed repository is a state where failures cannot be attributed.

**Files:**
- Modify (this repo): `README.md`, `CITATION.cff`, `pyproject.toml`, `docs/*.md`
- Modify (other repos): `research-programme/repos.yml` + generated `data/map.json`, `epistemic-adequacy-toolkit`, `publications/README.md`, `epistemic-adequacy-under-pressure-probe` (2 files)

- [ ] **Step 1: Rename on GitHub, then the remote**

```bash
gh repo rename epistemic-adequacy-sysml-v2-binding \
  --repo systems-researcher/epistemic-adequacy-metamodel --yes
git remote set-url origin \
  https://github.com/systems-researcher/epistemic-adequacy-sysml-v2-binding.git
git remote -v
```

GitHub redirects the old URL, so nothing breaks immediately — but the redirect is a courtesy, not a contract. Update every reference.

- [ ] **Step 2: Rename the working directory**

```bash
cd .. && mv epistemic-adequacy-metamodel epistemic-adequacy-sysml-v2-binding
cd epistemic-adequacy-sysml-v2-binding && . scripts/env.sh && "$PY" -m pytest -q 2>&1 | tail -2
```

The venv holds absolute paths; if the suite fails after the move, recreate it (`"$PY" -m venv --clear .venv` then reinstall) rather than editing paths by hand.

- [ ] **Step 3: Sweep the references**

```bash
grep -rln "epistemic-adequacy-metamodel" . --include=*.md --include=*.toml --include=*.cff --include=*.yml \
  | grep -v "\.git/" | grep -v "docs/adr/" | grep -v "docs/design/"
```

`docs/adr/` and `docs/design/` are **excluded on purpose**: they are extracted decision records and the design they cite, and renaming inside them makes a historical document assert a name that did not exist when it was written. The same rule Phase 1 applied to `docs/design/`.

Then the four sibling repositories:

```bash
cd ../research-programme
grep -rln "epistemic-adequacy-metamodel" repos.yml docs/ README.md
# update repos.yml's key AND every depends_on edge naming it, together,
# or `python -m scripts.build --check` fails its own consistency check
python -m scripts.build && python -m scripts.build --check && python -m pytest -q
```

- [ ] **Step 4: Verify and commit**

```bash
cd ../epistemic-adequacy-sysml-v2-binding && . scripts/env.sh
"$PY" -m pytest -q 2>&1 | tail -2
"$PY" scripts/check_release.py
git add -A && git commit -m "chore: rename to epistemic-adequacy-sysml-v2-binding

This repository is a binding, not a metamodel - the ontology it renders lives
in epistemic-adequacy-ontology and this repo consumes it at a pin. The name has
been wrong since Phase 1 landed.

docs/adr/ and docs/design/ are deliberately not swept: they are extracted
records and the design they cite, and renaming inside one makes a historical
document assert a name that did not exist when it was written."
git push
```

---

## Phase 3 exit criteria

1. `"$PY" -m pytest -q` reports **at least 294 passed** — the pre-refactor baseline — across all three tiers.
2. `library/EpistemicAdequacy.sysml` is generated from the pinned ontology plus `type-map.yaml`, and is **structurally identical** to `tests/fixtures/library-before.sysml`: same definitions, parameters, types, multiplicities and order.
3. `npx sysml-validate library/ --strict` is clean.
4. This repository contains **no schema of its own** — no `metamodel/`, no `eamm/load.py`.
5. `docs/conformance-claim.md`, `docs/annotation-burden.md` and `docs/round-trip-loss.md` are **byte-unchanged**.
6. `scripts/check_trace.py` and `scripts/check_profile_claim.py` both pass.
7. The repository is named `epistemic-adequacy-sysml-v2-binding`, and `research-programme`'s `python -m scripts.build --check` passes with the new key.

## What this plan does not do

- **Phase 4** (spec v0.2.0: `docs/ontology.md` becomes a pointer), **Phase 5** (write-side entities, `admissibility-spec`) and **Phase 6** (programme bookkeeping beyond the rename) are separate plans.
- The toolkit pin is not moved. `docs/conformance-claim.md` is scored against `6374b67`, and rescoring against a newer instrument is a different claim requiring its own justification.
- `docs/adr/` and `docs/design/` are not swept for the rename, per Task 7 Step 3.
