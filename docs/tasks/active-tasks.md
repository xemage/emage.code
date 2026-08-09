# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T382 | Execute repo-root update install (prove merge-safety + removal live) | devops-engineer | pending | P0 | T381, T388 | 2026-08-09 |
| T383 | Add literal-secret guard for generated MCP outputs | security-engineer | pending | P2 | T381 | 2026-08-09 |
| T384 | Document per-platform runtime MCP verification checklist | devops-engineer | pending | P2 | T381 | 2026-08-09 |
| T385 | Time-boxed re-attempt to resolve Pi's MCP config format | devops-engineer | pending | P2 | T381 | 2026-08-09 |
| T386 | Remove e2b/redis/figma/notion from servers.yaml; regenerate implementation/ trees | devops-engineer | pending | P1 | T381 | 2026-08-09 |
| T387 | Remove e2b/redis/figma/notion references from hand-authored docs | technical-writer | pending | P1 | T386, T381 | 2026-08-09 |
| T388 | Validation gate and merge server removal to develop | tech-lead | pending | P1 | T386, T387 | 2026-08-09 |

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.
>
> `T377`-`T388` (plan-033, MCP settings hardening) execution is in progress as of 2026-08-09 (explicit
> user go-ahead received). `T377`-`T381` (core merge-safety fix + validation gate) merged to `develop`
> via MR !164 (squash commit `02b42f0`, merge commit `453ffb2`) — see `completed-tasks.md`.
>
> Note on `T381`/`T388`'s Owner column: each is a combined `tech-lead` (read-only review) +
> `orchestrator` (git mechanics) task; the ledger's Owner cell holds only `tech-lead` because the
> owner-validity check (`tests/performance/test_team_health.py::test_task_owners_are_real_agents`)
> requires a single known agent slug per row, not a comma-joined list — see T375's precedent. The
> task brief itself documents both roles in full.

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
