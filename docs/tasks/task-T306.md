# Task T306 — Final gate: clean-install proof

**ID:** T306
**Owner:** qa-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T301, T303, T304, T305, T214
**Created:** 2026-07-31
**Completed:** —
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Produce the single evidence pack that proves plan-016's "Pattern A is clean, working, and
installable" claim is real, not asserted — the closing gate of this plan.

## Inputs
- Outputs of T301, T303, T304, T305, T214

## Expected outputs
- This file's Execution notes, containing every command's literal output below.

## Acceptance criteria
1. `make sync && make verify` → exit 0.
2. `python3 docs/tasks/validate-tasks.py` → exit 0.
3. `docker compose -f deploy/docker-compose-t226.yml ps` → 4 containers, all healthy.
4. `grep -c "CORRECTED 2026-07-31" docs/tasks/completed-tasks.md` → 19.
5. `test -f docs/artifacts/phase2-3-poc-debt-scorecard-v1.md` → exists.
6. `test -f docs/artifacts/t305-deployment-guide-validation-report-v1.md` → exists.
7. `docs/tasks/task-T214.md` shows `Status: done` with pasted real OID/error-string evidence for
   all 4 scenarios.
8. Per R8, every command's actual output — not a summary claim — is pasted into Execution notes.
   This is the artifact a future reader trusts instead of re-running everything themselves.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
