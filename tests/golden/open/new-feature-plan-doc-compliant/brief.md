# Case: new-feature-plan-doc-compliant

## Command under test
`/new-feature`

## Brief (illustrative — not executed live)
"Add a feature letting admins export the audit log as a signed CSV." A Phase 1 lightweight
plan document is authored before any implementation begins.

## What this checks
`implementation/knowledge/commands/new-feature.md` `## Phase 1: Plan & Approve` step 1, verbatim:

> 1. **Create a lightweight plan document** for this feature
>    - Write to `docs/plans/plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it
>    - Include: objective, affected components, task breakdown, dependency impact
>    - Reference protocol: `plan-approve-execute` skill § The Three Phases › Phase 1: Plan (Plan Document Format)

## Pass condition
Exactly one file in `fixture/docs/plans/` matches `plan-*.md`, the fixed prefix and suffix of the
`plan-<ID>.md` form, and it contains `## Objective`, `## Affected Components`, `## Task Breakdown`,
and `## Dependency Impact` sections. The check does not parse `<ID>`; the fixture's
`plan-001-audit-log-export.md` is a conforming name.

## Provenance
Hand-authored. When this case was authored, step 1 declared `docs/plans/feature-<slug>.md`. A
corpus survey (`find docs/plans -iname "feature-*"`) then found zero matches — this repo's real
plans all used the `/plan` command's `plan-NNN-<slug>.md` naming convention instead (see
`plan-required-sections-compliant`), never the `/new-feature` command's then-declared
`feature-<slug>.md` naming. No real `/new-feature`-shaped plan doc existed to source this case
from; see `new-feature-real-checkpoint-format-drift`, which used this same absence-of-precedent
as grounding for its `known_failing` status until `T520`.

`T596` (P32) changed step 1 to the text quoted above. `T597` realigned this case: the glob became
`plan-*.md` (formerly `feature-*.md`), with the same strength — still exactly one matching plan and
the same four headers — and the fixture was renamed to `plan-001-audit-log-export.md` (formerly
`feature-audit-log-export.md`, contents byte-identical).
