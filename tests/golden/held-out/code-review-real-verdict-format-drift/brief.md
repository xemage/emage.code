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

## Provenance of the current fixture
The current fixture is a byte-identical copy of the real `docs/artifacts/code-review-t619-v2.md`:
a Tech Lead review of the T619 change, authored as a `/code-review` output from the public
command and skill text (the artifact lists `implementation/knowledge/commands/code-review.md`
and the `code-review` and `validation-gates` skills among its inputs). It is the working
document of a real review, committed through the normal merge request flow, independently of
this case. It carries a bare `## VERDICT` heading followed by all eight `- **Field**: value`
bullets of the command's block, with a `Status` of `CONDITIONAL_PASS`. The file keeps the path
`fixture/docs/tasks/task-T365.md` because `expect.py` reads that exact path; only its content
changed. The "Brief" paragraph above describes the original fixture. `expect.py` is
byte-identical to the file it replaces, so the check is exactly as strong as before; only the
example moved.

## History: formerly known_failing / tracked_defect
Until baseline v21 this case was `known_failing` with `known_failing_category: tracked_defect`.
Its original fixture, a verbatim copy of `docs/tasks/task-T365.md`, wrote `## VERDICT: PASS`
(status inline in the heading, not as a separate `- **Status**:` bullet under a bare
`## VERDICT` heading) followed by `### Justification` prose: none of `Reviewed artifacts`,
`Must Fix count`, `Should Fix count`, `Nice to Have count`, `Blocker IDs`, `Reviewer` or
`Timestamp` appeared as structured fields. That was this repo's established verdict convention
for gate verdicts (also `task-T346.md`, `task-T336.md` and the validation-gate templates), not a
one-off mistake in T365, and T365 was a QA validation-gate task, not a `/code-review`
invocation.

`ADR-007` classified the case as branch 3b (omission, fix the corpus). A frozen historical
fixture cannot be retro-edited, so the case could never pass as fixtured and was not made to.
The exit that ADR-007 § 3b prescribes is the one taken: produce one conforming artifact of the
class (a review issued under the `/code-review` contract) and re-fixture the case against it.
The check is unchanged and no field was dropped, so the case moved from `known_failing` to
`expected_pass` under `docs/artifacts/promotion-and-golden-realignment-plan-v1.md` § 6.3
(grant G-1, item 12). The shipped `docs/tasks/task-T365.md` is untouched.
