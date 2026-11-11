# plan-147 — Tracked-debt register v12

**Created:** 2026-11-11
**Based on:** `docs/artifacts/tracked-debt-register-v11.md` (596 ids); `docs/plans/plan-145-release-v10.md` § Outcome; `docs/checkpoints/checkpoint-041-release-v10.0.0.md`; `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md` (with its Addendum and Outcome); `docs/checkpoints/checkpoint-042-plan-146-ca-pi-gemini.md`; ADR-013; ADR-014; the review artifacts listed under T783. The user's answer of 2026-11-11, verbatim: "v12 go".
**Scopes:** `T783`.

## Goal

The v10.0.0 release (plan-145) and plan-146 closed some ids, re-graded one, and opened about 80 new ones that only their review records track. v12 takes all of that over, so the v11.0.0 release plan can start from one current list.

## Facts since v11 that no artifact records (the orchestrator's record)

This section is the source for these facts.

**TD-T774-01: the installer's rsync skips an equal-length change (the orchestrator's id, never graded by a reviewer).** Both root refreshes of plan-146 (T774 on 2026-11-07, T781 on 2026-11-11) ran `scripts/install.sh --target <worktree> --platform all --projections-only` in a fresh worktree. In both, `python3 -m tests.functional.test_root_install_parity --print-drift` still listed declared paths after the refresh: in T774, four `context-retriever` agent files. The cause: `rsync -a` compares size and modification time only. After a fresh checkout, source and target carry the same checkout time, so a changed file of the same length is not copied. Touching the sources and running the refresh again copied them, and the drift emptied. The same skip can hit a user's `install.sh --update` whenever a new projection has the same length and time as the installed one. The orchestrator's suggested fix, for a later task: `rsync --checksum`, or a post-copy compare. No reviewer has graded it.

**A-19 is closed.** Checkpoint-041 records that the user deleted both probe tags. `git ls-remote --tags origin 'v9.0.0-gate*'` returned no tag on 2026-11-11.

**The Node image bump is not done.** The advisory was due on 2026-11-11. No task has started.

## Task Decomposition

1. **T783** (tech-lead): write `docs/artifacts/tracked-debt-register-v12.md`, a delta on v11, as v11 was on v10. Keep v11's section numbering where a section still applies. Do not repeat a row for an id that did not change: v11 and earlier stay the record of its text.
   - **Ids that changed since v11.** One row each, with the citation.
     - Every v11 id that plan-145 (the v10.0.0 release, T753 to T764) or plan-146 (T765 to T782) closed, re-graded, accepted again or made obsolete. Search the lines added in `92eb72c3..e098b7d9` for every v11 id; the reviews of plan-145 name some (for example SEC-T751-05, SEC-T751-09).
     - **SEC-T756-02:** re-graded from MEDIUM to LOW by review T768 (CONDITIONAL_PASS, its condition met by pipeline 3040148068). The user chose "No pin (Recommended)" for a CA pin.
     - **SEC-T657-01 / SEC-T658-01 (rest):** review T780 closes it by removal at v11.0.0, with no ADR-011 acceptance needed, and it reopens if the Opencode live check (K-20, A-7, SEC-T658-02) shows the per-agent denies are not honoured. v10.0.0 still ships it. Choose a status that says both, and explain it.
     - **The MEDIUMs accepted for v10.0.0 only** (ADR-011): SEC-T660-01, SEC-T665-01 and SEC-T702-09 each need a fix or a new acceptance from the user before v11.0.0. Say so on each row.
   - **Ids that did not change.** Account for every other v11 `open`, `tracked-LOW` and `accepted` id, compactly, as "Unchanged". Removing Pi and Gemini CLI may have made some v11 ids obsolete or moved their lines (any id that cites `pi.json`, `gemini.json`, `.pi/`, `.gemini/`, `emitMcpGemini`, `skipFormats` or `excludeTools`). Re-read those ids, and give a row to any that is now obsolete or stale. Do not re-rule the rest.
   - **One row for every new id, with the review record's grade and final status.** Take the status from the latest source; a later review, plan Outcome or ledger row overrides an earlier one.
     - Plan-145: SEC-T756-01 to -08 (`security-review-t756-accepted-mediums-v1.md`, `security-review-release-v10-v1.md`); SEC-T762-01 to -05; TL-T753-01 to -07 (`release-v10-audit-v1.md`); TL-T761-01 to -13 (`tech-lead-release-v10-v1.md`); TL-T763-01, -02 (`independent-check-t763-v1.md`); QA-T760-01 to -09 (`qa-release-v10-v1.md`). Plan-145 § Outcome and checkpoint-041 say which of these were fixed before the tag.
     - Plan-146: SEC-T768-01 to -06; SEC-T773-01, -02; TL-T773-01 to -04; SEC-T775-01 to -03 (closed by removal); SEC-T780-01 to -07 (-01 and -02 fixed); TL-T780-01 to -09. TL-T773-01 and TL-T780-01 are accepted residue, recorded in the ledger rows of T773 and T780.
     - TD-T774-01, above.
     - Search the lines added in `92eb72c3..e098b7d9` for any other id an artifact mints, and say what you find.
   - **The user's decisions since v11, quoted verbatim:** checkpoint-041 § Key decisions and plan-145 § Outcome ("develop go", "main go", "tag go" and the earlier answers there); plan-146 and checkpoint-042 § Key decisions; "v12 go". Each row claims only what these sources record.
   - **The orchestrator's rulings since v11**, marked as not the user's: TL-T761-03 (the `--projections-only` warning; the user may overrule); checkpoint-042's list (the T767 owner change, T771's narrowed test skip and the CI tag fetch, T778's deviations, the accepted residue TL-T773-01 and TL-T780-01).
   - **SEC-T762-04 carries two rule questions for the user,** unruled: can a plan's fix be "none possible", and does a new acceptance cure a passed deadline. Carry them to § 7 and to the next release checklist.
   - **The open items as batches.** Keep v11's letters with their scope; say which ones ended. Put the new LOW ids into batches by theme: new letters for new themes, existing letters where an id clearly belongs there. Mark any order you give as your suggestion. Carry SEC-T741-17's runner (A-20) and the open route of SEC-T735-06 and -07, still to be settled before batch R.
   - **Next release checklist (v11.0.0, MAJOR):** carry v11 § 6.2 and change only what plans 145 and 146 changed.
     - **Observed at the v10.0.0 tag** (checkpoint-041): item 6, item 8 (the rendering; its npm step does not run in a tag pipeline), item 14, item 28 (its limit holds: the project is public), D-T710-2. Say what each still leaves.
     - **Correct item 19:** changing the CI image review date no longer needs a test edit (T765). The audit's remark on `build.py:12` was wrong (T765).
     - **Add:** the release document carries the ADR-013 and ADR-014 Appendix A migration items and the frozen-state warnings (SEC-T773-02, SEC-T780-05). The release-doc gate checks migration items only on lines that mention Cursor (TL-T780-09).
     - **Add:** the three v10.0.0-only acceptances above; the user's two SEC-T762-04 questions; both CA-chain jobs must pass, including after the Node image bump; A-21 before the tag.
     - **Add:** run `--print-drift` after any root refresh (TD-T774-01).
     - Re-read every line citation in § 6.2 that points into a file plans 145 and 146 changed.
   - **Dates:** carry v11 § 6.3, and add or update: Brave acceptance ends 2027-01-30; GitLab token renewal 2027-01-28; CWSO bearer 2027-01-29; CI image review date 2027-02-19; the Node advisory of 2026-11-11.
   - **User actions:** carry v11 § 7. A-19 is closed (above). Add A-21 (presence only: `FF_GIT_URLS_WITHOUT_TOKENS`, the CA override variables, `GIT_SSL_NO_VERIFY`, the runner's `tls-ca-file` and `helper_image`; before the next tag or by 2027-02-19). Add the user's own `.vscode/settings.json` `gemini` auto-approve and the one Gemini mention in `.claude/settings.json` (ADR-014 Q4, SEC-T780-06). Git shows both files modified locally; do not open them, and record the action as unverified.
   - **What stays unverified:** carry v11 § 8. Drop what the v10.0.0 tag pipeline settled, and add the plan-145 and plan-146 reviews' lists. Keep separate what a real job proved, what GitLab's APIs proved, and what is hand trace.
   - *Acceptance:*
     - every v11 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up, and the register states whether any open item is above LOW;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T783 writes only the artifact.
- No `docker` command. Do not read the CWSO repository; its statuses carry over from v11.
- Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's `.claude/settings*.json` or `.vscode/*.json`.
- Run no mutation and no full suite. A test run has a time limit.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-11)

