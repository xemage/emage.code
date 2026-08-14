# Case: new-feature-real-artifact-versioning-drift (known_failing / tracked_defect)

## Command under test
`/new-feature`

## Brief (illustrative — not executed live)
Two real artifacts already in this repo's history, used as-is:
`docs/artifacts/adapter-evaluation-v1.md` and `docs/artifacts/benchmark-report-v1.md`.

## What this checks
`implementation/knowledge/commands/new-feature.md` Phase 3 step 8: "Produce versioned artifacts
for feature deliverables — Format: `<artifact-name>-v<major>.<minor>.md` — Store in
`docs/artifacts/`." The declared format requires a two-part `major.minor` version component.

## Why this is known_failing today
Both real fixture files use `-v1.md` (a single integer, no minor component) — not
`-v1.0.md`/`-v<major>.<minor>.md` as declared. This is not specific to these two files: `ls
docs/artifacts/ | grep -E '\-v[0-9]+\.[0-9]+\.md$'` returns zero matches across all 43 real
`docs/artifacts/*-v<N>.md` files in this repo at authoring time, while `grep -E
'\-v[0-9]+\.md$'` (single-integer version) matches all of them. The entire artifact corpus has
consistently used single-integer versioning, never the command's declared two-part
`major.minor` scheme.

## Category
`tracked_defect` — the command's declared filename format is unambiguous and mechanically
checkable; real practice across this repo's entire artifact history has consistently used a
different (simpler) convention instead. Either the command definition should be updated to
match the single-integer convention actually in use, or the convention itself needs to change
going forward — either way this is a concrete, trackable naming-contract violation.
