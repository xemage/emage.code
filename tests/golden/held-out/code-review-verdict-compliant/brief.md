# Case: code-review-verdict-compliant

## Command under test
`/code-review`

## Brief (illustrative — not executed live)
"Review the token-refresh implementation against `auth-token-refresh-v1.2.md`." Tech Lead runs
`/code-review`.

## What this checks
`implementation/knowledge/commands/code-review.md` §"Verdict Output" requires a `## VERDICT`
block with exactly these fields: `Status` (one of `PASS|CONDITIONAL_PASS|FAIL`), `Reviewed
artifacts`, `Must Fix count`, `Should Fix count`, `Nice to Have count`, `Blocker IDs`, `Reviewer`,
`Timestamp`.

## Pass condition
`fixture/review.md` contains a `## VERDICT` section with all eight required fields present as
`- **Field**: value` bullets, and `Status` is one of the three allowed values.

## Provenance
Hand-authored to the command's declared contract. See `code-review-real-verdict-format-drift`
(known_failing) for the same check run against a real Tech-Lead/QA verdict already in this repo's
history — this repo's actual verdict-writing practice (`## VERDICT: PASS` + prose `###
Justification`, per `docs/tasks/task-T365.md`, `task-T346.md`, `task-T336.md`) does not use this
field list, which is why this passing case's fixture had to be hand-authored.
