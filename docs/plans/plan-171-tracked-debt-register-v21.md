# plan-171 — Tracked-debt register v21

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v20.md` (725 ids);
- `docs/plans/plan-170-sec-t837-01-opencode-live-check.md` (§ Outcome);
- `docs/artifacts/mcp-agent-denials-evidence-v2.md`;
- `docs/artifacts/security-review-t847-opencode-live-v1.md`.

**Scopes:** `T848`.

## User decision (2026-11-19, verbatim)

> v21 go

## Facts since v20 (the orchestrator's record)

- **Merges:**
  - MR !694 (plan-169, register v20; develop `c764005a`).
  - MR !695 (plan-170), pinned to `84d43610`; develop `a6732334`.
- **Verification at `84d43610`:** the full suite passed in a clean worktree (2775 OK, skipped=25). Pipelines 3087443885 and 3087443847 succeeded.
- **Commit range:** `c764005a..a6732334`.
- **Ledger:** 0 active, 644 completed. No root drift.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| Leaves tracked-LOW as fixed | SEC-T837-01 (batch U) |
| New id, tracked-LOW | SEC-T847-01 |

**Expected totals:**
- 726 ids: 548 fixed, 47 accepted, 10 obsolete, 1 open (K-20), 120 tracked-LOW.
- The batch total is 121.

## Task Decomposition

1. **T848** (tech-lead): `docs/artifacts/tracked-debt-register-v21.md`, a delta on v20. It must contain:
   - A row for each changed or new id, with its source.
   - Status counts carried over from v20 that add up.
   - The § 5 batch table, including the batch the tech-lead proposes for SEC-T847-01.
   - Whether any open item is above LOW.
   - The § 1.2 search of the added lines in the range.
   - **The narrowed live-run notes** (T847), for SEC-T663-02, SEC-T837-03, SEC-T840-01 and SEC-T842-01:
     - The resolved rule list is observed on 1.19.2 (evidence v2).
     - A refused call is not observed (K-20).
     - Still unverified:
       - the mapping of `bash`, `edit`, `webfetch`, `websearch` and `task` onto tools at call time;
       - the 23 agents that were not run.

     No status changes.
   - **SEC-T663-03:** T847's note, with no change of status.
   - **SEC-T847-01:** register v21 records that evidence v2 § 4 supersedes v1 on Opencode's default (rule 0 is `*: allow`). This is the remediation's register part. The wiki pointer stays open with the id.
   - **§ 6.2 item 49:** update its "not observed in a live run" wording to match the narrowed notes.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-19.** T848 (tech-lead) wrote `docs/artifacts/tracked-debt-register-v21.md` in commit `3578cfe7`. It holds **726 ids**:

| Status | Ids |
|---|---:|
| fixed | 548 |
| accepted | 47 |
| obsolete | 10 |
| open (K-20) | 1 |
| tracked-LOW | 120 |

The batches total 121. Nothing open is above LOW.

**Changes from v20:**
- **Fixed:** SEC-T837-01. Batch U goes from 7 to 6.
- **New, tracked-LOW:** SEC-T847-01, in batch Y (the tech-lead's proposal). Batch Y goes from 10 to 11. The wiki pointer is still to do.
- **Batch J** is no longer listed, because it ended in v20.
- **Records only, with no status change:**
  - the narrowed live-run notes for SEC-T663-02, SEC-T837-03, SEC-T840-01 and SEC-T842-01 (§ 2.4);
  - T847's note on SEC-T663-03;
  - the wording of § 6.2 item 49.
- **§ 4.3** records a slip in T847's per-finding table: it gives SEC-T837-03's prior status as "open". v20 records it as fixed.

**The orchestrator's own verification:**
- **The parser** compared the § 5 tables of v20 and v21:
  - SEC-T837-01 leaves.
  - SEC-T847-01 enters.
  - The stated total is 121.
  - SEC-T663-02 shows as removed only because v20's ended batch J row is dropped.
- **The status tables add up:** 548 + 47 + 10 + 1 + 120 = 726.
- **The gates exit 0.**
- **The full suite and the pipeline** are recorded in the merge request.

**Budget:** T848 used about 38k tokens against 40k (the agent's estimate).
