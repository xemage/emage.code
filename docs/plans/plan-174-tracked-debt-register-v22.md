# plan-174 — Tracked-debt register v22

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v21.md` (726 ids);
- `docs/plans/plan-172-batch-p-brave-upstream-report.md` (§ Outcome);
- `docs/plans/plan-173-brave-2-1-5-pin-bump.md` (§ Outcome);
- `docs/artifacts/security-review-t850-brave-report-v1.md`;
- `docs/artifacts/security-review-t852-brave-2-1-5-v1.md`.

**Scopes:** `T854`.

## User decision (2026-11-19, verbatim)

> v22 go

## Facts since v21 (the orchestrator's record)

- **Merges:**
  - MR !696 (plan-171, register v21; develop `2be43862`).
  - MR !697 (plan-172, batch P; develop `4cf82a0b`).
  - MR !698 (plan-173, Brave 2.1.5; develop `0657ec2d`).
- **Verification:**
  - At `900deb79` (!697): the full suite passed, 2775 OK. The MR pipeline failed once on TD-T849-01 and passed on a retry of the same sha.
  - At `1e01a5d5` (!698): the full suite passed, 2778 OK (skipped=25), and all three pipelines succeeded.
- **The user filed SEC-T702-08 upstream on 2026-11-19:** https://github.com/brave/brave-search-mcp-server/issues/377. The issue is open, and its text is draft v2 § 4.
- **Root refresh T853:** approved by the user ("Refresh now (Recommended)"). Drift is `[]`.
- **Commit range:** `2be43862..0657ec2d`.
- **Ledger:** 0 active, 650 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| accepted → fixed | SEC-T702-09 (MEDIUM; its v11.0.0 acceptance ended with Brave 2.1.5, T852) |
| New ids, minted and fixed | SEC-T850-01, SEC-T850-02 (fixed by draft v2) |
| New id, tracked-LOW | TD-T849-01 (orchestrator id; `test_merge_task_docs` pid-in-random-name flake; plan-173 § Outcome) |
| Stays tracked-LOW, with a note | SEC-T702-08 (batch P): reported upstream as issue #377; it closes when a release with the fix is pinned |

**Expected totals:**
- 729 ids: 551 fixed, 46 accepted, 10 obsolete, 1 open (K-20), 121 tracked-LOW.
- The batch total is 122.

## Task Decomposition

1. **T854** (tech-lead): write `docs/artifacts/tracked-debt-register-v22.md`, a delta on v21. It must contain:
   - **A row for each changed or new id**, with its source.
   - **Status counts carried over from v21** that add up.
   - **The § 5 batch table:**
     - Propose a batch for TD-T849-01.
     - Update batch P's trigger: the issue is filed.
   - **Whether any open item is above LOW.**
   - **The § 1.2 search** of the added lines in the range.
   - **§ 6:**
     - The accepted MEDIUMs for v11.0.0 are now only SEC-T660-01 and SEC-T665-01.
     - Item 43 loses its SEC-T702-09 part.
     - § 6.3 loses the 2027-01-30 date.
     - Item 49 is unchanged.
   - **The checklist facts that changed:**
     - Brave 2.1.5 has npm provenance.
     - The release gate has no `--accept`.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-19.** T854 (tech-lead) wrote `docs/artifacts/tracked-debt-register-v22.md` in commit `baa7785e`. It holds **729 ids**:

| Status | Ids |
|---|---:|
| fixed | 551 |
| accepted | 46 |
| obsolete | 10 |
| open (K-20) | 1 |
| tracked-LOW | 121 |

The batches total 122. Nothing open is above LOW.

**Changes from v21:**
- **SEC-T702-09:** accepted → fixed. Its acceptance ended with Brave 2.1.5.
- **SEC-T850-01 and -02:** minted and fixed.
- **TD-T849-01:** new, tracked-LOW in batch I. Its trigger is the next edit of `test_merge_task_docs.py`, or its next CI failure.
- **Batch P:** SEC-T702-08 is reported upstream as issue #377. The id closes when a Brave release with the fix is pinned.
- **§ 6:**
  - The only MEDIUMs still accepted for v11.0.0 are SEC-T660-01 and SEC-T665-01, with their review on 2027-01-28.
  - Item 43 is narrowed to those two.
  - 2027-01-30 is removed.

**The orchestrator's own verification:**
- **The parser** compared the § 5 tables of v21 and v22: TD-T849-01 is added, and the stated total is 122.
- **The status tables add up:** 551 + 46 + 10 + 1 + 121 = 729.
- **2027-01-30** appears only as removed.
- **The gates** exit 0.
- **The full suite and the pipeline** are recorded in the merge request.

**Budget:** T854 used about 38k tokens against 40k (the agent's estimate).
