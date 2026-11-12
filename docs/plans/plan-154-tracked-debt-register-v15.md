# plan-154 — Tracked-debt register v15

**Created:** 2026-11-12
**Based on:** `docs/artifacts/tracked-debt-register-v14.md` (680 ids); `docs/plans/plan-153-context-retriever-low-residue.md` (§ Addendum, § Outcome); `docs/artifacts/security-review-t796-context-retriever-v1.md` (FAIL, SEC-T796-01); `docs/artifacts/security-review-t796-context-retriever-v2.md` (PASS); the ledger rows T795 to T797 in `docs/tasks/completed-tasks.md`. The user's answer of 2026-11-12, verbatim: "v15 go".
**Scopes:** `T798`.

## Goal

Since v14, plan-153 fixed batch O (SEC-T791-02, SEC-T791-03, QA-T792-1), and minted and fixed SEC-T796-01. These changes live only in the plan Outcome and the review records. v15 takes them over, so the v11.0.0 release plan starts from one current list.

## Facts since v14 that no artifact records (the orchestrator's record)

This section is the source for these facts.

- **Merges.**
  - MR !672 (develop `34f8ea7f`): register v14 (plan-152). Verified at `0d78e1da`: pipeline 3058912821 green, the full suite in a clean worktree 2719 OK (skipped=25).
  - MR !673 (squash `2addaef4`, develop `c7016af9`): plan-153, T795 to T797. Verified at `6bcccd68`: pipeline 3060303820 green, the full suite in a clean worktree 2731 OK (skipped=25). `--print-drift` gives `[]`; no root refresh was needed.
- **The user's words since v14, verbatim:** "O go" (plan-153; the orchestrator read it as the word for batch O as v14 defines it, and not as approval of a release, a tag or a root refresh); "v15 go".
- **Ledger:** 0 active, 594 completed after !673.
- **A clean-suite run at the superseded `15e427ba`** failed one timing test (`test_scaling_and_throughput`, `verify-throughput` cv 0.416 > 0.350) while another full suite ran on the same host; run alone it passed 3 of 3 (cv 0.03 to 0.07), and the final run at `6bcccd68` had no failure. The orchestrator records this as an observation, not an id, unless the tech lead finds an existing id it belongs to.
- **Not checked since v14:** SEC-T786-01's trigger (Alpine `nodejs` 24.22.3 in a `unit-tests` log) **(unverified)**.

## Task Decomposition

1. **T798** (tech-lead): write `docs/artifacts/tracked-debt-register-v15.md`, a delta on v14, as v14 was on v13. Keep v14's section numbering where a section still applies. Do not repeat a row for an id that did not change.
   - **Ids that changed since v14**, one row each with its citation:
     - **SEC-T791-02, SEC-T791-03:** fixed by T795, confirmed by T796 v1 and v2. **QA-T792-1:** fixed by T795; T796 confirmed it on review, and the orchestrator re-ran the printed lines (plan-153 § Outcome). Batch O ends.
     - Search the lines added in `34f8ea7f..c7016af9` for every v14 id, and give a row to any other v14 id whose status a source in that range changed.
   - **New ids**, one row each, with the source's grade and final status:
     - **SEC-T796-01** (SECURITY:LOW, blocking in T796 v1 under the gate rule; fixed by T797, confirmed by T796 v2).
     - T796 v2's observations O-1 and O-2 carry no grade and no action; say whether the register records them, and why.
     - Search the lines added in `34f8ea7f..c7016af9` for any other id an artifact mints, and say what you find.
   - **Ids that did not change:** account for every other v14 `open`, `tracked-LOW` and `accepted` id compactly, as "Unchanged". Do not re-rule them.
   - **The user's decisions since v14**, quoted verbatim from § Facts above. Each row claims only what its source records.
   - **The orchestrator's rulings since v14, marked as not the user's:** routing SEC-T796-01 to a fix instead of asking for a ruling on whether an exception message is logging (plan-153 § Addendum); no separate QA task, with the orchestrator's own re-run of QA-T792-1 (plan-153 § Task Decomposition item 3); the reading of "O go" in § Facts above; the timing-test observation in § Facts above.
   - **The open items as batches:** update the size table and the total; mark any order you give as your suggestion. v14's "Order" item for batch O is done.
   - **Next release checklist (v11.0.0, MAJOR):** carry v14 § 6.2, and change only what plan-153 changed. Re-read every line citation in § 6.2 that points into a file changed in `34f8ea7f..c7016af9` (`scripts/install.sh` and `implementation/runtime/memory/` changed). If the release document should report batch O or the behaviour changes of T795 (the server refuses a `.`/`..` remote; the new build warning; the printed `source` prefix), say where in § 6.2 or batch Q, or say there is no place.
   - **Dates:** carry v14 § 6.3 unchanged unless a source in the range changes a row.
   - **User actions:** carry v14 § 7 unchanged unless a source changes one.
   - **What stays unverified:** carry v14 § 8, add T796 v1 and v2 § Method and limits, and keep separate what a real job or run proved, what GitLab's APIs proved, and what is reading only.
   - *Acceptance:*
     - every v14 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up, and the register states whether any open item is above LOW;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T798 writes only the artifact.
- No `docker` command. Do not read the CWSO repository; its statuses carry over from v14.
- Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's `.claude/settings*.json` or `.vscode/*.json`.
- Run no mutation and no full suite. A test run has a time limit.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-12)

- **T798 is done** (commit `634a5f4b`). The register is `docs/artifacts/tracked-debt-register-v15.md`. It holds 681 ids: v14's 680 and 1 new (SEC-T796-01, minted and fixed in plan-153).

  | Status | Ids |
  |---|---:|
  | fixed | 508 |
  | accepted | 49 |
  | obsolete | 9 |
  | open | 1 (K-20) |
  | tracked-LOW | 114 |

- **Batches:** I 23, J 1, K 7, L 5, M 12, N 8, P 1, Q 10, R 4, S 1, V 15, X 10, Y 9, O 0 (ended), F 2, U 7, for a total of 115. No open item carries a grade above LOW on any scale.
- **§ 6.2:** only item 36 changed: the `install.sh` build-line citation moves to `:1739-1741` (read here), and the tech lead suggests that the release document report batch O and T795's behaviour changes there (venv prefix, the wider build warning, the `.`/`..` remote refusal, redacted userinfo). This is the tech lead's suggestion for release-manager, not a ruling.
- **Observations, no id:** T796 v2's O-1 and O-2; the timing test of plan-154 § Facts (mint an id only if it fails on a quiet host or in a pipeline job; the tech lead's suggestion).
- **The orchestrator's check:** the separate parser of the § 5 tables (each "as vN § 5" cell resolved to the register it names) shows that v15's batch ids equal v14's less SEC-T791-02, SEC-T791-03 and QA-T792-1; nothing else differs. The batches carried "as v14" resolve to the same rows in both registers; the parser's id pattern under-counts older id forms there equally in v14 and v15, so it does not re-count those sizes.
