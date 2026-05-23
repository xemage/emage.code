# Task T010 — Build sync and drift tooling

## Objective
Implement v3 sync and drift tooling to propagate canonical knowledge to generated surfaces and detect divergence.

## Inputs
- docs/artifacts/v3-schema-contract-v1.md
- v2/implementation/scripts/sync.mjs
- v2/implementation/scripts/verify.mjs

## Expected outputs
- v3/implementation/scripts/sync-v3.mjs
- v3/implementation/scripts/verify-v3.mjs

## Acceptance criteria
- Sync generates deterministic outputs for all supported platforms.
- Verify reports drift with actionable file-level diagnostics.
- Tooling works in CI and local development.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
