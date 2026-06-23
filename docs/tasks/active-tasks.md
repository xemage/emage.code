# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T214 | Pattern A integration test (3 agents, deterministic merge) | qa-engineer | in_progress | P0 | T212 | 2026-06-22 |
| T225 | Reward shaping: merge ±1 + `results.json` eval metric | backend-developer | in_progress | P1 | T224 ✅ | 2026-06-23 |
| T230 | Trainer bridge: Parquet trajectories → GRPO/SFT dataset | backend-developer | pending | P0 | T225 | 2026-06-19 |
| T231 | Fine-tune `<some-model>` (LoRA/GRPO) + redeploy behind HAL | backend-developer | pending | P1 | T230 | 2026-06-19 |
| T232 | sia-harness release gate + Ed25519 witness signing | devops-engineer | pending | P1 | T230 | 2026-06-19 |
| T233 | Closed-loop eval on held-out task; measure deltas | qa-engineer | pending | P0 | T231, T232 | 2026-06-19 |
| T234 | Cost/latency telemetry per generation | devops-engineer | pending | P2 | T233 | 2026-06-19 |

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
