# Case: new-feature-real-artifact-versioning-drift

## Command under test
`/new-feature`

## Brief (illustrative — not executed live)
Two real artifacts already in this repo's history, used as-is:
`docs/artifacts/adapter-evaluation-v1.md` and `docs/artifacts/benchmark-report-v1.md`.

## What this checks
`implementation/knowledge/commands/new-feature.md` Phase 3 step 8: "Produce versioned artifacts
for feature deliverables — Format: `<artifact-name>-v<N>.md`, per `AGENTS.md` § Artifact
Versioning — Store in `docs/artifacts/`."

## Pass condition
Both real artifacts under `fixture/docs/artifacts/` have filenames matching
`<artifact-name>-v<N>.md` — a single-integer version component.

## Why this was previously known_failing, and why it now passes
This case was `known_failing` / `tracked_defect` for as long as `new-feature.md` declared a
two-part `<artifact-name>-v<major>.<minor>.md` format. Both fixture files use `-v1.md`, and that
is not specific to them: `ls docs/artifacts/ | grep -E '\-v[0-9]+\.[0-9]+\.md$'` returned zero
matches across all 43 real `docs/artifacts/*-v<N>.md` files in this repo at authoring time, while
`grep -E '\-v[0-9]+\.md$'` (single-integer version) matched all of them.

`ADR-007` resolved that conflict on **branch 1** — authority conflict, therefore amend the
contract: the clause contradicted `AGENTS.md` § Artifact Versioning ("Immutable artifacts:
`<type>-v<N>.md`"), and a command may specialise `AGENTS.md` but may not mint a rival convention
for something `AGENTS.md` already governs. The corpus wins here because a higher-authority
document says so, not because it is the majority. The command was amended to the single-integer
form, and this case's checker now tests the contract that is in force.

## Provenance
Real artifacts, copied verbatim, never edited. The fixture is unchanged from authoring time and
always conformed — per `ADR-007` § "Corollary", a branch-1 amendment that changes only a name or
path leaves the fixture intact. Renaming a fixture file to `-v1.0.md` would invert the case,
making it assert the form `AGENTS.md` does *not* declare.
