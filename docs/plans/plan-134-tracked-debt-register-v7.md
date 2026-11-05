# plan-134 — Tracked-debt register v7

**Created:** 2026-11-05
**Based on:** `docs/artifacts/tracked-debt-register-v6.md` (517 ids), `docs/plans/plan-133-batch-h-release-gate-text.md` § Outcome, `docs/artifacts/security-review-t734-t736-batch-h-v1.md` and `docs/decisions/ADR-012-medium-acceptance-record.md`. The user's answer of 2026-11-05, verbatim: "v7 go".
**Scopes:** `T737`.

## Goal

Batch H (plan-133) closed 10 of its 11 ids and produced 11 new ones, 5 of them still tracked. Until now only the review record tracks those 5, and two of them (SEC-T735-08, SEC-T735-09) must reach the next release's checklist before that release starts. v7 takes them over, so the next fixing round and the next release start from one current list.

## Task Decomposition

1. **T737** (tech-lead): write `docs/artifacts/tracked-debt-register-v7.md`, a delta on v6. Keep v6's section numbering where a section still applies. Do not repeat a row for an id that did not change: v6 and v5 stay the record of its text.
   - **Ids that changed since v6.** One row each, with the citation. Fixed by batch H: SEC-T720-02 to -08; TD-T720-01; TD-T725-01; TD-T671-legacy (P10 by T735; the four parked remarks by T560 and T583, per plan-133 § The golden grant was not needed).
   - **SEC-T693-07 stays tracked.** SEC-T720-08 and SEC-T735-03 narrow it and do not close it. Batch H is finished, so it moves to batch R.
   - **Ids that did not change.** Account for every other v6 `open`, `tracked-LOW` and `accepted` id, compactly, by batch or by list, as "Unchanged".
   - **One row for every new id:** SEC-T735-01 to -09, SEC-T736-01 and -02, with the review record's status: 6 fixed (SEC-T735-01 to -05, SEC-T736-02), 5 tracked-LOW (SEC-T735-06 to -09, the rest of SEC-T736-01). Also any other id that a plan-133 artifact mints.
   - **A correction.** Registers v1 to v6 and plan-127 carried P13, P14, P15 and T565 as parked after T560 (`a6be07c6`) and T583 (`8dec82f3`) had fixed them. Say so, and cite plan-133. Do not edit earlier registers: they are immutable.
   - **The user's decisions since v6, quoted verbatim:** "v7 go"; "H go"; "Add it as ADR-012 (Recommended)"; "Grant it for batch H" (given, not used); "Yes, refresh in this MR (Recommended)"; "Record it, no new question (Recommended)"; "Add the sentence (Recommended)"; "Fix the three now (Recommended)". Record as the user's only what the question asked (`docs/plans/plan-133-batch-h-release-gate-text.md` § Changes after the first security review, and SEC-T735-01). `APPROVED_WITH_CHANGES` = Revise is the orchestrator's ruling, not the user's.
   - **The open items as batches.** Keep I, J, K, L, M, N, P, F and U with their v6 scope. Drop H.
     - **Q** (next release document) also takes SEC-T735-08 and SEC-T735-09, so it holds 3 ids.
     - **R** (new, release-gate text, second round) holds SEC-T735-06, SEC-T735-07, the rest of SEC-T736-01, and SEC-T693-07. Scope, owner and trigger as the review's § 4 supports. SEC-T735-07 changes ADR-011's A1 text, so its route must be confirmed first; say so.
   - **Next release checklist:** carry v6 § 6.2, drop item 5 (batch H did it), and add what SEC-T735-08 and SEC-T735-09 require, in the reviewer's words where possible:
     - when asking the user to re-accept a Medium: name the release, record the plan as shown, and show a deadline still ahead (ADR-012). Say this in item 2, against the four ids named there;
     - the Conditions block's `grade=` and `release=` slots and owner fields (`release-manager.md:183`);
     - the template's pointer sentence (`docs/releases/_template.md:90`): remove it before the independent check, or leave it;
     - the checker must not have authored or edited the release files for this release, so `@tech-lead` is the practical default (`release-manager.md:46`);
     - the batch H changes that a release author sees: the closed list after the check (`release-manager.md:46`), and hotfix eligibility (`release-workflow/SKILL.md:171`);
     - what plan-133 could not verify: whether targets receive `scripts/verify-release-docs.py` and `_template.md`.
   - **The tech lead's earlier recommendation** on SEC-T731-07 and SEC-T731-09(a) stays advice, and the user has not ruled on it. Keep it, marked so.
   - **Dates and user actions:** carry v6 § 6.3 and § 7. Add nothing that plan-133 does not support.
   - *Acceptance:*
     - every v6 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up and no open item is above LOW, or the register says so. Expected from the sources, to be checked and not assumed: 528 ids, 414 fixed, 46 accepted, 6 obsolete, 1 open, 61 tracked-LOW; batches I 10, J 1, K 7, L 5, M 12, N 11, P 1, Q 3, R 4, F 2, U 6, which is 62. Report any difference with the reason;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T737 writes only the artifact.
