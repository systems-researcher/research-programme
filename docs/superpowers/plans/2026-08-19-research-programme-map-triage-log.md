# Triage log — research-programme map implementation plan

| Finding | First seen | Last seen | Verdict | Rationale |
|---------|------------|-----------|---------|-----------|
| C1 URL-audit one-liner is a verified SyntaxError | R1 | R1 | Genuine | Introduced by my own earlier "hardening" of a fragile grep. Replaced with tests/check_external_links.py, which also asserts the allowed-host set |
| C2 refresh expected output arithmetically impossible | R1 | R1 | Genuine | Step claimed 10 refreshed AND three stale while also saying local entries are never queried. Rewritten: clean run is 10 refreshed, nothing on stderr |
| C3 authored README documents `python scripts/refresh.py` (ImportError) | R1 | R1 | Genuine | The plan's own Notes say scripts run as modules. README and spec §7 both corrected to `python -m` |
| M1 total gh failure still stamps a fresh generated_at | R1 | R1 | Genuine | Worst finding of the round: the page would publish a last-refreshed date describing no data. Added total_failure(), exit 1, live.json untouched, plus two tests and a spec §8 case |
| M2 all three strand classDefs identical; test passed vacuously | R1 | R1 | Genuine | Strand is carried by colour, so identical palettes erased it silently. STRAND_STYLE table added; new test asserts the three styles differ |
| M3 eye-check "arrows run earlier to later" falsified by the plan's own edges | R1 | R1 | Genuine | Reworded to name both deliberate backwards edges (spec depends on probe; Arch-B depends on Arch-A) |
| M4 nested fence truncates the authored README | R1 | R1 | Genuine | The markdown block contains a bash block. Outer fence changed to four backticks |
| M5 render:node-only unrestricted, so any study could be hidden | R1 | R1 | Genuine | Spec §4 claimed this was impossible; nothing enforced it. Rule 5 extended to reserve node-only for the terminus, with a test |
| A1 within-stage order alphabetical, so architecture reads A, C, B | R1 | R1 | Genuine (advisory, fixed) | Tie-break changed to authored order in repos.yml; test locks it |
| A2 folded scalars leave newlines inside rendered tags | R1 | R1 | Genuine (advisory, fixed) | _tidy() helper applied to every authored string |
| A3 build.py never catches RenderError | R1 | R1 | Genuine (advisory, fixed) | Caught, printed to stderr, exit 1 |
| A4 card titles used h3, same level as the stage headings containing them | R1 | R1 | Genuine (advisory, fixed) | Cards render h4 |
| A5 external links unmarked despite spec §6 | R1 | R1 | Genuine (advisory, fixed) | Arrow glyph plus screen-reader text; test asserts both |
| A6 spec names one LICENSE, plan creates two, MIT text not supplied | R1 | R1 | Genuine (advisory, fixed) | MIT text inlined; spec §5 layout reconciled |
| A7 description pulled into live.json but never rendered | R1 | R1 | Genuine (advisory, fixed) | LIVE_FIELDS cut to what the page renders (visibility, pushed_at); spec §4 shape updated |
| Self-caught: `import html` given as prose, not shown as code | R1 | R1 | Genuine (author) | Found by reconstructing the repo — extraction and a literal reader both miss it. Now shown as a code block |
| Self-caught: render test count stated 16, actual 15 | R1 | R1 | Genuine (author) | Added the missing authored-order test, bringing it to a real 16 |
| Self-caught: build.py assembled by prose across three tasks | R1 | R1 | Genuine (author) | A literal reader cannot reconstruct it unambiguously. Task 8 Step 5 now gives the complete final file |

## Round 1 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| URL-audit one-liner SyntaxError | Saboteur + New-Hire | CRIT | Genuine | Fixed |
| refresh expected output impossible | Saboteur + New-Hire | CRIT | Genuine | Fixed |
| README documents a command that ImportErrors | New-Hire + Auditor | CRIT | Genuine | Fixed |
| total gh failure stamps a false timestamp | Saboteur + Auditor | MAJ | Genuine | Fixed |
| strand classDefs identical, test vacuous | Auditor | MAJ | Genuine | Fixed |
| eye-check contradicted by authored edges | Saboteur + New-Hire | MAJ | Genuine | Fixed |
| nested fence truncates the README | New-Hire | MAJ | Genuine | Fixed |
| node-only could hide any study | Saboteur + Auditor | MAJ | Genuine | Fixed |
| seven advisories (ordering, whitespace, RenderError, headings, link marking, licences, unused live field) | Auditor / Saboteur / New-Hire | ADV | Genuine | All fixed |
| three author self-checks (missing import, wrong test count, build.py assembly) | Author | — | Genuine | Fixed |

