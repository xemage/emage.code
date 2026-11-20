# plan-185 — Tracked-debt register v27

**Created:** 2026-11-20
**Based on:**
- `docs/artifacts/tracked-debt-register-v26.md` (750 ids);
- `docs/plans/plan-184-batch-v-release-gate.md` (Outcome);
- `docs/artifacts/security-review-t885-batch-v-v1.md` (with its orchestrator addendum).

**Scopes:** `T886`.

## User decision (2026-11-20, verbatim)

> v27 go

## Facts since v26 (the orchestrator's record)

- **Merges:**
  - MR !711 (plan-183, register v26; develop `23884e50`).
  - MR !712 (plan-184, batch V; develop `fb577765`, pinned to `0356d308`; clean suite 2859 OK, skipped=25; pipelines 3093169686 and 3093169620).
- **T885 verdict:** PASS, with 0 CRITICAL, HIGH or MEDIUM findings.
- **Commit range:** `23884e50..fb577765`.
- **Ledger:** 0 active, 682 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed (batch V) | SEC-T748-03, -04, -05, -06, -07, -08, -09, -12; SEC-T751-01, -05, -06, -07, -09; SEC-T773-01; SEC-T811-03; TL-T819-05 |
| tracked-LOW → fixed (batch X) | SEC-T768-04 |
| Stays tracked-LOW, partly fixed | SEC-T751-08: residual bypass `` \| `a\|` `<b>` \| ``; follow-up is the HTML check on a parse with the GFM table rule enabled |
| Not taken, not open | SEC-T751-09's optional part (exact template placeholders) |
| New, tracked-LOW | SEC-T885-01, -02, -03, -04 |

Expected totals: 754 ids; fixed 575 + 17 = 592; tracked-LOW 116 − 17 + 4 = 103; open 1 (K-20). Batch V: 17 → 1 (SEC-T751-08) before the new ids are placed; X: 6 → 5. The tech-lead derives the totals and the § 5 batch table from v26 and this delta, and reports any difference.

## Task Decomposition

1. **T886** (tech-lead): write `docs/artifacts/tracked-debt-register-v27.md`, a delta on v26. It must contain:
   - **A row for each changed or new id**, with its source and status.
   - **Counts against v26 that add up**, and the § 5 batch table:
     - V shrinks to its residual;
     - SEC-T768-04 leaves X;
     - place SEC-T885-01 to -04 in batches (V, X, N or a new letter, with the reason).
   - **Whether any open item is above LOW.**
   - **The § 1.2 search** of the added lines in the range.
   - **§ 6:**
     - § 6.1: unchanged from v26 (SEC-T660-01 and SEC-T665-01 accepted for v12.0.0 only).
     - § 6.2: the next-release checklist. Carry v26's items and add T885's list of seven things the first `v*` tag pipeline must show, including the user's check that no CI/CD variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists at project, group or instance level.
     - § 6.3: v26's dates.
   - **§ 7, user actions:** v26's, plus that variable check.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-20.**

**T886** (tech-lead, `57e62214`): `docs/artifacts/tracked-debt-register-v27.md`.
- **Totals:** 754 ids: 592 fixed, 46 accepted, 12 obsolete, 1 open (K-20), 103 tracked-LOW. These match the expected delta in every id, status and total.
- **§ 5:** 104 items in all. Batch V goes from 17 to 4 (the SEC-T751-08 residual, plus SEC-T885-01, -02 and -03, with -03 first). Batch X stays at 6 (SEC-T768-04 leaves, SEC-T885-04 joins).
- **Nothing open is above LOW.**
- **§ 6.2:** new item 52, T885's seven tag-pipeline points, including the user's check for the two CI/CD variables.
- **Noted by the tech-lead:** plan-184's Outcome line "the 17 ids above and SEC-T768-04" reads as 18. The count is 17, with SEC-T768-04 among them. This is a wording slip only, and the plan is left as written.
- **Search range:** the § 1.2 search covered `23884e50..013a69df`, which includes this plan's commit. That commit adds no id.

**The orchestrator's own verification:**
- The register parser cannot read bold rows, so the V and X rows were read by hand.
- The § 5 sum (24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 4 + 6 + 11 + 2 + 6 + 3 = 104) and the status sum (592 + 46 + 12 + 1 + 103 = 754) were checked.
- The full suite and the pipeline are recorded in the merge request.

**Budget:** T886 used about 96k, against a budget of 50k.
