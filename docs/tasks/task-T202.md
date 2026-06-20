# Task T202 - ADR: CWSO×SIA integration patterns A/B/C (Polar already GA)

## Objective
Record the architectural decision for combining emage.code, CWSO, SIA, and `<some-model>`, including the
finding that Polar/rollout is already GA and the rationale for the A→B→C sequencing.

## Inputs
- `docs/plans/plan-009-cwso-emagecode-sia-integration.md` (§2, §4, §13)
- `docs/artifacts/cwso-mcp-contract-v1.md` (from T201)
- CWSO evidence: `services/cwso-rollout/src/*`, `orchestrator/internal/harness/*`, `docs/plans/plan-cwso-nextgen-phase6plus.md`

## Expected outputs
- `docs/decisions/ADR-0xx-cwso-sia-integration.md` (accepted) covering:
  - Pattern A (deterministic execution & merge backend)
  - Pattern B (SIA loop on CWSO with Polar capture)
  - Pattern C (weight updates from trajectories)
  - Decision: Polar is consumed, not rebuilt; A→B→C order

## Acceptance criteria
- ADR references Plan 009 and task IDs, lists alternatives considered and consequences.
- Explicit non-goal: "finishing Polar" (it is GA).
- Ownership boundaries between the four systems are stated.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
