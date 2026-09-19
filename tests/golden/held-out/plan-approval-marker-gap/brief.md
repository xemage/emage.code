# Case: plan-approval-marker-gap (known_failing / capability_gap)

## Command under test
`/plan`

## Brief (illustrative — not executed live)
`/plan` step 6 requires: "Present the plan for review — output a summary and wait for user
approval. Do NOT execute any tasks" before its Task Creation Precondition may be satisfied. This
case asks: given only the plan document as checked into the repo, can an automated, deterministic
check tell whether that approval step actually happened?

## Fixture (real)
`fixture/docs/plans/plan-030-mcp-remote-transport-alignment.md` — the same real, already-executed
plan used in `plan-task-creation-precondition-real` (its tasks T360–T367 are real, `done`, in
`docs/tasks/completed-tasks.md`), reused here to check a different property.

## Pass condition (as specified — deliberately not met by the fixture)
The plan document contains an explicit, structured approval marker: a `## Approval` section
containing a line matching `**Approved**` (or equivalent explicit approval record with a date).

## Why this is known_failing today, and why it's a capability_gap rather than a tracked_defect
`plan-030-mcp-remote-transport-alignment.md` has no `## Approval` section at all, yet its tasks
were dispatched and executed to completion (T360–T367, all `done`). This is not a case of "the
plan forgot to record something the contract requires it to record" — the command definition
(`plan.md`) itself never specifies *what* a machine-checkable approval record should look like;
step 6 only says to "wait for user approval" as a live, conversational gate, with no declared
persisted-artifact convention for it. There is therefore no way for a static, deterministic
`expect.py` to verify "was this plan actually approved before its tasks were created" from repo
state alone — at best it can check for an ad-hoc proxy marker (as this case does), which most real
plans (plan-030 included) never adopted, precisely because the contract never asked them to. That
is a genuine capability gap in the command surface's traceability, not a bug in any specific plan
document.

## Category
`capability_gap` — no near-term fix is implied; documenting this is the point.
