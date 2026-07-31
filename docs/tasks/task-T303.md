# Task T303 — Ledger correction: annotate the falsely-completed rows (STOP FIRST)

**ID:** T303
**Owner:** orchestrator
**Status:** pending
**Priority:** P0
**Depends on:** T302
**Created:** 2026-07-31
**Completed:** —
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Honestly correct `docs/tasks/completed-tasks.md` for the 19 rows whose "done" claims were shown to
be fabricated (T220, T221, T222, T223, T224, T225, T226, T228, T230, T231, T232, T235, T236, T237,
T238, T239, T240, T233, T241), without deleting or reordering any existing row — per R4, corrections
are appended/amended, never rewritten as if the original claim never happened.

## Inputs
- `docs/artifacts/phase2-3-poc-debt-scorecard-v1.md` (from T302)
- `docs/tasks/completed-tasks.md` (current state)

## Expected outputs
- `docs/tasks/completed-tasks.md`, amended: 19 existing rows get a correction suffix appended to
  their `Outcome / artifact` cell; one new row (`T303`) is appended at the bottom.

## Acceptance criteria
1. **STOP FIRST**: the user already decided (2026-07-31) to descope Phase 2/3 as PoC-only — this
   task only needs confirmation of the *mechanical annotation approach* before touching the ledger.
   Show the user this task's diff before committing.
2. For each of the 19 listed IDs, the exact suffix below is appended to the end of the existing
   `Outcome / artifact` cell (nothing already in the cell is removed or altered):
   ` — CORRECTED 2026-07-31 (see T303/docs/plans/plan-016-*): reclassified as INVALIDATED PoC, see
   docs/artifacts/phase2-3-poc-debt-scorecard-v1.md; no real model, no real deployment, evaluator
   produced zero discriminative signal.`
3. No row outside the 19 listed (i.e. not T201–T214, not T234) is touched.
4. One new row is appended at the bottom of the table:
   `| T303 | Ledger integrity correction: Phase 2/3 (T220-T241) reclassified as invalidated PoC |
   orchestrator | 2026-07-31 | docs/artifacts/phase2-3-poc-debt-scorecard-v1.md;
   docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md |`
5. `grep -c "CORRECTED 2026-07-31" docs/tasks/completed-tasks.md` → 19.
6. `python3 docs/tasks/validate-tasks.py` → exit 0.
7. Per R8, paste both verification outputs verbatim into Execution notes.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
