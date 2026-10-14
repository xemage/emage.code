# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T640 | Release body = the release document only; commit list to CHANGELOG.md only, merge commits excluded (T632 group C3, code part) | devops-engineer | pending | P1 | T635 | 2026-10-15 |
| T635 | Resolve the T625 review conditions C1-C3 (and the cheap Nice-to-Have items) for the release job | devops-engineer | pending | P1 | T625 | 2026-10-14 |
| T627 | Run a real /skillify interview with the user (GitLab API fallback workflow) and apply the /skillify template fix | orchestrator | pending | P1 | — | 2026-10-14 |
| T628 | Golden realignment A under grant G-1 (items 1-10, 11 if T627 is merged, 12 only if S-HO-1 allows it) | qa-engineer | pending | P1 | T625, T626 | 2026-10-14 |
| T629 | Evaluator baseline v21 | orchestrator | pending | P1 | T628 | 2026-10-14 |
| T630 | Promote tech-lead to stable | backend-developer | pending | P1 | T629 | 2026-10-14 |

> **Active rows (`plan-121`, release v8.0.0 wave 2; approved by the user on 2026-10-14).** T624 (apply the T621 rulings) and T625 (Tech Lead `/code-review` of the T619 MR) are done. Open: T626 (QA check of the T625 artifact), T627 (`/skillify` with the user), T628 (golden realignment under grant G-1), T629 (baseline v21), T630 (promote `tech-lead`), T631 (adopter docs), T632 (release-document ruling), T633 (release-level security audit), T634 (ADR-008 note), T635 (release-job conditions). Baseline v20; root drift 33 (declared by T624, waits for one user-approved root refresh). Item 12 of G-1 and T630 wait for the held-out read (the user adds a Bash permission rule).

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.

> `docs/tasks/completed-tasks.md` is the full archive of finished tasks, `docs/checkpoints/` holds the phase-boundary summaries, and the pre-2026-10-09 notes that used to sit here are kept verbatim in `docs/tasks/ledger-notes-archive.md`. A short table means little is currently in flight.


Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
