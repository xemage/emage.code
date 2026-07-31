# Task T304 — Real Docker build + healthcheck of the T226 compose stack

**ID:** T304
**Owner:** devops-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T300
**Created:** 2026-07-31
**Completed:** —
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Prove, for real, that CWSO's documented Docker Compose profile (`deploy/docker-compose-t226.yml`)
actually builds and runs — no mocked substitute, no assumption carried over from the fabricated
Phase 2/3 reports. This is the prerequisite for Wave 4 (deployment guide validation) and Wave 5
(the real T214 Pattern A test).

## Inputs
- `deploy/docker-compose-t226.yml`, `deploy/t226-phase2.env`
- `../CWSO` (orchestrator, git-shadow, merge-engine, rollout services)
- `docs/artifacts/cwso-mcp-contract-v1.md` (expected 11-tool MCP contract)

## Expected outputs
- A running, healthy 4-container CWSO stack (left running for Wave 4/5).
- This file's Execution notes containing all command outputs below.

## Acceptance criteria
1. Host-side pre-flight: `cd ../CWSO/orchestrator && go build ./...` — paste its exit code and
   output regardless of pass/fail (go IS installed on this host: `go1.26.3 linux/amd64`).
2. `docker compose -f deploy/docker-compose-t226.yml build` then `up -d`, then
   `docker compose -f deploy/docker-compose-t226.yml ps` and
   `docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"`.
3. `orchestrator`, `git-shadow`, `merge-engine`, `rollout` all show `Up` / `healthy`. If ANY service
   fails to build or is unhealthy: capture the FULL build/log output
   (`docker compose -f deploy/docker-compose-t226.yml logs <service>`), file a new bug task in this
   repo's ledger, do NOT mark this task done, do NOT substitute a smaller/mocked compose file, and
   hand off to T310.
4. If the stack is healthy, also run the MCP contract sanity check: mint an orchestrator-role JWT
   per plan-009 Appendix A and call `tools/list` against `http://127.0.0.1:8080/mcp` — expect a
   JSON-RPC response listing 11 tools.
5. Per R8, paste every command's literal output into Execution notes. Do NOT run
   `docker compose down` at the end — leave the stack up for T305/T214.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
