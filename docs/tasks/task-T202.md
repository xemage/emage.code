**Status:** done
**Completed:** 2026-06-20
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

## Additional brief content


## Objective
Create an Architecture Decision Record (ADR) that documents the three integration patterns (A/B/C) for combining emage.code, CWSO, SIA, and `<some-model>`, with explicit decision rationale and the finding that Polar/rollout is already GA (consume, don't rebuild).

## Context & Inputs
- **Plan**: docs/plans/plan-009-cwso-emagecode-sia-integration.md (§2 framing, §4 architecture, §13 recommendation)
- **MCP Contract Evidence**: docs/artifacts/cwso-mcp-contract-v1.md (from T201) — 11 tools, JWT auth, role-based permissions
- **Dev Profile Evidence**: docs/artifacts/cwso-dev-profile-t203-v1.md (from T203) — rollout capture verified, HAL working
- **CWSO Source References**:
  - Phase 9 (Polar/rollout) marked complete: `CWSO/docs/plans/plan-cwso-nextgen-phase6plus.md`
  - Rollout sidecar implementation: `CWSO/services/cwso-rollout/src/{config,capture,record,store}.rs`
  - Harness launcher + adapters: `CWSO/orchestrator/internal/harness/{launcher,registry,runtime}.go`
  - Reward hook: `merge_concurrent_results.rollout_session_id` field in schema

## Expected Outputs

**File**: `docs/decisions/ADR-0xx-cwso-sia-integration.md`

Structure (standard ADR 1.0):
1. **Title**: "Integrate emage.code, CWSO, SIA into a self-improving coding swarm"
2. **Status**: `Accepted` (by user on 2026-06-19)
3. **Context** (1–2 paragraphs):
   - Why: Four systems exist; opportunity to combine for deterministic execution + RL capture
   - What: Current state of each system (CWSO GA, SIA proven, emage.code orchestration, `<some-model>` TBD)
4. **Decision** (core):
   - **Pattern A** (deterministic execution & merge backend):
     - Route emage.code multi-agent tasks through CWSO's shadow workspaces + semantic merge
     - Usable immediately; no new infrastructure required
     - MCP tools enable concurrent isolation + AST-aware conflict resolution
   - **Pattern B** (SIA loop on CWSO with Polar capture):
     - Wrap an emage.code agent as a SIA target agent
     - Run generations through CWSO harness launcher (capture seam)
     - Reward = merge outcome ± 1 + task eval metric
     - No weight updates yet (SIA-H: harness-only)
   - **Pattern C** (weight updates from trajectories):
     - Feed Parquet trajectories to external trainer (GRPO/SFT)
     - sia-harness governs curate→train→eval→deploy lifecycle
     - Witness-signed + release-gated
   - **Sequence**: A (now) → B (cheap, safe PoC) → C (only after B proves trajectory quality)
5. **Consequences**:
   - **Positive**: Deterministic merges eliminate ad-hoc conflict resolution; Polar already GA (no rebuild needed); RL loop is reproducible and governed
   - **Negative**: Requires MCP client library in emage.code; harness-adapter image development; trainer bridge design
   - **Risk**: HAL GPU fallback (acceptable on CPU; priority for future if scaling to GPU)
6. **Alternatives Considered**:
   - **Alt 1**: Finish/enhance Polar first → Decision: **Rejected** — Polar is GA; focus on harness adapters and trainer bridge instead
   - **Alt 2**: Weight updates (Pattern C) first → Decision: **Rejected** — B is cheaper and validates trajectory quality first
   - **Alt 3**: Direct file I/O without CWSO shadow → Decision: **Rejected** — lose deterministic merging and conflict visibility
7. **Ownership Boundaries**:
   - **emage.code**: Task decomposition, delegation, validation gates, checkpoints
   - **CWSO**: Isolation, AST merge, concurrency, trajectory capture, reward emission
   - **SIA**: Generational improvement loop, eval contract
   - **`<some-model>` + trainer**: Weights + fine-tuning
   - **sia-harness**: Provenance (Ed25519 witness) + release gates

## Acceptance Criteria
- [ ] ADR references specific Task IDs (T201, T203, T210–T214, etc.) and Plan 009
- [ ] Explicit statement: "Polar is consumed (already GA); this plan does not rebuild it"
- [ ] System boundaries and ownership clearly stated
- [ ] Three patterns (A/B/C) and rationale for sequencing documented
- [ ] Alternative (Alt 1 = "finish Polar") marked as rejected with reasoning
- [ ] Security constraints noted (secrets via env only, no provider keys in trajectories)
- [ ] ADR filed and accepted (status = `Accepted`)

## Constraints
- Stay grounded in evidence (MCP contract snapshot, dev profile artifact, CWSO source)
- Keep ADR length ≤ 1500 words (enough detail, avoid excessive narrative)
- Do not propose new tools or architecture; document the decision for existing/planned work
- Focus on decision rationale, not implementation details (T210–T234 handle implementation)

## Blocker Protocol
If blocked, report:
- **Type**: `technical` | `dependency` | `unclear_requirements` | `external`
- **Severity**: `critical` | `major` | `minor`
- **Description**: What is blocking and why
- **Proposed mitigation**: One concrete next step to unblock

## Deliverable Verification
After completion, answer: **"Does the ADR clearly explain why we use Pattern A→B→C order and why Polar is not a blocker?"**