- **T783 is done.** The register is `docs/artifacts/tracked-debt-register-v12.md`. It holds 672 ids, 596 from v11 and 76 new:

  | Status | Ids |
  |---|---:|
  | fixed | 497 |
  | accepted | 49 |
  | obsolete | 9 |
  | open | 4 (K-20; QA-T760-01 to -03) |
  | tracked-LOW | 113 |

- **Batches:** I 23, J 1, K 7, L 5, M 12, N 8, P 1, Q 8, R 4, S 1, V 15, X 12, Y 8, Z 3, F 2, U 7, which is 117. Batch W has ended (TD-T746-01 fixed by T754). X, Y and Z are new.
- **The orchestrator's check.** A separate parser of the section 3 and section 5 tables of v11 and v12 gives:
  - the 76 new ids are exactly the ids the sources mint: SEC-T756-01 to -08, SEC-T762-01 to -05, TL-T753-01 to -07, TL-T761-01 to -13, TL-T763-01, -02, QA-T760-01 to -09, SEC-T768-01 to -06, SEC-T773-01, -02, TL-T773-01 to -04, SEC-T775-01 to -03, SEC-T780-01 to -07, TL-T780-01 to -09, TD-T774-01;
  - their statuses: 27 fixed, 40 tracked-LOW, 3 open, 3 accepted, 3 obsolete;
  - the 117 batch ids are unique, and every batch's size equals its list;
  - every v11 batch id is carried, except TD-T746-01.
- **Open above LOW.** No open id carries a `SECURITY:*` grade above LOW. QA-T760-01 to -03 carry `Medium` on QA's own scale: their release-document part was fixed before the v10.0.0 tag, and QA's C1 routes the code behind them to the next release (batch Z).
- **A correction of the orchestrator's record: the CI image review date.** Checkpoint-041, checkpoint-042 and this plan's § Task Decomposition give 2027-02-19. `.gitlab-ci.yml` reads `ci_images_reviewed_on: 2026-11-06`, and `tests/functional/test_ci_hash_pins.py` allows 120 days, so the test fails from **2027-03-07**, as TL-T761-08 said. The orchestrator re-read both lines. 2027-02-19 is SEC-T756-02's deadline as shown to the user and A-21's due date. The text above stays as written, and this section is its correction.
- **Rulings on what the tech lead left open.**
  - **SEC-T657-01/SEC-T658-01 and K-15 stay `accepted`,** with "closes by removal at v11.0.0": v10.0.0 still ships them, and they reopen if the Opencode live check fails.
  - **TD-T774-01 goes in batch I, ungraded.** A reviewer grades it when batch I is next worked.
  - **Batch Q's three v11 ids stay tracked-LOW.** They recur at every release, and no source closes them.
- **Token use.** T783 used about 226k tokens (the harness's count, which includes context) against a budget of 150k.
