# plan-061 — T509 dispatch plan coverage

**Status: dispatched.** Minimal coverage addendum, per the established `plan-042`/`plan-050`/
`plan-056`–`059` precedent: `test_every_active_task_has_a_plan` requires every active task's real
ledger ID to appear as a literal `T\d{3,}` token somewhere under `docs/plans/`.

`T509` — a design/scoping pass hardening the closed loop's improvement-detection logic, following
directly from `T507`'s real, disclosed finding (a `promote=True` result from `evaluate_promotion()`
that its own generating task judged was very likely not a genuine improvement). See
`docs/tasks/task-T509.md` for the full brief. Dispatched per the user's explicit instruction to
scope this hardening, given directly in response to the top-level session's own report of the T507
finding.
