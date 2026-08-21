<!--
Copyright (c) 2026 Jason D. Gower
SPDX-License-Identifier: CC-BY-4.0
-->

# Epistemic Adequacy Ontology — Phases 1 and 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up `epistemic-adequacy-ontology` as a language-agnostic repository whose entity model refuses SysML v2 types by construction, and give it a validation gate that runs SHACL over real claim-graph instances.

**Architecture:** Clone-and-strip `epistemic-adequacy-metamodel` to preserve the history of the ADRs that move, rename the package `eamm` → `eaont`, then remove every SysML v2 concern. Purification is enforced at load time: `load.py` stops accepting `KerML::`/`SysML::` prefixes and accepts four declared abstract reference types instead, so a language-specific type in `ontology.yaml` becomes a load error rather than a review finding. A minimal JSON reference binding supplies instance data, which a JSON-to-RDF lift feeds to `pyshacl` — so the shapes are judged against data a substrate emitted rather than, as today, against fixture graphs hand-built inside `tests/test_generate_shacl.py`.

**Tech Stack:** Python ≥ 3.14, PyYAML, rdflib ≥ 7.0, pyshacl ≥ 0.26, pytest ≥ 8.0. No Node, no JDK, no SysML v2 pilot — the ontology repository deliberately has none of the metamodel repository's tier-2 or tier-3 prerequisites.

**Spec:** [`2026-08-21-epistemic-adequacy-ontology-split-design.md`](2026-08-21-epistemic-adequacy-ontology-split-design.md)

**Scope:** Phases 1 and 2 of the design's §9 only. Phase 3 (rename and regenerate the SysML v2 binding), Phase 4 (spec v0.2.0), Phase 5 (write-side entities) and Phase 6 (programme bookkeeping) are separate plans. This plan produces a working, independently testable repository.

## Global Constraints

- **Python ≥ 3.14.** Inherited from the source repository's `pyproject.toml`.
- **Licences:** code and generated artefacts **MIT**; prose and design documents **CC-BY-4.0**. Every `.py` file carries `# SPDX-License-Identifier: MIT`; every `.md` carries an HTML-comment header with `SPDX-License-Identifier: CC-BY-4.0`. Turtle files carry provenance on the ontology node instead of an SPDX line — the existing release gate exempts them and that must stay true.
- **Namespace:** `https://systems-researcher.org/ns/epistemic-adequacy#`, bound to prefix `ea`. Unchanged by this plan. Changing it would invalidate every generated artefact and the shapes at once.
- **Versions:** `version: "0.1.0"`, `implements_spec: "0.1.0"` in `model/ontology.yaml`. Do not bump either in this plan.
- **All file writes use `newline="\n"`.** The repository normalises to LF; a generator writing platform newlines makes `check-drift` fail on Windows only.
- **`model/ontology.yaml` is the sole hand-edited schema artefact.** Everything under `ontology/` is generated and byte-compared. Never hand-edit a generated file.
- **No `KerML::` or `SysML::` string may appear in `model/ontology.yaml`** once Task 2 lands, and Task 2 makes this a test. The constraint is on the **schema**, not on `src/`: `load.py` must name those prefixes verbatim to refuse them.

---

### Task 1: Create the repository by clone-and-strip

**Decision recorded here, not in the design:** the repository is created by cloning `epistemic-adequacy-metamodel` and deleting what does not move, rather than by `git init` and copying. Ten of eleven ADRs move (design §6.3), and those decision records will be cited; clone-and-strip preserves their authorship history, `git init` discards it.

**Files:**
- Create: the repository `epistemic-adequacy-ontology`
- Delete: `library/`, `models/`, `java/`, `spikes/`, `vendor/`, `node_modules/`, `package.json`, `package-lock.json`, `conformance/`, `trace/clause-trace.yaml`, `src/eamm/read/`, `src/eamm/resolve/`, `src/eamm/extract/`, `src/eamm/pilot_home.py`, `src/eamm/generate/sysml.py`
- Rename: `src/eamm/` → `src/eaont/`, `metamodel/metamodel.yaml` → `model/ontology.yaml`
- Modify: `pyproject.toml`, `src/eaont/cli.py`

**Interfaces:**
- Consumes: nothing — this is the first task.
- Produces: package `eaont` importable from `src/`; console script `eaont` mapped to `eaont.cli:main`; `eaont.load.load_metamodel(path) -> Metamodel`; `eaont.cli.ROOT` as the repository root and `eaont.cli.SOURCE` as `ROOT / "model" / "ontology.yaml"`.

- [ ] **Step 1: Clone and strip**

```bash
cd ..                       # alongside the other programme repositories
git clone epistemic-adequacy-metamodel epistemic-adequacy-ontology
cd epistemic-adequacy-ontology
git remote remove origin    # a new remote is added when the repo is created on GitHub

git rm -r --quiet library models java spikes vendor conformance
git rm -r --quiet src/eamm/read src/eamm/resolve src/eamm/extract
git rm --quiet src/eamm/pilot_home.py src/eamm/generate/sysml.py
git rm --quiet trace/clause-trace.yaml package.json package-lock.json
rm -rf node_modules .pilot .venv build
git mv src/eamm src/eaont
mkdir -p model && git mv metamodel/metamodel.yaml model/ontology.yaml
rmdir metamodel
```

- [ ] **Step 1b: Delete the documents that stay with the binding**

The clone brings every finding document across, and all of them are about the
SysML v2 realisation. Per design §6.3, **ADR-010 is the one ADR that does not
move**, because usage-level claim anchoring was decided by a SysML v2 idiom.

```bash
git rm --quiet docs/adr/010-usage-level-claim-anchoring.md
git rm --quiet docs/conformance-claim.md docs/gap-register.md \
  docs/annotation-burden.md docs/round-trip-loss.md \
  docs/one-claim-five-representations.md docs/compatibility.md \
  docs/limitations.md docs/diagrams.md
git rm -r --quiet docs/plans docs/spikes docs/vocabularies

# The release gate's manifest is "49 required files, 96 headers", most of them
# just deleted. tests/test_check_release.py and tests/test_diagrams.py invoke
# it, so leaving it makes Step 6 fail for a reason that looks like a bad strip.
# Task 13's tests/test_release.py replaces its role against the new tree.
git rm --quiet scripts/check_release.py tests/test_check_release.py   tests/test_diagrams.py
```

Then remove ADR-010's row from `docs/adr/README.md` and add a line recording
where it went, so a reader following the numbering does not think it was lost:

```markdown
ADR-010 is not here. It moved to `epistemic-adequacy-sysml-v2-binding`,
because usage-level claim anchoring is a decision about how SysML v2 renders
a multiplicity, not about what the domain contains. The numbering is left
with a gap rather than renumbered: a cited ADR does not get a new number.
```

`docs/vocabularies/` is deleted because its three files (`lifecycle-stages`,
`revision-semantics`, `status-rank-order`) describe the substrate obligations
the *specification* owns. `status_rank_order` survives as data in
`model/ontology.yaml`, which is where the loader checks it.

**`docs/design/` is kept**, though it is largely about the SysML v2 realisation.
`docs/adr/README.md` cites it as the source every ADR was extracted from, and an
extracted decision record whose source has been deleted is weaker than one whose
source can be read. Add a one-line status note at its head saying it is retained
as the ADRs' cited source, describes the pre-split arrangement, and is superseded
by the split design. Do not edit its body — a cited source that has been
rewritten is no longer the source that was cited.

- [ ] **Step 2: Delete the tests that belong to the stripped modules**

The rule is mechanical: **a test goes if its subject went.** Reader, resolver,
extractor, the SysML library, the Apollo pair, the pilot, the trace and the
findings documents were all deleted above, so their tests go with them.

```bash
git rm --quiet \
  tests/test_apollo_bare.py tests/test_apollo_annotated.py \
  tests/test_apollo_source.py tests/test_apollo_delta.py \
  tests/test_plan3_prerequisites.py tests/test_trace.py \
  tests/test_gap_register.py tests/test_conformance_claim.py \
  tests/test_annotation_burden.py tests/test_round_trip_loss.py \
  tests/test_library_parses.py tests/test_generate_sysml.py \
  tests/test_cli_extract.py tests/test_extract_canonical.py \
  tests/test_extract_schema.py tests/test_extract_values.py \
  tests/test_pilot_reader.py tests/test_fetch_pilot.py \
  tests/test_read_base.py tests/test_read_model.py \
  tests/test_resolve_admissibility.py tests/test_resolve_rules.py \
  tests/test_one_claim_five_representations.py tests/test_compatibility.py \
  tests/test_task_order.py tests/test_vocabularies_agree.py \
  tests/test_plan1_complete.py
git rm -r --quiet tests/integration 2>/dev/null || true
```

If a listed path does not exist, drop it from the command and continue.

**Four survive, and they are the core suite:** `test_load.py`, `test_model.py`,
`test_generate_owl.py`, `test_generate_shacl.py` and `test_prov_alignment.py`. Do
not delete these. `tests/__init__.py` stays.

`test_vocabularies_agree.py`, `test_task_order.py`, `test_plan1_complete.py` and
`test_compatibility.py` are deleted because each asserts against a document or a
plan that Step 1b removes — they are gates on the binding's contents, not the
ontology's.

- [ ] **Step 3: Rewrite the package name across the tree**

```bash
grep -rl '\beamm\b' src tests pyproject.toml docs scripts 2>/dev/null \
  | xargs sed -i 's/\beamm\b/eaont/g'
```

The package rename is not the only path that moved. Nine test files hardcode the
schema's location, including `test_generate_owl.py`, `test_generate_shacl.py`,
`test_prov_alignment.py` and `test_load.py` — the four Step 2 forbids deleting.
Rewrite the path too, or Step 6 fails with `FileNotFoundError`:

```bash
grep -rl 'metamodel/metamodel.yaml' src tests scripts 2>/dev/null \
  | xargs sed -i 's|metamodel/metamodel\.yaml|model/ontology.yaml|g'
grep -rn 'metamodel' src tests || echo "no stale schema path"
```

- [ ] **Step 4: Point the CLI at the new source path and drop the SysML target**

In `src/eaont/cli.py`, replace the **`eaont`-package imports** and `TARGETS`
with the following. The stdlib imports at the top of the file — `argparse`,
`pathlib`, `sys` — all stay; `check_drift` and `main` need them.

```python
from eaont.generate.owl import render_ontology, render_prov_alignment
from eaont.generate.shacl import render_shapes
from eaont.load import load_metamodel

ROOT = pathlib.Path(__file__).parents[2]
SOURCE = ROOT / "model" / "ontology.yaml"

# path -> renderer. `extract` and the SysML library target moved to the binding.
TARGETS = {
    ROOT / "ontology" / "epistemic-adequacy.ttl": render_ontology,
    ROOT / "ontology" / "shapes.ttl": render_shapes,
    ROOT / "ontology" / "prov-alignment.ttl": render_prov_alignment,
}
```

Delete the `extract`, `_resolved_revision`, `_select_reader` functions and the `ReaderUnavailable` class entirely, and delete the `from eaont.read.model import ModelGraph` import. In `main()`, delete the `extract_p` subparser block and the `if args.command == "extract":` branch.

- [ ] **Step 5: Update `pyproject.toml`**

Change **only** these keys. Step 3's `sed` has already rewritten `eamm` to
`eaont` throughout, so `name` and the script target may already be correct;
`version`, `requires-python`, `[build-system]` and the rest stay as they are.

```toml
[project]
name = "eaont"
dependencies = ["pyyaml>=6.0", "rdflib>=7.0", "pyshacl>=0.26"]

[project.scripts]
eaont = "eaont.cli:main"
```

`pyshacl` stays declared and becomes genuinely used in Task 9.

- [ ] **Step 6: Install and run the surviving suite**

Run: `pip install -e ".[test]" && pytest -q`
Expected: PASS, five test files. Every remaining test concerns the loader, the
model, or a generator.

If a test fails with `ImportError` **or** `FileNotFoundError` **or** an assertion
naming a deleted path, it belonged to the stripped half and Step 2's list missed
it — delete it and record which one in the commit message, so the list can be
corrected for anyone repeating this. Do not repair such a test.

