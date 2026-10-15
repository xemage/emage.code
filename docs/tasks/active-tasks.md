# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T644 | Release branch, version markers and stale claims | release-manager | pending | P1 | T643 | 2026-10-15 |
| T645 | Write docs/releases/v8.0.0.md | release-manager | pending | P1 | T644 | 2026-10-15 |
| T648 | QA release gate | qa-engineer | pending | P1 | T644, T645, T647 | 2026-10-15 |
| T649 | Tech Lead review by area | tech-lead | pending | P1 | T645 | 2026-10-15 |
| T650 | Release-level security re-check | security-engineer | pending | P1 | T646, T655 | 2026-10-15 |
| T651 | Release manager verdict | release-manager | pending | P1 | T648, T649, T650 | 2026-10-15 |
| T652 | Publish v8.0.0 (release MRs, main merge, tag) | orchestrator | pending | P0 | T651 | 2026-10-15 |
| T654 | Evaluate Playwright MCP as the fetch replacement (hands-on) | devops-engineer | pending | P0 | T653 | 2026-10-15 |
| T655 | Remove the fetch server and apply the hardened Playwright entry | devops-engineer | pending | P0 | T654 | 2026-10-15 |

> **Active rows (`plan-122`, release v8.0.0 wave 3; approved by the user on 2026-10-15).** T644 (release branch and version markers), T645 (release document), T654 (evaluate Playwright MCP as the fetch replacement), T655 (remove fetch, harden Playwright), T648 (QA gate), T649 (Tech Lead review by area), T650 (security re-check), T651 (release manager verdict), T652 (publish; each outward step needs the user's approval). Baseline v21; root drift 0 (refresh 18 done).

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.

> `docs/tasks/completed-tasks.md` is the full archive of finished tasks, `docs/checkpoints/` holds the phase-boundary summaries, and the pre-2026-10-09 notes that used to sit here are kept verbatim in `docs/tasks/ledger-notes-archive.md`. A short table means little is currently in flight.


Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
