# Case: plan-task-creation-precondition-real

## Command under test
`/plan`

## Brief (illustrative — not executed live)
Validates `/plan`'s **Task Creation Precondition** (`implementation/knowledge/commands/plan.md`
§"Task Creation Precondition"): "no task row may be added to `docs/tasks/active-tasks.md` until
(a) the plan document it derives from exists ... and (b) ... Every task ID created from this plan
must appear in the plan document's text."

## Fixture (real)
- `fixture/docs/plans/plan-030-mcp-remote-transport-alignment.md` — real plan, landed
  2026-08-09, contains a "Task ID Index" table mapping `P030-06` to task `T365`.
- `fixture/docs/tasks/task-T365.md` — the real task brief for T365, whose `**Based on:**` header
  field cites `docs/plans/plan-030-mcp-remote-transport-alignment.md`.

## Pass condition
The task brief's `**ID:**` field equals `T365`, its `**Based on:**` field names the plan file
present in the fixture, and the literal string `T365` appears in that plan file's text (satisfying
the "every task ID created from this plan must appear in the plan document's text" clause).

## Provenance
Fully real: both files are unmodified copies of `docs/plans/plan-030-mcp-remote-transport-
alignment.md` and `docs/tasks/task-T365.md` from this repo's own history. This is a genuine,
already-satisfied instance of the precondition — not constructed to pass.
