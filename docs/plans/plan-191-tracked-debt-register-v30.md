# plan-191 — Tracked-debt register v30

**Created:** 2026-11-21
**Based on:**
- `docs/artifacts/tracked-debt-register-v29.md` (761 ids);
- `docs/plans/plan-190-batch-v-short-round.md` (Outcome);
- `docs/artifacts/security-review-t894-batch-v-v1.md` (with its addendum of the orchestrator's runs).

**Scopes:** `T895`.

## User decision (2026-11-21, verbatim)

> v30 go

## Facts since v29 (the orchestrator's record)

- **Merges:**
  - MR !717 (plan-189, register v29; develop `5fbb71de`).
  - MR !718 (plan-190, batch V short round; develop `a0c375e6`, pinned to `ac5967f4`; pipelines 3095706890 and 3095706810; clean suite 2874 OK, skipped=25).
- **T894 verdict:** CONDITIONAL_PASS at the first head `3c97074a`; 0 CRITICAL, HIGH or MEDIUM. SEC-T894-01 was a regression from the case-fold reorder (a mathematical or letterlike capital kept its capital, so a heading spelled with it was no longer caught). The orchestrator confirmed it by running it. T893 fixed it, with SEC-T894-02 and -03, in `e570a268` in the same MR. The condition named the orchestrator's run as the confirmation, so no second security review was held. The addendum of the artifact records a sweep of every code point against both names: 11,884 shapes the old gate caught that the new one does not (all characters whose accent-stripped base is a different ASCII letter; no look-alike, unverified visually) and 497 gained.
- **SEC-T888-02 is split:** part (a) (the `İ` expansion) is fixed; part (b) (non-letter look-alikes such as `∨`) is open and untouched. SEC-T888-01, -02(b) and -03 stay open. SEC-T888-04 is fixed.
- **SEC-T881-02 choice:** the user has still not answered (keep the lock with header lines 3-6, T891's recommendation, or regenerate with the 14-day review). The register records it as an open user action, not as a decision.
- **Commit range:** `5fbb71de..a0c375e6`.
- **Ledger:** 0 active, 691 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | SEC-T888-04 |
| Stays tracked-LOW, partly fixed | SEC-T888-02 (part (a) fixed in `4d71af64` and `e570a268`; part (b) open) |
| Stay tracked-LOW | SEC-T888-01, SEC-T888-03 |
| New, minted and fixed in the same MR | SEC-T894-01, SEC-T894-02, SEC-T894-03 |

Expected totals: 764 ids; fixed 600 + 1 + 3 = 604; accepted 46; obsolete 12; open 1 (K-20); tracked-LOW 102 − 1 = 101. Check: 604 + 46 + 12 + 1 + 101 = 764. Expected § 5: 102 items (101 + K-20). Batch V: SEC-T888-04 leaves; SEC-T888-01, SEC-T888-02 (part (b) only) and SEC-T888-03 stay, so V = 3. Every other batch is unchanged. The tech-lead derives the totals and the § 5 table from v29 and this delta, and reports any difference. Where the tech-lead finds that a SEC-T894 id is a restatement of an existing id, the v26 precedent (counted once) applies; say so.

## Task Decomposition

1. **T895** (tech-lead): write `docs/artifacts/tracked-debt-register-v30.md`, a delta on v29. It must contain:
   - **A row for each changed or new id**, with its source and status. SEC-T888-02 gets a row saying part (a) is fixed and part (b) is open. SEC-T894-01 gets a row saying it was a regression from T893's first commit, found by the review, confirmed by the orchestrator's run, and fixed before merge.
   - **Counts against v29 that add up**, and the § 5 batch table.
   - **Whether any open item is above LOW.**
   - **The § 1.2 search** of the added lines in the range `5fbb71de..a0c375e6`.
   - **§ 6:**
     - § 6.1: unchanged from v29.
     - § 6.2: the next-release checklist. Carry v29's items. Add to item 52 (or as a new item, your call) that the release-document gate now folds case, NFKD, marks and NFKC (SEC-T888-02(a), SEC-T894-01), so the tag's own release document must pass `scripts/verify-release-docs.py --tag` before the tag is cut, as already required.
     - § 6.3: v29's dates.
   - **§ 7, user actions:** v29's, including the open choice on SEC-T881-02.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-21.**

**T895** (tech-lead, `ac0da0c5`): `docs/artifacts/tracked-debt-register-v30.md`.
- **Totals:** 764 ids: 604 fixed, 46 accepted, 12 obsolete, 1 open (K-20), 101 tracked-LOW. These match the expected delta in every id, status and total, with no difference.
- **§ 5:** 102 items in all. Batch V goes from 4 to 3 (SEC-T888-04 leaves; SEC-T888-01, SEC-T888-02 part (b) only, and SEC-T888-03 stay). Every other batch is unchanged.
- **Counting:** SEC-T888-02 stays one id, tracked-LOW, with part (a) fixed. SEC-T894-01, -02 and -03 are three new ids counted as fixed and placed in no batch, following the v15 and v24 precedent for ids minted and fixed before merge. None restates an existing id.
- **Nothing open is above LOW.**
- **§ 6.2:** item 52 gains point 14: the release-document gate now folds case, NFKD, marks and NFKC (and case again), so the tag's own release document must pass `scripts/verify-release-docs.py --tag` before the tag is cut.
- **§ 7:** v29's user actions, with the SEC-T881-02 choice still open and not recorded as a decision.
- **Disclosures kept:** the sweep numbers are the orchestrator's own run, with the "different ASCII letter is no look-alike" reading unverified, and `e570a268` had no second security review.
- **§ 1.2:** the 366 added lines in `5fbb71de..a0c375e6` hold 18 id-like tokens; only SEC-T894-01, -02 and -03 are in no earlier register.

**The orchestrator's own verification:**
- The register parser cannot read bold rows, so the V row was read by hand.
- The § 5 sum (25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 4 + 11 + 2 + 6 + 3 = 102) and the status sum (604 + 46 + 12 + 1 + 101 = 764) were checked.
- The full suite and the pipeline are recorded in the merge request.

**Budget:** T895 used about 87k, against a budget of 50k.