- [ ] **Step 7: Verify the CLI works and produces no drift**

Run: `eaont check-drift`
Expected: `no drift across 3 generated artefacts`

The count is 3, not 4: the SysML library target is gone.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "chore: strip to ontology concerns, rename eamm to eaont

Clone-and-strip rather than a fresh init, so the ten ADRs that move keep
their authorship history. They will be cited."
```

---

### Task 2: Refuse SysML and KerML types at load time

This is the purification gate. Making it a load error rather than a review convention is what keeps the ontology agnostic under future edits.

**Files:**
- Modify: `src/eaont/load.py`
- Modify: `model/ontology.yaml`
- Test: `tests/test_load_abstract_refs.py`

**Interfaces:**
- Consumes: `eaont.load.load_text(src) -> Metamodel`, `eaont.load.MetamodelError` from Task 1.
- Produces: module constant `eaont.load.ABSTRACT_REFS = {"ElementRef", "ExpressionRef", "PredicateRef", "VocabularyRef"}`. Later tasks and every binding rely on these four names exactly.

- [ ] **Step 1: Write the failing test**

Create `tests/test_load_abstract_refs.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""The loader is the agnosticism gate: a language type must not load."""

import pytest

from eaont.load import ABSTRACT_REFS, MetamodelError, load_text

BASE = """
version: "0.1.0"
implements_spec: "0.1.0"
enumerations: {}
metadata_definitions:
  Derivation:
    level: claim
    clauses: [EA-REQ-02]
    doc: test fixture
    parameters:
      - {name: upstream, kind: ref, type: %s, multiplicity: "*"}
"""


def test_kerml_type_is_refused():
    with pytest.raises(MetamodelError) as exc:
        load_text(BASE % "KerML::Element")
    assert "KerML::Element" in str(exc.value)


def test_sysml_type_is_refused():
    with pytest.raises(MetamodelError) as exc:
        load_text(BASE % "SysML::EnumerationDefinition")
    assert "SysML::EnumerationDefinition" in str(exc.value)


def test_abstract_ref_is_accepted():
    m = load_text(BASE % "ElementRef")
    assert m.metadata_definitions["Derivation"].parameters[0].type == "ElementRef"


@pytest.mark.parametrize("name", sorted(ABSTRACT_REFS))
def test_every_abstract_ref_loads(name):
    m = load_text(BASE % name)
    assert m.metadata_definitions["Derivation"].parameters[0].type == name


def test_abstract_refs_are_exactly_four():
    assert ABSTRACT_REFS == {
        "ElementRef", "ExpressionRef", "PredicateRef", "VocabularyRef"
    }
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_load_abstract_refs.py -v`
Expected: FAIL with `ImportError: cannot import name 'ABSTRACT_REFS'`

- [ ] **Step 3: Implement the gate**

In `src/eaont/load.py`, replace the `EXTERNAL_PREFIXES` constant:

```python
# Types a parameter may name without the metamodel declaring them.
PRIMITIVES = {"String", "Boolean", "Integer", "Real"}

# Abstract reference types. A binding maps each to a concrete type in its own
# type map; the ontology never names one. These four are the whole of the
# binding contract's type surface — see docs/binding-contract.md.
ABSTRACT_REFS = {"ElementRef", "ExpressionRef", "PredicateRef", "VocabularyRef"}

# Prefixes that must never appear. This is the agnosticism gate: the ontology
# is language-independent because a language type cannot be loaded, not
# because reviewers remember to object.
REFUSED_PREFIXES = ("KerML::", "SysML::", "UML::", "OWL::")
```

Then rewrite `_check_types`:

```python
def _check_types(defs: dict, enums: dict) -> None:
    known = set(PRIMITIVES) | set(ABSTRACT_REFS) | set(enums) | set(defs)
    for d in defs.values():
        for p in d.parameters:
            if p.type.startswith(REFUSED_PREFIXES):
                raise MetamodelError(
                    f"{d.name}.{p.name} names the language type {p.type!r}. "
                    f"The ontology is language-independent; use one of "
                    f"{sorted(ABSTRACT_REFS)} and map it in the binding's "
                    f"type map."
                )
            if p.type in known:
                continue
            raise MetamodelError(
                f"{d.name}.{p.name} names an unknown type {p.type!r}"
            )
```

The refusal check runs **before** the membership check, so a language type gets the explanatory message rather than a bare "unknown type".

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_load_abstract_refs.py -v`
Expected: PASS, 8 tests — three unparametrised, one parametrised over the four
members of `ABSTRACT_REFS`, and the exactly-four assertion.

- [ ] **Step 5: Rewrite the seven typed parameters in `model/ontology.yaml`**

These seven, and only these seven (design §3.2):

| Definition | Parameter | Was | Becomes |
|---|---|---|---|
| `Derivation` | `upstream` | `KerML::Element` | `ElementRef` |
| `Derivation` | `alternatives` | `KerML::Element` | `ElementRef` |
| `Derivation` | `expression` | `KerML::Function` | `ExpressionRef` |
| `ConflictCheck` | `subject` | `KerML::Element` | `ElementRef` |
| `ConflictCheck` | `competing` | `KerML::Element` | `ElementRef` |
| `ConflictCheck` | `constraint` | `KerML::Predicate` | `PredicateRef` |
| `SubstrateDeclaration` | `statusVocabulary` | `SysML::EnumerationDefinition` | `VocabularyRef` |

```bash
sed -i 's/type: "KerML::Element"/type: ElementRef/;
        s/type: "KerML::Function"/type: ExpressionRef/;
        s/type: "KerML::Predicate"/type: PredicateRef/;
        s/type: "SysML::EnumerationDefinition"/type: VocabularyRef/' model/ontology.yaml
```

- [ ] **Step 5b: Update the generator comment that names the old prefixes**

`src/eaont/generate/owl.py` carries this comment at the end of
`_add_metadata_def`, and it will be false the moment Step 5 lands:

```python
        # External SysML/KerML metaclasses have no OWL range; the SysML layer
        # types them and the resolver enforces admissibility (design §3.9).
```

Replace it with:

```python
        # Abstract reference types have no OWL range: the ontology names what
        # a reference IS, and a binding's type map says what carries it. This
        # is a fall-through, not a special case - ElementRef reaches here by
        # matching none of the three branches above, exactly as KerML::Element
        # did, which is why abstracting the types changes no triple.
```

Do the same for any equivalent comment in `generate/shacl.py`. This is
documentation of the fall-through the whole of §9.1 rests on; leaving it
naming SysML would make the one load-bearing claim look like a special case.

- [ ] **Step 6: Verify no language type survives in the schema**

Run: `grep -rn "KerML::\|SysML::" model/ && echo FOUND || echo CLEAN`
Expected: `CLEAN`

**The scope is `model/`, not `src/`, and that is not a loophole.** `load.py` must
name `KerML::` and `SysML::` verbatim in `REFUSED_PREFIXES` in order to refuse
them, and Step 5b's comment explains the fall-through by naming them. A grep over
`src/` would fail on the gate's own implementation. What must contain no language
type is the **schema**, and `model/ontology.yaml` is the whole of it.

- [ ] **Step 6b: Update the provenance string the generators emit**

Both generators write `"Generated from metamodel/metamodel.yaml. Do not edit."`
into every artefact, and that path no longer exists. Left alone, all three
generated files cite a file the repository does not have.

```bash
grep -rn "metamodel/metamodel.yaml" src/eaont/generate/
sed -i 's|metamodel/metamodel\.yaml|model/ontology.yaml|g' src/eaont/generate/*.py
```

This changes the generated output, so it must happen **before** Step 7's
byte-compare — otherwise Step 7 reports drift that is this edit rather than the
type abstraction, and the §9.1 claim it exists to test is obscured. Regenerate
once after this edit, then run Step 7 against the result.

- [ ] **Step 7: Verify the generated ontology is byte-identical**

Run: `eaont check-drift`
Expected: `no drift across 3 generated artefacts`

**This is the design's §9.1 claim under test**, and Step 6b's provenance edit is
the one authorised difference — regenerate after 6b, then compare. Beyond that,
the generator emits no `rdfs:range` for any of the seven, so renaming their types
must change zero triples. If drift is reported here, §9.1 is wrong and the
discrepancy must be understood before continuing — do not regenerate to make it
green.

- [ ] **Step 8: Commit**

```bash
git add src/eaont/load.py model/ontology.yaml tests/test_load_abstract_refs.py
git commit -m "feat(load): refuse language types, accept four abstract refs

Abstracting the seven typed parameters changes zero triples, because the
generator already emitted no rdfs:range for any of them. check-drift is
the proof."
```

---

### Task 3: Move `RevisionSchemeKind` out to the binding

**Files:**
- Modify: `model/ontology.yaml`
- Test: `tests/test_no_binding_concerns.py`

**Interfaces:**
- Consumes: `eaont.load.load_metamodel`, `eaont.cli.SOURCE` from Task 1.
- Produces: nothing new. `SubstrateDeclaration` loses its `revisionScheme` parameter.

- [ ] **Step 1: Write the failing test**

Create `tests/test_no_binding_concerns.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""Binding concerns must not live in the ontology.

RevisionSchemeKind's member `apiCommit` is documented as "A SysML v2 API
service commit identity". A revision scheme is how a substrate names a
version of itself, which is a binding's business.
"""

from eaont.cli import SOURCE
from eaont.load import load_metamodel

M = load_metamodel(SOURCE)


def test_revision_scheme_kind_is_absent():
    assert "RevisionSchemeKind" not in M.enumerations


def test_substrate_declaration_has_no_revision_scheme():
    params = {p.name for p in M.metadata_definitions["SubstrateDeclaration"].parameters}
    assert "revisionScheme" not in params


def test_default_revision_scheme_is_absent():
    assert "default_revision_scheme" not in M.vocabularies


def test_no_api_commit_anywhere():
    text = SOURCE.read_text(encoding="utf-8")
    assert "apiCommit" not in text
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_no_binding_concerns.py -v`
Expected: FAIL — all four tests fail; the enumeration, the parameter, the default and the string are all present.

- [ ] **Step 3: Remove them from `model/ontology.yaml`**

Delete the whole `RevisionSchemeKind:` block from `enumerations:`. Delete this line from `SubstrateDeclaration.parameters`:

```yaml
      - {name: revisionScheme, kind: attribute, type: RevisionSchemeKind, multiplicity: "1"}
```

Delete these two lines from `vocabularies:`:

```yaml
  # EA-REQ-13. Design §3.8.
  default_revision_scheme: gitCommit
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_no_binding_concerns.py -v`
Expected: PASS, 4 tests.

- [ ] **Step 5: Regenerate and inspect the diff**

```bash
eaont generate
git diff --stat ontology/
git diff ontology/epistemic-adequacy.ttl | grep '^-' | grep -c 'RevisionSchemeKind\|revisionScheme'
```

Expected: only `ontology/` files changed, and the removed triples all mention `RevisionSchemeKind` or `revisionScheme`. Nothing else may disappear.

- [ ] **Step 6: Commit**

```bash
git add model/ontology.yaml ontology/ tests/test_no_binding_concerns.py
git commit -m "refactor: move RevisionSchemeKind to the binding

apiCommit is a SysML v2 API service commit identity. It was never ontology."
```

---

### Task 4: Settle `ProfileKind` and `CriticalityPolicyKind`

Design §12.1 leaves this open on purpose: both look like duplicates of what the specification already owns, and the design refuses to assume it. This task decides by inspection and then acts.

**Files:**
- Read: `../epistemic-adequacy-spec/conformance/profiles.md`, `../epistemic-adequacy-spec/conformance/clauses.yaml`
- Modify: `model/ontology.yaml` (conditionally)
- Create: `docs/adr/012-profiles-are-not-ontology.md` (conditionally)
- Test: `tests/test_no_binding_concerns.py` (extend)

**Interfaces:**
- Consumes: `eaont.load.load_metamodel`, `eaont.cli.SOURCE`.
- Produces: nothing new.

- [ ] **Step 1: Gather the evidence**

```bash
cd ../epistemic-adequacy-spec
python -c "
import yaml
d = yaml.safe_load(open('conformance/clauses.yaml'))
cl = d['clauses'] if isinstance(d, dict) and 'clauses' in d else d
for c in cl:
    print(c['id'], c['strength'])
