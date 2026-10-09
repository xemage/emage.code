---
name: "task-management"
description: "Manage the task lifecycle: create, read, update, transition, and archive tasks in docs/tasks/. Use when creating tasks, updating task status, building task dependency graphs, or archiving completed work."
---

# Task Management

## Rails
**Inputs**: Creating a new task, updating task status, querying active tasks,
building or updating a dependency graph, or archiving a completed/cancelled
task — any lifecycle event touching `docs/tasks/active-tasks.md` or
`docs/tasks/completed-tasks.md`, per the "When to Use" list below.

**Out of scope**: Does not decide *whether* a task is complete — that
judgment belongs to skill `verification-before-completion` (invoked as
step 1 of "Complete a Task" below) and, for a defined acceptance bar, the
task brief itself. This skill only governs the mechanical ledger
create/read/update/transition/archive operations once that judgment is made.

**Failure mode**: Writing `done`/`cancelled` into `active-tasks.md` instead
of archiving to `completed-tasks.md` in the same edit is a protocol
violation per the file's own INVARIANT. An agent other than the orchestrator
performing the archive (moving a row, not merely reporting completion), or
completing a task out of the mandated 4-step atomic order, breaks the audit
trail this skill exists to preserve.

## Purpose

Manage the full lifecycle of project tasks — creation, status tracking, dependency management, and archival — using structured markdown tables in `docs/tasks/`.

## When to Use

- Creating a new task for planned or discovered work
- Updating task status (e.g., starting work, marking blocked, submitting for review)
- Querying active tasks, filtering by status or assignee
- Building or updating task dependency graphs
- Archiving completed tasks to `completed-tasks.md`

## File Locations

| File | Purpose |
|------|---------|
| `docs/tasks/active-tasks.md` | Tasks in `pending`, `in_progress`, `blocked`, `in_review` ONLY |
| `docs/tasks/completed-tasks.md` | Archived tasks that have been completed and verified |

> ## INVARIANT (never violate)
> `active-tasks.md` MUST NEVER contain a row whose Status is `done` or `cancelled`.
> The row is removed in the SAME edit that sets the terminal status.
> Writing `done` into `active-tasks.md` is a protocol violation.

## Task Table Format

### active-tasks.md — 7 columns, in this exact order
| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T042 | Add rate limiting | backend-developer | in_progress | P1 | T040 | 2026-07-27 |

### completed-tasks.md — 5 columns, in this exact order
| ID | Title | Owner | Done on | Outcome / artifact |
|----|-------|-------|---------|--------------------|
| T042 | Add rate limiting | backend-developer | 2026-07-27 | src/mw/ratelimit.ts; docs/tasks/task-T042.md |

### Field rules
| Field | Rule |
|-------|------|
| ID | `T` + 3 or more digits. `T001`, `T042`, `T1001`. NEVER `T1` or `T01`. NEVER `BUG-7`. |
| Owner | Exact agent slug, kebab-case, from the installed agents folder. |
| Status | `pending` \| `in_progress` \| `blocked` \| `in_review` \| `done` \| `cancelled` |
| Priority | `P0` \| `P1` \| `P2`. NEVER `critical`/`high`/`medium`/`low`. |
| Depends on | Comma-separated task IDs, or `—` |
| Last update / Done on | `YYYY-MM-DD`, a real date |

### Field mapping when archiving
| active column | goes to |
|---------------|---------|
| ID, Title, Owner | copied as-is |
| Status | DROPPED (implied `done`) |
| Priority | DROPPED |
| Depends on | DROPPED |
| Last update | becomes `Done on` |
| — | new `Outcome / artifact`: semicolon-separated paths, MUST include `docs/tasks/task-<ID>.md` |

## Status Lifecycle

```
pending → in_progress → blocked → in_progress → in_review → done
                  │                                          │
                  └──────────────────────────────────────────┘
                           (can regress if review fails)
```

`done` and `cancelled` are TERMINAL → archive immediately (see § "Complete a Task").

Valid transitions:

| From | To | Trigger |
|------|----|---------|
| `pending` | `in_progress` | Agent picks up the task |
| `in_progress` | `blocked` | Dependency or blocker encountered |
| `in_progress` | `in_review` | Implementation complete, ready for validation |
| `blocked` | `in_progress` | Blocker resolved |
| `in_review` | `done` | Validation gate passed |
| `in_review` | `in_progress` | Review rejected, rework needed |
| any | `cancelled` | Work abandoned — orchestrator decision |
| `in_review` | `cancelled` | Rejected outright |

