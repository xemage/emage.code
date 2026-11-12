# plan-152 — Tracked-debt register v14

**Created:** 2026-11-12
**Based on:** `docs/artifacts/tracked-debt-register-v13.md` (675 ids); `docs/plans/plan-150-pin-checklist-no-docker.md` (§ Outcome); `docs/artifacts/security-review-t789-pin-checklist-v1.md`; `docs/plans/plan-151-context-retriever-code-residue.md` (§ Outcome); `docs/artifacts/security-review-t791-context-retriever-v1.md`; `docs/artifacts/qa-recheck-t792-context-retriever-v1.md`; the ledger rows T788 to T793 in `docs/tasks/completed-tasks.md`. The user's answer of 2026-11-12, verbatim: "v14 go".
**Scopes:** `T794`.

## Goal

Since v13, plan-150 fixed SEC-T786-02 and minted TD-T789-01, and plan-151 fixed the code behind QA-T760-01 to -03 and minted SEC-T791-01 to -03 and QA-T792-1. These changes live only in their plan Outcomes and review records. v14 takes them over, so the v11.0.0 release plan starts from one current list.

## Facts since v13 that no artifact records (the orchestrator's record)

This section is the source for these facts.

- **Merges.**
  - MR !668 (develop `713a14c6`): register v13 (plan-149).
  - MR !669 (develop `4cdf64ac`): plan-150, T788 and T789. Verified at `d1b24341`: pipeline 3057685976 green, the full suite in a clean worktree 2707 OK.
  - MR !670 (squash `d69ecad0`, develop `4aaf8d33`): plan-151, T790 to T792. Verified at `6c0bcdc4`: pipeline 3058131011 green, the full suite in a clean worktree 2719 OK (skipped=25).
  - MR !671 (develop `325aebb4`): T793, the root refresh, with the user's approval of 2026-11-12, verbatim: "refresh". Verified at `04401738`: pipeline 3058787632 green, the full suite in a clean worktree 2719 OK (skipped=25). `--print-drift` gives `[]` after the merge.
- **The user's words since v13, verbatim:** "Fix SEC-T786-02" (plan-150); "Continue with the next best step" (plan-151; the orchestrator read it as the word for batch Z, the first item of v13's suggested order, and not as approval of a release, a tag or a root refresh); "resume" (the two reviews of plan-151 were resumed after a usage limit); "refresh" (T793); "v14 go".
- **Ledger:** 0 active, 590 completed after !671.
- **Not checked since v13:** SEC-T786-01's trigger (Alpine `nodejs` 24.22.3 in a `unit-tests` log). No one has read a `unit-tests` log for it since T786 **(unverified)**.

## Task Decomposition