"
grep -n 'Minimal\|Governed\|Safety' conformance/profiles.md | head -30
cd ../epistemic-adequacy-ontology
```

- [ ] **Step 2: Apply the decision rule**

**`ProfileKind` is a duplicate if** `clauses.yaml`'s per-clause `strength` map already yields the three profile memberships that `ProfileKind`'s member docs list. Its `minimal` doc reads `EA-REQ-01, 02, 03, 05, 06`; check that this equals the set of clauses whose `strength.minimal` is `must`.

**`CriticalityPolicyKind` is a duplicate if** its two members correspond exactly to `EA-REQ-10`'s `strength.governed` and `strength.safety_critical` values — that is, if `declaredPerClaim` says nothing the `governed` strength does not already say, and `allCritical` says nothing the `safety_critical` strength does not already say.

Record the answer for each in the commit message. **If a duplicate, go to Step 3. If not a duplicate, go to Step 4.** Both branches are written out; do not improvise a third.

- [ ] **Step 3 (duplicate branch): Delete, and record why**

Delete the `ProfileKind` and/or `CriticalityPolicyKind` blocks from `enumerations:`, and the parameters that reference them from `SubstrateDeclaration`:

```yaml
      - {name: criticalityPolicy, kind: attribute, type: CriticalityPolicyKind, multiplicity: "1"}
      - {name: profileClaimed, kind: attribute, type: ProfileKind, multiplicity: "1"}
```

Extend `tests/test_no_binding_concerns.py`:

```python
def test_profile_kind_is_absent():
    """Conformance packaging belongs to the specification, not the ontology.

    clauses.yaml's per-clause strength map already determines profile
    membership. A second copy here is the drift this repository exists to end.
    """
    assert "ProfileKind" not in M.enumerations
    params = {p.name for p in M.metadata_definitions["SubstrateDeclaration"].parameters}
    assert "profileClaimed" not in params


def test_criticality_policy_kind_is_absent():
    assert "CriticalityPolicyKind" not in M.enumerations
    params = {p.name for p in M.metadata_definitions["SubstrateDeclaration"].parameters}
    assert "criticalityPolicy" not in params
```

Create `docs/adr/012-profiles-are-not-ontology.md`:

```markdown
<!--
Copyright (c) 2026 Jason D. Gower.
SPDX-License-Identifier: CC-BY-4.0
-->

# ADR-012 — Conformance profiles are not ontology

**Status:** accepted · **Source:** split design §6.1, §12.1

## Context

`metamodel.yaml` carried `ProfileKind` and `CriticalityPolicyKind`. Both
restate what `epistemic-adequacy-spec` already owns: `conformance/profiles.md`
in prose, and `clauses.yaml`'s per-clause `strength` map in machine-readable
form.

## Decision

Both are deleted, not relocated. A profile is a packaging of clause strengths,
which is a specification concern; the ontology says what exists, not which
subset of obligations a substrate elects.

## Consequences

`SubstrateDeclaration` loses `profileClaimed` and `criticalityPolicy`. A
substrate still declares a claimed profile — but it does so in the binding,
against the specification's vocabulary, with no second definition here.

Deleting rather than moving is the point. A relocated copy is still a copy,
and a second copy of a vocabulary is exactly the failure this repository was
created to end.

## Alternatives

**Relocate to the specification.** Rejected: `clauses.yaml` already carries the
information, so relocation would create the duplicate it was meant to avoid.
```

- [ ] **Step 4 (not-duplicate branch): Keep, and record why**

If Step 2 shows either enumeration says something the specification does not, keep it and add a `doc:` line to the enumeration recording what it adds that `clauses.yaml` does not. Then extend `tests/test_no_binding_concerns.py` with a test asserting the enumeration is present and its `doc` is non-empty, so the justification cannot later be silently deleted:

```python
def test_kept_conformance_enum_justifies_itself():
    """If it stays, it must say what it adds that clauses.yaml does not."""
    import re
    for name in ("ProfileKind", "CriticalityPolicyKind"):
        enum = M.enumerations.get(name)
        if enum is None:
            continue
        text = SOURCE.read_text(encoding="utf-8")
        block = text.split(f"\n  {name}:", 1)[1].split("\n\n", 1)[0]
        # Enumeration-level doc only. Every MEMBER carries a `doc:`, so a bare
        # `"doc:" in block` passes whether or not a justification was written -
        # a test that cannot fail is not a test.
        assert re.search(r"^    doc:", block, re.M), (
            f"{name} was kept but records no enumeration-level justification"
        )
```

- [ ] **Step 5: Run the tests**

Run: `pytest tests/test_no_binding_concerns.py -v`
Expected: PASS.

- [ ] **Step 6: Regenerate and commit**

```bash
eaont generate
git add -A
git commit -m "refactor: settle ProfileKind and CriticalityPolicyKind

<record here which branch was taken and the evidence from Step 1>"
```

---

### Task 5: Lock the Phase 1 diff

Design §9.1 states exactly what may change in the generated ontology during Phase 1. This task makes that a test, so a later edit cannot quietly add or drop a class.

**Files:**
- Create: `tests/test_phase1_diff.py`
- Create: `tests/fixtures/pre-split-classes.txt`

**Interfaces:**
- Consumes: `ontology/epistemic-adequacy.ttl` as generated by Tasks 2–4.
- Produces: `tests/fixtures/pre-split-classes.txt`, the baseline class list later plans compare against.

- [ ] **Step 1: Capture the pre-split baseline from the source repository**

```bash
mkdir -p tests/fixtures
BASE=../epistemic-adequacy-metamodel/ontology/epistemic-adequacy.ttl
grep -E "^ea:[A-Za-z]+ a owl:Class" "$BASE" \
  | sed 's/ a owl:Class.*//' | sort > tests/fixtures/pre-split-classes.txt
grep -E "^ea:[A-Za-z]+_[A-Za-z]+ a owl:" "$BASE" \
  | sed 's/ a owl:.*//' | sort -u > tests/fixtures/pre-split-properties.txt
wc -l tests/fixtures/pre-split-classes.txt tests/fixtures/pre-split-properties.txt
```

Expected: 25 classes — 13 metadata-definition classes and 12 enumeration classes
— and one line per generated property. Both baselines are needed: a class-only
comparison cannot see a property dropped from a class that survives.

- [ ] **Step 2: Write the failing test**

Create `tests/test_phase1_diff.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""The generated ontology differs from the pre-split baseline by exactly the
removals design §9.1 authorises, and by nothing else.

Abstracting the seven typed parameters is OWL-neutral, so it contributes no
difference at all. Anything unexpected here is a defect in the move.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).parents[1]
BASELINE = ROOT / "tests" / "fixtures" / "pre-split-classes.txt"
GENERATED = ROOT / "ontology" / "epistemic-adequacy.ttl"

# Set by Task 3, and by Task 4 if it took the duplicate branch.
AUTHORISED_REMOVALS = {"ea:RevisionSchemeKind", "ea:ProfileKind",
                       "ea:CriticalityPolicyKind"}

# The SubstrateDeclaration parameters whose types left with them (§9.1).
AUTHORISED_PROPERTIES = {"ea:SubstrateDeclaration_revisionScheme",
                         "ea:SubstrateDeclaration_profileClaimed",
                         "ea:SubstrateDeclaration_criticalityPolicy"}


def _classes(text: str) -> set[str]:
    return set(re.findall(r"^(ea:[A-Za-z]+) a owl:Class", text, re.MULTILINE))


def _properties(text: str) -> set[str]:
    return set(re.findall(r"^(ea:\w+_\w+) a owl:", text, re.MULTILINE))


def test_no_property_was_added_or_silently_dropped():
    """Classes alone are too coarse. §9.1 authorises property removals too,
    and a property quietly lost would not move the class count at all."""
    before = set((ROOT / "tests" / "fixtures" / "pre-split-properties.txt")
                 .read_text(encoding="utf-8").split())
    after = _properties(GENERATED.read_text(encoding="utf-8"))
    assert after - before == set(), f"unexpected new properties: {after - before}"
    removed = before - after
    assert removed <= AUTHORISED_PROPERTIES, (
        f"unauthorised property removals: {removed - AUTHORISED_PROPERTIES}"
    )


def test_no_class_was_added():
    before = set(BASELINE.read_text(encoding="utf-8").split())
    after = _classes(GENERATED.read_text(encoding="utf-8"))
    assert after - before == set(), f"unexpected new classes: {after - before}"


def test_every_removal_was_authorised():
    before = set(BASELINE.read_text(encoding="utf-8").split())
    after = _classes(GENERATED.read_text(encoding="utf-8"))
    removed = before - after
    assert removed <= AUTHORISED_REMOVALS, (
        f"unauthorised removals: {removed - AUTHORISED_REMOVALS}"
    )


def test_the_nine_domain_entities_survive():
    """Design §4.1. These carry domain warrant and must never be dropped."""
    after = _classes(GENERATED.read_text(encoding="utf-8"))
    for name in ("Agent", "Method", "Provenance", "EpistemicStatus",
                 "EvidenceAnchor", "Derivation", "Criticality",
                 "StandingChange", "Entry"):
        assert f"ea:{name}" in after, f"{name} was lost"


def test_the_four_service_entities_survive():
    """Design §4.1. Marked, not removed - the clauses still need them."""
    after = _classes(GENERATED.read_text(encoding="utf-8"))
    for name in ("GovernedClaim", "SubstrateDeclaration", "Unresolved",
                 "ConflictCheck"):
        assert f"ea:{name}" in after, f"{name} was lost"
```

- [ ] **Step 3: Run the tests**

Run: `pytest tests/test_phase1_diff.py -v`
Expected: PASS, 4 tests. If Task 4 took the not-duplicate branch, `AUTHORISED_REMOVALS` is a superset of what was actually removed, which `<=` permits.

- [ ] **Step 4: Commit**

```bash
git add tests/test_phase1_diff.py tests/fixtures/pre-split-classes.txt
git commit -m "test: lock the Phase 1 diff to the authorised removals"
```

---

### Task 6: Split `UnresolvedFieldKind`'s clause consequences into the trace

Every member's `doc` currently states a clause outcome — "Fails EA-REQ-10", "Satisfies EA-REQ-01". Those consequences belong to the specification. The enumeration stays; the consequence prose moves.

**Files:**
- Modify: `model/ontology.yaml`
- Create: `trace/spec-trace.yaml`
- Test: `tests/test_spec_trace.py`

**Interfaces:**
- Consumes: `eaont.load.load_metamodel`, `eaont.cli.SOURCE`.
- Produces: `trace/spec-trace.yaml` with top-level keys `entities` and `unresolved_fields`. Task 7 reads `entities`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_spec_trace.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""Clause consequences live in the trace, not in entity documentation."""

import pathlib

import yaml

from eaont.cli import SOURCE
from eaont.load import load_metamodel

ROOT = pathlib.Path(__file__).parents[1]
TRACE = yaml.safe_load((ROOT / "trace" / "spec-trace.yaml").read_text(encoding="utf-8"))
M = load_metamodel(SOURCE)


# If Task 4 took the keep branch, these two remain and their members ARE clause
# lists - that is what a conformance profile is. Exempting them is not a loophole:
# the rule is that a DOMAIN entity's doc must not state a clause consequence, and
# a profile is not a domain entity.
CONFORMANCE_ENUMS = {"ProfileKind", "CriticalityPolicyKind"}


def test_no_member_doc_names_a_clause():
    """A doc says what the member IS. What it costs is the spec's business."""
    for enum in M.enumerations.values():
        if enum.name in CONFORMANCE_ENUMS:
            continue
        for member in enum.members:
            assert "EA-REQ-" not in member.doc, (
                f"{enum.name}::{member.name} states a clause consequence"
            )


def test_every_unresolved_field_has_a_consequence():
    members = {m.name for m in M.enumerations["UnresolvedFieldKind"].members}
    assert set(TRACE["unresolved_fields"]) == members


def test_each_consequence_names_at_least_one_clause():
    for field, entry in TRACE["unresolved_fields"].items():
        assert entry["clauses"], f"{field} names no clause"
        for clause in entry["clauses"]:
            assert clause.startswith("EA-REQ-"), f"{field}: {clause!r}"
        assert entry["effect"] in {"satisfies", "fails", "raises", "excludes"}
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_spec_trace.py -v`
Expected: FAIL with `FileNotFoundError` on `trace/spec-trace.yaml`.

