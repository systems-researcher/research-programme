# Triage log — research-programme map design spec

| Finding | First seen | Last seen | Verdict | Rationale |
|---------|------------|-----------|---------|-----------|
| C1 node-only node/card link contradiction (L86, L207) | R1 | R1 | Genuine | Thesis node has no card, yet diagram nodes and derived "feeds" rows were specified to anchor to cards. Fixed: node-only emits no link, and feeds/depends rows render node-only keys as plain text |
| C2 `render` both required and defaulted (L119-120) | R1 | R1 | Genuine | Self-inflicted by the pre-loop edit. Fixed: explicit required/optional split plus a permitted-values table |
| M1 `method` required in prose, absent from `--check` rule 3 | R1 | R1 | Genuine | Silent omission. Fixed: added to the required-field list |
| M2 headline attribution asserted but never validated | R1 | R1 | Genuine | Fixed structurally: `headline` is now `{text, source}`, both required, enforced by new check rule 6 |
| M3 footer needs a last-refreshed date absent from `live.json` schema | R1 | R1 | Genuine | Fixed: `live.json` shape stated as top-level `generated_at` plus a `repos` object |
| M4 `Thesis-Work-Area` entry never shown; node-only exemption unstated | R1 | R1 | Genuine | Fixed: full entry given; node-only stated to grant no validation exemption |
| A1 strand/stage sets only in YAML comments | R1 | R1 | Genuine (advisory, fixed) | Cheap and correct. Folded into the permitted-values table |
| A2 diagram claimed strand rows, build described stage subgraphs | R1 | R1 | Genuine (advisory, fixed) | Fixed: subgraph per stage, strand carried by Mermaid `classDef` |
| A3 "offending key" unreportable on a YAML syntax error | R1 | R1 | Genuine (advisory, fixed) | Fixed: error table splits syntax errors (line/column) from semantic errors (key/field) |
| A4 workflow did not state `--check` blocks the commit | R1 | R1 | Genuine (advisory, fixed) | Fixed: non-zero exit stops the workflow before commit |
| Self-caught: `depends_on` optionality described as "no incoming dependencies" | R1 | R1 | Genuine (author) | Wrong edge direction introduced by the C2 fix. Corrected during the Phase 3 self-check |

## Round 1 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| node-only link contradiction | Auditor + New-Hire | CRIT | Genuine | Fixed |
| `render` required vs defaulted | Saboteur + Auditor | CRIT | Genuine | Fixed |
| `method` missing from check | Auditor + Saboteur | MAJ | Genuine | Fixed |
| headline attribution unvalidated | Auditor + Saboteur | MAJ | Genuine | Fixed |
| live.json missing refresh timestamp | New-Hire + Auditor | MAJ | Genuine | Fixed |
| thesis entry unshown, exemption unstated | New-Hire + Auditor | MAJ | Genuine | Fixed |
| value sets only in comments | New-Hire | ADV | Genuine | Fixed |
| strand rows vs stage subgraphs | New-Hire | ADV | Genuine | Fixed |
| YAML syntax error reporting | New-Hire | ADV | Genuine | Fixed |
| check does not block commit | New-Hire | ADV | Genuine | Fixed |

Lens coverage: saboteur 3, new_hire 7, auditor 6.
Fixes applied: 11 (10 reviewer findings + 1 author self-check)
Inflation rate: 0% (0 FP/Recurring/Design of 6 CRITICAL+MAJOR)
Validation: SKIP (no executable artefact yet — spec only)

## Round 2 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| Strand 2 table has no Stage column; no derivable stage value | New-Hire | MAJ | Genuine | Fixed: all three at `evidence`, plus a note that strand picks the section and stage picks the subgraph |
| Scope count vs entry count, Thesis-Work-Area vs excluded thesis infrastructure | Auditor | ADV | Genuine | Fixed: counts stated, and the distinction between the write-up area and the LaTeX/template infrastructure spelled out |
| `owner` in the permitted-values table is not a finite set | Auditor | ADV | Genuine | Fixed: `--check` validates shape (`local` or `[A-Za-z0-9-]+`), not account existence |
| Atomic-write guarantee covered only index.html, not the README rewrite | Auditor | ADV | Genuine | Fixed: both outputs written to temp and moved |
| First run has no data/live.json; build behaviour unstated | Saboteur | ADV | Genuine | Fixed: refresh creates it; build treats absent live data as empty, warns, never blocks |
| "One source of truth" vs header/stage prose with no home | Auditor | ADV | Genuine | Fixed: `repos.yml` gains `programme` and `stages` top-level blocks; check rule 8 enforces them |
| Self-caught: repository count wrong throughout (nine, should be ten) | Author | — | Genuine | Miscount in the original draft, surfaced by the A1 fix. Corrected to ten + three = thirteen entries |

Lens coverage: saboteur 1, new_hire 1, auditor 4.
Fixes applied: 7 (6 reviewer findings + 1 author self-check)
Inflation rate: 0% (0 FP/Recurring/Design of 1 CRITICAL+MAJOR)
Validation: SKIP (spec only, no executable artefact yet)

## Round 3 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| Strand headings/subtitles have no source in the content model | New-Hire | ADV | Genuine | Fixed: `strands` top-level block added; check rule 8 extended to cover it |
| No `--check` rule rejects a cyclic or self-referencing `depends_on` | Saboteur | ADV | Genuine | Fixed: check rule 9 requires a DAG and reports the full cycle path |
| Behaviour unstated when live.json exists but lacks an entry for a key | New-Hire | ADV | Genuine | Fixed: missing live entry falls back to an "awaiting refresh" badge, never fails the build |

Lens coverage: saboteur 1, new_hire 2, auditor 0.
Fixes applied: 3
Inflation rate: 0% (0 FP/Recurring/Design of 0 CRITICAL+MAJOR)
Validation: SKIP (spec only, no executable artefact yet)

## Converged — Round 3

Track 1: Reviewer returned NO_CRITICAL_OR_MAJOR.
Total rounds: 3  |  Total fixes: 21 (19 reviewer findings + 2 author self-checks)
Cumulative inflation rate: 0% — every finding across all three rounds triaged Genuine.
Document is ready.

## Post-convergence pass (author + advisor, Round 3)

| Finding | Source | Severity | Verdict | Action |
|---------|--------|----------|---------|--------|
| R3's per-key live-data fallback overlapped R2's whole-file rule, leaving stale-for-every-key undefined | Advisor | MAJ-equivalent | Genuine | Fixed: §5 now states both missing-data cases once; footer always renders `generated_at` when the file exists |
| `Thesis-Work-Area` carried `status: design`, a study-lifecycle value on a non-study | Advisor | ADV | Genuine | Fixed: `not-applicable` added to the enum, permitted by `--check` only on `render: node-only` entries |
| Ten-repo count asserted but not re-verified after the nine-to-ten correction | Advisor | ADV | Genuine | Verified: `gh repo list systems-researcher` returns exactly 10. Provenance recorded in §2 |
| "The project's one test" understated nine check rules | Advisor | Cosmetic | Genuine | Reworded |