1. **T794** (tech-lead): write `docs/artifacts/tracked-debt-register-v14.md`, a delta on v13, as v13 was on v12. Keep v13's section numbering where a section still applies. Do not repeat a row for an id that did not change.
   - **Ids that changed since v13**, one row each with its citation:
     - **SEC-T786-02:** fixed by T788, confirmed by T789 (PASS). It leaves batch Y.
     - **QA-T760-01, -02, -03:** fixed by T790, confirmed by T791 (security) and T792 (QA re-run). Batch Z ends.
     - Search the lines added in `713a14c6..325aebb4` for every v13 id, and give a row to any other v13 id whose status a source in that range changed.
   - **New ids**, one row each, with the source's grade and final status:
     - **TD-T789-01** (the orchestrator's id, no `SECURITY:*` grade; plan-150 § Outcome): batch Y, as plan-150 says.
     - **SEC-T791-01, -02, -03** (SECURITY:LOW; T791). SEC-T791-01's deadline is the v11.0.0 release document, before the tag: put it in batch Q and in § 6.2.
     - **QA-T792-1** (Low on QA's scale; T792).
     - Place SEC-T791-02, -03 and QA-T792-1 in a batch. Choose an existing letter or a new one, and say why.
     - Search the lines added in `713a14c6..325aebb4` for any other id an artifact mints, and say what you find.
   - **Ids that did not change:** account for every other v13 `open`, `tracked-LOW` and `accepted` id compactly, as "Unchanged". Do not re-rule them.
   - **The user's decisions since v13**, quoted verbatim from § Facts above. Each row claims only what its source records.
   - **The orchestrator's rulings since v13, marked as not the user's:** plan-150 § Outcome (keeping the writer's two registry API details; TD-T789-01 and its three parts; the release-docs-gate observation); plan-151 § Outcome (the skip-count explanation) and the reading of "Continue with the next best step" in § Facts above.
   - **The open items as batches:** update the size table and the total; mark any order you give as your suggestion. v13's "Order" item 1 (batch Z) and item 3 (SEC-T786-02) are done.
   - **Next release checklist (v11.0.0, MAJOR):** carry v13 § 6.2, and change only what plans 150 and 151 changed:
     - item 36 (batch Z) is done;
     - add SEC-T791-01's migration note: on an install with `.claude/` beside other platform folders, Cline and Opencode sessions now resolve as their own platform, which changes which shared-scope entries they see (T791 § Findings);
     - add QA-T760-01 to -03's code fix to what the release document reports as fixed, if v13 § 6.2 or batch Q has a place for it (say where, or say there is none);
     - re-read every line citation in § 6.2 that points into a file changed in `713a14c6..325aebb4` (`scripts/install.sh` changed; `.gitlab-ci.yml` did not).
   - **Dates:** carry v13 § 6.3 unchanged unless a source in the range changes a row.
   - **User actions:** carry v13 § 7 unchanged unless a source changes one. A-21 is still open.
   - **What stays unverified:** carry v13 § 8, add T791 § Method and limits and T792 § Method and limits, and keep separate what a real job or run proved, what GitLab's APIs proved, and what is reading only.
   - *Acceptance:*
     - every v13 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up, and the register states whether any open item is above LOW;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T794 writes only the artifact.
- No `docker` command. Do not read the CWSO repository; its statuses carry over from v13.
- Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's `.claude/settings*.json` or `.vscode/*.json`.
- Run no mutation and no full suite. A test run has a time limit.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-12)

- **T794 is done** (commit `0da8bd6b`). The register is `docs/artifacts/tracked-debt-register-v14.md`. It holds 680 ids: v13's 675 and 5 new (TD-T789-01, SEC-T791-01, SEC-T791-02, SEC-T791-03, QA-T792-1).

  | Status | Ids |
  |---|---:|
  | fixed | 504 |
  | accepted | 49 |
  | obsolete | 9 |
  | open | 1 (K-20) |
  | tracked-LOW | 117 |

- **Batches:** I 23, J 1, K 7, L 5, M 12, N 8, P 1, Q 10, R 4, S 1, V 15, X 10, Y 9, O 3 (new), F 2, U 7, for a total of 118; Z ended. No open item carries a `SECURITY:*` grade above LOW, and no open item carries QA's Medium any more.
- **The orchestrator's check:** a separate parser of the § 5 tables, resolving each "as vN § 5" cell to the register it names, shows that v14's batch ids equal v13's, less SEC-T786-02 and QA-T760-01 to -03, plus the five new ids; nothing else differs. Q, Y, Z and O differ from v13 by exactly those ids, and their stated sizes equal their lists. For the batches carried "as v13" (I, K, L, M, N, V) the parser's id pattern does not match every older id form, so it does not re-count their sizes; they resolve to the same source rows in v13 and v14 and are unchanged. Section 2.2 names every v13 tracked-LOW id except SEC-T756-05 and -06, which v13 already recorded as fixed.
- **The orchestrator's rulings (not the user's):** the new batch letter O, for SEC-T791-02, SEC-T791-03 and QA-T792-1, and the placement of all five new ids, as T794 proposes (register § 5). Plan-150's "batch Y drops to 8" is read as Y before TD-T789-01 was added; with it Y holds 9 (register § 4.3).
