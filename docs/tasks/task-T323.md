# Task T323 — Migrate `deploy/docker-compose-t226.yml` to registry images with a source-build override

**ID:** T323
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** T322 (must be READY, not just attempted)
**Created:** 2026-08-02
**Completed:** 2026-08-03
**Based on:** docs/plans/plan-017-deployment-docs-and-registry-hardening.md

## Objective
Switch the emage.code-side compose file to reference CWSO's published registry images by default,
fixing the hardcoded absolute-path portability defect as a side effect, while preserving a
documented, opt-in path for building from local source.

## Inputs
- `deploy/docker-compose-t226.yml` (current, `build:`-based)
- T322's READY disposition (confirmed tags)

## Expected outputs
- `deploy/docker-compose-t226.yml`, modified.
- `deploy/docker-compose-t226.build.yml` (new override file).

## Acceptance criteria
1. For each of the 4 CWSO services, `image: cwso/<service>:dev` + `build: context: ...` replaced
   with a single `image: registry.gitlab.com/em-age/emage.code.cwso/<service>:<confirmed-tag>`
   line (use T322's confirmed real tag — prefer a semver tag over `:latest` if one was published).
   `build:` blocks for these 4 services removed from the main file entirely.
2. `deploy/docker-compose-t226.build.yml` created containing ONLY the 4 services' `build:` blocks,
   using `context: ${CWSO_SOURCE_DIR:-../CWSO}` (relative-path env-var default, not the old
   hardcoded absolute path).
3. `sia-executor` and all other service configuration (ports, env vars, secrets, healthchecks)
   unchanged — this task is scoped to `image:`/`build:` fields only.
4. `grep -n "context: /home/emage/Code/emage/CWSO" deploy/docker-compose-t226.yml` → 0 matches.
5. `grep -c "registry.gitlab.com/em-age/emage.code.cwso" deploy/docker-compose-t226.yml` → 4.
6. `docker compose -f deploy/docker-compose-t226.yml pull` → exit 0, all 4 images actually pulled
   (literal output pasted).

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed: 2026-08-03

Changes made:
1. `deploy/docker-compose-t226.yml` switched from `cwso/*:dev` + `build:` to registry images:
   - `registry.gitlab.com/em-age/emage.code.cwso/orchestrator:v0.5.2`
   - `registry.gitlab.com/em-age/emage.code.cwso/git-shadow:v0.5.2`
   - `registry.gitlab.com/em-age/emage.code.cwso/merge-engine:v0.5.2`
   - `registry.gitlab.com/em-age/emage.code.cwso/rollout:v0.5.2`
2. Removed all 4 `build:` blocks for those services from the main compose file.
3. Created `deploy/docker-compose-t226.build.yml` with only the 4 service `build:` blocks using
   `context: ${CWSO_SOURCE_DIR:-../CWSO}`.

Verify output:
```
hardcoded context count: 0
registry refs count: 4
build override exists
```

`docker compose -f deploy/docker-compose-t226.yml pull` output:
```
[+] pull 21/21
✔ Image python:3.11-slim                                            Pulled 2.2s
✔ Image registry.gitlab.com/em-age/emage.code.cwso/git-shadow:v0... Pulled 6.6s
✔ Image registry.gitlab.com/em-age/emage.code.cwso/orchestrator:... Pulled 7.7s
✔ Image registry.gitlab.com/em-age/emage.code.cwso/merge-engine:... Pulled 7.3s
✔ Image registry.gitlab.com/em-age/emage.code.cwso/rollout:v0.5.2   Pulled 7.9s
```

Result: PASS
