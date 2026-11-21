# plan-197 — Tracked-debt register v33

**Created:** 2026-11-21
**Based on:**
- `docs/artifacts/tracked-debt-register-v32.md` (771 ids);
- `docs/plans/plan-196-batch-y-shipped-text.md` (Outcome);
- `docs/artifacts/security-review-t904-batch-y-v1.md` (with the orchestrator's addendum).

**Scopes:** `T905`.

## User decision (2026-11-21, verbatim)

> v33 go

## Facts since v32 (the orchestrator's record)

- **Merges:** MR !723 (plan-195, register v32; develop `813a8c17`) and MR !724 (plan-196, batch Y; develop `a1af3b58`, pinned to `204ee14a`; pipelines 3097772273 and 3097772199; clean suite 2883 OK, skipped=25).
- **T904 verdict:** PASS; 0 CRITICAL, HIGH or MEDIUM; 3 LOW new (SEC-T904-01 the `docker run` example in the pin-bump checklist is still a plain command; SEC-T904-02 a search for a current M-2 document, done by the orchestrator, none exists, so closed in the artifact's addendum; SEC-T904-03 the CI header names `eol_problems_of` while the test file's own comment says `eol_image_problems`, and both exist).
- **Fixed in the MR:** TL-T761-12, TL-T819-03, TL-T761-13, TL-T780-08, SEC-T847-01, TL-T761-08, TL-T753-07 (the T745 ledger row and a record-only brief).
- **TD-T789-01:** O-2 and flag 3 done; O-1 partly (its residue is SEC-T904-01).
- **Cannot be fixed at the source:** TL-T763-01 and TL-T763-02 (text in published release documents or immutable artifacts). TL-T763-02: K-35 (QA-T760-03) was fixed by T790, and no current document holds that M-2, so it is obsolete. TL-T763-01: the correction is recorded by `independent-check-t763-v1.md`; the published wording stays.
- **TL-T753-05:** open; its fix is in knowledge sources and needs mirror regeneration and a root refresh, which needs the user's approval.
- **Commit range:** `9493946b..a1af3b58`.
- **Ledger:** 0 active, 702 completed. Root drift prints `.vscode/mcp.json` only, which is the user's own uncommitted edit, not a source drift.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | TL-T761-12, TL-T819-03, TL-T761-13, TL-T780-08, SEC-T847-01, TL-T761-08, TL-T753-07 |
| tracked-LOW → obsolete | TL-T763-01, TL-T763-02 (cannot fix at source; the tech-lead may rule TL-T763-01 differently and says why) |
| Stay tracked-LOW | TD-T789-01 (O-2 and flag 3 done; O-1 residue = SEC-T904-01), TL-T753-05 (needs the user) |
| New, tracked-LOW | SEC-T904-01, SEC-T904-03 |
| New, minted and closed in the same MR | SEC-T904-02 |

Expected totals: 774 ids; fixed 612 + 7 + 1 = 620; accepted 46; obsolete 12 + 2 = 14; open 1 (K-20); tracked-LOW 100 − 7 − 2 + 2 = 93. Check: 620 + 46 + 14 + 1 + 93 = 774. Expected § 5: 94 items (93 + K-20). Batch Y: 11 − 7 − 2 + 2 = 4 (TL-T753-05, TD-T789-01, SEC-T904-01, SEC-T904-03). Every other batch is unchanged. The tech-lead derives the totals and the § 5 table from v32 and this delta, and reports any difference. TD-T789-01 and SEC-T904-01 share the O-1 point: say how you count them (the v26 precedent counts a restatement once; if you rule TD-T789-01 fixed with SEC-T904-01 as its residue, give the changed totals).

## Task Decomposition

1. **T905** (tech-lead): write `docs/artifacts/tracked-debt-register-v33.md`, a delta on v32. It must contain:
   - A row for each changed or new id, with source and status.
   - Counts against v32 that add up, and the § 5 batch table.
   - Whether any open item is above LOW.
   - The § 1.2 search of the added lines in `9493946b..a1af3b58`.
   - § 6.1 unchanged; § 6.2 carries v32's items (note the new `CONTRIBUTING.md` text for the first-tag list, item numbers as the register uses); § 6.3 v32's dates.
   - § 7: v32's user actions, adding the root refresh that TL-T753-05 needs, as a user decision when the user wants it.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Do not write a link-like text with a parenthesis in the target in prose.

## Outcome

**Done on 2026-11-21.**

**T905** (tech-lead, `6094cbb5`): `docs/artifacts/tracked-debt-register-v33.md`.
- **Totals:** 774 ids: 621 fixed, 46 accepted, 14 obsolete, 1 open (K-20), 92 tracked-LOW. **One difference from the expected delta, accepted by the orchestrator:** the tech-lead ruled TD-T789-01 fixed (O-2 and flag 3 done; its O-1 residue is exactly SEC-T904-01, so keeping both tracked would count one point twice, as v32 did for SEC-T888-01 and SEC-T900-02). The expected delta had 620 fixed, 93 tracked-LOW and § 5 of 94; the register states both sets and how to revert.
- **§ 5:** 93 items (25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 3 + 3 + 2 + 6 + 3). Batch Y is 3: TL-T753-05, SEC-T904-01, SEC-T904-03.
- **Rulings:** TL-T763-01 and TL-T763-02 are obsolete (the register-correction half of TL-T763-01 was done in v12 and in independent-check-t763; the published wording cannot be edited and is safe; K-35 was fixed by T790 and no current document holds that M-2). TL-T753-05 stays tracked-LOW. SEC-T904-02 is new and fixed in the same MR.
- **Nothing open is above LOW.**
- **§ 6.2:** item 52 gains point 16 (the new CONTRIBUTING.md text). § 7 adds the root refresh for TL-T753-05 as a user decision when wanted.
- **§ 1.2:** 700 added lines in `9493946b..a1af3b58`, 61 id-like tokens; only SEC-T904-01..03 are in no earlier register.
- **Not verified by the tech-lead:** the README-marker half of the TL-T761-12 text, the ca-chain job's `apk add` list, whether `--context` beats `DOCKER_HOST`.

**The orchestrator's own verification:** the totals and the § 5 sum were checked by hand; the gates pass. The full suite and the pipeline are recorded in the merge request.

**Budget:** T905 used about 95k, against a budget of 50k.
