# plan-200 — Tracked-debt register v34

**Created:** 2026-11-21
**Based on:**
- `docs/artifacts/tracked-debt-register-v33.md` (774 ids);
- `docs/plans/plan-198-tl-t753-05-root-refresh.md` (Outcome);
- `docs/plans/plan-199-batch-x-sec-t897-01.md` (Outcome);
- `docs/artifacts/security-review-t908-batch-x-v1.md` (with the orchestrator's addendum).

**Scopes:** `T910`.

## User decision (2026-11-21, verbatim)

> v34 go

## Facts since v33 (the orchestrator's record)

- **Merges:** MR !726 (plan-198, T906; develop `93d08065`, squash `a77549f6`, pinned to `a58539b2`; pipelines 3098006469 and 3098006356; clean suite 2883 OK, skipped=25) and MR !727 (plan-199, T908; develop `229459a2`, squash `bb1036f7`, pinned to `f3129407`; pipelines 3098092037 and 3098091973; clean suite 2883 OK, skipped=25).
- **Plan-198 (TL-T753-05):** the five knowledge-source places and two seeded wiki pages now say `verify-release-docs.py` is the authoring repository's script and a target lacks it (nine edits in six files). Mirrors regenerated, root refreshed in the same MR with `install.sh --projections-only` (14 derived files; the user's "Root refresh" was the approval). Drift prints `.vscode/mcp.json` only, the user's own uncommitted edit.
- **Plan-199 (SEC-T897-01):** the apk-pairing check in `tests/functional/test_ci_hash_pins.py` fails closed (8 new mutation cases); the checklist says `--allow-young` cannot override the future-time refusal. T909 verdict PASS; 0 CRITICAL, HIGH or MEDIUM; 2 LOW new: SEC-T909-01 (quote-split or variable forms of `apk`, `after_script` not scanned) and SEC-T909-02 (`<` and `>` refuse a legitimate constraint such as `git>=2.54`).
- **Unchanged in batch X:** SEC-T881-02 (the user chose "Keep the lock", decided) and SEC-T756-02 (the user's runner and variable side, A-21).
- **Commit range:** `1c835d3a..229459a2`.
- **Ledger:** 0 active, 705 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | TL-T753-05, SEC-T897-01 |
| New, tracked-LOW | SEC-T909-01, SEC-T909-02 |

Expected totals: 776 ids; fixed 621 + 2 = 623; accepted 46; obsolete 14; open 1 (K-20); tracked-LOW 92 − 2 + 2 = 92. Check: 623 + 46 + 14 + 1 + 92 = 776. Expected § 5: 93 items (92 + K-20). Batch Y: 3 − 1 = 2 (SEC-T904-01, SEC-T904-03). Batch X: 3 − 1 + 2 = 4 (SEC-T756-02, SEC-T881-02, SEC-T909-01, SEC-T909-02). Every other batch is unchanged. The tech-lead derives the totals and the § 5 table from v33 and this delta, and reports any difference.

## Task Decomposition

1. **T910** (tech-lead): write `docs/artifacts/tracked-debt-register-v34.md`, a delta on v33. It must contain:
   - A row for each changed or new id, with source and status.
   - Counts against v33 that add up, and the § 5 batch table.
   - Whether any open item is above LOW.
   - The § 1.2 search of the added lines in `1c835d3a..229459a2` for id-like tokens, set against registers v1 to v33.
   - § 6.1 unchanged; § 6.2 carries v33's items (check whether the range changes any item; the T906 wording touches shipped text a target gets, and the T908 test change touches no job); § 6.3 v33's dates (the young-pin lapse about 2026-11-24 and 11-25 and Brave 2.2.0 about 2026-11-26 are close).
   - § 7: v33's user actions; the root refresh for TL-T753-05 is done, so say so and drop it.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Do not write a link-like text with a parenthesis in the target in prose.

## Approval

- [ ] Approved by the user

## Outcome (2026-11-21)

**T910** (tech-lead, `f02f629e`): `docs/artifacts/tracked-debt-register-v34.md`.
- **Totals:** 776 ids: 623 fixed, 46 accepted, 14 obsolete, 1 open (K-20), 92 tracked-LOW. No difference from the expected delta.
- **§ 5:** 93 items (25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 4 + 2 + 2 + 6 + 3). Batch Y is 2 (SEC-T904-01, SEC-T904-03); batch X is 4 (SEC-T756-02, SEC-T881-02, SEC-T909-01, SEC-T909-02).
- **Nothing open is above LOW.** § 6.2 has no change (36 numbers, item 52 with 16 points); § 6.3 carries v33's dates; § 7 drops the root refresh (done).
- **Orchestrator correction:** the draft's § 4.1 said no user words were recorded for plan-199; plan-199 quotes "X go". Fixed in the register before the merge.
- **Not verified by the tech-lead:** the ledger count, merge shas, pipelines and suite results (taken from the plan); the orchestrator checked the totals and the § 5 sum by hand, and the suite and pipeline are recorded in the merge request.
- **Budget:** T910 used about 84k, against 50k.
