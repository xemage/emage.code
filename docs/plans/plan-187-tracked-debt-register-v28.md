# plan-187 — Tracked-debt register v28

**Created:** 2026-11-20
**Based on:**
- `docs/artifacts/tracked-debt-register-v27.md` (754 ids);
- `docs/plans/plan-186-batch-v-third-round.md` (Outcome);
- `docs/artifacts/security-review-t888-batch-v-v1.md` (with its orchestrator addendum).

**Scopes:** `T889`.

## User decision (2026-11-20, verbatim)

> v28 go

## Facts since v27 (the orchestrator's record)

- **Merges:**
  - MR !713 (plan-185, register v27; develop `94e430b2`).
  - MR !714 (plan-186, batch V third round; develop `94f6c09a`, pinned to `42d9f573`; pipelines 3093927440 and 3093927350; clean suite 2866 OK at `88bf0fcc`).
- **Flake on the final suite run:** at `42d9f573` four subtests of `test_an_at_sign_in_a_query_or_fragment_never_reaches_the_refusal` (`tests/functional/test_memory_indexing_pipeline.py:589`) failed: the test asserts that `bob` is not in the stderr, and the random temporary directory name `tmpmbobp4tw` contained it. Three re-runs of the module passed. Neither the test file nor the code it checks is in MR !714. Same kind as TD-T849-01.
- **T888 verdict:** PASS, with 0 CRITICAL, HIGH or MEDIUM findings.
- **Commit range:** `94e430b2..94f6c09a`.
- **Ledger:** 0 active, 685 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | SEC-T885-01, SEC-T885-02, SEC-T885-03, SEC-T751-08 |
| New, tracked-LOW | SEC-T888-01, -02, -03, -04 (all in `scripts/verify-release-docs.py`; -02 confirmed by the orchestrator's run); TD-T888-01 (the flake above; the orchestrator's id, no reviewer's grade) |

Expected totals: 759 ids; fixed 592 + 4 = 596; accepted 46; obsolete 12; open 1 (K-20); tracked-LOW 103 − 4 + 5 = 104. Check: 596 + 46 + 12 + 1 + 104 = 759. Expected § 5: 105 items (104 + K-20). Batch V: the four old ids leave and SEC-T888-01 to -04 enter (4 again); TD-T888-01 goes to a batch the tech-lead names, with the reason (it is a flaky test, like TD-T849-01 and the earlier test-flake items; see where those were placed). The tech-lead derives the totals and the § 5 batch table from v27 and this delta, and reports any difference.

## Task Decomposition

1. **T889** (tech-lead): write `docs/artifacts/tracked-debt-register-v28.md`, a delta on v27. It must contain:
   - **A row for each changed or new id**, with its source and status. SEC-T751-08 is closed: say what closed it (T887's widened narrow rule plus the table-rule parse, T888's correction of T885's bypass shape).
   - **Counts against v27 that add up**, and the § 5 batch table.
   - **Whether any open item is above LOW.**
   - **The § 1.2 search** of the added lines in the range `94e430b2..94f6c09a`.
   - **§ 6:**
     - § 6.1: unchanged from v27.
     - § 6.2: the next-release checklist. Carry v27's items; item 52 gains T888's six points for the `release` job's `-I` line (T888 artifact, last section).
     - § 6.3: v27's dates.
   - **§ 7, user actions:** v27's.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-20.**

**T889** (tech-lead, `384431e7`): `docs/artifacts/tracked-debt-register-v28.md`.
- **Totals:** 759 ids: 596 fixed, 46 accepted, 12 obsolete, 1 open (K-20), 104 tracked-LOW. These match the expected delta in every id, status and total.
- **§ 5:** 105 items in all. Batch V keeps 4 items, but its members change: SEC-T885-01, -02, -03 and SEC-T751-08 leave as fixed, and SEC-T888-01 to -04 enter. Batch I grows by one: TD-T888-01 (the flaky test), as the tech-lead suggests, following TD-T849-01's placement in v22. The tech-lead names K as the alternative.
- **Nothing open is above LOW.**
- **§ 6.2:** item 52 gains points 8 to 13, T888's six `release` job points. SEC-T885-03 reopens if points 8 to 12 fail.
- **§ 1.2:** the 497 added lines in `94e430b2..94f6c09a` hold no id beyond SEC-T888-01 to -04.

**The orchestrator's own verification:**
- The register parser cannot read bold rows, so the I and V rows were read by hand.
- The § 5 sum (25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 4 + 6 + 11 + 2 + 6 + 3 = 105) and the status sum (596 + 46 + 12 + 1 + 104 = 759) were checked.
- The full suite and the pipeline are recorded in the merge request.

**Budget:** T889 used about 89k, against a budget of 50k.
