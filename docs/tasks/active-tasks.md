# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|

> **0 active rows. `T514` closed 2026-09-24 — see `completed-tasks.md` for the full closure
> record.** `plan-064` Phase 10 is done, and it is the first task executed from the v8 roadmap.
> **5 agents promoted** (`backend-developer`, `context-retriever`, `devops-engineer`,
> `evaluation-agent`, `solution-architect`) — the agent category moves from 20/8 to **25 `stable` /
> 3 `experimental`**. The 3 that did not promote (`orchestrator`, `security-engineer`, `tech-lead`)
> each fail criteria **3 and 7** on a `known_failing`/`tracked_defect` golden case belonging to a
> command they own; each is a concrete, independently-actionable command-surface defect, and
> together they are the entire remaining distance to 28/28. **`plan-064` §1.3's hypothesis was
> confirmed but its count corrected upward, 4 → 5** — `backend-developer` was also available, missed
> because §1.3 drew on the Wave 2 artifact while that agent was a Wave 1 candidate blocked by the
> same already-resolved `T457` match. The implementer's own conflict of interest (`tech-lead` was
> one of the eight it evaluated) was actively controlled, not assumed away: the top-level session
> independently flipped `tech-lead` itself and confirmed the predicted `FAIL`; the implementer had
> reported its own failure honestly.

> **T514 dispatched 2026-09-24** — `plan-064` Phase 10, approved by the user for task-brief
> authoring. Re-runs promotion readiness for all 8 agents at `maturity: experimental`; `plan-064`
> §1.3's hypothesis is that four of them (`context-retriever`, `devops-engineer`,
> `evaluation-agent`, `solution-architect`) were blocked *solely* by `T456`/`T457`, both closed
> 2026-09-17. The brief treats that as a hypothesis to test, not a target to hit. **P2 is
> deliberate and disclosed**: the work genuinely is nice-to-have (it collects already-earned value
> and blocks nothing), and P2 also keeps this row out of criterion 7's open-defect scan — which at
> P0/P1 would block the very promotions the task exists to perform, the self-referential trap this
> repo has hit repeatedly. `check-maturity.py`'s own P2 filter was verified against the
> implementation before dispatch, not taken from the criteria document. See `docs/tasks/task-T514.md`
> and `docs/plans/plan-065-t514-dispatch-plan-coverage.md`.

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.

> 0 active rows. This is not a fresh project — 511 real tasks (`T001`-`T511`) have already run to
> completion; see `docs/tasks/completed-tasks.md` for the full archive and `docs/checkpoints/` for
> phase-boundary summaries, most recently `checkpoint-release-v7.0.0.md`. Do not treat an empty
> table as "no history exists" — it means no task is currently in flight.

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
