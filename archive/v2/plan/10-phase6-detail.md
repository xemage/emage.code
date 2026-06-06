# 10 — Phase 6 detail: Token governance & checkpoint compression

> Backfill of the v1 Phase-6 placeholder.

## Goal
Each phase has a token budget. The orchestrator tracks usage, warns at thresholds, and compresses context at phase boundaries.

## Budgets

| Phase | Budget | Compression trigger |
|-------|--------|---------------------|
| Planning | 80k | 64k (80%) |
| Architecture | 80k | 64k |
| Implementation | 120k | 96k |
| QA / Security / Release | 60k | 48k |

## Tracking format (in checkpoints)

```markdown
## Token usage
| Phase | Budget | Spent | % | Status |
|-------|--------|-------|---|--------|
| Planning | 80k | 64k | 80 | warn → compress at next handoff |
```

## Checkpoint compression contract

When the orchestrator hands work to a downstream agent, the agent receives **only**:
1. The latest phase checkpoint (`docs/checkpoints/checkpoint-<N>-<phase>.md`)
2. The agent's task brief (`docs/tasks/task-<ID>.md`)
3. Explicitly referenced artifact versions (e.g. `requirements-v1.md`)

It does **not** receive:
- Conversation history from earlier phases
- Other agents' working notes
- Plans from prior cycles

## Acceptance criteria
- [ ] `cost-token-governance/SKILL.md` documents budgets and tracking format.
- [ ] `checkpoint-protocol/SKILL.md` documents the compression contract.
- [ ] Orchestrator agents reference both skills.
- [ ] Every checkpoint template instance includes a `Token usage` table.

## Failure modes
- **Budget overshoot**: orchestrator must split the phase or escalate to user.
- **Missing checkpoint at phase boundary**: blocker `unclear_requirements` — orchestrator writes the checkpoint before any new delegation.