Lens coverage: saboteur 6, new_hire 5, auditor 8.
Fixes applied: 18 (15 reviewer findings + 3 author self-checks)
Inflation rate: 0% (0 FP/Recurring/Design of 8 CRITICAL+MAJOR)
Validation: PASS — repository reconstructed from the plan and executed: 40 tests pass (18/16/6, matching the stated counts), `--check` reports 13 entries and nine rules passing, the mutation script bites on all three mutations, the link audit reports 10 URLs across 2 allowed hosts, and the built page shows architecture cards in A/B/C order, three distinct strand palettes, and the thesis as a node with no card and no anchor.

## Round 2 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| T5S4 checks `git status` on an untracked repos.yml; the stated recovery `git checkout` errors | Saboteur | MAJ | Genuine | Fixed: Task 5 reordered so the commit precedes the mutation proof, which is what makes `git checkout` a real recovery path. Mutation proof committed separately |
| T6S7 `git diff --stat README.md` is vacuous before the file is tracked, and `--stat` cannot show which lines changed | Saboteur | ADV | Genuine | Fixed: direct inspection of the marker block plus a prose-intact grep; the git diff check applies from the next build onward |
| `pushed_at` collected into live.json but never rendered, against spec §4; the test name claimed otherwise | Auditor | ADV | Genuine | Fixed: rendered as a "last commit" badge, with a test. Both live fields are now shown |
| A strand whose members are all node-only emits a heading and subtitle with no cards | Saboteur | ADV | Genuine | Fixed: a card-less strand names its entries in a line instead. Test asserts the objective appears and no card is emitted |
| Local branch is `master`; Task 9 expects `main` | New-Hire | ADV | Genuine | Fixed: `git branch -M main` in Task 1 Step 1, with a verification command. The working repository was renamed too |
| Task 1 Files list claims a README no Task 1 step writes | New-Hire | ADV | Genuine | Fixed: removed, with a note that it belongs to Task 6 |
| Palette test proves distinctness but not coverage; a new strand would KeyError | Auditor | ADV | Genuine | Fixed: the test now asserts `set(STRAND_STYLE) == set(mapdata.STRANDS)` |

Lens coverage: saboteur 3, new_hire 2, auditor 2.
Fixes applied: 7
Inflation rate: 0% (0 FP/Recurring/Design of 1 CRITICAL+MAJOR)
Validation: PASS — repository reconstructed and executed again: 42 tests pass (18 mapdata, 18 render, 6 refresh, matching the stated counts); the build renders with and without live.json; the "last commit" badge appears when live data is present; the Assembly section names the thesis rather than standing empty; the link audit still reports 10 URLs across 2 allowed hosts.

## Round 3 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| Eye-check named two backward edges; the real classification is 16 forward, 5 same-stage, 2 backward, and one named edge is same-stage not backward | Saboteur | MAJ | Genuine | Half-finished Round 1 fix. Independently recomputed from repos.yml: 23 edges, 16/5/2 exactly. Both real backward edges now named (spec→probe, metamodel→toolkit), the same-stage one reclassified, and metamodel→toolkit documented in the card prose |
| Expected failure is ModuleNotFoundError; the real error is ImportError | Saboteur | ADV | Genuine | Fixed, with the reason: `scripts` exists from Task 1, so only the name is missing |
| Rule-2 test vacuous — rule 8's message satisfies both asserted substrings | Auditor | ADV | Genuine | Fixed by adding the stage to the fixture's stages block and asserting on "not one of". Verified by deletion: removing rule 2's stage check now fails exactly that test, where before it stayed green |
| Mutation proof exercised rules 2 and 7 only; a broken edge had no end-to-end proof | Auditor | ADV | Genuine | Fixed: fourth mutation rewrites a depends_on to a non-existent key. Verified — all four mutations now bite |
| Files lists omit mutate_check.py, check_external_links.py and Task 9's README edit; Task 6 says Modify for a file it creates | New-Hire | ADV | Genuine | All four lists corrected |
| Task 1 cites a `git init` the plan never runs | New-Hire | ADV | Genuine | Precondition stated, with a guarded `git init` for a from-nothing start |
| Spec §5 and §9 still showed `python scripts/build.py --check`, which the plan calls broken | Auditor | ADV | Genuine | Both corrected to module invocation; no path-form command remains in the spec |

Lens coverage: saboteur 2, new_hire 2, auditor 3.
Fixes applied: 7
Inflation rate: 0% (0 FP/Recurring/Design of 1 CRITICAL+MAJOR)
Validation: PASS — 42 tests pass (18/18/6); the mutation script now bites on four mutations including the dangling-edge one; the rule-2 test was mutation-tested and confirmed non-vacuous.