- Do not read the CWSO repository. Its statuses carry over from v6.
- Never open `tests/golden/held-out/`. Read no `.env*` or credential file.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-05)

- **T737 is done.** The register is `docs/artifacts/tracked-debt-register-v7.md`. It holds 528 ids, 517 from v6 and 11 new:

  | Status | Ids |
  |---|---:|
  | fixed | 414 |
  | accepted | 46 |
  | obsolete | 6 |
  | open | 1 (K-20) |
  | tracked-LOW | 61 |

- **No open item is above LOW.** Batches: I 10, J 1, K 7, L 5, M 12, N 11, P 1, Q 3, R 4, F 2, U 6.
- **The orchestrator's check.**
  - A separate parser of the section 5 tables of v6 and v7 gives 67 and 62 distinct ids, and each batch's stated size matches. The 10 ids that left are batch H's fixed ones; the 5 that entered are SEC-T735-06 to -09 and SEC-T736-01. SEC-T693-07 moved from H to R.
  - All 11 new ids have one row, with the review's status. The unchanged list in § 2.2 holds 55 distinct ids, and § 2.3 holds 5 and 41. Every accepted id occurs in v5 or v6 § 2.3, except TL-T708-07, which v6 § 6.1 records.
  - The cited lines were spot-checked on the tree: `release-manager.md:46, 183`, `validation-gates/SKILL.md:70`, `release-workflow/SKILL.md:171, 202`, `plan-approve-execute/SKILL.md:115`, `docs/releases/_template.md:90`, `scripts/install.sh:1296`, `scripts/verify-release-docs.py:522`, `plan-084:53-56`. `git diff --stat e95f8932 d76a43f7` over the reviewed paths is empty.
- **Rulings on what the tech lead left open.**
  - **SEC-T735-08 and -09 stay tracked-LOW in batch Q.** Register § 6.2 now carries what the reviewer asked, but they close only when a release has applied it.
  - **The correction.** Register § 2.4 is narrower than this plan's sentence, and it stands: v1 to v3 name P14 and P15, v4 names none, and plan-127, v5 and v6 name all four. P15 also needed T668.
  - **SEC-T693-07** stays `tracked-LOW` with the residual accepted by ruling. Batch R makes no edit for it.
  - **SEC-T735-06 and -07: the route is not settled.** Both fixes change text that an accepted ADR holds, and the reviewer asked for the route of -07 to be confirmed. Decide it before batch R starts. That -06 has the same question is the tech lead's reading.
  - **Owners and the trigger of batch R** stand as the tech lead's suggestions, marked so in the register. Review § 4 sets neither.
  - **The recommendation** on SEC-T731-07 and SEC-T731-09(a) is advice. The decision is the user's.
- **Not verified, and open for the next release:** each carried plan's actual deadline, which must be read before the user is asked (register § 6.2, item 2).
- **A habit to change.** `test_team_health` warns that only 1 of the last 10 subjects is a Conventional Commit, because the squash subjects read `plan-NNN: …`. This plan's squash subject and later ones use `docs(plan-NNN): …` or the matching type.
- **Token use.** T737 used about 120k tokens (the harness's count, which includes context) against a budget of 60k. The agent's report said the budget was respected, to its estimate.
