# Case: plan-real-doc-header-drift (known_failing / tracked_defect)

## Command under test
`/plan`

## Brief (illustrative — not executed live)
Same underlying request class as `plan-required-sections-compliant`, but this case validates a
**real** plan document already in this repo's history instead of a hand-authored one:
`docs/plans/plan-030-mcp-remote-transport-alignment.md` (landed 2026-08-09, drove real tasks
T360–T367).

## What this checks
The identical contract as `plan-required-sections-compliant`: `implementation/knowledge/commands/
plan.md` step 5 requires the six headers **Goal, Task Decomposition, Dependency Graph, Resource
Assignments, Risk Assessment, Open Questions**, verbatim.

## Why this is known_failing today
`plan-030-mcp-remote-transport-alignment.md` uses `## Objective` (not `## Goal`), `## Task
Breakdown` (not `## Task Decomposition`), `## Agent Assignments` (not `## Resource
Assignments`), and `## Risks & Mitigations` (not `## Risk Assessment`) — only `## Dependency
Graph` and `## Open Questions` match the declared contract verbatim. A corpus survey (`grep -rl
"Task Decomposition" docs/plans/*.md`, `grep -rl "Resource Assignments" docs/plans/*.md` —
both zero matches across all 34 real plan documents in this repo) confirms this is not an
isolated drift in plan-030 specifically; no real plan in this repo's history uses the command's
exact declared header set. plan-030 is used here as one concrete, representative, real instance
of that systemic drift.

## Category
`tracked_defect` — the command's own declared contract (§5 of `plan.md`) is unambiguous about
the required header names; the actual authoring practice across every real plan in this repo
has drifted from it. This is fixable either by updating the plan documents' headers or by
updating the command's declared contract to match established practice — either way it is a
real, trackable gap, not a permanent capability limitation.
