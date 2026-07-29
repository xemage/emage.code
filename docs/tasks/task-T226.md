**Status:** done
**Completed:** 2026-06-23
# Task T226 - Deploy CWSO + Polar infrastructure for Phase 2 live integration testing

## Objective
Deploy a working CWSO + Polar infrastructure instance with rollout enabled to enable live integration testing of the SIA harness (T223) with reward attachment (T224) and reward shaping (T225). This is a prerequisite for Phase 2 live integration testing (T228) and the closed-loop evaluation (T233).

## Inputs
- T203 prerequisites: CWSO dev profile bring-up (rollout enabled, Parquet store configured)
- T224/T225 output: reward attachment and shaping modules expect `CWSO_BASE_URL` and `CWSO_JWT_SECRET` environment variables
- Polar documentation: trajectory capture configuration, Parquet schema validation

## Expected outputs
- CWSO running on `localhost:8080` with rollout proxy enabled
- Polar sidecar capturing trajectories to Parquet store (queryable location documented)
- Environment file (`/tmp/phase2-infra.env` or similar) with:
  - `CWSO_BASE_URL=http://localhost:8080`
  - `CWSO_JWT_SECRET=<test-jwt-token>` (ephemeral for dev/testing)
  - `CWSO_ROLLOUT_TRAJECTORY_STORE_PATH=<path-to-parquet-store>`
- Documented bring-up steps (docker-compose command, env setup, verification checklist)
- Health check passing: `curl http://localhost:8080/healthz`
- MCP endpoint authenticated: `curl -H "Authorization: Bearer <JWT>" http://localhost:8080/mcp`

## Acceptance criteria
- CWSO and Polar both running and healthy (health checks pass)
- At least one test trajectory written to Parquet store (can be from a manual SIA dispatch via the harness)
- Environment variables accessible to SIA harness launcher (T223) and reward attachment (T224/T225)
- No hardcoded secrets; all credentials via environment or mounted secret files
- Documented teardown procedure (stop containers, cleanup)

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
