# Case: new-feature-plan-doc-compliant

## Command under test
`/new-feature`

## Brief (illustrative — not executed live)
"Add a feature letting admins export the audit log as a signed CSV." A Phase 1 lightweight
plan document is authored before any implementation begins.

## What this checks
`implementation/knowledge/commands/new-feature.md` Phase 1 step 1: "Create a lightweight plan
document for this feature — Write to `docs/plans/feature-<slug>.md` — Include: objective,
affected components, task breakdown, dependency impact."

## Pass condition
Exactly one file exists at `fixture/docs/plans/feature-<slug>.md` and contains `## Objective`,
`## Affected Components`, `## Task Breakdown`, and `## Dependency Impact` sections.

## Provenance
Hand-authored. A corpus survey (`find docs/plans -iname "feature-*"`) found zero matches — this
repo's real plans all use the `/plan` command's `plan-NNN-<slug>.md` naming convention instead
(see `plan-required-sections-compliant`), never the `/new-feature` command's declared
`feature-<slug>.md` naming. No real `/new-feature`-shaped plan doc exists to source this case
from; see `new-feature-real-checkpoint-format-drift` and
`new-feature-real-artifact-versioning-drift` for cases that use this same absence-of-precedent
as grounding for known-failing cases instead.
