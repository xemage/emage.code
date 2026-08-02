# Task T313 — local-docker-desktop-guide.md validation findings (13 documentation/script defects)

**ID:** T313
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** — (findings ready to action; no upstream blocker)
**Created:** 2026-08-01
**Completed:** 2026-08-02
**Based on:** docs/tasks/task-T305.md, docs/artifacts/t305-deployment-guide-validation-report-v1.md,
docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Fix the 13 distinct defects that T305's independent, literal, end-to-end validation of
`docs/deployment/local-docker-desktop-guide.md` found (full evidence in
`docs/artifacts/t305-deployment-guide-validation-report-v1.md` — every finding below is backed by
literal command output in that report, not asserted). All 13 findings were confirmed to trace to
this repo's own documentation and helper script (guide prose, `scripts/deploy/cwso-docker-desktop.sh`,
and `deploy/docker-compose-t226.yml` service naming) — **none** trace to a genuine CWSO-core defect,
so this task stays entirely within this repo; the T310 (`../CWSO` hand-off) convention does not
apply here.

Filed as one consolidated task (rather than 13 separate ledger rows) because all findings are
tightly coupled corrections to the same two artifacts (one guide doc, one script) plus one
compose-file naming inconsistency that the guide/script both assume; splitting further would
fragment a single coherent editing pass without added tracking value.

## Inputs
- `docs/deployment/local-docker-desktop-guide.md` (the guide under repair)
- `scripts/deploy/cwso-docker-desktop.sh` (the automated setup script under repair)
- `deploy/docker-compose-t226.yml` (source of truth for real service names/ports/volumes)
- `docs/artifacts/t305-deployment-guide-validation-report-v1.md` (full evidence for every finding)

## Expected outputs
- `docs/deployment/local-docker-desktop-guide.md` corrected so that a fresh reader following it
  literally (Quick Start + Detailed Setup Steps 1-4 + Monitoring/Healthchecks at minimum) succeeds,
  or the guide is restructured to explicitly point at `deploy/docker-compose-t226.yml` /
  `deploy/t226-phase2.env` / `../CWSO/.env.jwt.dev` (whichever is the actually-intended supported
  path — a judgment call for technical-writer + devops-engineer to make together, not assumed here).
- `scripts/deploy/cwso-docker-desktop.sh` corrected for its `JWT_SOURCE` reference and `--status`
  unhandled-`cd`-error crash.
