# plan-166 — Tracked-debt register v19

**Created:** 2026-11-14
**Based on:** `docs/artifacts/tracked-debt-register-v18.md` (711 ids); `docs/plans/plan-165-batch-i-followups.md` (§ Outcome); `docs/artifacts/security-review-t832-batch-i-followups-v1.md`.
**Scopes:** `T833`.

## User decision (2026-11-14, verbatim)

> v19 go

## Facts since v18 (the orchestrator's record)

- **Merges:** MR !689 (register v18; develop `198d35b1`) and MR !690 (plan-165; develop `ec06c266`).
- **Verification at `0ec9a571`:** the full suite passed in a clean worktree (2759 OK, skipped=25), and pipelines 3068677008 and 3068676985 succeeded.
- **Commit range:** `198d35b1..ec06c266`.
- **Ledger:** 0 active, 629 completed.

## Task Decomposition

1. **T833** (tech-lead): `docs/artifacts/tracked-debt-register-v19.md`, a small delta on v18. It records these statuses:
   - SEC-T829-01 and SEC-T829-02: fixed by T831; T832 passed.
   - SEC-T832-01 and SEC-T832-02: new, LOW, tracked in batch I.
   - SEC-T832-03: minted and fixed by the orchestrator; not re-reviewed.

   It also gives the status counts from v18, which must add up, the batch table, and whether any open item is above LOW.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-14.** T833 (tech-lead) wrote `docs/artifacts/tracked-debt-register-v19.md` in commit `30d04012`. It holds **714 ids**:

| Status | Ids |
|---|---:|
| fixed | 538 |
| accepted | 47 |
| obsolete | 10 |
| open (K-20) | 1 |
| tracked-LOW | 118 |

The batches total 119. Nothing open is above LOW.

**Changes from v18:**
- **Fixed:** SEC-T829-01 and SEC-T829-02.
- **New, tracked-LOW in batch I:** SEC-T832-01 and SEC-T832-02.
- **Minted and fixed:** SEC-T832-03, by the orchestrator, not re-reviewed.

**The orchestrator's own verification:**
- The parser compared the § 5 tables of v18 and v19: SEC-T829-01 and -02 leave, SEC-T832-01 and -02 enter, and the total stays 119.
- The status counts add up.
- The gates exit 0.
- The full suite and the pipeline are recorded in the merge request.

**Budget:** T833 used about 30k tokens against 40k (the agent's estimate).
