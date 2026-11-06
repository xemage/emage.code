# plan-139 — Tracked-debt register v9

**Created:** 2026-11-06
**Based on:** `docs/artifacts/tracked-debt-register-v8.md` (544 ids), `docs/plans/plan-138-gate-pin-and-strict-read.md` § Changes after the first security review, § Changes after the second security review and § Outcome, and `docs/artifacts/security-review-t741-gate-pin-v1.md`. The user's answer of 2026-11-06, verbatim: "v9 go".
**Scopes:** `T742`.

## Goal

Plan-138 closed two ids of batch S and produced 17 new ones, 6 of them still tracked. Until now only its review record tracks those 6, and v8 § 6.2 item 15 no longer matches the tests. v9 takes them over, so the next fixing round and the next release start from one current list.

## Task Decomposition

1. **T742** (tech-lead): write `docs/artifacts/tracked-debt-register-v9.md`, a delta on v8. Keep v8's section numbering where a section still applies. Do not repeat a row for an id that did not change: v8, v7, v6 and v5 stay the record of its text.
   - **Ids that changed since v8.** One row each, with the citation. Fixed by T741: SEC-T739-05, SEC-T739-01.
   - **Ids that did not change.** Account for every other v8 `open`, `tracked-LOW` and `accepted` id, compactly, by batch or by list, as "Unchanged".
   - **One row for every new id, with the review record's status:**
     - fixed: SEC-T741-01 to -05, -09, -10, -11, -13, -14, -15. Note that SEC-T741-11 closed for the same pipeline, and that its part across pipelines is SEC-T741-17;
     - tracked-LOW: SEC-T741-06, -07, -08, -12, -16, -17;
     - grades as the review gives them: SEC-T741-01 to -04, -09, -10 and -15 were MEDIUM and are resolved.
     - Also any other id that an artifact of plans 137 and 138 mints. Search the lines added in `c1ae6afe..80578802`.
   - **The user's decisions since v8, quoted verbatim:** "v9 go"; "05 01 go"; "Fix all four first (Recommended)"; "Finish T741 yourself"; "review go"; "Fix, narrow re-review (Recommended)"; "Invert the rule, then stop (Recommended)". Each row claims only what the plan records it asked. The stop clause of the last answer was not used, because no route above LOW was found.
   - **The orchestrator's rulings since v8**, marked as not the user's: plan-138 § Outcome, "Rulings".
   - **The open items as batches.** Keep I, J, K, L, M, N, P, Q, R, T, F and U with their v8 scope.
     - **S** loses SEC-T739-05 and -01, and takes the 6 new tracked ids, which gives 15. Keep review T739 § 4's order for its ids, and mark as your suggestion any place you give the new ones. Mark it as still open: no source binds S to a release.
     - **SEC-T739-06's fix** adds an `unset` line to the job's `before_script`. `PINNED_JOBS` now pins that value exactly, so the fix must change the constant `RELEASE_GATE_INSTALL` or the pin. Say so in that row.
     - **SEC-T741-16 and -17** each need something outside a test: a project setting, and a `.gitlab-ci.yml` change. Say so.
     - The route of SEC-T735-06 and -07 is still to be settled before batch R; carry that.
     - Re-read the current lines of batch N and batch S ids that point into `scripts/verify-release-docs.py` and `tests/functional/test_ci_hash_pins.py`: T741 moved them. Do not re-rule them; report any id T741 made stale.
   - **Next release checklist:** carry v8 § 6.2 and change only what plan-138 changed.
     - Rewrite item 15: `allow_failure` on any tag job now fails a test, and the job must still stay without it, because a PyPI outage is when someone will be tempted to add it.
     - **Add:** a new job in `.gitlab-ci.yml` needs an `if` from `NOT_TAG_CONDITIONS`, and adding a condition means checking that it is false on a tag.
     - **Add:** a digest bump across all jobs passes; an `apk` pin or a Python minor bump needs a test constant edit, and the CI header's bump recipe does not say so yet.
     - **Add:** a checked file must be valid UTF-8, and the gate names the path and offset.
     - Re-read every line citation in § 6.2 that points into `scripts/verify-release-docs.py`.
   - **Dates:** carry v8 § 6.3. Plan-138 adds none.
   - **User actions:** carry v8 § 7. Add what plan-138 and the review support:
     - the project's minimum role for pipeline variables (SEC-T741-16);
     - checking tag protection, which the review's § 5 lists as unverified and on which the merge guard's limit depends.
   - **What stays unverified:** carry v8 § 8's list, drop what plan-138 proved, and add the review's § 5. Keep separate what GitLab's lint proved and what is hand trace.
   - *Acceptance:*
     - every v8 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up and no open item is above LOW, or the register says so. Expected from the sources, to be checked and not assumed: 561 ids, 434 fixed, 46 accepted, 6 obsolete, 1 open, 74 tracked-LOW; batches I 10, J 1, K 7, L 5, M 12, N 8, P 1, Q 3, R 4, S 15, T 1, F 2, U 6, which is 75. Report any difference with the reason;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T742 writes only the artifact.
