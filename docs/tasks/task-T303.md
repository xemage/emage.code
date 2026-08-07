# Task T303 — Ledger correction: annotate the falsely-completed rows (STOP FIRST)

**ID:** T303
**Owner:** orchestrator
**Status:** done
**Priority:** P0
**Depends on:** T302
**Created:** 2026-07-31
**Completed:** 2026-07-31
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
STOP FIRST: prepared on local branch `docs/t303-ledger-correction` (off updated `develop`,
post-T302 merge) but NOT committed to remote pending explicit user confirmation of the mechanical
diff, per plan-016 R9 and this task's acceptance criterion 1. The full `git diff` of the
uncommitted change was relayed to the user via the orchestrator's report for sign-off before any
push or MR.

Mechanical edit performed exactly as specified: appended the exact suffix
` — CORRECTED 2026-07-31 (see T303/docs/plans/plan-016-*): reclassified as INVALIDATED PoC, see
docs/artifacts/phase2-3-poc-debt-scorecard-v1.md; no real model, no real deployment, evaluator
produced zero discriminative signal.` to the end of the existing Outcome/artifact cell for all 19
rows (T220, T221, T222, T223, T224, T225, T226, T228, T230, T231, T232, T235, T236, T237, T238,
T239, T240, T233, T241) — nothing already in any cell was removed or altered. No row outside the
19 listed (not T201-T214, not T234) was touched. Appended the new T303 row at the bottom of the
table exactly as specified. Also removed T303's own row from `docs/tasks/active-tasks.md` and set
this file's header to `Status: done` / `Completed: 2026-07-31`, per AGENTS.md § "Complete a Task"
— required because acceptance criterion 6 (`validate-tasks.py` exit 0) cannot pass while T303
exists in both ledgers simultaneously.

Verification output (verbatim, captured 2026-07-31):

```
$ grep -c "CORRECTED 2026-07-31" docs/tasks/completed-tasks.md
19
```

```
$ python3 docs/tasks/validate-tasks.py; echo "exit=$?"
TASK LEDGER: PASS (5 active, 146 completed)
exit=0
```

Both match acceptance criteria 5 and 6 exactly.
