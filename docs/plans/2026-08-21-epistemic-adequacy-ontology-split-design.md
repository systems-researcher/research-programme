<!--
Copyright (c) 2026 Jason D. Gower
SPDX-License-Identifier: CC-BY-4.0
-->

# Design: extracting the epistemic adequacy ontology

**Date:** 2026-08-21
**Repos affected:** `epistemic-adequacy-ontology` (new),
`epistemic-adequacy-spec` (→ v0.2.0),
`epistemic-adequacy-metamodel` (→ renamed `epistemic-adequacy-sysml-v2-binding`),
`admissibility-spec` (unblocked), `research-programme` (map, `repos.yml`)
**Status:** design approved 2026-08-21, not yet implemented

---

## 1. Purpose

Separate the **vocabulary** of epistemic adequacy from its **SysML v2
realisation**, so that the entity model can be stated, published and bound to
other languages without carrying SysML v2 assumptions, and so that the released
specification stops shipping a superseded copy of it.

Three outcomes:

1. One vocabulary, owned in one place, that both the read-side and write-side
   specifications quantify over.
2. A language-independence claim that is **demonstrable** rather than asserted,
   because a second binding exists and a validation gate runs.
3. A publishable ontology contribution that is not merely the specification's
   data model in OWL clothing.

## 2. Scope

**In scope.** The conceptual entity model, its OWL 2 and SHACL serialisation,
the contract a binding must satisfy, one minimal reference binding, the SysML v2
binding as it exists today, and the repository and programme bookkeeping that
follows.

**Out of scope.** The toolkit (`epistemic-adequacy-toolkit`) is unchanged. The
three architecture candidates are unchanged by this work — their misalignment to
the eighteen clauses is recorded in §11.5 as a pre-existing condition, not fixed
here. No clause text changes.

**Explicitly not built** (YAGNI, revisit only on evidence):

- A UML binding. The minimal reference binding is sufficient to demonstrate
  language-independence; UML is a stronger *contrast* for the binding paper and
  can be added when that paper is written.
- A separate repository for the reference binding. It is a conformance fixture,
  and a repository for a test fixture is overhead on a programme already at
  sixteen.
- Upper-ontology alignment (BFO, DOLCE). Required for an ontology-venue
  submission; not required for the layering chosen in §4.
- A SPARQL query surface. `library/Queries.sysml` already records that the
  executable SPARQL form is deferred; nothing here changes that.

## 3. The findings that force this

Every claim in this section was verified against the working trees on
2026-08-20 and 2026-08-21. Each is falsifiable by the command that produced it.

### 3.1 The released specification ships a superseded entity model

`epistemic-adequacy-spec/docs/ontology.md` was drafted **2026-05-13** in the
doctoral working papers and migrated into the specification **2026-08-18**. It is
a required file in the release gate (`scripts/check_release.py:49`) of a
repository released at **v0.1.0**. It defines fifteen entities. Against the
thirteen OWL classes the metamodel generates:

| | Count | Examples |
|---|---|---|
| Survive by name | 2 | `EpistemicStatus`, `Agent` |
| Renamed without the document recording it | 4 | `DerivationChain`→`Derivation`, `LinkedEvidence`→`EvidenceAnchor`, `ProvenanceRecord`→`Provenance`, `ContributionRecord`→`Entry` |
| No counterpart anywhere | 9 | `SubstrateCompleteness` (the entity carrying EA4), `ModelContent`, `GovernanceMetadata`, `ConsumptionQuery`, `ParticipationAction`, `ContributionGovernance`, `QuarantineArea`, `Substrate`, `EpistemicAdequacy` |
| Invented in the metamodel, absent from the ontology | 7 | `GovernedClaim`, `SubstrateDeclaration`, `Criticality`, `StandingChange`, `Unresolved`, `ConflictCheck`, `Method` |

`epistemic-adequacy-metamodel/docs/design/2026-08-19-metamodel-design.md` §3.3
additionally records that `docs/ontology.md` §6.2 asserts `hasEpistemicStatus` at
1..1 globally, which "would oblige a status on every attribute in the model" —
that is, the released document carries an assertion the programme knows to be
wrong.

**This is a defect in a published output today.** It is repaired as part of this
work (§5.3) and would need repairing even if the split were abandoned.

### 3.2 The seam is already visible in the generated ontology

`metamodel/metamodel.yaml` types seven parameters against the SysML v2 and KerML
metamodels:

