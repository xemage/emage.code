**Status:** done
**Completed:** 2026-06-20
# Task T201 - Live MCP contract snapshot + auth helper

## Objective
Capture a verifiable snapshot of the CWSO `v0.4.1` MCP contract from the running server and produce a
reusable, role-aware JWT/HTTP client helper so downstream tasks build against a pinned, tested surface.

## Inputs
- Live server: `http://127.0.0.1:8080/mcp`
- Dev JWT secret: `CWSO/.env.jwt.dev`
- JWT recipe: `CWSO/scripts/phase2-integration.py` (`mint_jwt`, claims `{role, iss:"cwso", aud:["cwso-mcp"], exp}`)
- Plan 009 §3.1 (11-tool surface)

## Expected outputs
- `docs/artifacts/cwso-mcp-contract-v1.md` — enumerated tools, input schemas, roles/tiers, error codes, rate limits
- Reusable auth/transport helper (mint HS256 JWT, `tools/list`, `tools/call`, ≥1.05s pacing, role selection)
- Snapshot test that fails if the live `tools/list` diverges from the recorded contract

## Acceptance criteria
- `tools/list` returns exactly the 11 documented tools for `orchestrator` and `worker` roles.
- Helper authenticates successfully; `planner` role is shown to be rejected (`403 unrecognised role`).
- Contract records that `commit_shadow`/`write_*` are worker-tier and `create/drop/dispatch` are planning-tier.
- Snapshot test runnable in CI against a dev profile.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
