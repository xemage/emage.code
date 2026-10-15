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

## Provenance of the current fixture
The current fixture, `fixture/docs/plans/plan-121-release-v8-wave-2.md`, is a byte-identical copy
of the real `docs/plans/plan-121-release-v8-wave-2.md`: the working plan for the Wave 2 tasks of
the v8.0.0 release, authored as a `/plan` output to the command's declared six headers
(`## Goal`, `## Task Decomposition`, `## Dependency Graph`, `## Resource Assignments`,
`## Risk Assessment`, `## Open Questions`, in that order). It is the working document of real work (it
drives the Wave 2 tasks) and was committed through the normal merge request flow, independently
of this case. The "Brief" paragraph above describes the original fixture
(`plan-030-mcp-remote-transport-alignment.md`), which this fixture replaced. `expect.py` is
byte-identical to the file it replaces, so the check is exactly as strong as before; only the
example moved.

## History: formerly known_failing / tracked_defect
Until baseline v21 this case was `known_failing` with `known_failing_category: tracked_defect`.
Its original fixture, a verbatim copy of `docs/plans/plan-030-mcp-remote-transport-alignment.md`,
used `## Objective`, `## Task Breakdown`, `## Agent Assignments` and `## Risks & Mitigations`
instead of the command's `## Goal`, `## Task Decomposition`, `## Resource Assignments` and
`## Risk Assessment`; only `## Dependency Graph` and `## Open Questions` matched. A corpus survey
(`grep -rl "Task Decomposition" docs/plans/*.md`, `grep -rl "Resource Assignments"
docs/plans/*.md`) found zero matches across the 34 real plan documents then in the repository, so
the drift was systemic and no real plan followed the declared header set.

`ADR-007` classified the case as branch 3b (omission, fix the corpus): the corpus was
heterogeneous, with no single alternative vocabulary to defer to (branch 3a did not fire), and no
quotable `AGENTS.md` contradiction existed (branch 1 did not fire). A frozen historical fixture
cannot be retro-edited, so the case could never pass as fixtured and was not made to. The exit
that ADR-007 § 3b prescribes is the one taken: produce one conforming artifact of the class and
re-fixture the case against it. Plan-121 is that artifact, the check is unchanged, and the case
moved from `known_failing` to `expected_pass` under
`docs/artifacts/promotion-and-golden-realignment-plan-v1.md` § 6.3 (grant G-1, items 7 to 10).
The old fixture's file was a copy; the shipped `docs/plans/plan-030-mcp-remote-transport-alignment.md`
is untouched.
