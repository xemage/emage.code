# Task T313 — local-docker-desktop-guide.md validation findings (13 documentation/script defects)

**ID:** T313
**Owner:** technical-writer
**Status:** pending
**Priority:** P1
**Depends on:** — (findings ready to action; no upstream blocker)
**Created:** 2026-08-01
**Completed:** —
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
<filled during execution>
