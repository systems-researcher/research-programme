<!--
Copyright (c) 2026 Jason D. Gower
SPDX-License-Identifier: CC-BY-4.0
-->

# Triage log — 2026-08-21-ontology-repo-phase-1-2.md

Adversarial review loop, 3 rounds requested. Reviewer: Opus, three hostile
lenses (Saboteur / New Hire / Auditor). Document: 2287 lines, 13 tasks, 82 steps.

Pre-loop check (2026-08-21): purpose/scope present; no placeholder artifacts;
122 fences balanced; all 27 `ea:` properties and all enum individuals the plan
references verified present in the generated ontology; tasks 1-13 contiguous.

| Finding | First seen | Last seen | Verdict | Rationale |
|---------|------------|-----------|---------|-----------|
| C1 sh:class on Unresolved.field rejects the lift's Literal | R1 | R1 | Genuine | `field` is typed `UnresolvedFieldKind`, so shacl.py emits `sh:class`. Reviewer ran pyshacl 0.40.1: 4 ClassConstraintComponent violations, `eaont validate` returns 1. Fixed: emit the enum individual; test compares local names. |
| C2 agnosticism grep fails on its own gate | R1 | R1 | Genuine | `load.py` must name `KerML::`/`SysML::` to refuse them, but Step 6, CI and exit criterion 4 grep `src/`. Fixed: scope to `model/`, with the reason stated so it does not read as a loophole. |
| C3 binding.yaml names SysML; its own test forbids it | R1 | R1 | Genuine | The attachment comment said "in SysML v2"; `test_binding_names_no_modelling_language` asserts absence. Fixed: reworded to "a language with an annotation mechanism"; the naming stays in binding-contract.md. |
| C4 surviving tests hardcode the moved schema path | R1 | R1 | Genuine | Nine test files reference `metamodel/metamodel.yaml`, four of them ones Step 2 forbids deleting. Step 3's sed rewrote only `eamm`. Fixed: added a path sed plus a verification grep. |
| M1 sixteen surviving tests reference deleted subjects | R1 | R1 | Genuine | Verified against the real tree: 35 test files, of which 27 must go. Fixed: full deletion list, the rule stated ("a test goes if its subject went"), five named survivors, and Step 6 widened to FileNotFoundError. |
| M2 kept-enum justification test cannot fail | R1 | R1 | Genuine | Split-to-blank-line pulled member `doc:` lines into the block, so any enum passed. Fixed: anchored regex on the enumeration-level key. |
| M3 Phase 1 diff test compares classes only | R1 | R1 | Genuine | Docstring claimed "and nothing else" while checking `owl:Class` lines alone; a dropped property was invisible. Fixed: second baseline over properties. |
| M4 test count stated as 7, collects 8 | R1 | R1 | Genuine | Parametrising over four ABSTRACT_REFS plus four unparametrised tests. Fixed. |
| M5 Task 6 forbids clause docs that Task 4 may keep | R1 | R1 | Genuine | If Task 4 keeps ProfileKind, its member docs are clause lists by definition. Fixed: exempted conformance enums, with the reason (a profile is not a domain entity). |
| A1 partial pyproject block reads as a replacement | R1 | R1 | Genuine (cheap) | Fixed: says only these keys change. |
| A2 import block replacement drops stdlib imports | R1 | R1 | Genuine (cheap) | Fixed: states argparse/pathlib/sys stay. |
| A3 "pyshacl imported nowhere" is false | R1 | R1 | Genuine — **defect in the committed design doc** | `tests/test_generate_shacl.py:62,76` call `pyshacl.validate` on hand-built fixtures. Author's original grep was truncated by `head`. Fixed in BOTH design §3.4/§7 and the plan: the real gap is that the shapes have never run over substrate-emitted instance data. |
| A4 exit criteria 6 and 7 unchecked | R1 | R1 | Genuine (cheap) | Fixed: two asserts in test_release.py; Task 12 must emit a `VERDICT:` line. |
| A5 docs/entities.md required by design §5.1, created by no task | R1 | R1 | Genuine | Fixed: Task 13 Step 1c, with a coverage test. |
| A6 docs/design deleted though the ADR README cites it | R1 | R1 | Genuine | Fixed: retained with a status note; body left unedited, since a rewritten source is no longer the source cited. |
| A7 CC-BY header never requested for new docs | R1 | R1 | Genuine (cheap) | Fixed in all three creating steps. |
| A8 generated artefacts cite a path the repo lacks | R1 | R1 | Genuine | Both generators emit "Generated from metamodel/metamodel.yaml". Fixed: new Step 6b, ordered before the byte-compare so §9.1's test is not obscured by this edit. |
| (author) tautological assertion introduced by the M3 fix | R1 | R1 | Genuine — self-caught | Phase 3 self-check found `assert ... or True` in the new property test. Removed. |

## Round 1 Summary

Reviewer: Opus, three lenses. lens_coverage: saboteur=5, new_hire=6, auditor=7.
Reviewer independently ran pyshacl 0.40.1 against the real shapes.ttl to confirm C1.

Findings: 4 CRITICAL, 5 MAJOR, 8 ADVISORY = 17. Genuine 17, FP 0, Design 0.
Fixes applied: 18 (17 findings + 1 self-caught regression).
Inflation rate: 0% (0 of 9 CRITICAL+MAJOR triaged FP/Recurring/Design).
Validation: fences balanced (136), no stale `model/ src/` greps, no `Literal(field)`.
