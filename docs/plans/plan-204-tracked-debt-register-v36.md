# plan-204 — Tracked-debt register v36

**Created:** 2026-11-28
**Based on:**
- `docs/artifacts/tracked-debt-register-v35.md` (780 ids);
- `docs/plans/plan-203-batch-x-apk-allowlist.md` (Outcome);
- `docs/artifacts/security-review-t914-batch-x-v1.md` (SEC-T915-01 to -04, with the orchestrator's addendum).

**Scopes:** `T916`.

## User decision (2026-11-28, verbatim)

> v36 go

## Facts since v35 (the orchestrator's record)

- **Merge:** MR !731 (plan-203, T914; develop `72cba2dd`, pinned to `82631d40`; pipeline with `unit-tests` 2873 OK, skipped=38; develop's own CI 2871, skipped=38; the difference is the two tests T914 added).
- **Plan-203 (T914):** the apk check in `tests/functional/test_ci_hash_pins.py` is an exact-line allowlist for `ca-chain-check-python` and the drift gate. No job, digest or pin changed.
- **T915 verdict:** PASS; 0 CRITICAL, HIGH or MEDIUM. SEC-T912-01, -02, -04 closed; SEC-T912-03 partly closed. New LOW: SEC-T915-01 (python CA job's lines not exactly pinned), -02 (its key set not pinned), -03 (apk line position not checked), -04 (one mutation tests a trailing space, not a verbatim move). SEC-T915-01 and -02 are one fix.
- **Unchanged in batch X:** SEC-T756-02 (the user's runner and variable side, A-21) and SEC-T881-02 (the user chose "Keep the lock").
- **Commit range:** `7f44fd35..72cba2dd`.
- **Ledger:** 0 active, 710 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | SEC-T912-01, SEC-T912-02, SEC-T912-04 |
| SEC-T912-03 → fixed by ruling | its residue is carried by SEC-T915-01 and -02 (the v35 rule for SEC-T909-01: the residue is counted once, as new ids) |
| New, tracked-LOW | SEC-T915-01, -02, -03, -04 |

Expected totals: 784 ids; fixed 625 + 4 = 629; accepted 46; obsolete 14; open 1 (K-20); tracked-LOW 94 − 4 + 4 = 94. Check: 629 + 46 + 14 + 1 + 94 = 784. Expected § 5: 95 items (94 + K-20). Batch X: still 6 items, with new members: SEC-T756-02, SEC-T881-02, SEC-T915-01 to -04. Every other batch is unchanged. The tech-lead derives the totals and the § 5 table from v35 and this delta, and reports any difference.

## Task Decomposition

1. **T916** (tech-lead): write `docs/artifacts/tracked-debt-register-v36.md`, a delta on v35, with the same sections as v35:
   - A row for each changed or new id, with source and status.
   - Counts against v35 that add up, and the § 5 batch table.
   - Whether any open item is above LOW.
   - The § 1.2 search of the added lines in `7f44fd35..72cba2dd` for id-like tokens, set against registers v1 to v35.
   - § 6.1 unchanged; § 6.2 carries v35's items (check whether the range changes any item; the T914 change is a test file only); § 6.3 v35's dates, with the Brave 2.2.0 date (about 2026-11-26) now passed, and say so plainly without deciding anything.
   - § 7: v35's user actions, plus the open question of the Brave 2.2.0 bump and SEC-T702-09 as the user's to rule on.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Do not write a link-like text with a parenthesis in the target in prose.

## Approval

- [ ] Approved by the user

## Outcome (2026-11-28)

**T916** (tech-lead, `d0a7fc65`): `docs/artifacts/tracked-debt-register-v36.md`. 784 ids: 629 fixed, 46 accepted, 14 obsolete, 1 open (K-20), 94 tracked-LOW. § 5: 95 items; batch X 6 (SEC-T756-02, SEC-T881-02, SEC-T915-01 to -04). Nothing open above LOW. The orchestrator re-added the totals and the § 5 sum by hand.
**Correction (orchestrator):** this plan's § 7 said SEC-T702-09 is an open question for the user. That was wrong. The v22 record has it fixed by the Brave pin bump to 2.1.5 (T851, T852), and `.mcp.json` pins 2.1.5. The v11.0.0 release document correctly records the acceptance of the 2.1.4 pin as shipped history. No count depends on it.
