# ADR-001 — Integrate emage.code, CWSO, and SIA into a self-improving coding swarm

> Filename: `ADR-001-cwso-sia-integration.md`

- **Status**: Accepted
- **Date**: 2026-06-20
- **Decider(s)**: solution-architect
- **Tasks**: T202 (decision record), T201 (MCP contract), T203 (dev profile); Phase 1: T210–T214; Phase 2: T220–T225; Phase 3: T230–T234
- **Evidence**: plan-009-cwso-emagecode-sia-integration.md §2 framing & §4 architecture; cwso-mcp-contract-v1.md (T201); cwso-dev-profile-t203-v1.md (T203)

## Context

Four systems now exist in the emage.code ecosystem:
- **emage.code orchestrator**: decomposes work into parallel agent tasks, validates gates, manages checkpoints
- **CWSO kernel** (Rust/Go): deterministic semantic merge via libgit2 + Tree-sitter AST; Polar (rollout+capture) sidecar already GA
- **SIA orchestrator** (Python): generational self-improvement loop (meta→target→feedback); contract via `evaluate.py` → `results.json`
- **`<some-model>`**: local open-weight model to be fine-tuned from RL trajectories

**Problem**: These systems operate in isolation. An opportunity exists to combine them into a single closed loop where emage.code orchestrates deterministic agent tasks through CWSO's concurrent merge engine, captures agent-model interactions via Polar, and drives self-improvement via SIA.

**Constraints**:
- CWSO MCP contract (11 tools, role-gated auth) is stable for integration window (evidence: T201)
- Polar/rollout is already GA; rebuilding is not justified (evidence: plan-009 §2.2, CWSO source)
- Secrets (JWT, provider keys) must be env-only; none committed to repo
- Integration must preserve emage.code's deterministic merge and audit trail semantics

## Decision

We adopt **three composable patterns** in sequence, plus explicit ownership boundaries:

### Pattern A: CWSO as deterministic execution & merge backend
Route emage.code's multi-agent tasks through CWSO shadow workspaces and AST-semantic merge:
1. emage.code calls `create_shadow_workspace` (per agent) → allocate in-memory libgit2 workspace
2. Each agent writes files via `write_shadow_file` → staged in shadow ODB
3. Agent commits via `commit_shadow` → tree OID created
4. emage.code calls `merge_concurrent_results` with all source workspaces → AST-aware semantic merge with reward hook (`rollout_session_id`)
5. Merge outcome (success, conflict details, tree OID) returned to emage.code for audit trail

**Value**: Deterministic concurrent merges eliminate ad-hoc conflict resolution; conflict visibility is explicit; requires zero new infrastructure.
**Timeline**: Usable now; implementation scope M/L (T210–T214).

### Pattern B: SIA target agent loop with Polar trajectory capture (harness-only, no weight updates)
Wrap one emage.code agent as a SIA *target agent*; run through CWSO harness launcher to intercept LLM calls via Polar proxy:
1. SIA meta/feedback agents propose improvements to target agent (prompt, behavior)
2. Target agent runs inside CWSO sandbox container; env includes `CWSO_OBJECTIVE_PROMPT` (from dispatch) + `OPENAI_BASE_URL` rewritten to `cwso-rollout` proxy
3. All LLM completions are captured as `CompletionRecord` (prompt/sampled token IDs, logprobs) → Parquet trajectory store
4. Merge outcome (from Pattern A) is attached as reward (`merge_concurrent_results` → `rollout_session_id`) + eval metric from `evaluate.py` (task success signal)
5. SIA stores generational feedback and selects next hypothesis

**Value**: Demonstrates end-to-end trajectory capture; validates reward shaping (merge + eval); decouples capture from weight updates.
**Constraint**: No weight updates yet — SIA-H only (harness improvement, not model weight improvement).
**Timeline**: Safe PoC; scope M (T220–T225).

### Pattern C: Weight updates from trajectories (SIA-W), governed by sia-harness
Feed Parquet trajectory store to external trainer; redeploy updated `<some-model>`:
1. Trainer consumes trajectories (T230: bridge reads Parquet → GRPO/SFT dataset)
2. Fine-tune `<some-model>` offline (LoRA/GRPO; T231)
3. Redeploy behind `cwso-hal` (reused T151 HAL provider route)
4. sia-harness wraps curate→train→eval→deploy as MCP-exposed personas (curator, trainer, evaluator, deployer); each step is witness-signed (Ed25519) and gated by release criteria (T232)
5. Repeat: new generations of SIA loop against retrained model

**Value**: Closed RL loop with provenance and release gates; model improves from observed agent/LLM interactions.
**Constraint**: Only viable after B validates trajectory quality and eval signal stability.
**Timeline**: Highest cost/complexity; scope L (T230–T234).

### Sequence Rationale: A → B → C

- **A first (now)**: Zero infrastructure; immediate value for emage.code's concurrent tasks. Proves CWSO MCP + audit trail. Gate: deterministic merge test (T214).
- **B second (cheap)**: Reuses A infrastructure; validates trajectory capture and reward signals before committing to trainer. Gate: trajectories in Parquet + eval metric visible (T225).
- **C third (only if B passes)**: Commits to expensive trainer loop only when trajectory quality is known. Gate: closed-loop eval delta measured (T233).

**Rationale for not doing C first**: Trajectory quality is unknown; committing trainer resources before validating reward signals risks poor model performance.

### Key Finding: Polar is GA and is consumed, not rebuilt

