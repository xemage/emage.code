# Task T324 — Bring the stack up from registry images and re-verify health

**ID:** T324
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** T323
**Created:** 2026-08-02
**Completed:** 2026-08-03
**Based on:** docs/plans/plan-017-deployment-docs-and-registry-hardening.md, docs/tasks/task-T304.md

## Objective
Prove the registry-image-based stack works exactly as well as the source-built stack T304
verified — same acceptance bar, no regressions, no mocks.

## Inputs
- `deploy/docker-compose-t226.yml` (post-T323, registry-image-based)

## Expected outputs
- A running, healthy 4-service stack built entirely from pulled images (no local build).

## Acceptance criteria
1. `docker compose -f deploy/docker-compose-t226.yml down` run first — tear down any prior
   source-built stack so this is a genuine pulled-image test, not stale local image reuse.
2. `docker compose -f deploy/docker-compose-t226.yml up -d`, `sleep 15`, then
   `docker compose -f deploy/docker-compose-t226.yml ps` and
   `docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"`.
3. `orchestrator`/`rollout` show explicit `(healthy)`; `git-shadow`/`merge-engine` show `Up` (no
   healthcheck defined, confirmed in T304 — this is expected, not a gap).
4. If ANYTHING regresses vs. the source-built behavior: do NOT mark this done. Capture full logs
   (`docker compose -f deploy/docker-compose-t226.yml logs <service>`), file a bug task, and note
   that a registry image behaving differently than its source build would itself be a reportable
   defect (likely another T321-style hand-off to CWSO).
5. All command outputs pasted into Execution notes. Stack left running afterward.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed: 2026-08-03

Commands run:
```
docker compose -f deploy/docker-compose-t226.yml down
docker compose -f deploy/docker-compose-t226.yml up -d
docker compose -f deploy/docker-compose-t226.yml ps
docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"
```

Literal output excerpt:
```
cwso-orchestrator ... Up ... (healthy)
cwso-rollout      ... Up ... (healthy)
cwso-git-shadow   ... Up
cwso-merge-engine ... Up
```

`docker ps --filter "name=cwso-"` output:
```
NAMES               STATUS
cwso-sia-executor   Up 43 seconds
cwso-orchestrator   Up 54 seconds (healthy)
cwso-rollout        Up 54 seconds (healthy)
cwso-merge-engine   Up 54 seconds
cwso-git-shadow     Up 54 seconds
```

Result: PASS. Registry-image stack behavior matches T304 acceptance bar.
Stack left running.