## Procedures

Every ledger write in this section (create, update, dependency bookkeeping, complete, cancel) is performed by an orchestrator: "Only orchestrators create/transition tasks. Agents report completion and blockers." (`AGENTS.md` § Task Protocol). An agent other than an orchestrator that applies this skill proposes the change to the orchestrator and does not write the ledger.

### 1. Create a Task

1. Open `docs/tasks/active-tasks.md`.
2. Determine the next available `TNNN` ID (increment the highest existing ID).
3. Add a new row to the table with status `pending`.
4. If the task depends on other tasks, set its `Depends on` cell to their IDs, comma-separated (`—` when there are none).
5. If other tasks depend on this task, add this task's ID to their `Depends on` cells. This row needs no entry of its own: the ledger has no `Blocks` or `BlockedBy` column (`AGENTS.md` § Task Protocol).

### 2. Update Task Status

1. Locate the task row by ID in `active-tasks.md`.
2. Validate the transition is allowed (see lifecycle table above).
3. Update the `Status` field.
4. If transitioning to `blocked`, file a blocker report (see `blocker-escalation` skill).
5. If transitioning to `done`, proceed to the archive procedure.

### 3. Manage Dependencies

1. When adding a dependency, record it once, in the dependent task's `Depends on` cell. The tasks a task blocks are the rows whose `Depends on` names it: they are derived, not stored.
2. Before transitioning a task to `in_progress`, verify that every task named in its `Depends on` cell is `done` (listed in `completed-tasks.md`, or marked `(done)`).
3. When a task reaches `done`, find the active rows whose `Depends on` names it and evaluate whether they can be unblocked (§ 6 rewrites those cells).

### 4. Complete a Task (ATOMIC — all 4 steps in one edit session)

Performed by the ORCHESTRATOR ONLY. Other agents report completion; they never move rows.

1. Verify acceptance criteria are met (skill: `verification-before-completion`).
2. APPEND one row to `docs/tasks/completed-tasks.md` using the 5-column schema
   and the field mapping above. Append at the BOTTOM.
3. DELETE the task's row from `docs/tasks/active-tasks.md`.
4. In `docs/tasks/task-<ID>.md`, set the header lines to:
       **Status:** done
       **Completed:** YYYY-MM-DD

Land these edits via a branch and MR, never a direct commit to `main`/`develop` — even
though this is a ledger-only change, see `git-workflow.md` § "Protected Branches — No
Direct Commits, Ever" (no exceptions for docs/ledger-only edits, including this one).

Never do step 3 without step 2. Never do step 2 without step 4.

### 5. Cancel a Task

Same 4 steps, except step 2's `Outcome / artifact` MUST start with
`CANCELLED: <reason>;` and step 4 sets `**Status:** cancelled`.

### 6. Dependency bookkeeping

When T-x is completed, for every active row whose `Depends on` contains T-x,
rewrite that cell as `T-x (done)`. NEVER delete the reference — it is the audit trail.

## Examples

### Creating a Task

```markdown
| T012 | Add rate limiting to API | backend-developer | pending | P1 | T010 | 2025-03-20 |
```

### Transitioning a Task

Before:
```markdown
| T012 | Add rate limiting to API | backend-developer | pending | P1 | T010 | 2025-03-20 |
```

After (T010 completed):
```markdown
| T012 | Add rate limiting to API | backend-developer | in_progress | P1 | T010 (done) | 2025-03-21 |
```

## Guidelines

- Never skip statuses in the lifecycle (e.g., do not go directly from `pending` to `in_review`).
- Record each dependency once, in `Depends on`; never add a `Blocks` or `BlockedBy` field.
- Archive immediately: the row leaves `active-tasks.md` in the same edit that sets `done` or `cancelled` (§ Complete a Task; `AGENTS.md` § Task Protocol). Never leave a terminal row there, not even for one checkpoint cycle.
- Use the `dependency-graphing` skill to visualize complex dependency chains.
- Task IDs are immutable once assigned. Never reuse an ID.
