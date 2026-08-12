# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T400 | Add `scripts/check-version-consistency.py` (plan-035 P0) | devops-engineer | pending | P0 | — | 2026-08-12 |
| T401 | Fix confirmed version drift (README.md, implementation/README.md) (plan-035 P0) | technical-writer | pending | P0 | — | 2026-08-12 |
| T402 | Split docs into end-user (quick-start) vs. contributor (CONTRIBUTING) entry points (plan-035 P0) | technical-writer | pending | P1 | — | 2026-08-12 |
| T403 | Relocate CWSO deployment guides out of docs/deployment/ (plan-035 P0) | technical-writer | pending | P1 | — | 2026-08-12 |
| T404 | Extend release gate to block on version-consistency failure (plan-035 P0) | release-manager | pending | P0 | T400 | 2026-08-12 |
| T405 | Rule-set hardening: `/plan` output precondition of task creation (plan-035 P0) | tech-lead | pending | P1 | — | 2026-08-12 |
| T406 | Validation gate + merge Phase 0 (T400-T405) to develop (plan-035 P0) | qa-engineer | pending | P0 | T400, T401, T402, T403, T404, T405 | 2026-08-12 |
| T417 | Install Harbor; verify with oracle smoke run (plan-035, pulled forward from Phase 1) | devops-engineer | pending | P1 | — | 2026-08-12 |

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.
>
> Based on: `docs/plans/plan-035-roadmap-v7-ground-up.md` (Phase 0 + T417 only — user-approved
> 2026-08-12). No task beyond T400-T406/T417 may be added until Gate G0 closes and the plan's two
> open questions are resolved by the user.

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
