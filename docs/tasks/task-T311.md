# Task T311 — cwso-rollout container fails healthcheck (405) + trajectory store write error

**ID:** T311
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Depends on:** — (external: fix owned by CWSO team, tracked via T310's hand-off into `../CWSO`); completion also required T312 (this-repo-owned healthcheck-wiring follow-on)
**Created:** 2026-07-31
**Completed:** 2026-08-01
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md, docs/tasks/task-T304.md

## Objective
Record, in this repo's own ledger, the real CWSO-core defect discovered while executing T304
(Wave 3 Docker build + healthcheck verification of `deploy/docker-compose-t226.yml`): the
`cwso-rollout` container builds and starts, but never becomes healthy. Two distinct issues were
observed in its logs/healthcheck history:

1. Its own Docker healthcheck (`curl -f http://127.0.0.1:8787/v1/models`, a bare GET) receives
   HTTP 405 Method Not Allowed from the `/v1/models` endpoint on every attempt (`FailingStreak: 6`,
   `curl: (22) The requested URL returned error: 405`, no recovery) — the healthcheck's HTTP
   method/path does not match what the service actually accepts.
2. Its startup log shows an unrecovered `ERROR`: `"trajectory store writer exited","error":"create
   rollout store \"./rollout_store\""` — the binary appears to write to a hardcoded relative path
   (`./rollout_store`) rather than the `CWSO_ROLLOUT_TRAJECTORY_STORE_PATH=/data/parquet-store`
   env var the compose file sets, and/or that relative path is not writable/does not exist inside
   the container's working directory.

This is a CWSO-core defect, out of scope for a fix from within this repo per plan-016 §3 Scope.
The actual issue-summary, fix-plan, and task briefs are written directly into the CWSO checkout
per T310 (see `docs/tasks/task-T310.md` and `../CWSO/docs/artifacts/emagecode-integration-defect-*`).
This task exists only so the ledger in THIS repo has a visible, honest record that T304 did not
pass and why — it stays `blocked` until CWSO's own team resolves the upstream issue and a
subsequent re-run of T304 (or a successor task) confirms `cwso-rollout` reports healthy.

## Inputs
- `docs/tasks/task-T304.md` Execution notes (full command outputs, logs, `docker inspect` evidence)
- `deploy/docker-compose-t226.yml` (the `rollout` service definition and its healthcheck)
- `../CWSO/deploy/Dockerfile.rollout`, CWSO's rollout source (not inspected further in this repo —
  out of scope; see T310's hand-off)

## Expected outputs
- This ledger row + brief, recording the defect and pointing to T310's upstream artifacts.
- No code changes in this repo or in `../CWSO` — documentation/tracking only.

## Acceptance criteria
1. Defect is described accurately with real evidence (quoted logs, `docker inspect` output) — done,
   see Execution notes below (copied from task-T304.md).
2. T310 has been executed for real, producing an issue-summary, fix-plan, and task briefs inside
   `../CWSO` (not this repo, not an external GitLab issue) — see `docs/tasks/task-T310.md`.
3. This task remains `blocked` (not `done`, not `cancelled`) until CWSO's own team ships a fix and
   a re-run of the T304-equivalent verification shows `cwso-rollout` healthy.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

- **Type:** external
- **Severity:** major
- **Description:** the fix lives in CWSO core (`../CWSO`, a separate repository maintained by a
  separate team), not in this repo. This repo cannot resolve it directly.
- **Mitigation:** T310 hands off a fully-specified issue-summary + fix-plan + task briefs into
  `../CWSO`'s own `docs/plans/`/`docs/tasks/` conventions, so CWSO's own maintainers can pick it up
  on their own schedule. This repo's Wave 4/5/6 work (plan-016) is blocked on that fix per plan-016's
  own GATE 3 ("Stop-if any container is missing or unhealthy — this blocks Waves 4 and 5 entirely").

## Execution notes

Full evidence (build output, `docker compose ps`, `docker inspect` healthcheck config and probe
history, container logs) is recorded verbatim in `docs/tasks/task-T304.md` Execution notes — not
duplicated here to avoid drift between two copies of the same evidence. Summary:

- `docker compose -f deploy/docker-compose-t226.yml build` — succeeded, all images built.
- `docker compose -f deploy/docker-compose-t226.yml up -d` — all 5 containers started.
- `cwso-orchestrator`: `Up ... (healthy)`.
- `cwso-git-shadow`, `cwso-merge-engine`: `Up` (no healthcheck defined in their images).
- `cwso-rollout`: `Up ... (unhealthy)`, `FailingStreak: 6`, healthcheck `curl -f
  http://127.0.0.1:8787/v1/models` returns HTTP 405 on every attempt.
- `cwso-rollout` log: `"trajectory store writer exited","error":"create rollout store
  \"./rollout_store\""`.

Upstream hand-off: `../CWSO/docs/artifacts/emagecode-integration-defect-cwso-rollout-unhealthy-v1.md`,
`../CWSO/docs/plans/plan-fix-cwso-rollout-healthcheck-and-trajectory-store.md`,
`../CWSO/docs/tasks/task-T169.md` and `task-T170.md` (CWSO's own next free task IDs, confirmed via
`grep -n "^| T" ../CWSO/docs/tasks/active-tasks.md ../CWSO/docs/tasks/completed-tasks.md | tail -5`
before writing — see task-T310.md Execution notes for the full grep output).

This task stayed `blocked` until CWSO's own team resolved the upstream defect.

### Resolution (2026-08-01)

CWSO's team shipped the fix upstream: `../CWSO` develop @ `29dea45`, commit `f7400f3
"fix(rollout): add /healthz liveness route and fix trajectory store path env var"`, produced via
their own `bugfix/T170-rollout-healthcheck-and-store-path` branch — exactly the remediation this
task's T310 hand-off (their T169/T170) requested. Independently re-verified (not just trusted from
their commit message): the trajectory-store write error is gone and `/data/parquet-store` is
correctly used; `GET /healthz` returns `200 {"status":"ok"}` inside the container. CWSO's board
also shows T169/T170 archived to their own completed-tasks board.

Re-verification surfaced one further, narrower, **this-repo-owned** issue (not a CWSO defect, so
T310 does not apply to it): `deploy/docker-compose-t226.yml`'s own Compose-level `healthcheck.test`
for the `rollout` service still targeted the old `/v1/models` endpoint, overriding CWSO's
now-correct image-baked healthcheck. Filed and fixed as **T312**
(`docs/tasks/task-T312.md`), merged via MR !89 (CI green). After that merge, `cwso-rollout` reports
`healthy` (see `docs/tasks/task-T304.md`'s 2026-08-01 re-verification section for full evidence:
`docker inspect` showing `"Status":"healthy"` with 4 consecutive successful probes).

Full re-verification evidence (build/up output, `docker compose ps`, `docker inspect`, MCP
`tools/list`) lives in `docs/tasks/task-T304.md` to avoid duplicating/drifting from a single source
of truth — this task's own acceptance criterion 3 ("a re-run of the T304-equivalent verification
shows `cwso-rollout` healthy") is now met by that re-verification.

**Resolved. Status: done.**
