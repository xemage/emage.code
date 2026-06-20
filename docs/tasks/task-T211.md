# Task T211 - Map emage.code agent roles → CWSO permission tiers

## Objective
Define the mapping from emage.code agent roles to CWSO permission tiers and dispatch parameters so the
orchestrator delegates work with least privilege.

## Inputs
- `ADR-0xx-cwso-sia-integration.md` (T202)
- emage.code agent roster (`knowledge/agents/`)
- CWSO tiers: planning (orchestrator) vs worker; `dispatch_concurrent_jobs.sandbox_profile` enum

## Expected outputs
- `docs/artifacts/role-tier-mapping-v1.md`: each emage.code role → {CWSO tier, default sandbox_profile, allowed tools}
- Rule that callers cannot request `docker-trusted` (server enforces); default to `gvisor-fast-ephemeral`

## Acceptance criteria
- Every write-capable agent maps to worker tier; review/orchestration roles map to planning tier.
- Mapping respects emage.code security guidelines (read-only agents get no write tools).
- Mapping consumed by T212.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
