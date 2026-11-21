# plan-193 — Tracked-debt register v31

**Created:** 2026-11-21
**Based on:**
- `docs/artifacts/tracked-debt-register-v30.md` (764 ids);
- `docs/plans/plan-192-batch-x-small-round.md` (Outcome, Addendum 1);
- `docs/artifacts/security-review-t897-batch-x-v1.md`.

**Scopes:** `T898`.

## User decision (2026-11-21, verbatim)

> v31 go

## Facts since v30 (the orchestrator's record)

- **Merges:** MR !719 (plan-191, register v30; develop `c8f07beb`) and MR !720 (plan-192, batch X small round; develop `b04ec271`, pinned to `da98b53f`; pipelines 3096950812 and 3096950796; clean suite 2876 OK, skipped=25).
- **T897 verdict:** PASS. SEC-T891-01 and SEC-T891-02 are fixed. SEC-T897-01 is new, LOW (the pairing check ignores non-`apk add` forms such as `sh -c`, `apk --no-cache add`; no current exposure), with a wording gap (checklist § 1 does not say `--allow-young` cannot override the future-time refusal) tracked with it.
- **SEC-T881-02:** the user chose "Keep the lock (Recommended)" on 2026-11-21. It stays tracked-LOW, now with the decision on record (no longer an open user action). SEC-T756-02 is untouched.
- **Commit range:** `a0c375e6..b04ec271`.
- **Ledger:** 0 active, 694 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | SEC-T891-01, SEC-T891-02 |
| New, tracked-LOW (batch X) | SEC-T897-01 |
| Stay tracked-LOW | SEC-T881-02 (decision on record), SEC-T756-02 |

Expected totals: 765 ids; fixed 604 + 2 = 606; accepted 46; obsolete 12; open 1 (K-20); tracked-LOW 101 − 2 + 1 = 100. Check: 606 + 46 + 12 + 1 + 100 = 765. Expected § 5: 101 items (100 + K-20). Batch X: SEC-T891-01 and -02 leave, SEC-T897-01 joins. Every other batch is unchanged. The tech-lead derives the totals and the § 5 table from v30 and this delta, and reports any difference.

## Task Decomposition

1. **T898** (tech-lead): write `docs/artifacts/tracked-debt-register-v31.md`, a delta on v30. It must contain:
   - A row for each changed or new id, with source and status (SEC-T881-02 gets the user's decision).
   - Counts against v30 that add up, and the § 5 batch table.
   - Whether any open item is above LOW.
   - The § 1.2 search of the added lines in `a0c375e6..b04ec271`.
   - § 6.1 unchanged; § 6.2 carries v30's items (add the SEC-T897-01 wording gap if it belongs to the checklist); § 6.3 v30's dates.
   - § 7: v30's user actions, with the SEC-T881-02 choice recorded as decided.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-21.**

**T898** (tech-lead, `7178ea8d`): `docs/artifacts/tracked-debt-register-v31.md`.
- **Totals:** 765 ids: 606 fixed, 46 accepted, 12 obsolete, 1 open (K-20), 100 tracked-LOW. They match the expected delta in every id, status and total.
- **§ 5:** 101 items (25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 3 + 11 + 2 + 6 + 3). Batch X is SEC-T756-02, SEC-T881-02 and SEC-T897-01; every other batch is unchanged.
- **SEC-T881-02:** the user's "Keep the lock (Recommended)" is recorded as decided (not an ADR-011 acceptance); the "regenerate now" option is closed.
- **Nothing open is above LOW.**
- **§ 1.2:** 631 added lines in `a0c375e6..b04ec271`, 45 id-like tokens; only SEC-T897-01 is in no earlier register.

**The orchestrator's own verification:** the totals and the § 5 sum were checked by hand (the parser cannot read bold rows); `validate-tasks`, `test_link_integrity` and `test_team_health*` pass. The full suite and the pipeline are recorded in the merge request.

**Budget:** T898 used about 80k, against a budget of 50k.
