# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T689 | GitLab token placement: no full-disk-encryption assumption (SEC-T665-03, D-3) | devops-engineer | pending | P2 | T687 | 2026-10-24 |
| T694 | CWSO JWT secret out of emage.code: scripts read `CWSO_JWT_SECRET` only, the committed (rotated) value removed | devops-engineer | pending | P1 | — | 2026-10-31 |
| T695 | CWSO repository: dead JWT value out of CI and docs; restart policy and configurable Origin allow-list | devops-engineer | pending | P1 | — | 2026-10-31 |
| T696 | CWSO dependency and toolchain security update: 16 Rust advisories, Go 1.26.10 for 10 standard library vulnerabilities | devops-engineer | pending | P1 | — | 2026-10-31 |

> **Active rows (`plan-123`, post-release follow-ups after v8.0.0; approved by the user on 2026-10-16).** T662, T678 and T679 (Cursor removal in three steps under the accepted ADR-010), T663 (Opencode per-agent denies), T665 (GitLab token scope: implementation of the accepted design), T666 and T667 (named GitLab tool sets), T668 to T670 (golden realignment B under grant G-2, evaluator baseline v22, promote `orchestrator`; baseline v22 approved by the user on 2026-10-16), T672 to T677 (themed debt tasks from the tracked-debt register) (themed debt tasks). Baseline v21 until T669; root drift 0.

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.

> `docs/tasks/completed-tasks.md` is the full archive of finished tasks, `docs/checkpoints/` holds the phase-boundary summaries, and the pre-2026-10-09 notes that used to sit here are kept verbatim in `docs/tasks/ledger-notes-archive.md`. A short table means little is currently in flight.


Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
