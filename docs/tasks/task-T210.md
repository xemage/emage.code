# Task T210 - `CwsoClient` library (JWT, tools/call, rate-limit pacing)

## Objective
Implement a reusable client library that emage.code uses to call CWSO MCP tools with correct role-based
JWT auth, request pacing, and typed wrappers for the 11 tools.

## Inputs
- `docs/artifacts/cwso-mcp-contract-v1.md` (T201)
- Auth helper from T201

## Expected outputs
- `CwsoClient` with: `initialize`, `tools/call` wrappers for all 11 tools, role selection (orchestrator/worker),
  HS256 JWT minting, ≥1.05s pacing + retry on 429, structured error mapping (e.g. `-32002` permission errors)
- Unit tests with a mocked transport

## Acceptance criteria
- All 11 tool wrappers callable with typed args matching the contract schemas.
- Worker-tier tools (`write_*`, `commit_shadow`, `merge_concurrent_results`) use a worker JWT; planning-tier use orchestrator JWT.
- 429 handling and pacing verified by test.
- No secrets hardcoded; secret read from env/file.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
