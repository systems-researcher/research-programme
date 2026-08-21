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

| C1 tests/negative survives and imports deleted packages | R2 | R2 | Genuine | Verified: `tests/negative/test_failure_modes.py` imports `eamm.read.model` and `eamm.resolve.run`, reads `conformance/failure-modes.yaml`; `testpaths=["tests"]` collects it. R1's C4/M1 fix stopped one directory short. Fixed. |
| M1 pre-split-properties.txt created but never tracked | R2 | R2 | Genuine | R1's M3 fix added the baseline; no `git add` covered it and no step runs `git add -A`. Fixed in the commit, Files and Interfaces. |
| M2 final commit omits limitations.md and entities.md | R2 | R2 | Genuine | Steps 1b/1c create them; Step 6's `git add` did not name them, so Step 1c's coverage test would raise FileNotFoundError in CI. Fixed. |
| M3 sed rewrites docs/design, which Step 1b forbids editing | R2 | R2 | Genuine | Verified: one `eamm` in the design doc. Fixed by excluding `docs/design` — the occurrence is historically correct, describing the pre-split package. |
| M4 Task 2 commit omits the generators and regenerated ontology | R2 | R2 | Genuine | Steps 5b/6b edit `generate/*.py`; omitting them pushes the provenance diff into Task 3 Step 5, which asserts "nothing else may disappear". Fixed. |
| M5 cloned CI workflow runs six stripped things | R2 | R2 | Genuine | Verified: `.github/workflows/validate.yml` references npm ci, library/, check_release, java/, integration and a secrets-gated private clone. Fixed: deleted in Step 1b; Task 13 writes the replacement. |
| A1 "Four survive" precedes five filenames | R2 | R2 | Genuine (cheap) | 34 − 27 − 2 = 5. Fixed. |
| A2 grep -c understates the removal | R2 | R2 | Genuine | Turtle wraps subjects; continuation lines match neither word. Fixed: inverted match that must print nothing. |
| A3 Interfaces signature omits ontology_path | R2 | R2 | Genuine | The R1 sh:class fix added a fourth argument to all four call sites but not to the Interfaces block. Fixed. |
| A4 nothing validates the substrate level | R2 | R2 | Genuine | `lift()` reads `claims` only, so `SubstrateDeclarationShape` has no target node and a green `eaont validate` implies coverage of EA-REQ-05/06/09/11/13 that it does not have. Recorded as limitation 2. |
| A5 ten scripts, two fixtures, a sha256 and NOTICE survive unlisted | R2 | R2 | Genuine | Fixed: deleted in Step 1b, NOTICE rewritten, plus a new Step 6b sweep for anything still naming a stripped subject. |
| A6 three different refusal sets | R2 | R2 | Genuine | Step 6 and exit criterion 4 grepped two prefixes, CI three, REFUSED_PREFIXES four — the loosest becomes the real gate. Fixed: all four everywhere. |
| A7 validate branch could fall through to generate | R2 | R2 | Genuine | `main()` ends `return generate()`; a branch placed after it makes `eaont validate` regenerate and still exit 0. Fixed: ordering stated, test asserts on stdout. |
| (author) C1 edit lost by an aborting fix script | R2 | R2 | Genuine — self-caught | The R2 script wrote once at the end, so a `sys.exit` on a later pattern discarded the in-memory C1 edit. Post-fix self-check caught it; C1 re-applied and verified present. |

## Round 2 Summary

Reviewer: Opus, three lenses. lens_coverage: saboteur=5, new_hire=2, auditor=6.
Reviewer built a replica repository, applied Tasks 2-4, generated the artefacts,
and ran the lift, pyshacl and every SPARQL query.

**Round 1's fixes independently validated:** the §9.1 zero-triple claim holds
byte-for-byte; the 25-class and 50-property baselines are exact; all three
fixtures conform; the `probably_fine` negative case is correctly refused; the
ADR-010 falsifier passes; Task 4's decision rule is decidable and lands on the
duplicate branch.

