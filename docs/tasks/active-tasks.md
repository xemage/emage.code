# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T661 | Decision: drop Cursor support completely (ADR-010 and inventory) | solution-architect | pending | P1 | — | 2026-10-16 |
| T662 | Implement the ADR-010 outcome: remove Cursor support | devops-engineer | pending | P1 | T661 | 2026-10-16 |
| T663 | Opencode per-agent denies (SEC-T658-01 fixable part) | devops-engineer | pending | P1 | — | 2026-10-16 |
| T664 | Design: GitLab token scope and environment handling (SEC-T660-01) | solution-architect | pending | P1 | — | 2026-10-16 |
| T665 | Implement the T664 token-scope decision | devops-engineer | pending | P1 | T664 | 2026-10-16 |
| T666 | Named GitLab tool sets for orchestrator and poc-orchestrator (SEC-T660-04) | devops-engineer | pending | P1 | — | 2026-10-16 |
| T667 | Named GitLab tool sets for devops-engineer, release-manager and poc-devops-engineer | devops-engineer | pending | P2 | T666 | 2026-10-16 |
| T668 | Golden realignment B under grant G-2 (prepare-release and /skillify cases) | qa-engineer | pending | P1 | — | 2026-10-16 |
| T669 | Evaluator baseline v22 | orchestrator | pending | P1 | T668 | 2026-10-16 |
| T670 | Promote orchestrator to stable | backend-developer | pending | P1 | T669 | 2026-10-16 |
| T671 | Tracked-debt register | tech-lead | pending | P1 | — | 2026-10-16 |
| T672 | Installer and generator robustness (tracked debt) | devops-engineer | pending | P2 | T671 | 2026-10-16 |
| T673 | Test quality (tracked debt) | qa-engineer | pending | P2 | T671 | 2026-10-16 |
| T674 | Documentation corrections (tracked debt) | technical-writer | pending | P2 | T671 | 2026-10-16 |
| T675 | CI and release tooling hardening (tracked debt) | devops-engineer | pending | P2 | T671 | 2026-10-16 |
| T676 | Supply-chain and verification checklist items (tracked debt) | devops-engineer | pending | P2 | T671 | 2026-10-16 |
| T677 | Function-size refactors (tracked debt) | devops-engineer | pending | P2 | T672, T675 | 2026-10-16 |

> **Active rows (`plan-123`, post-release follow-ups after v8.0.0; approved by the user on 2026-10-16).** T661 (ADR: drop Cursor support) and T662 (implementation), T663 (Opencode per-agent denies), T664 and T665 (GitLab token scope: design and implementation), T666 and T667 (named GitLab tool sets), T668 to T670 (golden realignment B under grant G-2, evaluator baseline v22, promote `orchestrator`; baseline v22 approved by the user on 2026-10-16), T671 (tracked-debt register) and T672 to T677 (themed debt tasks). Baseline v21 until T669; root drift 0.

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.

> `docs/tasks/completed-tasks.md` is the full archive of finished tasks, `docs/checkpoints/` holds the phase-boundary summaries, and the pre-2026-10-09 notes that used to sit here are kept verbatim in `docs/tasks/ledger-notes-archive.md`. A short table means little is currently in flight.


Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
