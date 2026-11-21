# plan-195 — Tracked-debt register v32

**Created:** 2026-11-21
**Based on:**
- `docs/artifacts/tracked-debt-register-v31.md` (765 ids);
- `docs/plans/plan-194-batch-v-fourth-round.md` (Outcome);
- `docs/artifacts/security-review-t900-batch-v-v1.md` (with the orchestrator's addendum).

**Scopes:** `T901`.

## User decision (2026-11-21, verbatim)

> v32 go

## Facts since v31 (the orchestrator's record)

- **Merges:** MR !721 (plan-193, register v31; develop `5775f17d`) and MR !722 (plan-194, batch V fourth round; develop `9493946b`, pinned to `f41bccea`; pipelines 3097540465 and 3097540427; clean suite 2883 OK, skipped=25).
- **T900 verdict:** CONDITIONAL_PASS at `f6ca9470`; 0 CRITICAL, 0 HIGH, 1 MEDIUM, 5 LOW new. The MEDIUM, SEC-T900-01 (exponential `CODE_SPAN_RE`, quadratic `COMMENT_RE`), was confirmed by the orchestrator's own timing and fixed in `2584bb45` in the same MR (linear scans, timing tests at the cap). No second security review was held, because the condition named the orchestrator's confirmation. SEC-T900-03 (error message) and SEC-T900-05 (vacuous assertion; timing tests) were fixed in the same commit. SEC-T900-02, -04 and -06 stay open, LOW.
- **Fixed in the MR:** SEC-T888-03; SEC-T888-02 (part (b); the ASCII look-alikes `|`, `l`, `1`, `0` stay non-wildcards by design, noted in SEC-T900-05); SEC-T888-01 (in the form the review asked for; its textual exclusion is SEC-T900-02).
- **Commit range:** `b04ec271..9493946b`.
- **Ledger:** 0 active, 697 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | SEC-T888-01, SEC-T888-02, SEC-T888-03 |
| New, minted and fixed in the same MR | SEC-T900-01 (MEDIUM), SEC-T900-03, SEC-T900-05 |
| New, tracked-LOW | SEC-T900-02, SEC-T900-04, SEC-T900-06 |

Expected totals: 771 ids; fixed 606 + 3 + 3 = 612; accepted 46; obsolete 12; open 1 (K-20); tracked-LOW 100 − 3 + 3 = 100. Check: 612 + 46 + 12 + 1 + 100 = 771. Expected § 5: 101 items. Batch V: the three SEC-T888 ids leave and SEC-T900-02, -04, -06 join (the tech-lead names the batch row; "release gate, fourth round" is the suggestion), so V = 3. Every other batch is unchanged. The tech-lead derives the totals and the § 5 table from v31 and this delta, and reports any difference. Where an id restates an existing one, the v26 precedent (counted once) applies; say so. SEC-T900-05 combined two points (vacuous assertion, ASCII look-alikes): say how you count it.

## Task Decomposition

1. **T901** (tech-lead): write `docs/artifacts/tracked-debt-register-v32.md`, a delta on v31. It must contain:
   - A row for each changed or new id, with source and status. SEC-T900-01 gets a row saying it was MEDIUM, found by the review, confirmed by the orchestrator's timing and fixed before merge (not accepted, not shipped).
   - Counts against v31 that add up, and the § 5 batch table.
   - Whether any open item is above LOW.
   - The § 1.2 search of the added lines in `b04ec271..9493946b`.
   - § 6.1 unchanged; § 6.2 carries v31's items (item 52: add that the gate now refuses a link it cannot read and a pipe-and-tag table paragraph, so the tag's own release document must pass `scripts/verify-release-docs.py --tag` before the tag is cut, as already required); § 6.3 v31's dates.
   - § 7: v31's user actions.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Addendum 1 — the request

The user's request is quoted above; there was no further dialog for this register.

## Outcome

**Done on 2026-11-21.**

**T901** (tech-lead, `7f39fb27`): `docs/artifacts/tracked-debt-register-v32.md`.
- **Totals:** 771 ids: 612 fixed, 46 accepted, 12 obsolete, 1 open (K-20), 100 tracked-LOW. They match the expected delta in every id, status and total, with no difference.
- **§ 5:** 101 items (25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 3 + 11 + 2 + 6 + 3). Batch V is "Release gate, fourth round": SEC-T900-02, -04 and -06 (the three SEC-T888 ids left it as fixed). Every other batch is unchanged.
- **Counting:** SEC-T900-05 is one id, fixed; the ASCII look-alike limit is a design limit, not a second id. SEC-T900-01 is MEDIUM, fixed before merge, never shipped, and no acceptance.
- **Nothing open is above LOW.**
- **§ 6.2:** item 52 gains point 15 (the gate refuses a link it cannot read and a pipe-and-tag table paragraph).
- **§ 1.2:** 830 added lines in `b04ec271..9493946b`, 45 id-like tokens; only SEC-T900-01..06 are in no earlier register.
- **Not traced by the tech-lead:** whether SEC-T900-03's fix lets the link pattern read empty or bracketed text (marked unverified).

**The orchestrator's own verification:** the totals and the § 5 sum were checked by hand; the gates pass. The full suite and the pipeline are recorded in the merge request.

**Budget:** T901 used about 80k, against a budget of 50k.