| Parameter | Declared type |
|---|---|
| `Derivation.upstream` | `KerML::Element` |
| `Derivation.alternatives` | `KerML::Element` |
| `Derivation.expression` | `KerML::Function` |
| `ConflictCheck.subject` | `KerML::Element` |
| `ConflictCheck.competing` | `KerML::Element` |
| `ConflictCheck.constraint` | `KerML::Predicate` |
| `SubstrateDeclaration.statusVocabulary` | `SysML::EnumerationDefinition` |

The OWL generator emits **no `rdfs:range`** for exactly these seven properties,
and for no others. Verified by grepping each property's block in
`ontology/epistemic-adequacy.ttl`: all seven return zero `rdfs:range` triples.

The agnostic layer is therefore already lossy at precisely the binding seam, and
silently so. Extraction makes that boundary explicit instead of implicit.

### 3.3 Nothing evaluates the SysML-typed references, so they abstract cleanly

The concern that `expression: KerML::Function` and `constraint: KerML::Predicate`
require an *evaluable* SysML construct — which would make the data model
irreducibly SysML-shaped — does not survive checking:

| Clause | What the check actually does |
|---|---|
| EA-REQ-02 | Check text: "an expression whose **inputs** are themselves resolvable claims". Resolution, not evaluation |
| EA-REQ-14 | `eakit/checks/ea4.py:44` reads `basis`, `derivation`, `status`, `provenance` and tests each for `is ABSENT`. No expression is touched |
| EA-REQ-15 | `eakit/checks/ea4.py:63` decides conflict by `s.value != claim.value` plus membership in `q.conflicts()`. The predicate is **never evaluated** |

All seven parameters reduce to element references or named handles. A store with
no modelling language — a graph, a relational schema, plain JSON — can honour
them with an identifier. **The logical data model is genuinely agnostic-able**,
which is what permits the cut line chosen in §5.

The genuinely SysML-bound material is the hand-written *behaviour*:
`library/Derivations.sysml` types against `ISQ::ForceValue`, and
`library/Constraints.sysml` documents `WithinTolerance` as stated in two bounds
"rather than an absolute value, **which the expression language does not
supply**". Schema is agnostic; behaviour is per-binding.

### 3.4 The ontology layer has no validation gate

`pyproject.toml:6` declares `pyshacl>=0.26` as a **runtime dependency**. It is
imported nowhere. `rdflib` appears only in `src/eamm/generate/owl.py` and
`src/eamm/generate/shacl.py` — emitters, never parsers. There is no
`pyshacl.validate()` call and no instance data to run one against.

The SHACL shapes are generated, byte-compared against a fresh render, and never
executed. That is adequate while the ontology is a subdirectory of a repository
whose real gate is the Apollo regression. It is **not** adequate for a standalone
artefact whose entire claim is language-independence.

### 3.5 The second binding does not yet exist in any form

`grep -ri "EA-REQ"` across `SysML-v2-API-Services`, `sysml-v2-metadata-graph` and
`sysml-v2-governed-substrate` returns **zero hits**, as does a search for
`epistemic-adequacy-spec` or "eighteen clauses". All three speak AC1–AC8 and
SR1–SR7, from the earlier candidate-architectures working document. The three
repositories date from 6–9 July 2026; `SPEC.md` v0.1.0 is dated 18 August 2026.

The architecture candidates therefore **predate the specification and are not
evidence of a live multi-binding requirement.** Any argument for this split that
rests on "Arch-B already needs it" is false and is not made here.

### 3.6 The write-side vocabulary slot is empty, right now

`admissibility-spec/SPEC.md` is 42 lines at **v0.0.0**. §2 reads in full:

> Terms. To be defined: contribution, author, warrant, review standing,
> admission, companion namespace, promotion.

Its own README states that the three architecture candidates "each invent their
admission conditions independently, because no specification states them" — the
same drift this design exists to prevent, one strand over, about to happen a
second time. Extending the ontology to the write side costs little **now** and
much later.

## 4. Layering and authority

The ontology is **conceptually prior**. The specification is **normatively
authoritative**. Where they disagree, `SPEC.md` governs.

```
epistemic-adequacy-ontology          entities, axioms, binding contract
        |  clauses quantify over it       (conceptually prior)
        v
epistemic-adequacy-spec              the 18 clauses  <-- GOVERNS
        |  realised by
        v
epistemic-adequacy-sysml-v2-binding  |  bindings/reference/  |  (uml, graph, ...)
```

