# plan-063 — T511 dispatch plan coverage

**Status: dispatched.** Minimal coverage addendum, per the established `plan-042`/`plan-050`/
`plan-056`–`059`/`061`/`062` precedent: `test_every_active_task_has_a_plan` requires every active
task's real ledger ID to appear as a literal `T\d{3,}` token somewhere under `docs/plans/`.

`T511` — implements Option B (the symmetric positive-effect classification) from `T509`'s design
pass (`docs/artifacts/promotion-improvement-hardening-design-v1.md`), per the user's explicit
instruction ("Build B"), completing all three hardening options after `T510` already built A + C.
See `docs/tasks/task-T511.md` for the full brief.
