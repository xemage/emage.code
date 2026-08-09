# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T382 | Execute repo-root update install (prove merge-safety + removal live) | devops-engineer | pending | P0 | T381, T388 | 2026-08-09 |
| T383 | Add literal-secret guard for generated MCP outputs | security-engineer | pending | P2 | T381 | 2026-08-09 |
| T384 | Document per-platform runtime MCP verification checklist | devops-engineer | pending | P2 | T381 | 2026-08-09 |
| T385 | Time-boxed re-attempt to resolve Pi's MCP config format | devops-engineer | pending | P2 | T381 | 2026-08-09 |

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.
>
> `T377`-`T388` (plan-033, MCP settings hardening) execution is in progress as of 2026-08-09 (explicit
> user go-ahead received). `T377`-`T381` (core merge-safety fix + validation gate) merged to `develop`
> via MR !164 (squash commit `02b42f0`, merge commit `453ffb2`); `T386`-`T388` (server registry
> removal + validation gate) merged via MR !166 (squash commit `0d5f9bc`, merge commit `f1ebfbf`) —
> see `completed-tasks.md`. Remaining: `T382`-`T385`.

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