- [ ] **Step 3: Create the trace**

Create `trace/spec-trace.yaml`, carrying the consequences currently in the member docs verbatim in meaning:

```yaml
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: CC-BY-4.0
#
# Clause consequences. The ontology says what an entity is; this file says what
# the specification makes of it. Split out of model/ontology.yaml so that a
# member's doc describes the member rather than its cost.

unresolved_fields:
  basis:
    clauses: [EA-REQ-01, EA-REQ-14]
    effect: satisfies
    note: Satisfies EA-REQ-01 and removes basis as an EA-REQ-14 failure.
  derivation:
    clauses: [EA-REQ-02, EA-REQ-12, EA-REQ-14]
    effect: satisfies
    note: Satisfies EA-REQ-02 and EA-REQ-12, and removes derivation as an EA-REQ-14 failure.
  alternatives:
    clauses: [EA-REQ-04]
    effect: satisfies
    note: Satisfies EA-REQ-04.
  evidence:
    clauses: [EA-REQ-10]
    effect: fails
    note: Declaring evidence unreachable is not evidence.
  status:
    clauses: [EA-REQ-05, EA-REQ-14]
    effect: fails
    note: Fails EA-REQ-05; removes status as an EA-REQ-14 failure.
  criticality:
    clauses: [EA-REQ-10]
    effect: raises
    note: Raises EA-REQ-10 to MUST for the claim.
  provenance:
    clauses: [EA-REQ-08, EA-REQ-09, EA-REQ-14]
    effect: fails
    note: >-
      Fails EA-REQ-08 and EA-REQ-09, but removes provenance as an EA-REQ-14
      failure: a marker is a verdict where absence is silence.
  entry:
    clauses: [EA-REQ-16, EA-REQ-17, EA-REQ-18]
    effect: excludes
    note: >-
      Fails EA-REQ-16 alone. EA-REQ-17 and 18 exclude the claim from their
      populations, so they return not_applicable.

entities: {}   # populated by Task 7
```

- [ ] **Step 4: Rewrite the member docs in `model/ontology.yaml`**

Each `UnresolvedFieldKind` member's `doc` becomes a description of the marker, with no clause named. For example:

```yaml
      - name: evidence
        doc: >-
          A declared gap where a retrievable source for the claim would sit.
      - name: criticality
        doc: >-
          A declared gap where the claim's safety classification would sit.
      - name: entry
        doc: >-
          A declared gap where the record of how the claim entered the
          authoritative record would sit.
```

Apply the same treatment to `basis`, `derivation`, `alternatives`, `status` and `provenance`. Then sweep every other enumeration for a member doc containing `EA-REQ-` and rewrite it the same way — the test checks all of them, not just this one.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/test_spec_trace.py -v`
Expected: PASS, 3 tests.

The loader's duplicate-doc rule (`ea_req_06` requires pairwise-distinct definitions) still applies. If two rewritten docs collide, `load_text` raises `MetamodelError` — reword rather than weakening the rule.

- [ ] **Step 6: Regenerate, verify, commit**

```bash
eaont generate
pytest -q
git add model/ontology.yaml ontology/ trace/spec-trace.yaml tests/test_spec_trace.py
git commit -m "refactor: move clause consequences out of entity docs into the trace

A doc says what a member is. What it costs a substrate is the spec's business."
```

---

### Task 7: Mark every entity — domain warrant or decidability service

Design §4.1. This is the ontology's contribution, and the test is what keeps it honest as entities are added.

**Files:**
- Create: `docs/warrant.md`
- Modify: `trace/spec-trace.yaml`
- Test: `tests/test_warrant.py`

**Interfaces:**
- Consumes: `trace/spec-trace.yaml` key `entities` from Task 6.
- Produces: each entry under `entities` has keys `warrant` (`domain` or `decidability`), `serves` (list of clause ids, empty for `domain`), and `adr` (string or null).

- [ ] **Step 1: Write the failing test**

Create `tests/test_warrant.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""Design §4.1: every entity declares its warrant, and no entity escapes.

Nine carry domain warrant. Four exist so a clause is checkable and must name
the clause. An unmarked entity is the failure mode this file prevents.
"""

import pathlib

import yaml

from eaont.cli import SOURCE
from eaont.load import load_metamodel

ROOT = pathlib.Path(__file__).parents[1]
TRACE = yaml.safe_load((ROOT / "trace" / "spec-trace.yaml").read_text(encoding="utf-8"))
ENTITIES = TRACE["entities"]
M = load_metamodel(SOURCE)

DOMAIN = {"Agent", "Method", "Provenance", "EpistemicStatus", "EvidenceAnchor",
          "Derivation", "Criticality", "StandingChange", "Entry"}
DECIDABILITY = {"GovernedClaim", "SubstrateDeclaration", "Unresolved",
                "ConflictCheck"}


def test_every_entity_is_marked():
    assert set(ENTITIES) == set(M.metadata_definitions)


def test_the_split_is_nine_and_four():
    domain = {n for n, e in ENTITIES.items() if e["warrant"] == "domain"}
    decidability = {n for n, e in ENTITIES.items() if e["warrant"] == "decidability"}
    assert domain == DOMAIN
    assert decidability == DECIDABILITY


def test_no_third_category():
    for name, entry in ENTITIES.items():
        assert entry["warrant"] in {"domain", "decidability"}, name


def test_every_service_entity_names_its_clause():
    for name, entry in ENTITIES.items():
        if entry["warrant"] == "decidability":
            assert entry["serves"], f"{name} claims decidability service but names no clause"


def test_domain_entities_serve_nothing():
    """A domain entity is argued on its own terms. If it needs a clause to
    justify it, it is a decidability-service entity wearing the wrong label."""
    for name, entry in ENTITIES.items():
        if entry["warrant"] == "domain":
            assert not entry["serves"], f"{name} is marked domain but names a clause"


def test_warrant_doc_mentions_every_entity():
    text = (ROOT / "docs" / "warrant.md").read_text(encoding="utf-8")
    for name in ENTITIES:
        assert name in text, f"{name} is unmentioned in docs/warrant.md"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_warrant.py -v`
Expected: FAIL — `test_every_entity_is_marked` fails because `entities` is `{}`.

- [ ] **Step 3: Populate `entities` in `trace/spec-trace.yaml`**

Replace `entities: {}` with:

```yaml
entities:
  Agent:                {warrant: domain,       serves: [], adr: ADR-001}
  Method:               {warrant: domain,       serves: [], adr: null}
  Provenance:           {warrant: domain,       serves: [], adr: null}
  EpistemicStatus:      {warrant: domain,       serves: [], adr: ADR-005}
  EvidenceAnchor:       {warrant: domain,       serves: [], adr: ADR-004}
  Derivation:           {warrant: domain,       serves: [], adr: null}
  Criticality:          {warrant: domain,       serves: [], adr: ADR-003}
  StandingChange:       {warrant: domain,       serves: [], adr: ADR-009}
  Entry:                {warrant: domain,       serves: [], adr: ADR-002}
  GovernedClaim:        {warrant: decidability, serves: [EA-REQ-13], adr: ADR-008}
  SubstrateDeclaration: {warrant: decidability,
                         serves: [EA-REQ-05, EA-REQ-06, EA-REQ-09, EA-REQ-11, EA-REQ-13],
                         adr: ADR-007}
  Unresolved:           {warrant: decidability, serves: [EA-REQ-12], adr: null}
  ConflictCheck:        {warrant: decidability, serves: [EA-REQ-15], adr: null}
```

- [ ] **Step 4: Write `docs/warrant.md`**

Create `docs/warrant.md` with the CC-BY-4.0 header — `tests/test_release.py`
(Task 13) requires one on every file under `docs/`, and every document this plan
creates must carry it. Then:

```markdown
# Warrant: what the domain requires, and what decidability adds

Thirteen entities. Nine are argued on their own terms — remove the eighteen
clauses and they still describe how an engineering record carries what is
known about a value. Four exist because a clause would otherwise be
uncheckable, and each names the clause it serves.

The distinction is the result, not the bookkeeping. *What must a record hold
to describe its own basis* and *what must it additionally hold for a machine
to decide groundedness* are different questions, and only the second is new.

## Domain warrant

| Entity | Why it exists independently | Record |
|---|---|---|
| `Agent` | A claim has a party responsible for it. PROV-O aligned; delegation is `onBehalfOf`, not an agent kind | ADR-001 |
| `Method` | A value is produced by some means, and the means is a thing, not a string | — |
| `Provenance` | Agent and method together, as typed references | — |
| `EpistemicStatus` | A value has a standing, and separately a currency: a superseded verification is still a verification | ADR-005 |
| `EvidenceAnchor` | A claim points at a retrievable source. Access status is excluded: it is a fact about a past check | ADR-004 |
| `Derivation` | A value comes from somewhere — inputs, evidence, alternatives, an expression | — |
| `Criticality` | Whether a claim carries safety consequence, and on what stated basis | ADR-003 |
| `StandingChange` | Standing changes, and the change has an author and a reason | ADR-009 |
| `Entry` | How a value entered the record, and what review it has had | ADR-002 |

## Decidability service

These four are not claims about the domain. They exist so that a clause has a
decidable subject or a determinate answer, and each is listed with the clause
that requires it.

| Entity | Serves | Why the clause cannot be checked without it | Record |
|---|---|---|---|
| `GovernedClaim` | EA-REQ-13 | Without an explicit marker, "which attributes are governed?" is undecidable and every clause's subject population must be guessed. ADR-008 states outright that it "is not epistemic metadata" | ADR-008 |
| `SubstrateDeclaration` | EA-REQ-05, 06, 09, 11, 13 | Five clauses require declarations that are properties of the substrate, not of any claim: a status vocabulary, a lifecycle stage set, a resolution boundary | ADR-007 |
| `Unresolved` | EA-REQ-12 | A declared gap is a verdict where absence is silence. Without it, "not recorded" and "recorded as missing" are indistinguishable | — |
| `ConflictCheck` | EA-REQ-15 | The clause requires the conflict query to return the conflicting *pair*, which a bare constraint failure does not supply | — |

## Why this marking is load-bearing

A specification pulls entities into an ontology. Left unmarked, the ontology
accumulates them and the domain claim quietly becomes "whatever the clauses
needed". `tests/test_warrant.py` refuses an unmarked entity and refuses a
domain-marked entity that names a clause, so the boundary cannot erode without
a failing test.

## For the write side

Write-side entities land in Phase 5 and inherit EA5's `hypothesis` status,
because `SPEC.md` labels EA5 and its three clauses that way and the label is
not decorative. They are marked here when they arrive.
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/test_warrant.py -v`
Expected: PASS, 6 tests.

- [ ] **Step 6: Commit**

```bash
git add docs/warrant.md trace/spec-trace.yaml tests/test_warrant.py
git commit -m "docs(warrant): nine entities on domain warrant, four on decidability

The marking is the contribution. A test refuses an unmarked entity and a
domain-marked entity that needs a clause to justify it."
```

---

### Task 8: The reference binding and the binding contract

A minimal JSON binding, labelled a conformance fixture. It supplies the instance data the SHACL gate needs and demonstrates that a substrate with no modelling language can satisfy the contract.

**Files:**
- Create: `bindings/reference/binding.yaml`
- Create: `bindings/reference/instances/grounded.json`
- Create: `bindings/reference/instances/ungrounded.json`
- Create: `docs/binding-contract.md`
- Test: `tests/test_binding_contract.py`

**Interfaces:**
- Consumes: `eaont.load.ABSTRACT_REFS` from Task 2.
- Produces: `bindings/reference/binding.yaml` with keys `ontology_version`, `types` (one per member of `ABSTRACT_REFS`), and `namespace`. Task 9's lift reads `namespace`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_binding_contract.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""A binding must map every abstract reference type, and nothing else.

The reference binding is a conformance fixture, not a production binding. Its
job is to prove the contract is satisfiable without a modelling language.
"""

