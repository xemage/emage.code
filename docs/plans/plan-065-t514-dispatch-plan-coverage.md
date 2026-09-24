# plan-065 — T514 dispatch plan coverage

**Status: dispatched.** Minimal coverage addendum, per the established `plan-042`/`plan-050`/
`plan-056`–`059`/`061`–`063` precedent: `test_every_active_task_has_a_plan` requires every active
task's real ledger ID to appear as a literal `T\d{3,}` token somewhere under `docs/plans/`.

`plan-064` (the v8 roadmap) specifies Phase 10 in full but lists its task IDs as `—`, since no
ledger IDs existed when it was written. This addendum supplies the binding.

`T514` — Phase 10's work as a single task: re-run promotion readiness for all 8 agents currently at
`maturity: experimental`, promote those that qualify, and record the real blocker for those that do
not. Owner `tech-lead`, following the `T433`/`T434`/`T435` promotion-wave precedent rather than
`plan-064`'s own provisional table (which named Product Owner — the precedent for that is `T436`, a
demotion *assessment* producing no file changes, which is a different shape of work).

Merged into one task rather than `plan-064`'s two rows: evaluating all eight is a prerequisite for
knowing which four qualify, so the "re-assess the remaining four" row is a byproduct of doing the
first row properly rather than separable work.

See `docs/tasks/task-T514.md` for the full brief, including the disclosed conflict of interest
(`tech-lead` is itself one of the eight under evaluation) and the reasoning behind the P2 priority.