- Do not read the CWSO repository. Its statuses carry over from v8.
- Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file.
- Run no mutation, and no full suite. A test run has a time limit.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-06)

- **T742 is done.** The register is `docs/artifacts/tracked-debt-register-v9.md`. It holds 561 ids, 544 from v8 and 17 new:

  | Status | Ids |
  |---|---:|
  | fixed | 434 |
  | accepted | 46 |
  | obsolete | 6 |
  | open | 1 (K-20) |
  | tracked-LOW | 74 |

- **Batches:** I 10, J 1, K 7, L 5, M 12, N 8, P 1, Q 3, R 4, S 15, T 1, F 2, U 6, which is 75. No open item is above LOW, with the qualification v8 made: TD-T739-01 has no reviewer's grade. All 7 MEDIUMs of review T741 are resolved.
- **The orchestrator's check.**
  - A separate parser of the section 5 tables of v8 and v9 gives 71 and 75 distinct ids, and each batch's stated size matches. The 2 ids that left are SEC-T739-01 and -05. The 6 that entered are SEC-T741-06, -07, -08, -12, -16, -17. Only batch S changed.
  - Each of the 17 new ids has one row in section 3.
  - The cited lines were spot-checked on the tree: `verify-release-docs.py:165, 169, 190, 257`, `test_ci_hash_pins.py:70, 237, 1051`, `test_verify_release_docs.py:1240, 1278`, `.gitlab-ci.yml:18`.
- **An edit after the tech lead's commit, by the orchestrator.** Register § 4.1 marked what "review go" answered as **(unverified)**, because plan-138 does not quote it. The orchestrator asked that question: whether to launch a new Security Engineer on T741's second round. The user's whole answer was, verbatim, "Launch a new Security Engineer on T741. review go". The row now says so.
- **Rulings on what the tech lead left open.**
  - **v8 § 8's list.** "Drop what plan-138 proved" found little to drop, and that stands: only GitLab's rendering of invalid bytes left the list, and it became moot rather than proved, because the gate now refuses such files.
  - **The date outside the plan stands, as a marked line below the table.** `.gitlab-ci.yml:18` says `ci_images_reviewed_on: 2026-10-22`, and `MAX_REVIEW_AGE_DAYS` is 120, so `test_the_review_date_is_present_and_fresh` starts to fail after 2027-02-19. The orchestrator confirmed the date arithmetic and the constant; the test was not run at that date. This plan's sentence "Plan-138 adds none" was about plan-138 and stays true.
  - **The raw U+2028 at `test_verify_release_docs.py:1240`** goes with SEC-T738-06's note. The id's scope does not change.
  - **Batch S's order after the T739 ids, and SEC-T739-06 with SEC-T741-17 in one change,** stand as the tech lead's suggestions, marked so in the register.
- **Open for the user, not ruled here.**
  - Whether any of batch S runs before the next tag.
  - The route of SEC-T735-06 and -07, before batch R.
- **Token use.** T742 used about 166k tokens (the harness's count, which includes context) against a budget of 120k.

