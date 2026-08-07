# Task T305 — Follow `local-docker-desktop-guide.md` literally, end to end

**ID:** T305
**Owner:** qa-engineer
**Status:** done
**Priority:** P1
**Depends on:** T304 (done)
**Created:** 2026-07-31
**Completed:** 2026-08-01
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Independently verify that `docs/deployment/local-docker-desktop-guide.md` (plan-013's deliverable)
actually works for a reader who did not write it — the guide has existed since 2026-06/07 but has
never been independently validated end-to-end.

## Inputs
- `docs/deployment/local-docker-desktop-guide.md`
- The live CWSO stack from T304 (for comparison — the guide should be followed on its own terms,
  not assumed identical to T304's exact steps)

## Expected outputs
- `docs/artifacts/t305-deployment-guide-validation-report-v1.md` (new file)

## Acceptance criteria
1. Every command in the guide is run exactly as written; the actual output is recorded — not
   assumed from the guide's prose.
2. Every claim in the guide ("you should now see X", "curl should return Y") is checked against the
   actual output obtained, not against what the guide asserts.
3. Any failing step, missing prerequisite, or output inconsistent with the guide's description is
   filed as a new bug task (next available T-ID) referencing the exact guide section/line and the
   literal failing output. Do not silently fix the guide's prose in this task.
4. If a failure's root cause traces to a CWSO-core defect (not just guide wording), it is also
   routed through T310's convention (issue-summary + fix-plan + task briefs in `../CWSO`).
5. `docs/artifacts/t305-deployment-guide-validation-report-v1.md` lists, per guide section: command
   run, actual output, PASS/FAIL against the guide's claim.
6. Per R8, the report itself IS the evidence — no summary claim without the actual output quoted
   beneath it.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed 2026-08-01 by a qa-engineer subagent (delegated by orchestrator) against the live,
healthy CWSO stack (`deploy/docker-compose-t226.yml`, all 4 target services Up/healthy following
T304/T312). Full command-by-command evidence lives in
`docs/artifacts/t305-deployment-guide-validation-report-v1.md` (not duplicated here).

**Verdict: FAIL.** The guide fails at its very first verification command (`curl
http://localhost:8080/health` returns `401 missing bearer token`, not the documented JSON healthy
payload) and its Detailed Setup cannot be completed as literally written because Step 1 references
`deploy/docker-compose-local-dev.yml`/`.env` files that do not exist anywhere in the repo.

**Scope-mismatch pre-check:** confirmed via `ls -la deploy/` that only `docker-compose-t226.yml`
and `t226-phase2.env` exist — the guide's named "local-dev" files were never created. The
automated setup script (`scripts/deploy/cwso-docker-desktop.sh`) is internally consistent with the
real T226 files but its own `JWT_SOURCE` variable (`deploy/.env.jwt.dev`) also doesn't exist.

**Security guardrail compliance:** per `.claude/rules/security-guidelines.md`, the qa-engineer
subagent correctly declined to read/source `.env`/`.env.*` files (Step 2 Option A,
`deploy/.env.jwt.dev`); this was recorded as an additional finding (#3) rather than worked around.
Downstream JWT-dependent steps used Option B (freshly-generated secret) instead, with the
resulting auth mismatch documented explicitly as a substitution artifact, not a guide defect.

**13 distinct findings** were logged (5 critical/high, blocking a fresh reader end-to-end; see the
report's "Findings / Bugs Summary" table for full detail with literal output per finding). All 13
were confirmed to trace to this repo's own documentation/scripts/compose-naming — **none trace to
a genuine CWSO-core defect**, so no T310 hand-off was required for this task (acceptance criterion
4 correctly evaluated as not applicable).

Filed as consolidated bug task **T313** (`docs/tasks/task-T313.md`), owner technical-writer,
covering all 13 findings with per-item acceptance criteria, rather than 13 separate ledger rows
(they are a single coherent editing pass across two artifacts plus one naming decision).

**Deliverable:** `docs/artifacts/t305-deployment-guide-validation-report-v1.md` (new file), listing
per guide section: command run, literal output, PASS/FAIL against the guide's claim, per
acceptance criteria 1/2/5/6.

**Git workflow:** branch `test/t305-deployment-guide-validation`, commit `7555ec1`
(`test(t305): validate local-docker-desktop-guide.md end to end`), MR !91
(https://gitlab.com/em-age/emage.code/-/merge_requests/91), CI green (pipeline
https://gitlab.com/em-age/emage.code/-/pipelines/2724231869 — sync-no-diff,
validation-super-gate, verify-knowledge-drift, unit-tests, markdown-links all passed), merged by
orchestrator via `glab mr merge 91 --squash --yes`.

Live stack confirmed untouched throughout and after — all 4 target services still Up/healthy, no
`docker compose down` executed at any point.

**T305: done.**