This is ADR-006's formula applied one level up. That ADR already rules on the
same question between the ontology and the data model: *"Authority here is
editorial, not conceptual. The ontology remains conceptually prior."* The
programme is consistent with itself in adopting the same split here.

**Why not ontology-governs.** Logical priority genuinely runs ontology → spec: a
requirement constrains a domain, and the domain must be characterised before it
can be constrained. But an ontology that answers to nothing outside itself has no
falsifier — it defines its own domain. Below the specification it is falsifiable,
because the specification supplies the test. The empirical case is decisive and
local: `docs/ontology.md` *was* ontology-first, conceptually prior, genuinely
implementation-agnostic, and ungated, and it rotted in fourteen weeks (§3.1).

**Why not spec-governs alone.** Spec-first has a visible failure mode in the
record: ADR-002 sets the review vocabulary at four members because "four members
are the minimum that makes the clause checkable" — a clause deciding an
ontological question — and ADR-008 introduces `GovernedClaim` and then states
that it "is not epistemic metadata." Under spec-governs alone, nothing would
notice.

**What the split reading buys.** It obliges the marking in §4.1, which neither
pure position produces.

### 4.1 Domain warrant versus decidability service

Every entity is declared in one of two categories, in `docs/warrant.md`, with the
clause named for the second:

| Category | Count | Entities |
|---|---|---|
| **Domain warrant** — argued on their own terms | 9 | `Agent`, `Method`, `Provenance`, `EpistemicStatus`, `EvidenceAnchor`, `Derivation`, `Criticality`, `StandingChange`, `Entry` |
| **Decidability service** — exist so a clause is checkable | 4 | `GovernedClaim` (ADR-008), `SubstrateDeclaration` (ADR-007), `Unresolved` (EA-REQ-12), `ConflictCheck` (EA-REQ-15) |

This marking is the ontology's contribution, not bookkeeping: *what the domain
requires* and *what machine-decidability additionally requires* are different
questions, and the answer to the second is the interesting one. It is also the
strongest available response to a reviewer holding OMG SACM, because it is a
result rather than a class diagram.

## 5. Repository layout after the split

### 5.1 `epistemic-adequacy-ontology` (new)

```
model/ontology.yaml           sole hand-edited source (was metamodel/metamodel.yaml)
ontology/
  epistemic-adequacy.ttl      generated - OWL 2
  shapes.ttl                  generated - SHACL
  prov-alignment.ttl          generated - PROV-O
bindings/reference/
  binding.yaml                the type map for the reference binding
  instances/*.json            claim-graph instances - the SHACL fixture
src/eaont/
  generate/{owl,shacl,prov}.py   moved from eamm, mechanism unchanged
  validate.py                 NEW - JSON to RDF lift, then pyshacl over instances
  cli.py                      eaont generate | check-drift | validate
docs/
  entities.md                 the entity model
  warrant.md                  §4.1 - the nine-versus-four marking
  binding-contract.md         what a binding must supply. The paper's contribution
  competency-questions.md     one per clause-relevant query
  related-work.md             SACM, PROV-O, nanopublications, SEPIO, Toulmin
  adr/                        the ontological ADRs (§6.3)
trace/spec-trace.yaml         entity to clause served, or "domain warrant"
```

Licence follows the specification: prose CC-BY-4.0, code and generated artefacts
MIT.

### 5.2 `epistemic-adequacy-sysml-v2-binding` (renamed)

Keeps everything that is about SysML v2, which is most of the current repository:
`library/` (now generated from the pinned ontology plus a type map), the
hand-written `Derivations`/`Constraints`/`Queries`, `src/eamm/` reader → resolver
→ extractor and the `eamm` CLI, `models/` and the Apollo reference pair, `java/`
and pilot provisioning, `trace/clause-trace.yaml`, and all five findings
documents (conformance claim, gap register, annotation burden, round-trip loss,
one-claim-five-representations).

Gains `type-map.yaml` — the SysML v2 answer to the binding contract:

```yaml
ontology_version: "0.1.0"
types:
  ElementRef:     "KerML::Element"
  ExpressionRef:  "KerML::Function"
  PredicateRef:   "KerML::Predicate"
  VocabularyRef:  "SysML::EnumerationDefinition"
enumerations:
  RevisionSchemeKind: [gitCommit, apiCommit, tag]
defaults:
  revision_scheme: gitCommit
```

### 5.3 `epistemic-adequacy-spec` (→ v0.2.0)