import json
import pathlib

import yaml

from eaont.load import ABSTRACT_REFS

ROOT = pathlib.Path(__file__).parents[1]
BINDING = yaml.safe_load(
    (ROOT / "bindings" / "reference" / "binding.yaml").read_text(encoding="utf-8"))
INSTANCES = sorted((ROOT / "bindings" / "reference" / "instances").glob("*.json"))


def test_binding_maps_every_abstract_ref():
    assert set(BINDING["types"]) == ABSTRACT_REFS


def test_binding_maps_nothing_else():
    """A binding that invents a type is not honouring the contract."""
    assert set(BINDING["types"]) - ABSTRACT_REFS == set()


def test_binding_pins_the_ontology_version():
    assert BINDING["ontology_version"] == "0.1.0"


def test_binding_names_no_modelling_language():
    """A binding that has to mention another language to explain itself is
    not independent of it. The explanation lives in the contract document."""
    text = (ROOT / "bindings" / "reference" / "binding.yaml").read_text(encoding="utf-8")
    for token in ("KerML", "SysML", "UML"):
        assert token not in text, f"the reference binding names {token}"


def test_instances_exist_and_parse():
    assert INSTANCES, "no instance files"
    for path in INSTANCES:
        doc = json.loads(path.read_text(encoding="utf-8"))
        assert doc["claims"], f"{path.name} holds no claims"


def test_one_instance_is_grounded_and_one_is_not():
    names = {p.stem for p in INSTANCES}
    assert {"grounded", "ungrounded"} <= names
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_binding_contract.py -v`
Expected: FAIL with `FileNotFoundError` on `bindings/reference/binding.yaml`.

- [ ] **Step 3: Write the binding**

Create `bindings/reference/binding.yaml`:

```yaml
# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
#
# The reference binding. A CONFORMANCE FIXTURE, not a production binding.
#
# It exists to demonstrate that the four abstract reference types can be
# honoured by a substrate with no modelling language at all - here, plain JSON
# in the toolkit's canonical claim graph shape - and to supply the instance
# data `eaont validate` runs SHACL against.

ontology_version: "0.1.0"
namespace: "https://systems-researcher.org/ns/reference-binding#"

# Every abstract reference resolves to a string identifier scoped by the
# namespace above. That is the whole mapping: nothing here is evaluated, which
# is why a store without an expression language can be a conforming binding.
types:
  ElementRef:    {carrier: string, resolves_to: claim_id}
  ExpressionRef: {carrier: string, resolves_to: expression_name}
  PredicateRef:  {carrier: string, resolves_to: predicate_name}
  VocabularyRef: {carrier: string, resolves_to: vocabulary_name}

# The attachment relation. The ontology says what an EpistemicStatus IS; it
# says nothing about how one is attached to a claim, because a language with an
# annotation mechanism gets that edge from the mechanism and needs no property.
# A binding without one must supply the relation, in its own namespace.
# Discovered while writing this binding - see docs/binding-contract.md, which
# names the language and explains why this file does not.
attachment:
  status:      hasStatus
  criticality: hasCriticality
  derivation:  hasDerivation
  provenance:  hasProvenance
  entry:       hasEntry
  unresolved:  hasUnresolved
```

- [ ] **Step 4: Write the instances**

Create `bindings/reference/instances/grounded.json`:

```json
{
  "claims": [
    {
      "id": "SIC::engine::thrustSeaLevel",
      "element": "SIC::engine",
      "property": "thrustSeaLevel",
      "value": 6770,
      "value_type": "number",
      "status": "verified",
      "criticality": "safety_critical",
      "basis": [{"target": "EV::rocketdyne-f1-acceptance", "kind": "evidence"}],
      "evidence": [{"target": "EV::rocketdyne-f1-acceptance", "kind": "evidence"}],
      "derivation": {"expression": "Measured", "inputs": []},
      "provenance": {"agent": "AG::propulsion-team", "method": "MT::test",
                     "stage": "TechnicalReview"},
      "entry": {"origin_class": "human", "review_state": "reviewed"}
    },
    {
      "id": "SIC::stage::thrustTotal",
      "element": "SIC::stage",
      "property": "thrustTotal",
      "value": 33850,
      "value_type": "number",
      "status": "verified",
      "criticality": "safety_critical",
      "basis": [{"target": "SIC::engine::thrustSeaLevel", "kind": "claim"}],
      "evidence": [{"target": "EV::rocketdyne-f1-acceptance", "kind": "evidence"}],
      "derivation": {"expression": "SumOverCount",
                     "inputs": ["SIC::engine::thrustSeaLevel"]},
      "provenance": {"agent": "AG::propulsion-team", "method": "MT::analysis",
                     "stage": "TechnicalReview"},
      "entry": {"origin_class": "human", "review_state": "reviewed"}
    }
  ],
  "status_vocabulary": [
    {"term": "placeholder", "definition": "A value present only to keep the model well formed."},
    {"term": "assumption", "definition": "A working input adopted pending confirmation."},
    {"term": "target", "definition": "A value the design is committed to achieving."},
    {"term": "verified", "definition": "A value established by analysis or test against recorded evidence."}
  ],
  "lifecycle_stages": ["Draft", "PeerReview", "TechnicalReview",
                       "CertificationReview", "Baseline"],
  "evidence_ids": ["EV::rocketdyne-f1-acceptance"]
}
```

Create `bindings/reference/instances/ungrounded.json` — the same shape with the second claim's warrant removed, so SHACL has something that must fail:

```json
{
  "claims": [
    {
      "id": "SIC::stage::thrustTotal",
      "element": "SIC::stage",
      "property": "thrustTotal",
      "value": 34500,
      "value_type": "number",
      "status": {"unresolved": "no standing was ever assigned"},
      "basis": {"unresolved": "no basis recorded"},
      "derivation": {"unresolved": "no derivation recorded"},
      "provenance": {"unresolved": "no provenance recorded"}
    }
  ],
  "status_vocabulary": [
    {"term": "placeholder", "definition": "A value present only to keep the model well formed."},
    {"term": "assumption", "definition": "A working input adopted pending confirmation."},
    {"term": "target", "definition": "A value the design is committed to achieving."},
    {"term": "verified", "definition": "A value established by analysis or test against recorded evidence."}
  ],
  "lifecycle_stages": ["Draft", "PeerReview", "TechnicalReview",
                       "CertificationReview", "Baseline"],
  "evidence_ids": []
}
```

- [ ] **Step 5: Write `docs/binding-contract.md`**

Create it with the CC-BY-4.0 header, then:

```markdown
# The binding contract

What a substrate must supply to carry this ontology. Four type mappings and
three obligations — nothing else, and in particular nothing that presumes a
modelling language.

## The four abstract reference types

| Abstract type | What it must resolve to | Never |
|---|---|---|
| `ElementRef` | An identifier for a governed claim or a model element in the substrate | An inline copy of the referent |
| `ExpressionRef` | An identifier naming a derivation expression | An evaluated result |
| `PredicateRef` | An identifier naming a conflict predicate | An evaluated truth value |
| `VocabularyRef` | An identifier naming the published status vocabulary | A copy of its members |

**No conformance check evaluates an `ExpressionRef` or a `PredicateRef`.**
EA-REQ-02 checks that an expression's *inputs* resolve. EA-REQ-14 reads four
fields for presence. EA-REQ-15 decides conflict by value inequality and
membership in the conflict set. The toolkit's canonical claim graph carries
`derivation.expression` as a plain string, which is the same fact seen from
the other end.

That is why a graph store, a relational schema or plain JSON can be a
conforming binding: the contract asks for identity and resolution, never for
an expression language.

## The four obligations

1. **Pin the ontology version.** A binding is correct only with respect to one
   version. `binding.yaml` carries `ontology_version`.
2. **Map every abstract reference type, and no others.** A binding that
   invents a type is not honouring the contract; a binding that omits one
   cannot carry the ontology.
3. **Supply the attachment relation.** See below.
4. **Emit instances a SHACL run can validate.** The shapes in `ontology/` are
   the acceptance test.

## The attachment relation, and why the ontology does not define it

The ontology defines what an `EpistemicStatus` is, and what a `Derivation` is.
It defines **no relation attaching either to a claim.** `GovernedClaim` carries
`claimId` and `revision` and nothing else — ADR-008 made it a bare population
marker on purpose.

That is not an omission. In SysML v2 the attachment *is* the annotation
mechanism: writing `@EpistemicStatus { ... }` on an element attaches it, and no
property is needed because the language supplies one. The ontology inherited
that silence.

A binding without an annotation mechanism — a graph, a relational schema, JSON
— has to say how a status belongs to a claim, and it says so in **its own
namespace**, never in `ea:`. The reference binding declares six such relations
under `attachment:` in `binding.yaml`.

**This was discovered by writing the reference binding**, which is what a
second binding is for. It is recorded here rather than fixed in the ontology
for two reasons: adding attachment properties to `GovernedClaim` would
contradict ADR-008's population-marker decision, and the SysML v2 binding would
then carry properties it has no use for.

The consequence for a reader is small but real: `ea:` triples describe the
annotation nodes, and the edges joining them to claims are binding-local. A
query written against one binding's attachment vocabulary does not run against
another's. Whether that should change is a question for the ontology's next
version, and it is a better question than the design anticipated.

## Worked examples

`bindings/reference/` is the minimal case — JSON, no modelling language,
identifiers as strings. `epistemic-adequacy-sysml-v2-binding` is the full
case, mapping the same four types to `KerML::Element`, `KerML::Function`,
`KerML::Predicate` and `SysML::EnumerationDefinition`.

The two together are the language-independence claim. One binding could not
make it.
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `pytest tests/test_binding_contract.py -v`
Expected: PASS, 6 tests.

- [ ] **Step 7: Commit**

```bash
git add bindings/ docs/binding-contract.md tests/test_binding_contract.py
git commit -m "feat(bindings): a reference binding with no modelling language

Four type mappings, three obligations. Nothing is evaluated, which is why a
JSON store can conform."
```

---

### Task 9: Lift canonical claim graph JSON into RDF

**Files:**
- Create: `src/eaont/lift.py`
- Test: `tests/test_lift.py`

**Interfaces:**
- Consumes: `eaont.generate.owl.EA` (the `ea:` namespace), `bindings/reference/binding.yaml` key `namespace`.
- Produces: `eaont.lift.lift(document: dict, namespace: str) -> rdflib.Graph`. Task 10 calls this.

- [ ] **Step 1: Write the failing test**

Create `tests/test_lift.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""Canonical claim graph JSON -> RDF, so SHACL has instances to judge."""

import json
import pathlib

import rdflib
from rdflib import RDF

from eaont.generate.owl import EA
from eaont.lift import lift

ROOT = pathlib.Path(__file__).parents[1]
NS = "https://systems-researcher.org/ns/reference-binding#"
GROUNDED = json.loads(
    (ROOT / "bindings" / "reference" / "instances" / "grounded.json")
    .read_text(encoding="utf-8"))
UNGROUNDED = json.loads(
    (ROOT / "bindings" / "reference" / "instances" / "ungrounded.json")
    .read_text(encoding="utf-8"))


def test_every_claim_becomes_a_governed_claim():
    g = lift(GROUNDED, NS)
    claims = set(g.subjects(RDF.type, EA.GovernedClaim))
    assert len(claims) == len(GROUNDED["claims"])


def test_status_becomes_a_typed_standing():
    g = lift(GROUNDED, NS)
    standings = set(g.objects(None, EA.EpistemicStatus_standing))
    assert EA.EpistemicStatusKind_verified in standings


def test_derivation_expression_is_a_reference_not_a_literal():
    """ExpressionRef is a reference type. A binding resolves it to an
    identifier; it is never inlined and never evaluated."""
    g = lift(GROUNDED, NS)
    expressions = list(g.objects(None, EA.Derivation_expression))
    assert expressions, "no expression lifted"
    assert all(isinstance(e, rdflib.URIRef) for e in expressions)
    assert any(str(e) == NS + "SumOverCount" for e in expressions)


def test_upstream_points_at_the_lifted_claim():
    g = lift(GROUNDED, NS)
    upstream = set(g.objects(None, EA.Derivation_upstream))
    assert rdflib.URIRef(NS + "SIC::engine::thrustSeaLevel") in upstream


def test_markers_become_unresolved_nodes():
    g = lift(UNGROUNDED, NS)
    markers = set(g.subjects(RDF.type, EA.Unresolved))
    assert len(markers) == 4     # status, basis, derivation, provenance


def test_marker_records_which_field_it_occupies():
    """The field is an enumeration member, not a string: the shape says
    `sh:class ea:UnresolvedFieldKind`, so a literal would be refused."""
    g = lift(UNGROUNDED, NS)
    fields = {str(o).rsplit("UnresolvedFieldKind_", 1)[-1]
              for o in g.objects(None, EA.Unresolved_field)}
    assert fields == {"status", "basis", "derivation", "provenance"}


def test_lift_is_deterministic():
    """Same input, same triples. Otherwise the gate is not reproducible."""
    a, b = lift(GROUNDED, NS), lift(GROUNDED, NS)
    assert set(a) == set(b)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_lift.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eaont.lift'`

