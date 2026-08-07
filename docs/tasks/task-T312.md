# Task T312 — Fix stale rollout healthcheck target in docker-compose-t226.yml

**ID:** T312
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** T304 (blocked, re-verification in progress)
**Created:** 2026-08-01
**Completed:** 2026-08-01
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md, docs/tasks/task-T304.md, docs/tasks/task-T311.md

## Objective
Fix a genuine, fully-diagnosed defect in this repo's own `deploy/docker-compose-t226.yml`: the
`rollout` service's Compose-level `healthcheck.test` still targets the old
`http://127.0.0.1:8787/v1/models` endpoint (which intentionally returns HTTP 405 for a bare GET —
confirmed correct, POST-only behavior), even though CWSO's own upstream fix (commit `f7400f3`,
merged via their `bugfix/T170-rollout-healthcheck-and-store-path` branch, in response to this
repo's T310 hand-off) added a working `GET /healthz` liveness route and correctly updated CWSO's
own `deploy/Dockerfile.rollout` baked-in `HEALTHCHECK` to use it. Because Docker Compose's
service-level `healthcheck:` unconditionally overrides any image-baked `HEALTHCHECK`, our own
compose file's stale target masks the now-correct upstream fix. This is a defect in an artifact
this repo owns (not CWSO core), diagnosed directly (not guessed) via `docker exec cwso-rollout
curl -i http://127.0.0.1:8787/healthz` (→ `200 {"status":"ok"}`) vs `.../v1/models` (→ `405`,
correctly POST-only). The `orchestrator` service's healthcheck two lines up (line ~66) already
correctly targets `/healthz` via `wget` — this is a consistency fix, not a new pattern.

## Inputs
- `deploy/docker-compose-t226.yml` (line 154, the `rollout` service's `healthcheck.test`)
- `docs/tasks/task-T304.md` (2026-08-01 re-verification Execution notes — full diagnostic evidence)
- `docs/tasks/task-T311.md` (original defect record)
- `../CWSO` commit `f7400f3` (upstream fix this correction is completing the integration of)

## Expected outputs
- `deploy/docker-compose-t226.yml` with line 154 changed from
  `test: ["CMD", "curl", "-f", "http://127.0.0.1:8787/v1/models"]` to
  `test: ["CMD", "curl", "-f", "http://127.0.0.1:8787/healthz"]`.
- A feature/bugfix branch off `develop`, commit, push, MR referencing T312, CI green, merged.
- `cwso-rollout` reporting `healthy` after `docker compose up -d` (or
  `--force-recreate rollout`) picks up the change.

## Acceptance criteria
1. `deploy/docker-compose-t226.yml` line 154 (or wherever it lands after edit) reads
   `test: ["CMD", "curl", "-f", "http://127.0.0.1:8787/healthz"]`.
2. After recreating the `rollout` container, `docker inspect cwso-rollout --format
   '{{json .State.Health}}'` shows `"Status":"healthy"` with at least 2 consecutive successful
   probes (paste literal output).
3. `docker compose -f deploy/docker-compose-t226.yml ps` shows all of `orchestrator`,
   `git-shadow`, `merge-engine`, `rollout` as `Up`/`healthy` (git-shadow/merge-engine have no
   healthcheck defined, plain `Up` is acceptance per T304 precedent).
4. No other line in `deploy/docker-compose-t226.yml` is touched (R2: one task = one file/change).
5. Branch named `bugfix/t312-rollout-healthcheck-target` off `develop`; commit message
   `fix(t312): correct cwso-rollout healthcheck target to /healthz`; MR opened referencing T312;
   CI green before merge.
6. Stack left running afterward (do NOT `docker compose down`).

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed 2026-08-01 by a devops-engineer subagent (delegated by orchestrator).

**1. `git status` (initial):** clean `develop` aside from orchestrator-owned in-flight docs
(`active-tasks.md` modified, `task-T312.md` untracked) — left untouched by this task.

**2. Branch:** `git checkout develop && git pull --ff-only && git checkout -b
bugfix/t312-rollout-healthcheck-target` — created cleanly from up-to-date `develop`.

**3. Edit** — `deploy/docker-compose-t226.yml`, one line changed (`git diff`: 1 file, +1/-1):
```diff
-      test: ["CMD", "curl", "-f", "http://127.0.0.1:8787/v1/models"]
+      test: ["CMD", "curl", "-f", "http://127.0.0.1:8787/healthz"]
```

**4. Apply + verify:**
```
$ docker compose -f deploy/docker-compose-t226.yml up -d --force-recreate rollout
 Container cwso-rollout Recreated / Starting / Started

$ docker inspect cwso-rollout --format '{{json .State.Health}}'   (checked at t+15s and t+35s)
{"Status":"healthy","FailingStreak":0,"Log":[
  {"ExitCode":0,"Output":"...{\"status\":\"ok\"}"},
  {"ExitCode":0,"Output":"...{\"status\":\"ok\"}"},
  {"ExitCode":0,"Output":"...{\"status\":\"ok\"}"},
  {"ExitCode":0,"Output":"...{\"status\":\"ok\"}"}
]}
```
4 consecutive successful `/healthz` probes (exceeds the ≥2 required).

**5. All 4 target services:**
```
NAMES               STATUS
cwso-rollout        Up 45 seconds (healthy)
cwso-orchestrator   Up 6 minutes (healthy)
cwso-git-shadow     Up 6 minutes
cwso-merge-engine   Up 6 minutes
cwso-sia-executor   Up 6 minutes
```

**6. Commit:** `ccb86fb` — `fix(t312): correct cwso-rollout healthcheck target to /healthz` (1 file
changed, 1 insertion, 1 deletion — `active-tasks.md`/`task-T312.md` remained un-staged, confirming
scope discipline).

**7. Push:** `bugfix/t312-rollout-healthcheck-target` pushed to `origin`.

**8. MR:** https://gitlab.com/em-age/emage.code/-/merge_requests/89
(`bugfix/t312-rollout-healthcheck-target` → `develop`), description includes defect explanation,
diff, and healthy-verification evidence.

**9. CI:** polled to completion — **success**
(`sync/sync-no-diff`, `verify/validation-super-gate`, `verify/verify-knowledge-drift`,
`test/unit-tests`, `lint/markdown-links` all green). Pipeline:
https://gitlab.com/em-age/emage.code/-/pipelines/2724102773 (SHA `ccb86fb7`).
Per this task's delegation brief, the subagent correctly did **not** merge and reported back
awaiting orchestrator sign-off.

**10. Merge (orchestrator, not the subagent):** `glab mr merge 89 --squash --yes` — merged as
commit `de3d245` (merge of `35a18ca` "fix(t312): correct cwso-rollout healthcheck target to
/healthz"). Local `develop` synced via `git checkout develop && git pull --ff-only` —
fast-forwarded `390be4d..de3d245` cleanly.

Stack left running throughout (no `docker compose down`).

**All acceptance criteria met.** No blockers. **T312: done.**
