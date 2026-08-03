# Task T317 — WAVE 0: Baseline

**ID:** T317
**Owner:** orchestrator
**Status:** done
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-02
**Completed:** 2026-08-03
**Based on:** docs/plans/plan-017-deployment-docs-and-registry-hardening.md

## Objective
Establish a clean baseline before Wave 1+: confirm working-tree state in both `emage.code` and
`../CWSO`, and record whether the plan-016 live CWSO stack is still running.

## Inputs
- Current git state of `emage.code` and `../CWSO`.

## Expected outputs
- This file's Execution notes with literal output of all three baseline commands.

## Acceptance criteria
1. `git status --porcelain` (emage.code) output pasted.
2. `git -C ../CWSO status --porcelain` output pasted.
3. `docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"` output pasted.
4. Absence of a running stack is noted but NOT treated as a blocker for T318/T319/T320/T321
   (documentation and hand-off tasks don't require a live stack).

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed: 2026-08-03

### `git status --porcelain` (emage.code)
```
 M docs/tasks/active-tasks.md
?? docs/plans/plan-017-deployment-docs-and-registry-hardening.md
?? docs/tasks/task-T317.md
?? docs/tasks/task-T318.md
?? docs/tasks/task-T319.md
?? docs/tasks/task-T320.md
?? docs/tasks/task-T321.md
?? docs/tasks/task-T322.md
?? docs/tasks/task-T323.md
?? docs/tasks/task-T324.md
?? docs/tasks/task-T325.md
?? docs/tasks/task-T326.md
```

### `git -C ../CWSO status --porcelain`
```
(empty — CWSO working tree is clean)
```

### `docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"`
```
NAMES     STATUS
(empty — no CWSO containers are running)
```

### Disposition
The plan-016 live stack is NOT running. This is expected and not a blocker for Wave 1
(T318/T319/T320) or Wave 3 (T321), which are documentation/hand-off tasks. Wave 5
(T323/T324) will bring the stack up fresh from registry images once T322 is READY.

**Status: DONE**