`docs/ontology.md` becomes a normative pointer to the ontology repository at a
pinned version. The file remains, because `check_release.py:49` requires it; its
stale content does not. The glossary is aligned to ontology terms. The authority
statement is restated per §4.

Version 0.2.0 rather than 0.1.1: acquiring a normative dependency on an external
artefact is structural, even though no clause text changes.

### 5.4 The reference binding is not a repository

It lives at `bindings/reference/` inside the ontology repository, labelled a
**conformance fixture, not a production binding**. Its job is to be the instance
data the SHACL gate runs against, and to demonstrate that a substrate with no
modelling language can satisfy the binding contract. Making it a repository would
add a sixteenth entry to the programme map for a test fixture.

## 6. What moves

### 6.1 Purification of `ontology.yaml`

Three changes to what is today `metamodel.yaml`:

1. **The seven typed parameters** (§3.2) become abstract: `ElementRef`,
   `ExpressionRef`, `PredicateRef`, `VocabularyRef`. Safe per §3.3. Each binding
   supplies the concrete type through its type map.
2. **`RevisionSchemeKind` leaves** for the binding. Its member `apiCommit` is
   documented in-file as "A SysML v2 API service commit identity" — it was never
   ontology. `default_revision_scheme: gitCommit` leaves with it.
3. **`ProfileKind` and `CriticalityPolicyKind` are checked, then deleted or
   moved.** Both appear to duplicate what `conformance/profiles.md` and
   `clauses.yaml`'s per-profile strength map already own in the specification. If
   they are duplicates they are deleted, not relocated. **This check is a task in
   the plan, not an assumption of this design.**

`UnresolvedFieldKind` splits. The concept "a declared gap occupying field F" is
ontology; every member's doc string currently reads as a clause consequence
("Fails EA-REQ-10", "Satisfies EA-REQ-01"), and those consequences belong to the
specification. The enumeration stays; the consequence prose moves to
`trace/spec-trace.yaml`.

### 6.2 Write-side entities

Added to serve `admissibility-spec` §2's undefined terms, and marked
**hypothesis** in `docs/warrant.md` because EA5 and its three clauses carry that
label in `SPEC.md`. `Entry` already covers part of this ground and is extended
rather than duplicated. The precise entity set is settled with the
`admissibility-spec` author as the first task of Phase 5, not fixed here.

### 6.3 ADRs follow their subject

Ten of the eleven ADRs move to the ontology repository, because their subject is
the entity model or the generation architecture, both of which move: 001 (origin
is not agent kind), 002 (four-member review state), 003 (criticality has three
states), 004 (evidence excludes access status), 005 (superseded is not a
standing), 006 (L2 is the generation source), 007 (the metamodel is two-level),
008 (the governed claim marker), 009 (status rank order is total), and 011
(absent criticality relaxes).

ADR-008 is the exemplar of the decidability-service category and is cited by
`docs/warrant.md`. **It is not duplicated.** A design whose purpose is to end a
two-copy drift cannot itself ship a decision record in two places; the binding
repository cross-references it at its new home.

**ADR-010 stays with the SysML v2 binding** — the only one that does. Usage-level
claim anchoring was decided by how SysML v2 idiomatically renders five F-1
engines — one usage with multiplicity 5 — and the ADR concedes that "where five
instances genuinely differ in standing, this metamodel cannot say so." That is a
language shape constraining what the model can express, and it is the live
falsifier of this whole design (§11.1).

## 7. Gates

| Gate | Repo | Status | Mechanism |
|---|---|---|---|
| Generated TTL equals render(`ontology.yaml`) | ontology | exists | byte-compare, `eaont check-drift` |
| **SHACL validates reference-binding instances** | ontology | **NEW** | JSON to RDF lift, then `pyshacl` |
| Competency questions answered over the fixture | ontology | NEW | one assertion per question |
| Generated `.sysml` equals render(pinned ontology + type map) | sysml binding | NEW | byte-compare, same mechanism |
| `ontology_version` pin matches the resolved ontology | sysml binding | NEW | CI assertion |
| Apollo regression green | sysml binding | exists | unchanged; see §10 |
| Spec's pinned ontology version matches the ontology version | cross-repo | NEW | CI assertion |

The SHACL gate is the one that matters. It is what converts the ontology from
generated Turtle nobody executes into an artefact with a falsifier, and it uses
shapes that already exist and a dependency that is already declared.

## 8. Papers and boundaries

