# plan-179 — Tracked-debt register v24

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v23.md` (732 ids);
- `docs/plans/plan-177-batch-x-ci-images-ca-runner.md` (§ Outcome);
- `docs/plans/plan-178-batch-ab-opencode-third-round.md` (§ Outcome);
- `docs/artifacts/security-review-t860-batch-x-v1.md`;
- `docs/artifacts/security-review-t862-batch-ab-v1.md`.

**Scopes:** `T865`.

## User decision (2026-11-19, verbatim)

> v24go

## Facts since v23 (the orchestrator's record)

- **Merges:**
  - MR !701 (plan-176, register v23; develop `aedc43f0`).
  - MR !702 (plan-178, batch AB), pinned to `c6f65f43`; develop `59f809a6`.
  - MR !703 (plan-177, batch X), pinned to `9f1b46cd`; develop `a66444c4`.
- **Verification:**
  - At `c6f65f43`: the full suite passed, 2799 OK (skipped=25), and pipelines 3089211327 and 3089211173 succeeded.
  - At `9f1b46cd`: the full suite passed, 2815 OK (skipped=25), and pipelines 3089309359 and 3089309252 succeeded, including both CA-chain jobs.
- **Root refreshes:** T863 and T864, both approved by the user. The drift is `[]` on a clean checkout.
- **Commit range:** `aedc43f0..a66444c4`.
- **Ledger:** 0 active, 661 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | SEC-T756-07, SEC-T756-08, SEC-T768-01, SEC-T768-02, SEC-T768-03, SEC-T768-05 (batch X); SEC-T856-01, SEC-T856-03 (batch AB) |
| New, minted and fixed | SEC-T860-03 (fixed by the orchestrator, `17f16d36`); SEC-T862-01 (fixed by the orchestrator, `f9f3a86b`) |
| New, tracked-LOW | SEC-T860-01, SEC-T860-02, SEC-T862-02 |
| Stay tracked-LOW, with a changed note | SEC-T856-02 (narrowed: only a parent-directory `grep` remains); SEC-T756-02, SEC-T768-04, TL-T761-11, SEC-T811-05 (batch X; SEC-T811-05 is now a written user action) |

**Expected totals:**
- 737 ids: 565 fixed, 46 accepted, 10 obsolete, 1 open (K-20), 115 tracked-LOW.
- The batch total is 116.

## Task Decomposition

1. **T865** (tech-lead): `docs/artifacts/tracked-debt-register-v24.md`, a delta on v23. It must contain:
   - **A row for each changed or new id**, with its source.
   - **Counts against v23** that add up.
   - **The § 5 batch table:** shrink X and AB, and propose batches for the three new LOW ids.
   - **Whether any open item is above LOW.**
   - **The § 1.2 search** of the added lines in the range.
   - **§ 6:**
     - The CI image review now fails from **2027-03-20** (`ci_images_reviewed_on: 2026-11-19` + 120 days).
     - Item 49 (d) restated from T862 § 4.
     - 2027-01-28 and 2027-01-29 unchanged.
   - **§ 7, user actions:**
     - SEC-T811-05 with SEC-T860-02: the runner hardening steps in checklist § 3.
     - `/tmp/evidence-run`, optional removal.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-19.** T865 (tech-lead) wrote `docs/artifacts/tracked-debt-register-v24.md` in commit `b2d17208`. It holds **737 ids**:

| Status | Ids |
|---|---:|
| fixed | 565 |
| accepted | 46 |
| obsolete | 10 |
| open (K-20) | 1 |
| tracked-LOW | 115 |

The batches total 116. Nothing open is above LOW.

**Changes from v23:**
- **Fixed:** eight batch ids, SEC-T756-07, -08, SEC-T768-01, -02, -03, -05, SEC-T856-01 and -03.
- **Minted and fixed:** SEC-T860-03 and SEC-T862-01.
- **New, tracked-LOW:** SEC-T860-01 and -02 go to batch X, and SEC-T862-02 to batch AB, as the tech-lead proposed.
- **Batch sizes:** X goes from 10 to 6, and AB from 3 to 2.
- **§ 6.3:** the CI image review fails from 2027-03-20.
- **§ 7:** the runner steps for the user. The unknown-key check and the out-of-cycle patch trigger (SEC-T860-02) are not yet written into the checklist.

**The orchestrator's own verification:**
- **The parser** does not read the bold `**X**` and `**AB**` rows. I read both by hand:
  - X holds SEC-T756-02, SEC-T768-04, TL-T761-11, SEC-T811-05 and the new SEC-T860-01 and -02;
  - AB holds SEC-T856-02 and the new SEC-T862-02;
  - the stated sum is 116.
- **The status tables add up:** 565 + 46 + 10 + 1 + 115 = 737.
- **The gates** exit 0.
- **The full suite and the pipeline** are recorded in the merge request.

**A correction, recorded here:** the orchestrator's message to the user after the batch X merge named "check the runner log for an unknown-key warning" as a checklist step. It is in fact what SEC-T860-02 asks for, and it is not yet written in checklist § 3 (T865 § 7).

**Budget:** T865 used about 38k tokens against 40k (the agent's estimate).
