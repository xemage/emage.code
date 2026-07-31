# Task T310 — Document confirmed CWSO-core defects directly in the CWSO repository

**ID:** T310
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Depends on:** T304 (conditional — see below)
**Created:** 2026-07-31
**Completed:** —
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
For any real CWSO-core defect surfaced by T304 or T305 (build failure, service that never turns
healthy, MCP contract mismatch, or anything outside "what's needed to get its own documented Docker
Compose profile running"), hand the fix to CWSO's own team by writing directly into their
repository using their own emage.code-style conventions — never via an external GitLab issue, and
never by patching CWSO's code from within this repo.

**This task runs conditionally.** If T304 and T305 found no CWSO-core defect, skip this task
entirely and record a one-line reason why in Execution notes.

## Inputs
- T304 / T305 Execution notes (exact commands run, full log output, environment details)
- `../CWSO/docs/plans/_template.md`, `../CWSO/docs/tasks/_template.md`
- `../CWSO/docs/tasks/active-tasks.md`, `../CWSO/docs/tasks/completed-tasks.md` (to find the next
  free CWSO task ID — do not assume it)

## Expected outputs (per confirmed defect)
- `../CWSO/docs/artifacts/emagecode-integration-defect-<slug>-v1.md` (issue summary)
- `../CWSO/docs/plans/plan-<next-slug>.md` (fix plan, CWSO's own template, status "draft — awaiting
  approval")
- `../CWSO/docs/tasks/task-T<NNN>.md` (one per task in the fix plan's graph, CWSO's own next IDs)

## Acceptance criteria
1. Before writing anything, run `grep -n "^| T" ../CWSO/docs/tasks/active-tasks.md | tail -1` and
   `grep -n "^| T" ../CWSO/docs/tasks/completed-tasks.md | tail -1` to confirm the next unused CWSO
   task ID.
2. Issue summary contains: exact commands run, full verbatim log/error output, environment
   (`docker --version`, host OS, `go version`), and which emage.code plan/task surfaced it.
3. Fix plan follows `../CWSO/docs/plans/_template.md` exactly (Goal/Scope/Task graph/Agent
   assignments/Artifact flow). If root cause is unknown, the Goal section says so plainly — no
   invented, unverified fix.
4. Task briefs follow `../CWSO/docs/tasks/_template.md` exactly, one per task graph node.
5. `../CWSO/docs/tasks/active-tasks.md` is NOT modified — scheduling into CWSO's live queue is
   CWSO's own maintainers' decision, not ours.
6. Per R8, paste `ls -la` output for every new file's path into Execution notes, plus the reserved
   CWSO task IDs (so a later run of this task doesn't collide with them).

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