`publications/README.md` records `status: none` for every row but the probe, so
the boundaries are still free to set.

| Paper | Claims | Depends on |
|---|---|---|
| **Ontology** | The entity model; the domain-warrant versus decidability-service result (§4.1); the binding contract | Needs the reference binding to exist, or "language-independent" is asserted rather than shown |
| **Specification** | The eighteen clauses, profiles, conformance | Already largely the NIER paper |
| **SysML v2 binding** | Annotation burden per governed claim; round-trip loss; what the language cannot carry | Strongest with a second *real* binding for contrast; adequate with one plus the reference fixture |

**The ontology paper's positioning is unwritten and is a risk, not a task already
done.** `grep -ril "SACM\|assurance case\|Toulmin\|nanopublication\|GSN"` across
the spec, metamodel and publications repositories returns nothing outside `.venv`
and `.git` noise. OMG SACM is a standardised metamodel for claims, evidence and
argumentation with a MOF/UML realisation; an ontology paper in this space that
does not position against it will not survive review. `docs/related-work.md` in
the new repository exists to discharge this.

## 9. Sequencing

| Phase | Work | Done when |
|---|---|---|
| 1 | Create the ontology repository. Move and purify `ontology.yaml`, move generators and ontological ADRs | `eaont check-drift` reports no drift; the generated TTL differs from today's by exactly the removals in §9.1 and nothing else |
| 2 | Reference binding, JSON to RDF lift, `pyshacl` gate, competency questions | `eaont validate` passes over the fixture; **the ADR-010 test (§11.1) has a recorded answer** |
| 3 | Rename to `epistemic-adequacy-sysml-v2-binding`. Add `type-map.yaml`, regenerate `library/` from the pinned ontology | Generated `.sysml` byte-matches; **the full Apollo regression is green** |
| 4 | Spec to v0.2.0: pointer, glossary, authority statement | Release gate passes; `validate_manifest.py` passes; no clause text changed |
| 5 | Write-side entities; hand `admissibility-spec` its vocabulary | `admissibility-spec` §2 terms resolve to ontology entities |
| 6 | Programme bookkeeping: `repos.yml`, `data/map.json`, README table, publications table | `python -m scripts.build --check` passes; `python -m pytest` green |

**Phase 2 precedes Phase 3 deliberately.** The reference binding is where the
ADR-010 test runs. If it fails, the layering needs revisiting, and finding that
out before renaming a pushed repository is cheaper than after.

### 9.1 The expected diff to the generated ontology, in Phase 1

Abstracting the seven typed parameters (§6.1 item 1) is **provably OWL-neutral**:
the generator already emits no `rdfs:range` for any of them (§3.2), so replacing
`KerML::Element` with `ElementRef` changes the YAML and not one triple of the
Turtle. That removes most of the risk from the largest-sounding change in this
design, and it makes Phase 1 verifiable by byte-compare rather than by review.

The generated TTL should therefore differ from today's by exactly these removals
and nothing else:

| Removed | Because |
|---|---|
| `ea:RevisionSchemeKind` and its three members | Moves to the binding (§6.1 item 2) |
| `ea:SubstrateDeclaration_revisionScheme` | Its type left with it |
| `ea:ProfileKind`, `ea:SubstrateDeclaration_profileClaimed` | Only if §12.1 confirms the duplication |
| `ea:CriticalityPolicyKind`, `ea:SubstrateDeclaration_criticalityPolicy` | Only if §12.1 confirms the duplication |

Any other difference is a defect in the move, not an intended consequence of it.
Write-side additions (§6.2) land in Phase 5 and must not appear here.

## 10. Success criteria

1. `eaont check-drift` and `eaont validate` both pass in the ontology
   repository, the latter over real instance data.
2. The SysML v2 binding's **full Apollo regression passes unchanged** — 274 tests
   with all three tiers provisioned. This is the proof the refactor preserved
   behaviour; a passing generation gate alone is not.
3. `docs/conformance-claim.md`, `docs/annotation-burden.md` and
   `docs/round-trip-loss.md` report the same numbers as before the split, or the
   difference is explained.
4. `epistemic-adequacy-spec` passes its release gate at v0.2.0 with no clause
   text changed and no stale entity model in `docs/ontology.md`.
5. `admissibility-spec` §2 names ontology entities instead of an empty list.
6. `python -m scripts.build --check` and `python -m pytest` pass in
   `research-programme`.
