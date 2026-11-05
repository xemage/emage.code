# plan-137 — Tracked-debt register v8

**Created:** 2026-11-05
**Based on:** `docs/artifacts/tracked-debt-register-v7.md` (528 ids), `docs/plans/plan-135-batch-n-two-gate-fixes.md` § Outcome, `docs/plans/plan-136-release-gate-markdown-parser.md` § Outcome, `docs/artifacts/security-review-t738-batch-n-two-v1.md` and `docs/artifacts/security-review-t739-gate-parser-v1.md`. The user's answer of 2026-11-05, verbatim: "v8 go".
**Scopes:** `T740`.

## Goal

Plans 135 and 136 closed three ids of batch N and produced 16 new ones, 12 of them still tracked. Until now only two review records and one plan outcome track those 12, and v7 § 6.2 item 7 no longer matches the gate. v8 takes them over, so the next fixing round and the next release start from one current list.

## Task Decomposition

1. **T740** (tech-lead): write `docs/artifacts/tracked-debt-register-v8.md`, a delta on v7. Keep v7's section numbering where a section still applies. Do not repeat a row for an id that did not change: v7, v6 and v5 stay the record of its text.
   - **Ids that changed since v7.** One row each, with the citation. Fixed: SEC-T731-07 (T738), SEC-T731-08 (T739), SEC-T731-09 (part (a) by T738, part (b) by T739). SEC-T731-09 stays one id.
   - **Ids that did not change.** Account for every other v7 `open`, `tracked-LOW` and `accepted` id, compactly, by batch or by list, as "Unchanged".
   - **One row for every new id, with the review record's status:**
     - SEC-T738-01, -03, -04, -05: fixed (the first three by T739, -05 by the orchestrator after the review, not re-reviewed);
     - SEC-T738-02, -06: tracked-LOW;
     - SEC-T739-01 to -09: tracked-LOW;
     - TD-T739-01: tracked-LOW. It is the orchestrator's id and no reviewer graded it; say so.
     - Also any other id that an artifact of plans 134 to 136 mints. Search the lines added in `ecea7b5c..b79ee2d1`.
   - **The user's decisions since v7, quoted verbatim:** "v8 go"; "N two go"; "parser go". Each row claims only what the plan records it asked. "parser go" settles what plan-135 left open for the user, and v7's recommendation on SEC-T731-07 and SEC-T731-09(a) is overtaken by "N two go".
   - **The orchestrator's rulings since v7**, marked as not the user's: plan-135 § Outcome and plan-136 § Outcome, including the timing limit raised from 1.0 s to 5.0 s.
   - **The open items as batches.** Keep I, J, K, L, M, P, Q, R, F and U with their v7 scope.
     - **N** loses SEC-T731-07, -08 and -09 and keeps 8 ids. Its "do first" mark went with SEC-T731-09. Re-read the lines the 8 cite: `scripts/verify-release-docs.py` was largely rewritten. Do not re-rule them; report any id that the rewrite made stale.
     - **S** (new; release gate after the parser) holds SEC-T738-02, SEC-T738-06, SEC-T739-01 to -06, -08, -09 and TD-T739-01, which is 11 ids. Use review § 4's order, with SEC-T739-05 and -01 first. Owner devops-engineer, per review § 4. Mark as open: review § 4 says "next sprint", and no source binds it to a release.
     - **T** (new) holds SEC-T739-07 alone, because review § 4 says it needs its own plan.
     - The route of SEC-T735-06 and -07 is still to be settled before batch R; carry that.
   - **Next release checklist:** carry v7 § 6.2 and change only what plans 135 and 136 changed.
     - Rewrite item 7's second bullet: the blank-line rule is gone, `## Migration Guide <!-- x -->` now counts, and the Cursor item follows the parser (read `has_cursor_migration_item` and `--help` for the exact rule). Item 7's third bullet: `scripts/install.sh` is now also refused for the separators (SEC-T731-07), and its line citations need re-reading.
     - **Add:** watch `release-docs-gate` in the first tag pipeline, because no MR pipeline runs its install, and a release candidate would prove it first. Each publishing step needs the user's approval.
     - **Add:** the job must stay without `allow_failure`, because a PyPI outage is when someone will be tempted to add it (review § 1). SEC-T739-05 records that no test catches this yet.
     - **Add:** a local gate run needs the parser; the install command is the one the gate prints.
     - **Add:** a regeneration of `ci/requirements-ci.txt` needs `ci/requirements-release.txt` too; a test enforces the match.
     - Re-read every line citation in § 6.2 that points into `scripts/verify-release-docs.py`.
   - **Dates and user actions:** carry v7 § 6.3 and § 7. Add nothing that plans 135 and 136 do not support.
   - **What stays unverified:** carry v7 § 8's list and add what the two reviews and plan-136 name: the install in a tag pipeline; GitLab's rendering of front matter, invalid bytes and sanitized attributes; the flags on `WIKI_TOKEN`; `pip-audit`, which did not run; 4.2.0 for TD-T739-01; the merged commit's two later changes, which the reviewer did not see (the timing limit and its comment).
   - *Acceptance:*
     - every v7 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up and no open item is above LOW, or the register says so. Expected from the sources, to be checked and not assumed: 544 ids, 421 fixed, 46 accepted, 6 obsolete, 1 open, 70 tracked-LOW; batches I 10, J 1, K 7, L 5, M 12, N 8, P 1, Q 3, R 4, S 11, T 1, F 2, U 6, which is 71. Report any difference with the reason;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T740 writes only the artifact.