Findings: 1 CRITICAL, 5 MAJOR, 7 ADVISORY = 13. Genuine 13, FP 0, Design 0.
Fixes applied: 14 (13 findings + 1 self-caught lost edit).
Inflation rate: 0% (0 of 6 CRITICAL+MAJOR triaged FP/Recurring/Design).
Validation: fences balanced (138), no duplicate step labels, limitations
numbered 1-4, every created file named in a git add, tests/negative present.

| C1 the R1 path sed matches nothing in tests and everything in the generators | R3 | R3 | Genuine — **R1 fix was inverted** | The four surviving tests build the path as `parents[1] / "metamodel" / "metamodel.yaml"`; the literal `metamodel/metamodel.yaml` appears in NO surviving test (only in two files R2 deletes) and in the three generator provenance strings. Reviewer ran Task 1 verbatim: 10 failed, 8 errors, all FileNotFoundError. Fixed: sed the segment form, scoped to `tests/`. |
| C2 Task 1 leaves ontology/ drifted and never regenerates | R3 | R3 | Genuine | Consequence of C1: the sed hit the generators, so Step 7's `check-drift` printed DRIFT on all three and exited 1. Fixed by C1's scoping, plus an explicit warning at Step 7 not to clear drift by regenerating — that would overwrite the evidence with the mistake's output. |
| C3 the R2 inverted grep can never print nothing | R3 | R3 | Genuine — **R2 fix was self-contradictory** | R2's own prose said continuation lines match neither word, then asserted the inverted match prints nothing. Measured: 9 lines. Fixed: anchor on removed subject lines (`^-ea:`), which still catches every dropped class and property. |
| M1 Step 6b's expected-survivor list is wrong and premature | R3 | R3 | Genuine | It named `REFUSED_PREFIXES` and Step 5b's comment, neither of which exists until Task 2. Real Task-1 hits are pyproject.toml, cli.py, owl.py:132, test_load.py. Fixed: real list, "justify or reword" not "delete", and deferred until after Task 2. |
| A1 the verification grep is unreachable | R3 | R3 | Genuine | `grep -rn 'metamodel' src tests \|\| echo "no stale schema path"` can never echo — `load_metamodel` and `MetamodelError` always match. That unreachable branch is precisely why C1 shipped undetected through two rounds. Fixed with C1. |

## Round 3 Summary

Reviewer: Opus, three lenses. lens_coverage: saboteur=2, new_hire=4, auditor=3.
Reviewer cloned the source repository and **executed Task 1 verbatim**. It did not
complete.

Findings: 3 CRITICAL, 1 MAJOR, 1 ADVISORY = 5. Genuine 5, FP 0, Design 0.
Fixes applied: 5.
Inflation rate: 0% (0 of 4 CRITICAL+MAJOR triaged FP/Recurring/Design).
Validation: fences balanced (140); 8 targeted assertions pass, including that
Round 2's `tests/negative` fix survived this round's edits.

**Not converged.** Verdict was ISSUES_FOUND, so Track 1 does not apply. Track 2
requires an inflation rate of 70% or more; this round's was 0%, so it does not
apply either. Two of the three CRITICALs were defects introduced by earlier
rounds' own fixes.

## Loop status after 3 requested rounds

| Round | CRIT | MAJ | ADV | Genuine | FP | Inflation | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | 4 | 5 | 8 | 17/17 | 0 | 0% | ISSUES_FOUND |
| 2 | 1 | 5 | 7 | 13/13 | 0 | 0% | ISSUES_FOUND |
| 3 | 3 | 1 | 1 | 5/5 | 0 | 0% | ISSUES_FOUND |
| **Total** | **8** | **11** | **16** | **35/35** | **0** | **0%** | **not converged** |

Plus 2 author-self-caught regressions (a tautological assertion in R1, a lost
edit in R2), fixed at the time.

