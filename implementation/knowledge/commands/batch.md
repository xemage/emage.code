---
description: "Decompose a sweeping change into independent units for parallel execution across worktrees. Use for large refactors, migrations, or cross-cutting changes."
agent: "orchestrator"
argument-hint: "Describe the change to batch-process..."
maturity: experimental
audience: both
---

You are in **Batch Processing mode**. Decompose a large change into independent units that can be worked on in parallel across isolated worktrees.

## Instructions

1. **Analyse the change** — understand the full scope and identify natural boundaries (by module, feature, layer, or file group).
2. **Decompose into independent units** — each unit must be:
   - Self-contained (no cross-unit dependencies within a batch)
   - Independently testable
   - Small enough for a single agent session

   Write the decomposition to a plan document at `docs/plans/plan-<ID>.md`, following the structure `/plan` step 5 declares (`Goal`, `Task Decomposition`, `Dependency Graph`, `Resource Assignments`, `Risk Assessment`, `Open Questions`) — an independent batch renders as a `Dependency Graph` with no edges, which is the visual proof of step 2's constraint — plus one additional required section:
   - **Batch Manifest** — one row per unit: `| Task ID | Description | Assigned agent | Branch |`. This is where the branch is written down; `docs/tasks/active-tasks.md` is not (step 5). Each `Branch` cell must equal `agent/<Assigned agent>/<Task ID>`, so the manifest cannot drift from the ledger row it describes.
3. **Create worktree isolation** — for each unit:
   - Allocate the unit's task ID, ledger row and task brief first (step 5) — the branch name contains the task ID
   - Create a dedicated worktree and branch using the worktree-isolation skill
   - Branch naming: `agent/<agent-name>/<task-id>`, per `git-workflow.md` § "Agent Worktree Branch Naming" and the worktree-isolation skill's own convention
4. **Delegate to agents** — assign each unit to the appropriate agent (backend, frontend, qa, devops, docs) with clear instructions and acceptance criteria.
5. **Track progress** — record each unit as a task in `docs/tasks/active-tasks.md`, using that file's own 7-column schema (`AGENTS.md` § Task Protocol) and never a five-field manifest row, which its validator rejects:
   - Format (7 columns, exact order):
     `| T<NNN> | BATCH <slug>: <description> | <agent-slug> | pending | P0\|P1\|P2 | <dep-ids or —> | YYYY-MM-DD |`
   - Use the NEXT sequential `T<NNN>` ID for every unit. NEVER a `U<n>` or any other non-`T` unit ID — non-`T` rows fail `docs/tasks/validate-tasks.py` check `C3` and are silently deleted by `install.sh --update`.
   - Write a `docs/tasks/task-T<NNN>.md` brief per unit, whose `**Based on:**` field cites the step 2 plan document.
   - `Depends on` must not name another unit of the same batch — that is step 2's independence constraint, and `validate-tasks.py` checks `C12`/`C13`/`C14` are what enforce it. A dependency on a task *outside* the batch is permitted.
   - The branch is **not** a ledger column. It is `agent/<agent-slug>/T<NNN>` — determined by the row's own `Owner` and `ID` per step 3 — and is written out in the step 2 plan document's Batch Manifest.
   - Thereafter, track progress by transitioning each unit row's `Status` through the lifecycle in skill `task-management`. The ledger is authoritative for status; the manifest is not a second status record.
6. **Collect results** — as units complete, verify each passes its acceptance criteria.
7. **Guide PR creation** — once all units are verified:
   - Help the user create a PR for each branch
   - Suggest a merge order that respects any integration constraints
   - Recommend a final integration test after all merges

## Important

- Never modify the main branch directly. All work happens in worktree branches.
- If a unit turns out to have a dependency on another unit, flag it immediately and re-plan.
- Present the decomposition plan for user approval before creating worktrees.
- The order is fixed by the artifacts themselves: plan document (step 2) → user approval → ledger rows and task briefs (step 5) → worktrees and branches (step 3) → delegation (step 4). A unit's branch cannot be named before its task ID exists, and per `/plan` § "Task Creation Precondition" no unit row may be created until the step 2 plan document exists and has been presented for review.

## Rails

**Inputs**: A free-text description of the sweeping change to decompose (`{{input}}`).
**Out of scope**: Modifying the main branch directly — all work happens in worktree branches; merging units without user-approved PR review; writing a batch-shaped manifest row into `docs/tasks/active-tasks.md` — that file's columns are fixed by `AGENTS.md` § Task Protocol, and the manifest lives in the step 2 plan document.
**Failure mode**: If a unit turns out to depend on another unit after decomposition, flags it immediately and re-plans rather than continuing with a broken parallel split.

## Change Description

{{input}}