- Do not read the CWSO repository. Its statuses carry over from v7.
- Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-05)

- **T740 is done.** The register is `docs/artifacts/tracked-debt-register-v8.md`. It holds 544 ids, 528 from v7 and 16 new:

  | Status | Ids |
  |---|---:|
  | fixed | 421 |
  | accepted | 46 |
  | obsolete | 6 |
  | open | 1 (K-20) |
  | tracked-LOW | 70 |

- **Batches:** I 10, J 1, K 7, L 5, M 12, N 8, P 1, Q 3, R 4, S 11, T 1, F 2, U 6, which is 71. No open item is above LOW, with one qualification: TD-T739-01 has no reviewer's grade.
- **The orchestrator's check.**
  - A separate parser of the section 5 tables of v7 and v8 gives 62 and 71 distinct ids, and each batch's stated size matches. The 3 ids that left are SEC-T731-07, -08 and -09. The 12 that entered are SEC-T738-02, -06, SEC-T739-01 to -09 and TD-T739-01. Only batch N changed among the old batches.
  - Each of the 16 new ids has a row in section 3.
  - The cited lines were spot-checked on the tree: `verify-release-docs.py:20, 144, 432, 503, 526, 548, 566, 569, 584, 599, 622, 160, 164, 177, 185`, `publish-release.py:629, 750`, `test_ci_hash_pins.py:180, 404`, `test_verify_release_docs.py:696, 701, 1056`, `CONTRIBUTING.md:164, 408, 439`, `.gitlab-ci.yml:196, 206`, `_template.md:3`. Only `scripts/verify-release-docs.py` changed under `scripts/`, `implementation/`, `docs/releases/`, `docs/decisions/` and `ci/js/` since v7.
- **An edit after the tech lead's commit, by the orchestrator.** The tech lead ran the bold-lead shapes of § 6.2 item 7 on 3.0.0 only and marked 4.2.0 **(unverified)**. The orchestrator installed the release lock in a throwaway virtual environment and ran them on 4.2.0: text then a bold lead False, text then a heading True, a blank line then a bold lead True, `## Migration Guide <!-- x -->` True. The register now says so, in § 6.2 item 7 and § 8.
- **Rulings on what the tech lead left open.**
  - **The extra bullet in § 6.2 item 7 stands.** The blank-line rule is gone as a gate rule, but a bold lead must still open its own paragraph. A release author needs both facts, and "the blank-line rule is gone" in plan-136 § Outcome and this plan's brief was too short on its own.
  - **TD-T739-01 stays `tracked-LOW`,** filed by this plan and qualified in the register's section 1.
  - **SEC-T738-06:** raw U+2028 and U+2029 also occur at `test_verify_release_docs.py:494` and `:989`, confirmed by the orchestrator. The id's scope does not change; whoever fixes it reads the register's note.
  - **SEC-T738-05's record** stands as the register words it. T739 removed the code, so no later review can confirm the wording.
- **Open for the user, not ruled here.**
  - Whether any of batch S runs before the next tag. SEC-T739-01 to -04 remain routes for the Cursor check, and SEC-T739-05 is the pin that would catch `allow_failure` on the job. No source binds them to a release.
  - The route of SEC-T735-06 and -07, before batch R.
- **Token use.** T740 used about 142k tokens (the harness's count, which includes context) against a budget of 60k.