35 findings, zero false positives, three rounds. The reviewer has not yet
returned a clean round, and the rate at which fixes introduce new defects — two
of Round 3's three CRITICALs were R1 and R2 fixes — argues for at least one more
round before this plan is executed.

| C1 test_load.py's enumeration count goes red at Task 3 and stays red | R4 | R4 | Genuine | Verified: `tests/test_load.py:18` asserts `len(m.enumerations) == 12`; Task 3 makes it 11 and Task 4's duplicate branch 9. Reviewer measured `assert 9 == 12`. Fixed: Step 3b and Step 4b update it, plus a full `pytest -q` before every commit from Task 3 on. |
| C2 rewording owl.py's PROV string drifts a byte-compared artefact | R4 | R4 | Genuine — **R3 M1 fix was wrong** | R3's sweep told the implementer to "reword" `owl.py:132`. It is a `Literal` inside `render_prov_alignment`, emitted as an `rdfs:comment` into `prov-alignment.ttl`. Measured: `DRIFT ontology/prov-alignment.ttl`, exit 1. Fixed: marked leave-alone, with the general rule that a string a generator emits is content, not commentary. |
| M1 sweep returns 8 files, the list names 4 | R4 | R4 | Genuine | README.md and CITATION.cff were unlisted, and the stated rule ("a hit is a file Step 1b missed — delete it") would have deleted both. Fixed: six-row table with an explicit action per hit. |
| M2 CITATION.cff listed as Modify with no step saying what | R4 | R4 | Genuine | It ships titled "Metamodel", points `repository-code` at the old repo, and carries the Airbus MPL-2.0 attribution for a model Task 1 deletes. No test reads the prose. Fixed: new Task 13 Step 5b. |
| A1 trace/ does not exist when Task 6 writes into it | R4 | R4 | Genuine | Step 1b deletes both its files and git does not track empty directories. Fixed: `mkdir -p trace`. |
| A2 ReviewStateKind::promoted's clause link would be deleted, not moved | R4 | R4 | Genuine | Task 6's sweep hits it, but spec-trace.yaml had slots only for `unresolved_fields` and `entities`. Fixed: added `enumeration_members`, since that link is why ADR-002 settled on four members. |
| A3 the VERDICT line is required by Task 13 but never specified in Task 12 | R4 | R4 | Genuine | Task 13's release test parses it; Task 12 never said to write it, and the final `git add` omitted the file. Both fixed. |
| A4 Task 2's Files list omits the generators it edits | R4 | R4 | Genuine (cheap) | Steps 5b and 6b modify `generate/owl.py` and `generate/shacl.py`. Fixed. |
| A5 Task 5 states 4 tests, block defines 5 | R4 | R4 | Genuine (cheap) | The property-diff test added in R1's M3 fix was never counted. Fixed. |
| (structural) nothing runs the full suite until Task 6 | R4 | R4 | Genuine — from the reviewer's prose | Tasks 3-5 ran single-file pytest only; Task 4 Step 6 commits `-A` having run no test. That is how C1 hid for four rounds. Fixed: `pytest -q` before every commit from Task 3 onward, red suite blocks the commit. |

## Round 4 Summary

Reviewer: Opus, three lenses. lens_coverage: saboteur=2, new_hire=3, auditor=4.
Reviewer cloned the source repository and **executed all 13 tasks to completion**.
All seven exit criteria passed — 88 tests, no drift, shapes hold over 3 instances,
CLEAN — but only after one unauthorised patch commit fixing C1.

**Every Round 3 fix held**: the segment-form sed, Step 7's drift check and Step 5's
`^-ea:` filter all behaved exactly as written.

Findings: 2 CRITICAL, 2 MAJOR, 5 ADVISORY = 9, plus 1 structural from the prose.
Genuine 10, FP 0, Design 0. Fixes applied: 10.
Inflation rate: 0% (0 of 4 CRITICAL+MAJOR triaged FP/Recurring/Design).
Validation: fences balanced (146), no duplicate step labels, 11 targeted assertions pass.

