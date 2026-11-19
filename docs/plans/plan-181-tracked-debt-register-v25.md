# plan-181 — Tracked-debt register v25

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v24.md` (737 ids);
- `docs/plans/plan-180-batch-x-text-and-sec-t862-02.md` (§ Outcome);
- `docs/artifacts/security-review-t867-batch-x-text-v1.md`.

**Scopes:** `T868`.

## User decision (2026-11-19, verbatim)

> v25 go

## Facts since v24 (the orchestrator's record)

- **Merges:**
  - MR !704 (plan-179, register v24; develop `04401057`).
  - MR !705 (plan-180), pinned to `62dcbe62`; develop `b28ce5d1`.
- **Verification at `62dcbe62`:**
  - the full suite passed in a clean worktree: 2832 OK (skipped=25);
  - pipelines 3089984650 and 3089984508 succeeded.
- **Root drift:** none (`[]`).
- **Commit range:** `04401057..b28ce5d1`.
- **Ledger:** 0 active, 664 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | SEC-T860-01 and SEC-T860-02 (batch X); SEC-T862-02 (batch AB) |
| New, tracked-LOW | SEC-T867-01, SEC-T867-02, SEC-T867-03 |

**Expected totals:**
- 740 ids: 568 fixed, 46 accepted, 10 obsolete, 1 open (K-20), 115 tracked-LOW.
- The batch total is 116.

## Task Decomposition

1. **T868** (tech-lead): `docs/artifacts/tracked-debt-register-v25.md`, a delta on v24. It must contain:
   - a row for each changed or new id, with its source;
   - status counts against v24 that add up;
   - the § 5 batch table, with a proposed batch for SEC-T867-01 to -03;
   - whether any open item is above LOW;
   - the § 1.2 search of the added lines in the range;
   - § 6, with the dates unchanged (2027-01-28, 2027-01-29, 2027-03-20) and the brave 2.1.5 exception noted, which lapses on 2026-11-24;
   - § 7: the user's runner steps for SEC-T811-05, now complete in checklist § 3, and the optional removal of `/tmp/evidence-run`.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-19.** T868 (tech-lead) wrote `docs/artifacts/tracked-debt-register-v25.md` in commit `bc9430b3`. It holds **740 ids**:

| Status | Ids |
|---|---:|
| fixed | 568 |
| accepted | 46 |
| obsolete | 10 |
| open (K-20) | 1 |
| tracked-LOW | 115 |

The batches total 116. Nothing open is above LOW.

**Changes from v24:**
- **Fixed:** SEC-T860-01 and SEC-T860-02 (text), and SEC-T862-02.
- **New, tracked-LOW:** SEC-T867-01 and -02 go to batch X, and SEC-T867-03 to batch AB (the tech-lead's proposal). X and AB keep their sizes, 6 and 2.
- **§ 6.3:** both young-pin exceptions lapse by themselves: brave 2.1.5 about 2026-11-24, `server-filesystem` 2.4.0 about 2026-11-25. Either can pass up to almost a day early because of SEC-T867-02.
- **§ 7:** the runner steps for SEC-T811-05 are complete in checklist § 3. The removal of `/tmp/evidence-run` is optional.

**The orchestrator's own verification:**
- I read the bold X and AB rows of § 5 by hand. The stated total is 116.
- The status tables add up.
- The gates exit 0.
- The full suite and the pipeline are recorded in the merge request.

**Budget:** T868 used about 38k tokens against 40k (the agent's estimate).
