# T508 — Fix `plan-035`'s stale per-phase status headers

**Status:** done

**Closure note:** All six status lines fixed, checkpoint citations independently re-verified. See
`docs/tasks/completed-tasks.md`'s T508 row for full detail.
**Owner:** Technical Writer
**Priority:** P1
**Depends on:** none (docs-only correction)
**Based on:** `docs/plans/plan-060-v7-release-readiness-and-closure.md` §4, `docs/plans/plan-035-roadmap-v7-ground-up.md`.

## Objective

`docs/plans/plan-035-roadmap-v7-ground-up.md` has a `**Status:**` header at the top of every phase
section. Phase 1's (line 280) was updated to `APPROVED` when that phase was approved. Phases 2
through 6's headers were never updated and still read:

```
**Status: proposed — not approved for task-brief authoring or execution.**
```

at lines 325 (Phase 2), 564 (Phase 3), 595 (Phase 4), 623 (Phase 5), 648 (Phase 5's RAG
sub-section), and 680 (Phase 6) — even though all of these phases were, in reality, approved and
executed this project cycle, with real checkpoints closing their gates. This is exactly the kind of
documentation drift `plan-035`'s own §2.6 risk table warns about ("Doc drift returns after Phase 0")
— the roadmap is the one document a future session is most likely to read cold and trust literally,
and right now it would mislead one into thinking none of Phases 2–6 ever happened.

## What to do

For each of the six stale status lines, replace `**Status: proposed — not approved for task-brief
authoring or execution.**` with a status reflecting the real, current state, citing the real
checkpoint(s) that closed that phase's gate. **Verify every citation directly against the named
checkpoint file's actual content before writing it — do not take the mapping below as pre-verified.**
Likely correct anchors, subject to your own confirmation:

| Line | Phase | Likely closing checkpoint(s) |
|---|---|---|
| 325 | Phase 2 — MCP Conformance | `docs/checkpoints/checkpoint-022-phase2-complete.md` |
| 564 | Phase 3 — Maturity Ladder | `docs/checkpoints/checkpoint-029-phase3-t433-gate-g2-closed.md`, `docs/checkpoints/checkpoint-032-phase3-complete.md` |
| 595 | Phase 4 — Task-Tier Routing | `docs/checkpoints/checkpoint-033-phase4-phase5-complete-gate-g3-closed.md` |
| 623 | Phase 5 — Persistent Memory / RAG (intro) | `docs/checkpoints/checkpoint-033-phase4-phase5-complete-gate-g3-closed.md` |
| 648 | Phase 5 — RAG sub-section | same as line 623 |
| 680 | Phase 6 — Closed Loop | `docs/checkpoints/checkpoint-034-phase6-six-task-implementation-complete.md` |

For Phase 6 specifically, the new status text must reflect the real, nuanced state honestly, not a
blanket "done": the six originally-scoped tasks are implemented and merged, but read
`docs/tasks/completed-tasks.md`'s `T507` row (and `docs/artifacts/t507-closed-loop-cycle-v1.md`)
first — a real end-to-end cycle has now run, produced a real merge request, and the human gate
correctly caught a non-improvement before it landed. State plainly that Phase 6's own acceptance
criteria around demonstrated held-out-suite improvement and an accepted change's lineage document
remain open, not implied as closed. Do not round this up to "complete."

Use a status phrasing parallel to Phase 1's own `**Status: APPROVED for task-brief authoring and
execution (<date>).**` pattern, but each should also name the real checkpoint(s) that closed it —
e.g. `**Status: APPROVED and executed. Gate G2 closed per checkpoint-029/032 (2026-09-XX).**` (use
the real dates from the cited checkpoints, not a placeholder).

## Constraints

- **Docs-only.** Edit only `docs/plans/plan-035-roadmap-v7-ground-up.md`'s six status lines (plus,
  if genuinely necessary for a line's grammar, the immediately adjacent sentence — do not rewrite
  any other part of the roadmap's content, findings, or phase specifications).
- Do not touch `docs/plans/plan-060-v7-release-readiness-and-closure.md` or any task ledger file —
  this task's own status transition is handled by the top-level session, the same way `T506`'s was,
  since you have no `execute`/Bash tool access to commit/push/open an MR yourself. Write the edited
  roadmap file's content and report back; the top-level session performs the git operations.
- When citing this project's own branching/commit conventions document, use a paraphrase rather
  than its literal filename in any prose you write into `docs/tasks/active-tasks.md`,
  `docs/tasks/completed-tasks.md`, or this brief — that literal filename is a `stable`-tier
  component id and trips `check-maturity.py`'s self-referential-defect check if it appears verbatim
  in open P0/P1 task-ledger text. This does not restrict the roadmap document itself, which is not
  scanned by that check.
- Do not invent or round up a checkpoint's actual content — if a phase's real closure state is more
  qualified than "done" (as Phase 6's is), say so plainly rather than picking the cleaner-sounding
  status.

## Acceptance criteria

- [ ] All six stale `**Status: proposed — not approved...**` lines replaced with accurate,
      checkpoint-cited status text
- [ ] Every checkpoint citation verified directly against that checkpoint file's real content, not
      assumed from this brief's table
- [ ] Phase 6's new status text does not overstate completion — explicitly notes the open items
      (held-out-suite improvement, lineage document for an accepted change)
- [ ] No other content in `plan-035-roadmap-v7-ground-up.md` changed
- [ ] `python3 docs/tasks/validate-tasks.py` and `python3 implementation/scripts/check-maturity.py --verbose` both pass after this task's own ledger entries are written (top-level session verifies this as part of closing the task)

## Blocker protocol

Standard: `technical | dependency | unclear_requirements | external`, severities
`critical | major | minor`, max 2 retries before escalation.