- [ ] **Step 3: Implement the lift**

Create `src/eaont/lift.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""Canonical claim graph JSON -> RDF, so the SHACL shapes have instances.

The shapes were generated and byte-compared but never executed, because
nothing lifted instance data into the graph they judge. This module is that
step, and it is why `pyshacl` stops being a declared dependency nobody
imports.

Reference-typed fields become URIRefs into the binding's namespace, never
literals. That is the contract: a binding resolves a reference to an
identifier, and nothing here evaluates one.

Two namespaces, and the split is load-bearing. `ea:` carries the annotation
nodes and their own properties, because the ontology defines those. The edges
joining an annotation to a claim are `bind:`, because the ontology defines no
attachment relation - in SysML v2 the annotation mechanism is the attachment,
so nothing needed naming. A binding without that mechanism supplies its own.
See docs/binding-contract.md.
"""

from __future__ import annotations

import rdflib
from rdflib import RDF, Literal, URIRef

from eaont.generate.owl import EA

# Claim fields whose value may instead be an {"unresolved": "..."} marker.
MARKABLE = ("status", "criticality", "basis", "alternatives", "evidence",
            "derivation", "provenance", "entry")

# Values the ontology requires and the canonical claim graph does not carry.
# Every one of these is a lossy carrier, declared rather than hidden.
UNKNOWN = "unknown"
REVIEW_STATE = {"reviewed": "promoted", "unreviewed": "unreviewed"}


def _method_kind(method_id: str) -> str:
    """MT::test -> test. An unrecognised suffix falls back to `judgement`,
    the weakest member, so a bad guess never inflates a claim's warrant."""
    suffix = method_id.rsplit("::", 1)[-1]
    known = {"analysis", "test", "simulation", "tradeStudy", "judgement",
             "transcription"}
    return suffix if suffix in known else "judgement"


def _is_marker(value) -> bool:
    return isinstance(value, dict) and "unresolved" in value


def lift(document: dict, namespace: str) -> rdflib.Graph:
    """One canonical claim graph document into one RDF graph."""
    g = rdflib.Graph()
    g.bind("ea", EA)
    ns = rdflib.Namespace(namespace)
    g.bind("bind", ns)

    for claim in document.get("claims", []):
        _add_claim(g, ns, claim)
    return g


def _add_claim(g: rdflib.Graph, ns, claim: dict) -> None:
    subject = ns[claim["id"]]
    g.add((subject, RDF.type, EA.GovernedClaim))
    g.add((subject, EA.GovernedClaim_claimId, Literal(claim["id"])))

    for field in MARKABLE:
        if field not in claim:
            continue
        value = claim[field]
        if _is_marker(value):
            _add_marker(g, ns, subject, field, value["unresolved"])
        else:
            _ADDERS[field](g, ns, subject, value)


def _add_marker(g, ns, subject, field: str, missing: str) -> None:
    node = ns[f"{subject.split('#')[-1]}::unresolved::{field}"]
    g.add((node, RDF.type, EA.Unresolved))
    # `field` is typed UnresolvedFieldKind, so the generated shape carries
    # `sh:class ea:UnresolvedFieldKind` and refuses a literal. Verified against
    # ontology/shapes.ttl: a Literal here yields one ClassConstraintComponent
    # violation per marker, and `eaont validate` returns 1.
    g.add((node, EA.Unresolved_field, EA[f"UnresolvedFieldKind_{field}"]))
    g.add((node, EA.Unresolved_missing, Literal(missing)))
    # `since` is multiplicity 1 in the ontology and has NO carrier in the
    # canonical claim graph, whose marker is {"unresolved": "<text>"} and
    # nothing else. The binding supplies a constant rather than inventing a
    # date. See the lossy-carrier note in docs/binding-contract.md.
    g.add((node, EA.Unresolved_since, Literal(UNKNOWN)))
    g.add((subject, ns.hasUnresolved, node))


def _add_status(g, ns, subject, value) -> None:
    node = ns[f"{subject.split('#')[-1]}::status"]
    g.add((node, RDF.type, EA.EpistemicStatus))
    g.add((node, EA.EpistemicStatus_standing, EA[f"EpistemicStatusKind_{value}"]))
    g.add((node, EA.EpistemicStatus_currency, EA.CurrencyKind_current))
    g.add((subject, ns.hasStatus, node))


def _add_criticality(g, ns, subject, value) -> None:
    node = ns[f"{subject.split('#')[-1]}::criticality"]
    g.add((node, RDF.type, EA.Criticality))
    g.add((node, EA.Criticality_safetyCritical,
           Literal(value == "safety_critical")))
    g.add((node, EA.Criticality_basis, Literal(f"declared {value}")))
    g.add((subject, ns.hasCriticality, node))


def _derivation_node(g, ns, subject):
    node = ns[f"{subject.split('#')[-1]}::derivation"]
    g.add((node, RDF.type, EA.Derivation))
    g.add((subject, ns.hasDerivation, node))
    return node


def _add_derivation(g, ns, subject, value) -> None:
    node = _derivation_node(g, ns, subject)
    # ExpressionRef: a reference to a named expression, not the expression.
    g.add((node, EA.Derivation_expression, ns[value["expression"]]))
    for target in value["inputs"]:
        g.add((node, EA.Derivation_upstream, ns[target]))


def _add_basis(g, ns, subject, value) -> None:
    node = _derivation_node(g, ns, subject)
    for ref in value:
        if ref["kind"] == "claim":
            g.add((node, EA.Derivation_upstream, ns[ref["target"]]))


def _add_alternatives(g, ns, subject, value) -> None:
    node = _derivation_node(g, ns, subject)
    for ref in value:
        g.add((node, EA.Derivation_alternatives, ns[ref["target"]]))


def _add_evidence(g, ns, subject, value) -> None:
    node = _derivation_node(g, ns, subject)
    for ref in value:
        anchor = ns[ref["target"]]
        g.add((anchor, RDF.type, EA.EvidenceAnchor))
        g.add((anchor, EA.EvidenceAnchor_uri, Literal(ref["target"])))
        g.add((node, EA.Derivation_evidence, anchor))


def _add_provenance(g, ns, subject, value) -> None:
    node = ns[f"{subject.split('#')[-1]}::provenance"]
    g.add((node, RDF.type, EA.Provenance))
    agent = ns[value["agent"]]
    g.add((agent, RDF.type, EA.Agent))
    g.add((agent, EA.Agent_id, Literal(value["agent"])))
    # kind and name are multiplicity 1 and the canonical graph carries only an
    # id. `person` is the binding's declared default, not a fact read from the
    # document, and docs/binding-contract.md says so.
    g.add((agent, EA.Agent_kind, EA.AgentKind_person))
    g.add((agent, EA.Agent_name, Literal(value["agent"])))
    g.add((node, EA.Provenance_agent, agent))
    method = ns[value["method"]]
    g.add((method, RDF.type, EA.Method))
    g.add((method, EA.Method_id, Literal(value["method"])))
    g.add((method, EA.Method_kind, EA[f"MethodKind_{_method_kind(value['method'])}"]))
    g.add((method, EA.Method_description, Literal(value["method"])))
    g.add((node, EA.Provenance_method, method))
    if value.get("stage"):
        g.add((node, EA.Provenance_reviewStage, Literal(value["stage"])))
    g.add((subject, ns.hasProvenance, node))


def _add_entry(g, ns, subject, value) -> None:
    node = ns[f"{subject.split('#')[-1]}::entry"]
    g.add((node, RDF.type, EA.Entry))
    g.add((node, EA.Entry_origin, EA[f"OriginKind_{value['origin_class']}"]))
    # The canonical graph flattens four review states into two - see ADR-002's
    # declared consequence. Unflattening `reviewed` is sound rather than a
    # guess: the claim was emitted as a GovernedClaim, so it is held out as
    # part of the authoritative record, and a rejected claim is not. The
    # ambiguity ADR-002 records bites a consumer reading the flattened form,
    # not a binding that also knows the claim is governed.
    g.add((node, EA.Entry_reviewState,
           EA[f"ReviewStateKind_{REVIEW_STATE[value['review_state']]}"]))
    g.add((subject, ns.hasEntry, node))


_ADDERS = {
    "status": _add_status,
    "criticality": _add_criticality,
    "basis": _add_basis,
    "alternatives": _add_alternatives,
    "evidence": _add_evidence,
    "derivation": _add_derivation,
    "provenance": _add_provenance,
    "entry": _add_entry,
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_lift.py -v`
Expected: PASS, 7 tests.

If `test_markers_become_unresolved_nodes` reports a count other than 4, check that `ungrounded.json` marks exactly `status`, `basis`, `derivation` and `provenance` — the fixture and the assertion must agree.

- [ ] **Step 5: Commit**

```bash
git add src/eaont/lift.py tests/test_lift.py
git commit -m "feat(lift): canonical claim graph JSON into RDF

References become URIRefs, never literals and never evaluated. This is the
step that was missing between generated shapes and a SHACL run."
```

---

### Task 10: Run SHACL, and wire it to `eaont validate`

The gate the ontology repository does not have today.

**Files:**
- Create: `src/eaont/validate.py`
- Modify: `src/eaont/cli.py`
- Test: `tests/test_validate.py`

`tests/test_generate_shacl.py` already calls `pyshacl.validate` on graphs it
builds itself. Leave it alone: it tests the *generator*, and it stays valuable
for exactly that. What it cannot do is tell you the shapes hold over a
substrate's output, which is what this task adds.

**Interfaces:**
- Consumes: `eaont.lift.lift(document, namespace)` from Task 9.
- Produces: `eaont.validate.validate_instance(path, shapes_path, namespace) -> tuple[bool, str]`, and the CLI subcommand `eaont validate`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_validate.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""SHACL over real instances. The gate that makes this a checked artefact."""

import pathlib

import pytest

from eaont.cli import main
from eaont.validate import validate_instance

ROOT = pathlib.Path(__file__).parents[1]
SHAPES = ROOT / "ontology" / "shapes.ttl"
ONT = ROOT / "ontology" / "epistemic-adequacy.ttl"
INSTANCES = ROOT / "bindings" / "reference" / "instances"
NS = "https://systems-researcher.org/ns/reference-binding#"


def test_grounded_instance_conforms():
    ok, report = validate_instance(INSTANCES / "grounded.json", SHAPES, NS, ONT)
    assert ok, report


def test_validation_report_is_returned_either_way():
    _, report = validate_instance(INSTANCES / "grounded.json", SHAPES, NS, ONT)
    assert isinstance(report, str) and report


def test_cli_validate_returns_zero():
    assert main(["validate"]) == 0


def test_a_status_outside_the_vocabulary_is_refused(tmp_path):
    """A gate that cannot fail is not a gate.

    `EpistemicStatus.standing` is typed `EpistemicStatusKind`. A standing of
    "probably_fine" lifts to ea:EpistemicStatusKind_probably_fine, which is not
    one of the four individuals the ontology declares.
    """
    import json
    broken = json.loads((INSTANCES / "grounded.json").read_text(encoding="utf-8"))
    broken["claims"][0]["status"] = "probably_fine"
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    ok, _ = validate_instance(path, SHAPES, NS, ONT)
    assert not ok, (
        "the shapes accepted a standing outside the declared vocabulary"
    )
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_validate.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eaont.validate'`

- [ ] **Step 3: Implement the validator**

Create `src/eaont/validate.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""SHACL over lifted claim-graph instances.

`pyshacl` is a declared dependency that no module under `src/` imports. The
shapes are run once already, in tests/test_generate_shacl.py, against fixture
graphs hand-built inside the test - which shows they hold over data written to
satisfy them. This module runs them over data a substrate emitted instead.
"""

