# plan-132 — Tracked-debt register v6

**Created:** 2026-11-04
**Based on:** `docs/artifacts/tracked-debt-register-v5.md` (500 ids), `docs/plans/plan-131-batch-g-release-tooling.md` § Outcome, and `docs/artifacts/security-review-t730-t732-batch-g-v1.md`. The user's answer of 2026-11-04, verbatim: "Register v6".
**Scopes:** `T733`.

## Goal

Batch G (plan-131) closed most of its 14 ids and produced 17 new ones, 11 of them still tracked. Until now only the review record tracks those 11. v6 takes them over, so the next fixing round and the next release start from one current list.

## Task Decomposition

1. **T733** (tech-lead): write `docs/artifacts/tracked-debt-register-v6.md`, a delta on v5. Keep v5's section numbering where a section still applies. To keep it short, do not repeat a row for an id that did not change: v5 stays the record of its text.
   - **Ids that changed since v5.** One row each, with the citation:
     - fixed by batch G: SEC-T716-01 to -05; SEC-T715-01 to -04; SEC-T676-14; SEC-T677-01 (JavaScript, by T732; Bash is still measured line by line and its two gaps stay in the guard's docstring, so say so in the row);
     - accepted: TL-T708-07 ("Accept as is (Recommended)", basis D-T700-1).
   - **Ids that did not change.** Account for every other v5 `open`, `tracked-LOW` and `accepted` id, compactly, by batch or by list, as "Unchanged".
   - **Two batch G ids that stay open:** SEC-T702-08 (the user: "Keep it tracked") and TD-T723-01 (next release document). Batch G itself is finished, so give each a new home.
   - **One row for every new id:** SEC-T730-01 to -06, SEC-T731-01 to -09, SEC-T732-01 and -02, with the review record's status: 6 fixed, 11 tracked-LOW. Also any other id that a plan-131 artifact mints.
   - **The user's decisions since v5, quoted verbatim:** "Register v6"; "G go"; SEC-T702-08 "Keep it tracked"; TL-T708-07 "Accept as is (Recommended)"; SEC-T677-01 "Add a JS parser"; "Fix now in this batch (Recommended)"; "Allow its reads (Recommended)"; "Fix the three now (Recommended)".
   - **The open items as batches.** Keep H, I, J, K, L, M, F and U with their v5 scope, and put the 11 new ids in a new batch N (release tooling, second round), with scope, owner and trigger. Name SEC-T731-09(a) as the one-line fix the reviewer gave, and note that its false PASS needs a crafted release document.
   - **Next release checklist:** carry v5 § 6.2, drop what batch G did, and add:
     - TD-T723-01;
     - the visible changes in plan-131 § Outcome (escaped `CHANGELOG.md` entries, the blank-line rule for the Cursor item, refused line separators);
     - what plan-131 could not verify: GitLab's rendering of the escaped entries, the npm step in a tag pipeline, and the lock on the musl image beyond the MR pipeline.
   - **Dates and user actions:** carry v5 § 6.3 and § 7. Trivy 0.76.1 (TD-T728-02) became adoptable today, 2026-11-04. Add nothing that plan-131 does not support.
   - *Acceptance:*
     - every v5 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up and no open item is above LOW, or the register says so;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T733 writes only the artifact.
- Do not read the CWSO repository. Its statuses carry over from v5.
- Never open `tests/golden/held-out/`. Read no `.env*` or credential file.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-04)

- **T733 is done.** The register is `docs/artifacts/tracked-debt-register-v6.md`. It holds 517 ids, 500 from v5 and 17 new:

  | Status | Ids |
  |---|---:|
  | fixed | 398 |
  | accepted | 46 |
  | obsolete | 6 |
  | open | 1 (K-20) |
  | tracked-LOW | 66 |

- **No open item is above LOW.** Batches: H 11, I 10, J 1, K 7, L 5, M 12, N 11, P 1, Q 1, F 2, U 6.
- **The orchestrator's check.**
  - A separate parser of v5's rows gives 67 tracked-LOW, 45 accepted and 1 open. All 45 accepted rows occur in v6.
  - Expanding section 5 of both registers gives 68 and 67 distinct ids, and each batch's stated size matches. The 12 ids that left are the 11 fixed by batch G and TL-T708-07; the 11 that entered are batch N.
  - All 17 new ids have one row. The cited lines were spot-checked on the tree: `verify-release-docs.py:435, 522, 622`, `publish-release.py:442, 537-538, 629, 750`, `check-main-develop-drift.py:68`, `.gitlab-ci.yml:97, 104`, `ci/requirements-ci.txt:405`, `test_publish_release_t730.py:77`, `brave-audit-acceptance-v3.md:47`.
- **Rulings on what the tech lead left open.**
  - **The three gaps.** Register § 8 marks as **(unverified)** which ids "Fix now in this batch (Recommended)" covered. The question put to the user named them: SEC-T730-01, SEC-T731-01 and SEC-T731-02.
  - **Batches P and Q** and skipping the letter O stand as the tech lead chose them. Batch P's trigger stays the user's: "Keep it tracked" sets no date.
  - **Residuals without an id.** The `mailto:` autolink (SEC-T716-03) and the two Bash gaps (SEC-T677-01) stay recorded in their parents' rows; no id is minted for them here.
  - **The tech lead's recommendation** to do SEC-T731-07 and SEC-T731-09(a) before the next tag is advice, not a condition. The decision is the user's.
- **Token use.** T733 used about 130k tokens (the harness's count, which includes context) against a budget of 60k. The agent's own estimate was about 50k.
