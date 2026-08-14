# Case: code-review-real-verdict-format-drift (known_failing / tracked_defect)

## Command under test
`/code-review`

## Brief (illustrative — not executed live)
Same check as `code-review-verdict-compliant`, run against a real verdict already in this
repo's history: `docs/tasks/task-T365.md`'s own `## VERDICT: PASS` / `### Justification`
section (T365 was itself a QA validation-gate task, not a `/code-review` invocation, but its
verdict-writing convention is representative of this repo's actual practice for every gate
verdict, including Tech Lead code reviews — see `task-T346.md`, `task-T336.md` for the same
pattern).

## What this checks
`implementation/knowledge/commands/code-review.md` §"Verdict Output": a `## VERDICT` block with
`Status`, `Reviewed artifacts`, `Must Fix count`, `Should Fix count`, `Nice to Have count`,
`Blocker IDs`, `Reviewer`, `Timestamp` fields as `- **Field**: value` bullets.

## Why this is known_failing today
`task-T365.md` writes `## VERDICT: PASS` (status inline in the heading, not as a separate
`- **Status**:` bullet under a bare `## VERDICT` heading) followed by `### Justification` prose
— none of `Reviewed artifacts`, `Must Fix count`, `Should Fix count`, `Nice to Have count`,
`Blocker IDs`, `Reviewer`, or `Timestamp` appear as structured fields anywhere. This is this
repo's actual, consistent verdict convention (also used by `task-T346.md`, `task-T336.md`,
`docs/checkpoints/checkpoint-016-phase0-ground-truth-complete.md`'s "VERDICT: PASS" reference,
and the QA/Tech-Lead agent definitions' own "Structured Test Report" / validation-gate
templates), not a one-off mistake in T365 specifically.

## Category
`tracked_defect` — the command's declared field list is unambiguous; real practice across every
gate verdict in this repo has drifted to a different, narrower convention. Either the command
definition or the established practice should be reconciled; until then this is a real,
trackable contract violation.
