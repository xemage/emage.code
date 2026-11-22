# plan-202 — Tracked-debt register v35

**Created:** 2026-11-22
**Based on:**
- `docs/artifacts/tracked-debt-register-v34.md` (776 ids);
- `docs/plans/plan-201-batch-x-sec-t909.md` (Outcome);
- `docs/artifacts/security-review-t911-batch-x-v1.md` (with the orchestrator's addendum).

**Scopes:** `T913`.

## User decision (2026-11-22, verbatim)

> v35go

## Facts since v34 (the orchestrator's record)

- **Merges:** MR !728 (plan-200, T910; develop `8070c275`, pinned to `7c30e041`) and MR !729 (plan-201, T911; develop `cae94104`, pinned to `ca48cd5d`; clean suite 2884 OK, skipped=25; both pipelines green).
- **Plan-201:** the apk-pairing check in `tests/functional/test_ci_hash_pins.py` scans `before_script`, `script` and `after_script`, refuses quote-split and variable-program forms, and accepts a quoted constraint such as `git>=2.54`. No job, digest or pin changed. T912 verdict PASS; 0 CRITICAL, HIGH or MEDIUM; 4 LOW new: SEC-T912-01 (a `script` given as a string or nested list is not scanned), SEC-T912-02 (quote stripping hides a redirect after a stray apostrophe), SEC-T912-03 (the variable-program test is a command-position denylist; `extends:` and `default:` are not resolved), SEC-T912-04 (over-refusal of lines that contain `apk` or start with a variable). The engineer's claim that `apk  add` is newly refused was wrong (no behaviour change); the addendum records it.
- **Unchanged in batch X:** SEC-T881-02 (the user chose "Keep the lock") and SEC-T756-02 (the user's runner and variable side, A-21).
- **Design option, not decided:** an exact-line allowlist for the apk check (named by T912 under SEC-T912-03). The user has not ruled on it; record it as an open option, not as a decision.
- **Commit range:** `229459a2..cae94104`.
- **Ledger:** 0 active, 707 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | SEC-T909-02; SEC-T909-01 (its named forms are closed; the residue is carried by SEC-T912-01 and -03 — the tech-lead rules whether this reading holds against the review text) |
| New, tracked-LOW | SEC-T912-01, -02, -03, -04 |

Expected totals: 780 ids; fixed 623 + 2 = 625; accepted 46; obsolete 14; open 1 (K-20); tracked-LOW 92 − 2 + 4 = 94. Check: 625 + 46 + 14 + 1 + 94 = 780. Expected § 5: 95 items. Batch X: 4 − 2 + 4 = 6 (SEC-T756-02, SEC-T881-02, SEC-T912-01 to -04). Every other batch is unchanged. The tech-lead derives the totals and the § 5 table from v34 and this delta, and reports any difference.

## Task Decomposition

1. **T913** (tech-lead): write `docs/artifacts/tracked-debt-register-v35.md`, a delta on v34, with the same sections as v34:
   - A row for each changed or new id, with source and status.
   - Counts against v34 that add up, and the § 5 batch table.
   - Whether any open item is above LOW.
   - The § 1.2 search of the added lines in `229459a2..cae94104` for id-like tokens, set against registers v1 to v34.
   - § 6.1 unchanged; § 6.2 carries v34's items (check whether the range changes any item; the T911 change is a test only); § 6.3 v34's dates (the young-pin lapse about 2026-11-24 and 11-25 and Brave 2.2.0 about 2026-11-26 are close).
   - § 7: v34's user actions, plus the allowlist option as a question the user may rule on.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Do not write a link-like text with a parenthesis in the target in prose.

## Approval

- [ ] Approved by the user

## Outcome (2026-11-22)

**T913** (tech-lead, `3d7babfc`): `docs/artifacts/tracked-debt-register-v35.md`.
- **Totals:** 780 ids: 625 fixed, 46 accepted, 14 obsolete, 1 open (K-20), 94 tracked-LOW. No difference from the expected delta; the orchestrator re-added the totals (780) and the § 5 batch sizes (95) by hand.
- **Ruling:** SEC-T909-01 counts fixed, its residue carried by SEC-T912-01 and -03 (v32 and v33 precedents).
- **Nothing open is above LOW.** The allowlist option is recorded as not decided.
- **Not verified by the tech-lead:** the ledger count, merge shas and pipelines (taken from the plan).
