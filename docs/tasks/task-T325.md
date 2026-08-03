# Task T325 — Fix the now-actually-working "Updating CWSO Image" instructions

**ID:** T325
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T324
**Created:** 2026-08-02
**Completed:** 2026-08-03
**Based on:** docs/plans/plan-017-deployment-docs-and-registry-hardening.md

## Objective
`local-docker-desktop-guide.md`'s "Updating CWSO Image" section and
`cwso-docker-desktop.sh --update` both call `docker-compose pull`, which was dead prior to T323
(no `image:` field existed to pull against). Now that T323/T324 make it real, update the
documentation and script to match actual working behavior.

## Inputs
- `docs/deployment/local-docker-desktop-guide.md` § "Updating CWSO Image"
- `scripts/deploy/cwso-docker-desktop.sh` (`--update` path)
- T324's confirmation that pull-based updates work

## Expected outputs
- Both files updated to reflect real, current, working behavior.

## Acceptance criteria
1. Guide prose no longer implies or states behavior inconsistent with the now-working
   `image:`-based compose file.
2. `bash scripts/deploy/cwso-docker-desktop.sh --update` actually run and produces real output
   showing images pulled/updated — pasted into Execution notes.
3. `bash scripts/deploy/cwso-docker-desktop.sh --update` exits 0.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed: 2026-08-03

Files updated:
1. `docs/deployment/local-docker-desktop-guide.md` ("Updating CWSO Image" section)
   - now uses:
     - `docker compose -f deploy/docker-compose-t226.yml pull`
     - `docker compose -f deploy/docker-compose-t226.yml up -d --force-recreate`
     - `bash scripts/deploy/cwso-docker-desktop.sh --update`
2. `scripts/deploy/cwso-docker-desktop.sh`
   - migrated runtime operations to `docker compose -f deploy/docker-compose-t226.yml ...`
   - removed `deploy/local-dev` hard dependency in update/status/log functions
   - updated verification endpoint checks to `/healthz` (orchestrator, rollout)

Verify command:
`bash scripts/deploy/cwso-docker-desktop.sh --update`

Literal output excerpt:
```
=== Updating CWSO Deployment ===
Pulling latest images...
[+] pull 5/5
✔ Image registry.gitlab.com/em-age/emage.code.cwso/orchestrator:v0.5.2 ... Pulled
✔ Image registry.gitlab.com/em-age/emage.code.cwso/git-shadow:v0.5.2 ... Pulled
✔ Image registry.gitlab.com/em-age/emage.code.cwso/merge-engine:v0.5.2 ... Pulled
✔ Image registry.gitlab.com/em-age/emage.code.cwso/rollout:v0.5.2 ... Pulled
Recreating containers...
... cwso-orchestrator Healthy ...
=== Verifying Deployment ===
✓ orchestrator is running
✓ rollout is running
✓ Orchestrator health check passed
✓ Rollout proxy health check passed
✓ Deployment updated successfully
```

Result: PASS (exit 0)
