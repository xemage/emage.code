# Task T408 (plan-035: `T41B`) — Budget guard for `tb-delta.sh`

**ID:** T408
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Depends on:** T418 (done)
**Created:** 2026-08-13
**Completed:** 2026-08-13
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` (Phase 1, §2.4, Layer 2 table, row
named `T41B` in the plan's own text — renamed to `T408` in this ledger per
`docs/tasks/active-tasks.md`'s "Task ID note"; the ID format `T41B` does not match this repo's
enforced `^T\d{3,}$` format).

This is a companion brief to `docs/tasks/task-T419.md`, not a standalone task. Per the plan's own
sequencing note, the budget guard is "likely implemented alongside T419 rather than as a fully
separate artifact" — it is being executed by the same `devops-engineer` dispatch, in the same
worktree/commit(s), as T419. **This file exists to satisfy this repo's task-ledger invariant that
every row in `active-tasks.md` has its own `task-<ID>.md` brief** (`docs/tasks/
validate-tasks.py`'s `C7` check) — it is not a separate scope of work with independent acceptance.

## Objective
See `docs/tasks/task-T419.md`'s "T408 — budget guard specifics" section for the full
requirements: hard cap per invocation (time and/or cost), abort on projected overrun, economy
model default for iteration, frontier model reserved for release baselines, and demonstrated (not
merely described) proof that the guard actually aborts an over-budget run.

## Acceptance criteria (subset of task-T419.md's, specific to the guard)
1. Budget guard demonstrably aborts an artificially-capped run before completion.
2. Economy model is the default; a frontier-model override exists and is documented.
3. Guard configuration (cap, model tier) is documented in `docs/benchmarks/tb-delta-runner.md`
   (or task-T419.md's equivalent output).

## Git workflow
Same worktree/branch as T419 (`/home/emage/Code/emage/worktrees/phase1-tb-delta`,
`feature/T418-phase1-tb-delta-harness-v6.12.0`). No separate commit required — T419's commit(s)
cover this work; reference "Refs T419, T408" in the commit message.

## Constraints
Covered by task-T419.md's token budget (~55k combined). No separate file ownership beyond what
task-T419.md already specifies.

## Completion addendum (2026-08-13)

Closed alongside T419 in the same dispatch/commit. See `docs/tasks/task-T419.md`'s Completion
addendum for the full narrative (interrupted first dispatch, the deprecated-economy-model defect
that silently broke the original smoke test, the fresh real-Docker re-verification of both the
smoke test and this task's own budget-guard abort demonstration, and the orchestrator's
independent artifact-level verification of every claim). This task's specific 3 acceptance
criteria (guard demonstrably aborts; economy-default with documented frontier override; guard
configuration documented) were verified as part of that same pass — the abort re-verification
(RUN_ID `20260813T193832Z`, real 747s probe, real exit-2 abort, real `budget-guard.json` on disk,
no scorecard produced) is this task's own specific evidence, independently decoded and confirmed
by the orchestrator, not merely cited from the agent's report. Status set to `done`.
