# Task T318 — Rewrite `docs/deployment/README.md` to name the real files

**ID:** T318
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T317
**Created:** 2026-08-02
**Completed:** 2026-08-03
**Based on:** docs/plans/plan-017-deployment-docs-and-registry-hardening.md

## Objective
Fix `docs/deployment/README.md`, which currently instructs readers to `cd deploy/local-dev` and
inspect volumes named `cwso-local-dev_orchestrator-data` — a directory and naming scheme that has
not existed since before the real `deploy/docker-compose-t226.yml` stack. Never mentions the real
compose file by name.

## Inputs
- `docs/deployment/README.md` (current, stale)
- `deploy/docker-compose-t226.yml`, `deploy/t226-phase2.env` (the real files)
- `scripts/deploy/cwso-docker-desktop.sh` (the real automated setup script)

## Expected outputs
- `docs/deployment/README.md`, corrected in place.

## Acceptance criteria
1. Every `deploy/local-dev` reference replaced with the real `deploy/` layout (no subdirectory).
2. Quick start / Common Deployment Tasks sections use
   `docker compose -f deploy/docker-compose-t226.yml <subcommand>` and real container names
   (confirm via `docker ps --filter "name=cwso-"` if a stack is running, else
   `grep container_name deploy/docker-compose-t226.yml`).
3. `scripts/deploy/cwso-docker-desktop.sh` given clear, prominent placement as the real entry
   point.
4. Proxmox/GCP sections' content untouched in this task (that's T320's disclaimer-only change).
5. `grep -c "deploy/local-dev" docs/deployment/README.md` → 0.
6. `grep -c "docker-compose-t226.yml" docs/deployment/README.md` → 1 or more.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed: 2026-08-03 (delegated to technical-writer subagent)

### Substitutions made

| # | Found | Replaced with |
|---|-------|---------------|
| 1 | `cd deploy/local-dev && docker-compose logs -f` | `docker compose -f deploy/docker-compose-t226.yml logs -f` |
| 2 | `cd deploy/local-dev && docker-compose down` | `docker compose -f deploy/docker-compose-t226.yml down` |
| 3 | `docker volume inspect cwso-local-dev_orchestrator-data` | `docker volume inspect cwso-runtime` (actual named volume from compose file) |
| 4 | `` `docker-compose logs` → check for port conflicts `` | `` `docker compose -f deploy/docker-compose-t226.yml logs` → check for port conflicts `` |

Script prominence: `scripts/deploy/cwso-docker-desktop.sh` was already the primary Quick Start entry point — no change needed.

### Verify output
```
grep -c "deploy/local-dev" docs/deployment/README.md
0
```
```
grep -c "docker-compose-t226.yml" docs/deployment/README.md
3
```

**Result: PASS** (0 stale references; 3 ≥ 1 correct references)
