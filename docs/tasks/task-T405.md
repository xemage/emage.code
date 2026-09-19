# Task T405 — Rule-set hardening: make `/plan` output a precondition of task creation

**ID:** T405
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Depends on:** —
**Created:** 2026-08-12
**Completed:** —
**Based on:** docs/plans/plan-035-roadmap-v7-ground-up.md (Phase 0, §2.4)

This brief is self-contained.

## Objective
Today, `tests/performance/test_team_health.py::TestPlanCoverage::test_every_active_task_has_a_plan`
is a **soft** check: it `self.skipTest(...)` (does not fail) when there are active tasks but no
plan documents under `docs/plans/`, and only fails when there *are* plan documents but a task's ID
isn't mentioned in any of them. There is no upstream rule that actually forces a plan to exist
before a task can be created in the first place — this is the exact gap plan-035's Part 1.3 names
("Plan-coverage test failure... a plan-drift detector with no upstream rule forcing plan
creation"). Close the gap at the source: amend `implementation/knowledge/commands/plan.md` and the
orchestrator's own instruction/knowledge file so that no task row may enter
`docs/tasks/active-tasks.md` without a `plan-NNN` reference, and add the **inverse** assertion to
`tests/performance/test_team_health.py` — i.e. a hard failure (not a skip) when a task exists with
no corresponding plan, removing today's soft-skip escape hatch for the "no plan documents at all"
case.

## Inputs
- `implementation/knowledge/commands/plan.md` (full file, 32 lines at brief-authoring time) — the
  `/plan` slash command's own instructions. It currently ends at "Present the plan for review" with
  no explicit statement that task creation is gated on the plan document existing.
- `implementation/knowledge/agents/orchestrator.md` — the orchestrator's canonical
  instruction/knowledge source (projected into `.claude/agents/orchestrator.md` etc. by
  `implementation/scripts/sync.mjs`). Find and read the section describing task creation /
  Plan-Approve-Execute — this is almost certainly the "Task Management" or "Plan-Approve-Execute
  Protocol" section; confirm the exact heading by reading the file rather than assuming.
- `tests/performance/test_team_health.py`, specifically `TestPlanCoverage` (around lines 165-189 at
  brief-authoring time) and its helpers `_real_tasks()` (line 67) and `_plan_files()` (line 79) —
  read the full class and both helpers before editing.
- `AGENTS.md` (root, canonical) — the "Task Protocol" section. Check whether it already implies
  plan-first task creation and needs the same explicit tightening, or whether it's silent and
  should point at `implementation/knowledge/commands/plan.md`'s now-explicit rule instead of
  duplicating it.

## Expected outputs
- `implementation/knowledge/commands/plan.md` — amended with an explicit statement that a task row
  may not be added to `docs/tasks/active-tasks.md` until the plan document it's based on exists
  and has been through the Plan phase's approval step. (This file is a knowledge-base *source* —
  confirm whether editing it here is sufficient or whether the projected copies under
  `.github/`, `.claude/`, etc. are regenerated via `implementation/scripts/sync.mjs` and should not
  be hand-edited separately; the "Knowledge Base" section of `AGENTS.md` states per-platform
  folders are **generated**, so edit only the canonical `implementation/knowledge/commands/
  plan.md` source and regenerate via the sanctioned sync mechanism — do not hand-edit any
  projected copy.)
- `implementation/knowledge/agents/orchestrator.md` — amended in whichever section governs task
  creation, cross-referencing the same rule (a task row requires a `plan-NNN` reference at
  creation time, not just eventually).
- `tests/performance/test_team_health.py` — `TestPlanCoverage.test_every_active_task_has_a_plan`
  (or a new adjacent test method, your call on which reads more clearly) changed so that the
  "active tasks exist but zero plan documents exist" case is a **hard failure**, not a
  `self.skipTest(...)`. Preserve the existing "tasks exist, plans exist, but this specific task
  isn't referenced by any of them" failure path unchanged — you're removing the skip escape hatch
  for the *no-plans-at-all* case, not rewriting the whole test.
- Regenerated platform projections via the sanctioned sync mechanism (confirm the exact command —
  likely `node implementation/scripts/sync.mjs --root implementation`, run in write mode this
  time, not `--check`, since your source content actually changed) so `.claude/commands/plan.md`,
  `.github/...`, etc. reflect your `implementation/knowledge/commands/plan.md` edit. Run `node
  implementation/scripts/sync.mjs --root implementation --check` afterward to confirm zero drift.

## Acceptance criteria
1. `implementation/knowledge/commands/plan.md` explicitly states the plan-before-task-creation
   precondition.
2. `implementation/knowledge/agents/orchestrator.md` cross-references the same rule in its task
   creation section.
3. A test run against a scratch/fixture state simulating "active tasks exist, `docs/plans/`
   directory is empty" now fails the suite (hard failure), where today it would `skipTest`.
4. The existing failure path (tasks exist, plans exist, task ID not referenced) is unchanged and
   still fails correctly — do not weaken this path while fixing the other.
5. `node implementation/scripts/sync.mjs --root implementation --check` reports zero drift after
   you regenerate the projections (i.e. your source edit and the regenerated output are in sync).
6. `python3 tests/run.py` exits 0 (no regression) except for the intentional, expected change in
   `TestPlanCoverage`'s behavior described above.
7. `implementation/scripts/generate-registry.py --check` passes (confirms registry metadata for
   `plan.md`/`orchestrator.md` is still internally consistent after your edits).

## Blocker protocol
- If editing the test to remove the skip path would break other tests that rely on the skip
  behavior for legitimate reasons (e.g. a test fixture repo state with genuinely no tasks and no
  plans, which should still be allowed to have neither) — `type: technical`, `severity: minor` —
  report and propose a narrower fix (e.g. only hard-fail when tasks exist AND plans dir is empty,
  which is what's specified above; a fully-empty repo with neither tasks nor plans should remain
  fine, check `_real_tasks()`'s existing empty-check logic before assuming otherwise).
- If the sanctioned sync/regeneration command differs from what's stated above — `type:
  unclear_requirements`, `severity: minor` — confirm against `CONTRIBUTING.md`'s documented sync
  workflow before guessing.

## Git workflow
Same shared branch as T400–T404: `feature/T400-phase0-ground-truth-v6.11.0`. You have Bash access
(per your agent definition) — commit your own change directly to this branch, but **do not push**
and **do not open a merge request**; T406 performs the final validation gate and merge for the
whole batch. Commit with a Conventional Commit message, e.g.:
```
refactor(rules): make /plan output a precondition of task creation

TestPlanCoverage previously skipped (not failed) when active tasks
existed but no plan documents did at all, leaving no upstream rule
actually forcing plan creation before task creation. Amend
plan.md/orchestrator.md to state the precondition explicitly and
harden the test to a hard failure for that case.

Refs T405
```

## Constraints
- Token budget: ≤25k tokens.
- File ownership: `implementation/knowledge/commands/plan.md`,
  `implementation/knowledge/agents/orchestrator.md`, `tests/performance/test_team_health.py`, plus
  the regenerated projection output from the sanctioned sync command (do not hand-edit any
  projected copy directly).
- Per `.claude/rules/security-guidelines.md`, Tech Lead is read-only during *review* phases but
  this is an authoring task (rule-set hardening), not a review — you have write access here, as
  reflected in your agent definition's tool list.