from __future__ import annotations

import json
import pathlib

import rdflib
from pyshacl import validate as shacl_validate

from eaont.lift import lift


def validate_instance(instance_path, shapes_path, namespace: str,
                     ontology_path) -> tuple[bool, str]:
    """(conforms, report). The report is returned whether or not it conformed,
    because a passing run that prints nothing is indistinguishable from a run
    that checked nothing."""
    document = json.loads(pathlib.Path(instance_path).read_text(encoding="utf-8"))
    data = lift(document, namespace)

    # `sh:class ea:EpistemicStatusKind` resolves rdf:type in the DATA graph,
    # and the enumeration members are typed in epistemic-adequacy.ttl, not in
    # shapes.ttl. Without this parse every sh:class constraint fails - for a
    # correct standing exactly as for a bogus one, which would make the gate
    # look strict while testing nothing.
    data.parse(str(ontology_path), format="turtle")

    shapes = rdflib.Graph()
    shapes.parse(str(shapes_path), format="turtle")

    conforms, _, text = shacl_validate(
        data_graph=data,
        shacl_graph=shapes,
        advanced=True,
        inference="none",     # deliberate: judge what the binding emitted,
                              # not what a reasoner could infer from it
    )
    return conforms, text
```

- [ ] **Step 4: Wire the CLI**

In `src/eaont/cli.py`, add near the other imports:

```python
BINDING = ROOT / "bindings" / "reference" / "binding.yaml"
INSTANCES = ROOT / "bindings" / "reference" / "instances"
SHAPES = ROOT / "ontology" / "shapes.ttl"
ONTOLOGY = ROOT / "ontology" / "epistemic-adequacy.ttl"
```

Add the command:

```python
def validate() -> int:
    """Run the shapes over every reference-binding instance."""
    import yaml

    from eaont.validate import validate_instance

    namespace = yaml.safe_load(BINDING.read_text(encoding="utf-8"))["namespace"]
    failures = []
    for path in sorted(INSTANCES.glob("*.json")):
        # ungrounded.json is a fixture for the FAILING case: its claims carry
        # markers where warrant would be. A marker is a well-formed Unresolved
        # node, so it conforms structurally - what it fails is a clause, and
        # clauses are the toolkit's business, not SHACL's.
        ok, report = validate_instance(path, SHAPES, namespace, ONTOLOGY)
        print(f"{'PASS' if ok else 'FAIL'} {path.name}")
        if not ok:
            failures.append((path.name, report))

    for name, report in failures:
        print(f"\n--- {name} ---\n{report}", file=sys.stderr)
    if failures:
        return 1
    print(f"shapes hold over {len(list(INSTANCES.glob('*.json')))} instances")
    return 0
```

In `main()`, add `sub.add_parser("validate")` beside the others, and the dispatch branch:

```python
    if args.command == "validate":
        return validate()
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/test_validate.py -v`
Expected: PASS, 4 tests.

If `test_grounded_instance_conforms` fails, read the report before changing anything. The likely cause is a shape whose `sh:minCount` is 1 for a property the lift does not populate — the fix is to populate it in the lift or enrich `grounded.json`, **never** to loosen a generated shape, which would be hand-editing a generated file.

`test_a_status_outside_the_vocabulary_is_refused` is known to be able to fail,
which is what makes it a gate: `ea:EpistemicStatusShape_standing sh:class
ea:EpistemicStatusKind` is present in the generated shapes (verified
2026-08-21), and `probably_fine` lifts to an individual carrying no such type.
If it nonetheless passes, the ontology graph is not reaching the data graph —
re-read the `data.parse` line above before touching the test.

- [ ] **Step 6: Run the whole suite and the CLI**

```bash
pytest -q
eaont check-drift
eaont validate
```

Expected: all green; `no drift across 3 generated artefacts`; `shapes hold over 2 instances`.

- [ ] **Step 7: Commit**

```bash
git add src/eaont/validate.py src/eaont/cli.py tests/test_validate.py
git commit -m "feat(validate): run SHACL over reference-binding instances

pyshacl was declared and never imported, so the shapes were generated,
byte-compared and never executed. They now judge real instance data."
```

---

### Task 11: Competency questions

An ontology is evaluated by what it can answer. These are the questions, as executable assertions over the lifted graph.

**Files:**
- Create: `docs/competency-questions.md`
- Test: `tests/test_competency_questions.py`

**Interfaces:**
- Consumes: `eaont.lift.lift` from Task 9.
- Produces: nothing consumed downstream.

- [ ] **Step 1: Write the failing test**

Create `tests/test_competency_questions.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""Competency questions, as SPARQL over the lifted reference instances.

An ontology is evaluated by what it can answer. Each question here is one a
clause makes a substrate answer, asked of the ontology instead.
"""

import json
import pathlib

from eaont.lift import lift

ROOT = pathlib.Path(__file__).parents[1]
NS = "https://systems-researcher.org/ns/reference-binding#"
GRAPH = lift(
    json.loads((ROOT / "bindings" / "reference" / "instances" / "grounded.json")
               .read_text(encoding="utf-8")),
    NS,
)
PREFIX = """
PREFIX ea: <https://systems-researcher.org/ns/epistemic-adequacy#>
PREFIX bind: <https://systems-researcher.org/ns/reference-binding#>
"""


def ask(query: str):
    return list(GRAPH.query(PREFIX + query))


def test_cq1_what_is_this_claim_derived_from():
    """EA-REQ-02."""
    rows = ask("""
        SELECT ?up WHERE {
          bind:SIC%3A%3Astage%3A%3AthrustTotal bind:hasDerivation ?d .
          ?d ea:Derivation_upstream ?up .
        }
    """)
    assert rows, "a derived claim reports no upstream"


def test_cq2_what_standing_does_this_claim_have():
    """EA-REQ-05."""
    rows = ask("""
        SELECT ?standing WHERE {
          ?c a ea:GovernedClaim ; bind:hasStatus ?s .
          ?s ea:EpistemicStatus_standing ?standing .
        }
    """)
    assert len(rows) == 2


def test_cq3_who_produced_this_value_and_how():
    """EA-REQ-08."""
    rows = ask("""
        SELECT ?agent ?method WHERE {
          ?c bind:hasProvenance ?p .
          ?p ea:Provenance_agent ?agent ; ea:Provenance_method ?method .
        }
    """)
    assert len(rows) == 2


def test_cq4_what_evidence_supports_this_claim():
    """EA-REQ-10."""
    rows = ask("""
        SELECT ?anchor WHERE {
          ?d ea:Derivation_evidence ?anchor .
          ?anchor a ea:EvidenceAnchor .
        }
    """)
    assert rows


def test_cq5_is_every_claim_answerable_on_all_four_fields():
    """EA-REQ-14: the groundedness query returns a determinate verdict."""
    rows = ask("""
        SELECT ?c WHERE {
          ?c a ea:GovernedClaim ;
             bind:hasStatus ?s ;
             bind:hasDerivation ?d ;
             bind:hasProvenance ?p .
        }
    """)
    assert len(rows) == 2, "a claim in the grounded fixture is not answerable"


def test_cq6_the_expression_is_named_never_inlined():
    """The binding contract: ExpressionRef resolves to an identifier."""
    rows = ask("""
        SELECT ?e WHERE { ?d ea:Derivation_expression ?e . FILTER(isIRI(?e)) }
    """)
    assert rows, "an expression was lifted as a literal"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_competency_questions.py -v`
Expected: FAIL on CQ1. The cause is specific and the fix is not a fork:
SPARQL does **not** percent-decode inside a prefixed name, so
`bind:SIC%3A%3Astage%3A%3AthrustTotal` builds an IRI that keeps the literal
`%3A` and never matches `ns["SIC::stage::thrustTotal"]`. Replace the prefixed
name with a full IRI in angle brackets:

```sparql
<https://systems-researcher.org/ns/reference-binding#SIC::stage::thrustTotal>
```

Do **not** rename the claim identifiers to avoid the colons — the `SIC::` form
is the Apollo echo that makes the fixture legible, and it is what a real
substrate emits.

- [ ] **Step 3: Make the questions pass**

Adjust only the query syntax to match the identifiers the lift actually produces. If a question genuinely cannot be answered, that is a finding about the ontology, not the test — record it in `docs/competency-questions.md` under "unanswerable" and leave the test skipped with a reason, rather than deleting it.

- [ ] **Step 4: Write `docs/competency-questions.md`**

Create it with the CC-BY-4.0 header, listing each question in prose, the clause it corresponds to, the SPARQL that answers it, and the answer over the reference instances. Add a closing section:

```markdown
## Why these six

Each is a question a clause obliges a substrate to answer, asked of the
ontology instead. They are the ontology's acceptance test: if the entity model
cannot answer a question the specification makes a substrate answer, the model
is short an entity or a relation.

Answerability here is necessary and not sufficient. It shows the vocabulary
can express the question; whether a real substrate answers it correctly is the
toolkit's business, and whether the answer changes an AI consumer's behaviour
is a probe's.
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/test_competency_questions.py -v`
Expected: PASS, 6 tests.

- [ ] **Step 6: Commit**

```bash
git add docs/competency-questions.md tests/test_competency_questions.py
git commit -m "test(cq): six competency questions as SPARQL over the reference instances"
```

---

### Task 12: The ADR-010 test — can the ontology express per-instance standing?

Design §11.1 names this the live falsifier of the whole arrangement. Run it deliberately and record the answer either way.

**Files:**
- Create: `docs/adr-010-test.md`
- Create: `bindings/reference/instances/per-instance.json`
- Test: `tests/test_adr010_anchoring.py`

**Interfaces:**
- Consumes: `eaont.lift.lift`, `eaont.validate.validate_instance`.
- Produces: a recorded verdict in `docs/adr-010-test.md`.

- [ ] **Step 1: Write the probe fixture**

Create `bindings/reference/instances/per-instance.json` — five engine instances, each with its own standing, which the SysML v2 binding cannot represent because it anchors to a usage with multiplicity 5:

```json
{
  "claims": [
    {"id": "SIC::engine1::thrustSeaLevel", "element": "SIC::engine1",
     "property": "thrustSeaLevel", "value": 6770, "value_type": "number",
     "status": "verified",
     "derivation": {"expression": "Measured", "inputs": []},
     "provenance": {"agent": "AG::propulsion-team", "method": "MT::test"}},
    {"id": "SIC::engine2::thrustSeaLevel", "element": "SIC::engine2",
     "property": "thrustSeaLevel", "value": 6770, "value_type": "number",
     "status": "assumption",
     "derivation": {"expression": "Measured", "inputs": []},
     "provenance": {"agent": "AG::propulsion-team", "method": "MT::judgement"}}
  ],
  "status_vocabulary": [
    {"term": "placeholder", "definition": "A value present only to keep the model well formed."},
    {"term": "assumption", "definition": "A working input adopted pending confirmation."},
    {"term": "target", "definition": "A value the design is committed to achieving."},
    {"term": "verified", "definition": "A value established by analysis or test against recorded evidence."}
  ],
  "lifecycle_stages": ["Draft", "PeerReview", "TechnicalReview",
                       "CertificationReview", "Baseline"],
  "evidence_ids": []
}
```

- [ ] **Step 2: Write the test**

Create `tests/test_adr010_anchoring.py`:

```python
# Copyright (c) 2026 Jason D. Gower. See LICENSE.
# SPDX-License-Identifier: MIT
"""Design §11.1 - the live falsifier.