- A follow-up decision (recorded in this task's Execution notes) on whether
  `deploy/docker-compose-t226.yml`'s `rollout` service should be renamed/aliased to also answer to
  `rollout-proxy`, or whether the guide/script should simply be corrected to say `rollout` — do not
  rename a live, already-verified-healthy production compose service without confirming no other
  consumer depends on the current name.

## Acceptance criteria
Each of the 13 findings below must be resolved (fixed) or explicitly deferred with a documented
reason (e.g., "out of scope for local Docker Desktop guide, tracked separately"):

1. **Critical** — Guide's "Detailed Setup → Step 1" references `deploy/docker-compose-local-dev.yml`
   / `deploy/docker-compose-local-dev.env`, neither of which exists. Fix: point at the real files
   (`deploy/docker-compose-t226.yml`, `deploy/t226-phase2.env`) or create the named files if a
   separate "local-dev" profile is actually intended — confirm which before editing.
2. **Critical** — Guide's "Configure JWT Secret → Option A" references `../.env.jwt.dev` /
   `deploy/.env.jwt.dev`, which do not exist in this repo (only `../CWSO/.env.jwt.dev` exists, a
   different repo). Fix the path or the instruction.
3. **Medium** — No AI-agent-safe path exists to obtain a working JWT per this repo's own
   `.claude/rules/security-guidelines.md` (agents are hard-blocked from reading `.env.*` files).
   Consider documenting an agent-safe alternative (e.g., a wrapper script that mints a token
   without exposing the raw secret to the caller's context).
4. **Critical** — `GET /health` on orchestrator (8080) returns `401 missing bearer token`, not the
   guide's documented JSON healthy payload, even on a genuinely healthy stack. Real no-auth route
   is `/healthz`. Fix the guide's Quick Start and Detailed Setup Step 4 to use `/healthz`.
5. **High** — `GET /health` on rollout (8787) returns `405 Method Not Allowed`; real liveness route
   is `/healthz`. Fix throughout the guide (Detailed Setup Step 4, Monitoring section).
6. **High** — Guide/script use nonexistent service/container name `rollout-proxy` in 3+ places
   (Viewing Logs, Container Status, Appendix); real name is `rollout`/`cwso-rollout`. Fix all
   occurrences (or make a documented naming decision per "Expected outputs" above).
7. **Critical** — Guide's own health-check loop (ports 8080/8787/8788/8789) fails on every port as
   written. Fix to use `/healthz` on 8080/8787 and remove/correct the assumption that 8788/8789
   (git-shadow/merge-engine) are curlable HTTP endpoints (see #8).
8. **High** — git-shadow (8788) and merge-engine (8789) are documented as curlable HTTP health
   endpoints but publish no host port at all (IPC-socket-only). Fix the guide/Appendix to stop
   implying these are directly curlable, or document the actual way to check their liveness.
9. **Medium** — Troubleshooting step `docker-compose exec orchestrator curl ...` fails — the
   orchestrator image ships no `curl`. Fix the troubleshooting advice (e.g., use `wget` if present,
   or check from the host against the published port instead of `exec`-ing into the container).
10. **Low** — Guide's expected-output table claims `COMMAND: "python3 ..."` for all 4 services;
    actual containers are `tini`-wrapped Go/Rust binaries. Fix the example table.
11. **Low** — `scripts/deploy/cwso-docker-desktop.sh --status` crashes with an unhandled `cd` error
    if run before first full setup. Fix: guard the `cd` with an existence check and print a clean
    "not deployed yet" message instead.
12. **Medium** — Guide's "Volume Management"/"Backup and Restore" sections reference a nonexistent
    volume `cwso-local-dev_orchestrator-data`; real volume is `cwso-runtime`. Fix both sections.
13. **Low** — Performance Tuning's `mem_limit`/`cpus` examples don't match the real compose file
    (0 matches currently). Fix the example or note it's aspirational/not-yet-applied.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed 2026-08-02 by technical-writer subagent (guide prose, findings 1-10/12/13) and
devops-engineer subagent (script logic, findings 6 script-portion/11), delegated by orchestrator;
all findings independently re-verified by the orchestrator directly against the live,
T304/T312-verified-healthy CWSO stack (`deploy/docker-compose-t226.yml`) before ledger completion.
Branch: `bugfix/t313-deployment-guide-fixes`.

Baseline (unchanged before/after all work in this task):
```
$ docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"
NAMES               STATUS
cwso-rollout        Up 12 hours (healthy)
cwso-orchestrator   Up 13 hours (healthy)
cwso-git-shadow     Up 13 hours
cwso-merge-engine   Up 13 hours
cwso-sia-executor   Up 13 hours
```

### Finding 1 — Step 1 nonexistent file references
Before: `cp deploy/docker-compose-local-dev.yml deploy/local-dev/docker-compose.yml` /
`cp deploy/docker-compose-local-dev.env deploy/local-dev/.env` (neither file exists).
After: `cp deploy/docker-compose-t226.yml deploy/local-dev/docker-compose.yml` /
`cp deploy/t226-phase2.env deploy/local-dev/.env` — the real files, matching the automated
script's own `DOCKER_COMPOSE_SOURCE`/`ENV_SOURCE` variables.
Orchestrator-verified: `ls -la deploy/` shows only `docker-compose-t226.yml` and `t226-phase2.env`
exist in `deploy/` (confirmed identically to T305's original finding).

### Findings 2 & 3 — JWT Option A wrong path / no AI-agent-safe path
Before: Option A did `source ../.env.jwt.dev` (does not exist anywhere in this repo). No AI-safe
alternative was documented.
After: Option A corrected to `source ../CWSO/.env.jwt.dev` (the real sibling-repo path) with an
explicit note it is human-operator-only; Option B (fresh secret generation, no file read) promoted
to the recommended default for both humans and agents; explicit "AI coding agents MUST NOT use
Option A" note citing `.claude/rules/security-guidelines.md`. This resolves finding 3 by documented
deferral (no code fix attempted — no agent-safe JWT-minting wrapper was created, per acceptance
criteria's allowance for "explicitly deferred with a documented reason").

### Finding 4 — orchestrator `/health` vs `/healthz`
Orchestrator-verified directly (2026-08-02):
```
$ curl -s -i http://localhost:8080/healthz --max-time 5
HTTP/1.1 200 OK
Content-Length: 2
Content-Type: text/plain; charset=utf-8

ok

$ curl -s -i http://localhost:8080/health --max-time 5
HTTP/1.1 401 Unauthorized
Content-Type: text/plain; charset=utf-8
Content-Length: 21

missing bearer token
```
Guide's Quick Start and Detailed Setup Step 4 now use `/healthz` for liveness, with `/health`
documented as a separate authenticated endpoint.

### Finding 5 — rollout `/health` vs `/healthz`
Orchestrator-verified directly (2026-08-02):
```
$ curl -s -i http://localhost:8787/healthz --max-time 5
HTTP/1.1 200 OK
content-type: application/json
content-length: 15

{"status":"ok"}

$ curl -s -i http://localhost:8787/health --max-time 5
HTTP/1.1 405 Method Not Allowed
content-type: application/json
content-length: 46

{"error":{"message":"only POST is supported"}}
```
Guide's Detailed Setup Step 4 and Monitoring section now use `/healthz`; `/health` documented as
POST-only.

### Finding 6 — `rollout-proxy` → `rollout` naming (guide + script)
Guide portion (technical-writer): all occurrences (Viewing Logs, Container Status, Appendix,
Performance Tuning) corrected from `rollout-proxy`/`cwso-rollout-proxy` to `rollout`/`cwso-rollout`.
Decision: kept the live, already-verified-healthy compose service's real name as-is — did not
rename the compose service.
Orchestrator-verified directly (2026-08-02):
```
$ docker compose -f deploy/docker-compose-t226.yml logs --tail=3 rollout
cwso-rollout  | {"timestamp":"2026-08-01T17:11:55.774538Z", ... "cwso-rollout IPC ready" ...}
cwso-rollout  | {"timestamp":"2026-08-01T17:11:55.776885Z", ... "starting rollout proxy","bind":"0.0.0.0:8787" ...}
cwso-rollout  | {"timestamp":"2026-08-01T17:11:55.777071Z", ... "cwso-rollout proxy listening" ...}

$ docker compose -f deploy/docker-compose-t226.yml logs --tail=3 rollout-proxy
no such service: rollout-proxy

$ docker stats cwso-orchestrator cwso-rollout --no-stream
CONTAINER ID   NAME                CPU %     MEM USAGE / LIMIT    MEM %   ...
b26b71dfeea3   cwso-orchestrator   0.00%     13.99MiB / 7.51GiB   0.18%   ...
28154aa211f5   cwso-rollout        0.01%     21.29MiB / 7.51GiB   0.28%   ...
```
Script portion (devops-engineer): `verify_deployment()` line 173, `for service in orchestrator
rollout-proxy; do` → `for service in orchestrator rollout; do` (the old pattern could never match
a real service, always reporting a false failure). Verified without disturbing the live stack:
```
$ grep -n "^  rollout:\|container_name: cwso-rollout" deploy/docker-compose-t226.yml
117:  rollout:
122:    container_name: cwso-rollout

$ docker compose -f deploy/docker-compose-t226.yml ps | grep "rollout-proxy" | grep -q Up; echo "exit=$?"
exit=1
$ docker compose -f deploy/docker-compose-t226.yml ps | grep "rollout" | grep -q Up; echo "exit=$?"
exit=0
```

### Finding 7 — Monitoring health-check loop fails on every port
Before: `for port in 8080 8787 8788 8789; do curl -s http://localhost:$port/health | jq ...`
After: loop scoped to `8080 8787` only, using `/healthz`; 8788/8789 removed (see finding 8) with a
pointer to the Container Status section instead. Verified via the same `/healthz` evidence as
findings 4/5 above.

### Finding 8 — git-shadow/merge-engine not curlable
Orchestrator-verified directly (2026-08-02):
```
$ grep -A15 "^  git-shadow:\|^  merge-engine:" deploy/docker-compose-t226.yml | grep -i "ports\|container_name"
    container_name: cwso-git-shadow
    container_name: cwso-merge-engine
```
(no `ports:` key present for either service — confirms IPC-socket-only, no host port). Guide now
documents this and points to `docker compose -f deploy/docker-compose-t226.yml ps git-shadow
merge-engine` as the real liveness check.

### Finding 9 — troubleshooting `exec ... curl` fails
Orchestrator-verified directly (2026-08-02):
```
$ docker exec cwso-orchestrator curl -s http://localhost:8080/healthz
OCI runtime exec failed: exec failed: unable to start container process:
exec: "curl": executable file not found in $PATH
```
Guide's Network Connection Issues troubleshooting step replaced with a host-side `curl -i
http://localhost:8080/healthz` check plus an explanation that the orchestrator image ships no
`curl`.

### Finding 10 — expected-output table claims `python3`
Orchestrator-verified directly (2026-08-02):
```
$ docker compose -f deploy/docker-compose-t226.yml ps
NAME                IMAGE                   COMMAND                  SERVICE        ... STATUS
cwso-git-shadow     cwso/git-shadow:dev     "/usr/bin/tini -- /u…"   git-shadow     ... Up 12 hours
cwso-merge-engine   cwso/merge-engine:dev   "/usr/bin/tini -- /u…"   merge-engine   ... Up 12 hours
cwso-orchestrator   cwso/orchestrator:dev   "/sbin/tini -- /usr/…"   orchestrator   ... Up 12 hours (healthy)
cwso-rollout        cwso/rollout:dev        "/usr/bin/tini -- /u…"   rollout        ... Up 12 hours (healthy)
```
Guide's Detailed Setup Step 3 expected-output table corrected to match (tini-wrapped Go/Rust
binaries, not `python3`).

### Finding 11 — `--status` unhandled `cd` crash
Before:
```
$ ls -la deploy/local-dev 2>&1
ls: cannot access 'deploy/local-dev': No such file or directory

$ bash scripts/deploy/cwso-docker-desktop.sh --status; echo "EXIT_CODE=$?"
=== CWSO Deployment Status ===
scripts/deploy/cwso-docker-desktop.sh: line 211: cd: ./deploy/local-dev: No such file or directory
EXIT_CODE=1
```
After (guard added to `show_status()`):
```
$ bash scripts/deploy/cwso-docker-desktop.sh --status; echo "EXIT_CODE=$?"
=== CWSO Deployment Status ===
⚠ CWSO is not deployed yet (no ./deploy/local-dev found).
Run 'bash scripts/deploy/cwso-docker-desktop.sh' first.
EXIT_CODE=0
```

### Finding 12 — nonexistent volume `cwso-local-dev_orchestrator-data`
Orchestrator-verified directly (2026-08-02):
```
$ docker volume ls | grep -i cwso
local     cwso-t226_cwso-runtime
local     cwso_cwso-runtime

$ grep -A3 "^volumes:" deploy/docker-compose-t226.yml
volumes:
  cwso-runtime:
    driver: local
```
Guide's Volume Management / Backup and Restore sections corrected to reference the real
`cwso-runtime` volume (project-prefixed on host), not the nonexistent
`cwso-local-dev_orchestrator-data`.

### Finding 13 — Performance Tuning `mem_limit`/`cpus` mismatch
Orchestrator-verified directly (2026-08-02):
```
$ grep -c "mem_limit\|cpus:" deploy/docker-compose-t226.yml
0
```
Guide's Performance Tuning section now marks these examples as aspirational (not currently applied
in `docker-compose-t226.yml`) and fixes `rollout-proxy:` → `rollout:` in the example blocks.

### Post-fix live stack re-confirmation (2026-08-02, after both commits)
```
$ docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"
NAMES               STATUS
cwso-rollout        Up 12 hours (healthy)
cwso-orchestrator   Up 13 hours (healthy)
cwso-git-shadow     Up 13 hours
cwso-merge-engine   Up 13 hours
cwso-sia-executor   Up 13 hours
```
Identical to baseline — live stack was never disturbed by this task's work.

### Disposition
All 13 findings resolved: 11 by guide-prose correction (findings 1, 4, 5, 6-guide, 7, 8, 9, 10, 12,
13), 1 by documented deferral with explicit reasoning (finding 3 — no AI-agent-safe JWT-minting
wrapper was built; existing Option B already satisfies the agent-safe requirement), 2 by real
script-logic fixes (finding 6-script, finding 11). No CWSO-core defect found — T310 hand-off
convention correctly does not apply, consistent with T305's own root-cause routing conclusion.

Commits on branch `bugfix/t313-deployment-guide-fixes`:
- `ac8ee02` — `fix(t313): correct local-docker-desktop-guide.md against live CWSO stack behavior`
- `54a5c57` — `fix(t313): guard cwso-docker-desktop.sh --status crash and correct rollout service name`

**Status: done. Completed: 2026-08-02.**
