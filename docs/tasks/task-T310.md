# Task T310 — Document confirmed CWSO-core defects directly in the CWSO repository

**ID:** T310
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Depends on:** T304 (conditional — see below)
**Created:** 2026-07-31
**Completed:** 2026-07-31
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

**This task runs — T304 found a real CWSO-core defect (`cwso-rollout` unhealthy).** Executed
2026-07-31 by devops-engineer subagent (delegated by orchestrator), independently re-verified by
orchestrator.

### Step 1 — confirm next free CWSO task ID (per acceptance criterion 1)

```
$ grep -n "^| T" ../CWSO/docs/tasks/active-tasks.md | tail -1
17:| T168 | Back-merge main into develop and clean up | release-manager | pending | P0 | T167 | 2026-07-27 |
$ grep -n "^| T" ../CWSO/docs/tasks/completed-tasks.md | tail -1
63:| T157 | v0.4.0 release readiness | release-manager | 2026-06-09 | Migrated from active-tasks.md board cleanup |
```
Highest used CWSO task ID across both ledgers: T168. Next free IDs used: **T169**, **T170**.
Re-confirmed by orchestrator independently after the subagent's writes — no collision:
`grep -n "T169\|T170" ../CWSO/docs/tasks/active-tasks.md ../CWSO/docs/tasks/completed-tasks.md`
returned no hits (i.e. T169/T170 did not already exist anywhere in either ledger).

### Step 2 — files written into `../CWSO`

```
-rw-r--r-- 1 emage emage 9433 Jul 31 19:49 /home/emage/Code/emage/CWSO/docs/artifacts/emagecode-integration-defect-cwso-rollout-unhealthy-v1.md
-rw-r--r-- 1 emage emage 5802 Jul 31 19:49 /home/emage/Code/emage/CWSO/docs/plans/plan-fix-cwso-rollout-healthcheck-and-trajectory-store.md
-rw-r--r-- 1 emage emage 3627 Jul 31 19:50 /home/emage/Code/emage/CWSO/docs/tasks/task-T169.md
-rw-r--r-- 1 emage emage 3410 Jul 31 19:50 /home/emage/Code/emage/CWSO/docs/tasks/task-T170.md
```
(orchestrator independently re-ran `ls -la` on all four paths after the subagent's report — matches
exactly, files exist with the sizes above.)

- **Issue summary** (`emagecode-integration-defect-cwso-rollout-unhealthy-v1.md`): Producer/Task/
  Created/Based-on header block, Scope/Context, Commands Run (verbatim, copied from task-T304.md),
  full verbatim evidence (container status, rollout container logs, `docker inspect` Healthcheck +
  State.Health JSON, relevant compose YAML excerpt), Environment (Docker 29.6.2, Ubuntu 24.04.4 LTS
  WSL2, go1.26.3), two Root Cause Candidates explicitly marked unconfirmed, Impact, and a pointer to
  emage.code plan-016 / task T304 as the origin.
- **Fix plan** (`plan-fix-cwso-rollout-healthcheck-and-trajectory-store.md`): follows CWSO's own
  `docs/plans/_template.md` exactly. Status: "draft — awaiting approval". Goal section states plainly
  that root cause is unconfirmed and that T169 (investigation) must precede T170 (fix) — no invented
  fix proposed. Task graph: `T169 --> T170`. Includes Risks & mitigations covering API-contract risk
  on `/v1/models` and deployment-compat risk on the trajectory store path.
- **Task briefs**: `task-T169.md` (root-cause investigation, owner backend-developer, status pending,
  requires source-grounded evidence for both candidates before any fix is proposed) and `task-T170.md`
  (implement + verify the confirmed fix only, owner backend-developer, status pending, depends on
  T169, requires a `fix-verification-v1.md` artifact with real rebuild/health-probe evidence). Both
  follow CWSO's `docs/tasks/_template.md` exactly.

### Step 3 — `../CWSO/docs/tasks/active-tasks.md` was NOT modified (per acceptance criterion 5)

```
$ git diff --stat -- docs/tasks/active-tasks.md   (run inside ../CWSO)
 docs/tasks/active-tasks.md | 2 ++
 1 file changed, 2 insertions(+)
```
This 2-line diff pre-existed the start of this session (confirmed via SHA-256 hash comparison
before/after the subagent's writes — identical hash, `6af2035a...`), i.e. it is unrelated,
pre-existing local state in the CWSO checkout that this task did not create or touch. No commit was
made in `../CWSO` (per plan-016's instruction to leave files uncommitted unless the repo's own
workflow rules were independently confirmed, which they were not in this session).

### Disposition

T310's acceptance criteria are met: next free CWSO IDs confirmed before writing, issue summary
contains exact commands + verbatim logs + environment + originating plan/task, fix plan follows
CWSO's template with root cause explicitly marked unconfirmed, task briefs follow CWSO's template,
`../CWSO/docs/tasks/active-tasks.md` untouched, and `ls -la` evidence pasted above for all four new
files. Reserved CWSO task IDs for future reference: **T169, T170** (do not reuse).