ADR-010 anchors a claim to a SysML v2 usage, so five engines rendered as one
usage with multiplicity 5 share one standing. If the ONTOLOGY inherited that
limit, it is SysML-shaped and the layering is wrong. If a binding with no
modelling language can carry per-instance standing, the limit is the
binding's and the ontology is clear.
"""

import json
import pathlib

import rdflib
from rdflib import RDF

from eaont.generate.owl import EA
from eaont.lift import lift
from eaont.validate import validate_instance

ROOT = pathlib.Path(__file__).parents[1]
NS = "https://systems-researcher.org/ns/reference-binding#"
ns = rdflib.Namespace(NS)
PATH = ROOT / "bindings" / "reference" / "instances" / "per-instance.json"
DOC = json.loads(PATH.read_text(encoding="utf-8"))


def test_per_instance_standing_is_expressible():
    """The falsifier. If this fails, stop and re-read design §11.1."""
    g = lift(DOC, NS)
    standings = {}
    for claim in g.subjects(RDF.type, EA.GovernedClaim):
        for status in g.objects(claim, ns.hasStatus):
            for standing in g.objects(status, EA.EpistemicStatus_standing):
                standings[str(claim)] = str(standing)
    assert len(standings) == 2
    assert len(set(standings.values())) == 2, (
        "two instances of the same part could not carry different standings; "
        "the ontology inherited ADR-010's anchoring limit"
    )


def test_per_instance_fixture_still_conforms():
    ok, report = validate_instance(
        PATH, ROOT / "ontology" / "shapes.ttl", NS,
        ROOT / "ontology" / "epistemic-adequacy.ttl")
    assert ok, report
```

- [ ] **Step 3: Run the test**

Run: `pytest tests/test_adr010_anchoring.py -v`

**If PASS:** the ontology's claim identity is a free-form string, so per-instance anchoring is available to any binding that wants it, and ADR-010 is a SysML v2 limitation rather than an ontology one. Record that.

**If FAIL:** stop. Do not proceed to Task 13 or to Phase 3. The design's §11.1 falsifier has fired: claim anchoring is SysML-shaped, and the layering decision in §4 needs revisiting with the user before any repository is renamed.

- [ ] **Step 4: Record the verdict**

Create `docs/adr-010-test.md` with the CC-BY-4.0 header, stating: the question, the fixture, the command, the observed result, and the conclusion. Write it to be readable by someone who was not present — this is the record that the falsifier was actually run rather than assumed away.

Include the consequence explicitly: if it passed, `epistemic-adequacy-sysml-v2-binding` inherits ADR-010's limitation and the ontology does not, which is a finding for the binding paper — *what the language cannot carry* — and belongs in `docs/round-trip-loss.md` over there.

- [ ] **Step 5: Commit**

```bash
git add bindings/reference/instances/per-instance.json \
        tests/test_adr010_anchoring.py docs/adr-010-test.md
git commit -m "test: run the ADR-010 falsifier and record the verdict

Design §11.1 named this the cheapest thing that could invalidate the split.
It was run, not assumed."
```

---

### Task 13: Related work, README, and CI

The positioning the design flags as an unwritten risk, plus the repository's front door and its gates in CI.

**Files:**
- Create: `docs/related-work.md`, `docs/limitations.md`, `docs/entities.md`, `README.md`
- Create: `.github/workflows/validate.yml`
- Modify: `CITATION.cff`
- Test: `tests/test_release.py`

**Interfaces:**
- Consumes: every command from Tasks 1–12.
- Produces: nothing consumed downstream.

- [ ] **Step 1: Write `docs/related-work.md`**

With the CC-BY-4.0 header, as with every document under `docs/` — Step 4's
release test checks for it.

The design §8 records that nothing in the programme mentions SACM, assurance cases, Toulmin or nanopublications. This document discharges that. It must cover, with a verified citation for each:

- **OMG SACM** (Structured Assurance Case Metamodel) — a standardised metamodel for claims, evidence and argumentation with a MOF/UML realisation. The closest prior art, and the one a reviewer will raise first. State plainly what is shared (claim, evidence, argument structure) and what differs: SACM structures an argument a human assessor reads; this ontology structures a record so a machine consumer can decide groundedness without one.
- **W3C PROV-O** — already aligned in `ontology/prov-alignment.ttl`. Say what is imported and what is added.
- **Nanopublications and SEPIO** — claim-plus-evidence-plus-provenance in scientific publishing. Same triad, different domain and no conformance obligations.
- **Toulmin's argument model** — the ancestor of claim/warrant/backing vocabulary. Acknowledge the debt.

Follow the specification's `docs/references.md` convention: every source verified, and any claim that could not be anchored to a passage recorded as such rather than quietly asserted.

- [ ] **Step 1b: Write `docs/limitations.md`**

The metamodel repository's copy was deleted in Task 1 — it catalogued the
SysML v2 realisation's limits, which are the binding's. This one carries the
ontology's. Give it the CC-BY-4.0 header, as every file under `docs/` needs one
for Step 4's release test. Start it with at least these three, all discovered
while building the reference binding rather than anticipated by the design:

1. **The ontology defines no attachment relation.** `GovernedClaim` carries
   `claimId` and `revision`; nothing joins it to the `EpistemicStatus` or
   `Derivation` that describes it. Every binding supplies that edge in its own
   namespace, so a query written against one binding's attachment vocabulary
   does not run against another's.

   State this as a **deliberate deferral with a reason**, not an oversight — a
   reader will stop on it, because the relation between a claim and what is
   known about it plainly exists in the world whatever SysML's annotation
   syntax does. The reason is ADR-008: `GovernedClaim` is a population marker
   answering *is this part of the authoritative record*, and every other
   annotation answers *what is known about it*. Giving the marker attachment
   properties would collapse that distinction, which is load-bearing for how
   an unannotated substrate is still assessable. Whether the next version
   should add a neutral `ea:describes` is a real open question and belongs
   here as one.
2. **The canonical claim graph is a lossy carrier.** `Unresolved.since`,
   `Agent.kind`, `Agent.name`, `Method.kind` and `Method.description` are
   multiplicity 1 in the ontology and have no field in the canonical form, so
   a binding lifting from it supplies declared defaults. A SHACL pass over
   such instances therefore proves the shapes hold over *reconstructed* data.
3. **Whatever `docs/adr-010-test.md` records**, in the words it records it.

- [ ] **Step 1c: Write `docs/entities.md`**

Design §5.1 lists this as the entity model and no earlier task creates it. It is
the human-readable pass over the thirteen definitions in `model/ontology.yaml`:
one section per entity, its parameters with types and multiplicities, and a
sentence on what it is for. Cross-link each to its row in `docs/warrant.md`
rather than restating the warrant.

Keep it generated-adjacent, not generated: it is prose about the schema, and a
generator that emitted prose would emit the same sentence thirteen times. But add
a test asserting every entity in `model/ontology.yaml` has a section, so it
cannot fall behind:

```python
def test_entities_doc_covers_every_definition():
    text = (ROOT / "docs" / "entities.md").read_text(encoding="utf-8")
    for name in load_metamodel(SOURCE).metadata_definitions:
        assert f"## {name}" in text, f"docs/entities.md omits {name}"
```

- [ ] **Step 2: Write `README.md`**

Cover: what the repository is, the conceptually-prior/normatively-subordinate relationship to the specification (design §4) stated in those words, the three-tier layout (`model/` → `ontology/` → `bindings/`), how to run the three gates, and a "what this is not" section — not a standard, not a checker, not a study.

- [ ] **Step 3: Write the CI workflow**

Create `.github/workflows/validate.yml`:

```yaml
name: validate
on: [push, pull_request]

jobs:
  ontology:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.14"}
      - run: pip install -e ".[test]"
      - run: pytest -q
      - run: eaont check-drift
      - run: eaont validate
      - name: no language type may enter the schema
        # model/ only: load.py names the prefixes in order to refuse them.
        run: |
          ! grep -rn "KerML::\|SysML::\|UML::" model/
```

The final step is the agnosticism gate at the CI level, backing up the load-time refusal from Task 2. Two independent checks, because this is the property the repository exists to hold.

- [ ] **Step 4: Write the release test**

Create `tests/test_release.py` asserting: every `.py` under `src/` carries an
SPDX-MIT line; every `.md` under `docs/` carries a CC-BY-4.0 header;
`model/ontology.yaml`'s `version` matches `CITATION.cff`; and
`bindings/reference/binding.yaml`'s `ontology_version` matches
`model/ontology.yaml`'s `version`.

Exit criteria 6 and 7 are otherwise unchecked prose, so assert them here too:

```python
def test_adr010_verdict_is_recorded_and_passed():
    """Exit criterion 6. The falsifier must have been RUN, not assumed away,
    and a FAIL blocks Phase 3 rather than being noted and stepped over."""
    text = (ROOT / "docs" / "adr-010-test.md").read_text(encoding="utf-8")
    assert "VERDICT:" in text, "no verdict line in docs/adr-010-test.md"
    verdict = text.split("VERDICT:", 1)[1].split("\n", 1)[0].strip()
    assert verdict.startswith("PASS"), f"ADR-010 falsifier verdict is {verdict!r}"


def test_related_work_positions_against_sacm():
    """Exit criterion 7."""
    text = (ROOT / "docs" / "related-work.md").read_text(encoding="utf-8")
    assert "SACM" in text
    assert "omg.org" in text or "doi.org" in text, "SACM is named but not cited"
```

`docs/adr-010-test.md` must therefore carry a line beginning `VERDICT: PASS` or
`VERDICT: FAIL`. Add that requirement to Task 12 Step 4 when you write it.

```python
def test_binding_pin_matches_the_ontology_version():
    """A binding pinned to a version the ontology no longer is, is a binding
    generating against a contract that moved."""
    import yaml
    m = yaml.safe_load((ROOT / "model" / "ontology.yaml").read_text(encoding="utf-8"))
    b = yaml.safe_load(
        (ROOT / "bindings" / "reference" / "binding.yaml").read_text(encoding="utf-8"))
    assert b["ontology_version"] == m["version"]
```

- [ ] **Step 5: Run everything**

```bash
pytest -q
eaont check-drift
eaont validate
grep -rn "KerML::\|SysML::" model/ && echo FOUND || echo CLEAN
```

Expected: all tests pass; no drift across 3 artefacts; shapes hold over 3 instances; `CLEAN`.

- [ ] **Step 6: Commit**

```bash
git add README.md docs/related-work.md .github/ CITATION.cff tests/test_release.py
git commit -m "docs: position against SACM, and put the three gates in CI

The programme mentioned no assurance-case prior art anywhere. An ontology
paper in this space that does not position against SACM will not survive
review."
```

---

## Phase 1 and 2 exit criteria

All of the following, verified by running them:

1. `pytest -q` green.
2. `eaont check-drift` reports `no drift across 3 generated artefacts`.
3. `eaont validate` reports `shapes hold over 3 instances`.
4. `grep -rn "KerML::\|SysML::" model/` finds nothing. (`src/` is excluded by design — `load.py` names the prefixes in order to refuse them.)
5. `tests/test_warrant.py` passes — every entity marked, nine and four.
6. `docs/adr-010-test.md` records a verdict, and it is PASS. **A FAIL here blocks Phase 3.**
7. `docs/related-work.md` positions against SACM with a verified citation.

## What this plan does not do

Phases 3–6 are separate plans and none of their work belongs here:

- The `epistemic-adequacy-metamodel` repository is **not renamed** and **not modified** by this plan. It keeps working exactly as it does today, still generating its own `ontology/` from its own `metamodel.yaml`. The two coexist until Phase 3.
- `epistemic-adequacy-spec` is untouched; `docs/ontology.md` stays stale until Phase 4.
- No write-side entity is added. That is Phase 5, and it starts with a conversation about `admissibility-spec` §2's seven undefined terms.
- `repos.yml`, `data/map.json` and the programme README still describe the world as it was. That is Phase 6.
