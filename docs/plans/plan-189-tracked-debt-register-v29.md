# plan-189 — Tracked-debt register v29

**Created:** 2026-11-20
**Based on:**
- `docs/artifacts/tracked-debt-register-v28.md` (759 ids);
- `docs/plans/plan-188-batch-x-round.md` (Outcome);
- `docs/artifacts/security-review-t891-batch-x-v1.md` (with its orchestrator addendum).

**Scopes:** `T892`.

## User decision (2026-11-20, verbatim)

> v29 go

## Facts since v28 (the orchestrator's record)

- **Merges:**
  - MR !715 (plan-187, register v28; develop `d524f90e`).
  - MR !716 (plan-188, batch X; develop `54d240ed`, pinned to `0a6f5fc6`; pipelines 3095116496 and 3095116436; clean suite 2872 OK, skipped=25).
- **T891 verdict:** PASS, with 0 CRITICAL, HIGH or MEDIUM findings.
- **SEC-T881-02 is not fixed.** A fresh single-cut-off compile of `ci/requirements-ci.txt` differs from the committed lock in 6 pins (certifi, pycparser, pydantic, pydantic-core, sse-starlette, starlette). T890 reported 7; its own pin lists and T891 show 6. T891 recommends keeping the lock, with header lines 3-6 as the record, and doing the one-cut-off regeneration at the next full regeneration with the 14-day review. **The user has not answered this choice**; the register records the recommendation as the standing position, not as a user decision.
- **Commit range:** `d524f90e..54d240ed`.
- **Ledger:** 0 active, 688 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed (batch X) | SEC-T885-04, SEC-T867-01, SEC-T867-02, TL-T761-11 |
| Follows its v26 status | TL-T876-04 (v26 recorded it as joining SEC-T867-01 and -02; say how it is counted now) |
| Stays tracked-LOW | SEC-T881-02 (not fixed, by design), SEC-T756-02 (left alone) |
| New | SEC-T891-01 (pairing check covers only the image and `openssl`), SEC-T891-02 (a future publication time counts as young, not an error), SEC-T891-03 (restates SEC-T881-02 with the count of 6; follow the v26 precedent for a restated or duplicate id and say which status you give it) |

Expected totals if SEC-T891-03 counts as a new tracked-LOW id: 762 ids; fixed 596 + 4 = 600; accepted 46; obsolete 12; open 1 (K-20); tracked-LOW 104 − 4 + 3 = 103. Check: 600 + 46 + 12 + 1 + 103 = 762. Expected § 5: 104 items. Batch X: the four fixed ids leave, SEC-T756-02 and SEC-T881-02 stay, and SEC-T891-01 to -03 enter (all on the CI-pin and lock surface, devops-engineer), so X = 5. The tech-lead derives the totals and the § 5 table from v28 and this delta, and reports any difference, including how SEC-T891-03 and TL-T876-04 are counted.

## Task Decomposition

1. **T892** (tech-lead): write `docs/artifacts/tracked-debt-register-v29.md`, a delta on v28. It must contain:
   - **A row for each changed or new id**, with its source and status.
   - **Counts against v28 that add up**, and the § 5 batch table.
   - **Whether any open item is above LOW.**
   - **The § 1.2 search** of the added lines in the range `d524f90e..54d240ed`.
   - **§ 6:**
     - § 6.1: unchanged from v28.
     - § 6.2: the next-release checklist. Carry v28's items. Item 17 (the next full regeneration of `ci/requirements-ci.txt`) now also says: the one-cut-off regeneration moves the six pins named above, needs the checklist's 14-day review and an advisory audit, and the header fix (SEC-T881-02) waits for it; regenerate sooner only if an advisory names one of the six committed pins.
     - § 6.3: v28's dates.
   - **§ 7, user actions:** v28's, plus the open choice on SEC-T881-02 (keep the lock and header lines 3-6, T891's recommendation, or regenerate with the 14-day review).

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-20.**

**T892** (tech-lead, `e31cdae7`): `docs/artifacts/tracked-debt-register-v29.md`.
- **Totals:** 761 ids: 600 fixed, 46 accepted, 12 obsolete, 1 open (K-20), 102 tracked-LOW.
- **§ 5:** 103 items in all. Batch X goes from 6 to 4: SEC-T885-04, SEC-T867-01 (with TL-T876-04), SEC-T867-02 and TL-T761-11 leave as fixed; SEC-T756-02 and SEC-T881-02 stay; SEC-T891-01 and -02 enter. Every other batch is unchanged.
- **One difference from the orchestrator's expected delta, and the orchestrator's ruling.**
  - The expected delta counted SEC-T891-03 as a new id (762 ids, 103 tracked-LOW, § 5 of 104, X of 5).
  - The tech-lead counts it with SEC-T881-02, because T891 itself says it restates SEC-T881-02 "with the count". The precedents are v26 (TL-T876-04 is SEC-T867-01) and v17 (QA-T818-01 is TD-T774-01).
  - **Ruling: the tech-lead's counting stands.** SEC-T891-03 is not an id. The totals above are the record, and the figures in this plan's "expected totals" paragraph are superseded.
- **Nothing open is above LOW.**
- **§ 6.2:** item 17 is amended as planned: six pins move, the 14-day review and an advisory audit are needed, the header fix waits for the regeneration, and it comes sooner only if an advisory names one of the six committed pins.
- **§ 7:** the SEC-T881-02 choice is recorded as open for the user. The register does not say the user decided.
- **§ 1.2:** the 420 added lines in `d524f90e..54d240ed` hold 11 distinct id tokens; only SEC-T891-01, -02 and -03 are in no earlier register.

**The orchestrator's own verification:**
- The register parser cannot read bold rows, so the X row was read by hand.
- The § 5 sum (25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 4 + 4 + 11 + 2 + 6 + 3 = 103) and the status sum (600 + 46 + 12 + 1 + 102 = 761) were checked.
- The duplicate precedent was found in v26 § 1.2.
- The full suite and the pipeline are recorded in the merge request.

**Budget:** T892 used about 84k, against a budget of 50k.