**Evidence**:
- CWSO Phase 9 (Polar/rollout) marked complete in plan-cwso-nextgen-phase6plus.md
- Rollout sidecar (`cwso-rollout/src/{config,capture,record,store}.rs`) implements four-step capture: detect → normalize → forward+store → denormalize
- `CompletionRecord` schema (prompt_token_ids, sampled_token_ids, logprobs, finish_reason, timestamp_ns) is stable (T201)
- Parquet trajectory store and KV prefix cache (differential prompting, T150/T151) are operational
- Reward hook (`merge_concurrent_results.rollout_session_id`) exists in schema (T136)

**Decision consequence**: Do **not** spend effort rebuilding or "finishing" Polar. Instead, focus scope on:
1. Real harness-adapter images (Pattern B) — stubs today, need actual Go/TS agent runners
2. External trainer bridge (Pattern C) — Polar emits trajectories; nothing consumes them yet
3. Reward shaping beyond merge ±1 (Pattern B/C) — integrate eval signals from SIA

### Ownership Boundaries

| System | Responsibilities | Does NOT do |
|--------|-----------------|-------------|
| **emage.code** | Task decomposition; agent delegation; validation-gate verdicts; checkpoint lifecycle | Merge logic; trajectory capture; model fine-tuning |
| **CWSO** | Shadow workspace isolation; AST-semantic merge; concurrent job dispatch; trajectory capture via rollout; reward emission | Task decomposition; RL training; code validation logic |
| **SIA** | Generational improvement loop (meta→target→feedback); eval.py contract; results.json feedback | Merge; capture; weight updates; harness orchestration |
| **`<some-model>` + trainer** | Model weights; fine-tuning (GRPO/SFT from trajectory data) | Execution; merging; capture; improvement loop control |
| **sia-harness** | Release gates (gated.yaml); Ed25519 witness signing; governance personas (curator, trainer, evaluator, deployer); agentdb memory | Implementation of training; capture; merge |

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| **Alt 1: Finish Polar first** | Ensures rollout infrastructure is "complete" | Polar is already GA; effort spent on non-blocking tasks; harness adapters remain stubs; trainer bridge still TBD | Chosen to reject. Evidence: plan-009 §2.2 + CWSO source audit. Focus on harness adapters (Pattern B) and trainer bridge (Pattern C) instead. |
| **Alt 2: Pattern C (weight updates) first** | Faster to "close the loop" if successful | Trajectory quality unknown; high cost if reward signals are wrong; unvalidated harness adapters; trainer not yet designed | Chosen to reject. B is cheaper validation step; gates C. |
| **Alt 3: Direct filesystem I/O without CWSO** | Simpler integration; avoid MCP dependency | Lose deterministic merging; conflict heuristics become ad-hoc; no audit trail of merge decisions; no trajectory capture seam | Chosen to reject. CWSO merges are semantic + conflict-aware; emage.code's determinism depends on it. |

## Consequences

**Positive**:
- Deterministic concurrent merges eliminate error-prone manual conflict resolution
- Polar infrastructure is already available; no rebuild effort required
- RL loop is reproducible and governed via sia-harness gates + witness signing
- Pattern A provides immediate value; B/C are optional follow-ups

**Negative**:
- Requires MCP client library in emage.code (T210)
- Harness-adapter images for SIA targets must be built (T220); today only shell-command works
- Trainer bridge design and implementation (T230–T231) is L-scope and outside emage.code core
- HAL GPU provider fallback observed (T203 blocker); acceptable on CPU; priority if scaling to GPU workloads

**Risks introduced**:
- CWSO MCP contract changes could break integration (mitigate: T202 decision locks patterns until contract bump)
- Trajectory data volume unknown; storage/query performance TBD (mitigate: T225 PoC validates scale before T230)
- Reward signal from eval.py may not correlate with model improvement (mitigate: Phase 3 eval gates T233)

**Follow-ups**:
- T210–T214 (Pattern A: concurrent merge + MCP client)
- T220–T225 (Pattern B: harness adapters + capture PoC)
- T230–T234 (Pattern C: trainer bridge + sia-harness governance)

## Security constraints

- **No provider secrets in trajectories**: API keys, auth headers, and prompt injections must not be persisted in the Parquet store. Implement via request/response filtering in cwso-rollout.
- **Secrets via environment only**: JWT secret (dev: `.env.jwt.dev`), provider API keys, model credentials delivered via env vars or mounted files at runtime. Never committed to Git.
- **Audit trail for all reward attachments**: Every `rollout_session_id` must be traceable to a specific emage.code task ID and SIA generation.
- **sia-harness witness signing**: All train/deploy steps must be signed with Ed25519 witness keys; signature verification is mandatory before weight deployment.

## Validation

**How we confirm Pattern A is correct**:
- Integration test: 3 emage.code agents concurrently edit a Go/Python/Rust repo; deterministic semantic merge produces consistent tree OID; audit trail shows all agent commits and merge heuristics (T214).

**How we confirm Pattern B is correct**:
- SIA generation runs through CWSO harness launcher; LLM calls appear in Parquet trajectory store with token IDs + logprobs; merge reward (±1) + eval metric are attached; no provider secrets leak (T225 + security review).

**How we confirm Pattern C is correct**:
- Closed-loop eval: N SIA generations against a fixed held-out task; measure performance deltas (success rate, token efficiency) after model fine-tuning; witness signatures present on train/deploy steps (T233).