7. Every entity in the ontology is either marked domain warrant or names the
   clause it serves. No unmarked entities.

## 11. Risks carried

### 11.1 ADR-010 is the live falsifier

Claim-anchoring granularity was set by a SysML v2 idiom. If the reference binding
wants per-instance standing and the ontology cannot express it, then the
anchoring model is SysML-shaped, the ontology is not agnostic, and
ontology-conceptually-prior stops being a stance and becomes a requirement.
**Tested explicitly in Phase 2 and recorded either way.** It costs a page.

### 11.2 The write-side entities rest on an untested hypothesis

EA5 and EA-REQ-16/17/18 are labelled `hypothesis` in `SPEC.md`, and the label is
not decorative. Write-side entities inherit that status and are marked in
`docs/warrant.md`. If EA5 is revised by experiment, they change.

### 11.3 A version pin becomes load-bearing

Cross-repository generation replaces a single-repository build. The SysML
binding's library is only correct with respect to a pinned ontology version, and
the specification only cites a pinned version. Three CI assertions (§7) replace
what was one in-repository byte-compare. This is a real reduction in tightness,
accepted in exchange for a single vocabulary.

### 11.4 The rename ripples

`epistemic-adequacy-metamodel` is pushed to `systems-researcher` and is currently
three commits ahead of origin. References: six files in `research-programme`, two
in `epistemic-adequacy-under-pressure-probe`, one each in
`epistemic-adequacy-toolkit` and `publications`. Ten files. GitHub redirects the
old URL, so the cost is bookkeeping, not breakage — but `repos.yml` keys and
`depends_on` edges must be updated together or `scripts/build.py` will fail its
own check.

### 11.5 The architecture candidates remain misaligned

Arch-A, B and C speak AC1–AC8 and SR1–SR7 and carry zero EA-REQ references
(§3.5). This design does not fix that, and does not depend on it being fixed. It
is recorded here because it will surface as soon as any of those repositories is
picked up, and because it is the reason the reference binding — not Arch-B — is
the second binding.

## 12. Open questions

1. **Are `ProfileKind` and `CriticalityPolicyKind` duplicates?** §6.1 assumes
   they are; Phase 1 must confirm against `conformance/profiles.md` and
   `clauses.yaml` before deleting anything.
2. **What form does the reference binding take** — plain JSON, or a small
   relational schema? JSON is closer to the canonical claim graph the toolkit
   already consumes and is therefore cheaper; a relational form is a stronger
   demonstration. Decide at the start of Phase 2.
3. **Does the ontology repository go public at creation, or on first
   publication?** The specification is public; the metamodel is private. No
   dependency forces either.

## 13. Rejected alternatives

**Split at L1 only** — the ontology repository takes the OWL and SHACL, and
`metamodel.yaml` stays with the SysML binding. Rejected: with the ontology below
the specification as a shared vocabulary, the vocabulary cannot live downstream of
one binding. The specification would be citing terms owned by the SysML
repository.

**No split; a `bindings/` directory in one repository.** Cheapest, and it keeps
every gate in one place. Rejected: it yields no independently citable artefact,
which is the stated motivation, and the repository becomes a monolith carrying
the ontology, three bindings and a pilot toolchain.

**Ontology above the specification, as domain theory the clauses operationalise.**
Strongest as a standalone academic artefact and the easiest to position against
SACM. Rejected on two grounds: it removes the ontology's only falsifier (§4), and
the empirical case against it is local and decisive — `docs/ontology.md` was
exactly this and rotted in fourteen weeks. Revisit if the target venue becomes an
ontology venue, accepting the additional programme of upper-ontology alignment
and multi-domain evaluation that implies.

**UML as the second binding.** A better contrast for the binding paper than a
minimal fixture. Deferred, not rejected: it costs weeks and a toolchain, and
language-independence is demonstrable without it.

**Realigning Arch-B (Neo4j) as the second binding.** Would fix §11.5 at the same
time and is the hardest test of agnosticism. Deferred: it pulls
architecture-strand effort forward and is disproportionate to the claim being
demonstrated.

**Moving `canonical-claim-graph.schema.json` from the toolkit to the ontology.**
Superficially attractive — a schema defining what a claim graph is looks like
ontology. Rejected: three repositories depend on the toolkit's editable-install
contract, and `TOOLKIT_PIN` is recorded in `docs/conformance-claim.md`. The
validation gate this design wants is obtained by shipping SHACL that validates
claim-graph instances, with the schema staying where it is.