Scope caveat carried forward: the reviewer wrote related-work, limitations,
binding-contract, competency-questions, adr-010-test, ADR-012 and README as
test-satisfying stubs, so defects reachable only from full prose remain unchecked.

**Not converged** — verdict ISSUES_FOUND; Track 2 needs 70% inflation against 0%.

| M1 Task 3's commit is red in history though the tree is green | R5 | R5 | Genuine | Step 3b edits `tests/test_load.py`; Step 6's `git add` did not name it. Reviewer ran pytest at all 13 task commits: 12 green, that one red (`1 failed, 39 passed`, `assert 11 == 12`). CI is `on: [push]`. Fixed: added to the git add and both Files lists. |
| M2 Task 12's fixture prose contradicts its own test | R5 | R5 | Genuine | Prose said "five engine instances"; the JSON holds two and Step 2 asserts `len == 2`. Writing five fails the falsifier, and Step 3 then orders a full halt on a false alarm. Fixed: two, with why two is the minimum counterexample. |
| M3 Task 13 Step 1c's test has no home file | R5 | R5 | Genuine | Given with undefined `ROOT`, `SOURCE`, `load_metamodel` and no file named; Step 6's `git add` covers only `tests/test_release.py`, so a new file would stay untracked. Fixed: homed there, with imports. |
| A1 sweep table asserts a count that is wrong | R5 | R5 | Genuine | Said eight files with six rows; measured after Task 2 it returns 13, including `__pycache__` and `.egg-info` that Step 6's editable install creates. Fixed: exclude build output, add the two real rows, drop the count claim, correct `test_load.py`'s stated reason. |
| A2 .vscode/settings.json is tracked and names the old package | R5 | R5 | Genuine | Verified: it carries an `eamm fetch-pilot` task plus references to `library/`, `.pilot`, `package.json` and `metamodel/metamodel.yaml` — all deleted. The only shipped file still naming `eamm`. Fixed: deleted in Step 1b. |
| A3 the schema's own header describes a deleted artefact | R5 | R5 | Genuine | `model/ontology.yaml` still says `library/EpistemicAdequacy.sysml` is generated from it and byte-compared. Nothing sweeps `model/`, so no other check catches it — and it heads the one file the repository calls its single source of truth. Fixed in Task 2 Step 5. |
| A4 ADR-012 created but never indexed | R5 | R5 | Genuine (cheap) | Task 1 Step 1b already edits `docs/adr/README.md`, so the table is known to exist. Fixed. |
| A5 "these three" above a list of four | R5 | R5 | Genuine (cheap) | The substrate-level limitation added in R2 was never counted. Fixed. |
| A6 CITATION rewrite names three fields, misses two | R5 | R5 | Genuine (cheap) | `license-url` also points at the old repository and `keywords` still lists "SysML v2". Fixed. |

## Round 5 Summary

Reviewer: Opus, three lenses. lens_coverage: saboteur=1, new_hire=3, auditor=4.
Reviewer executed all 13 tasks verbatim on a fresh clone and then ran pytest at
**every one of the 13 task commits**.

**A verbatim run now needs zero unauthorised edits.** All 13 tasks complete: 88
tests, no drift, shapes hold over 3 instances, CLEAN, all seven exit criteria.
Round 4's C1 patch is no longer necessary. Every stated Expected matched,
including the CQ1 percent-encoding failure and the ADR-010 PASS.

**First round with no CRITICAL findings.**

Findings: 0 CRITICAL, 3 MAJOR, 6 ADVISORY = 9. Genuine 9, FP 0, Design 0.
Fixes applied: 9.
Inflation rate: 0% (0 of 3 CRITICAL+MAJOR triaged FP/Recurring/Design).
Validation: fences balanced (148), 9 targeted assertions pass.

**Not converged** — verdict ISSUES_FOUND on three MAJORs. Track 2 needs 70%
inflation against 0%.
