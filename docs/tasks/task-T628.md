# T628 — Golden realignment A under grant G-1 (items 1-10, 11 if T627 is merged, 12 only if S-HO-1 allows it)

**ID:** T628
**Owner:** qa-engineer
**Status:** done
**Status note (orchestrator, 2026-10-15):** Item 12 is allowed. The orchestrator completed the read/audit step S-HO-1 on 2026-10-15 (identified by predicate only: the single held-out `/code-review` case with `status: known_failing` and `known_failing_category: tracked_defect`; no id recorded). Result: a review that follows the public `/code-review` text can satisfy the case's unchanged `check()` (the T625 review `docs/artifacts/code-review-t619-v2.md` has all eight verdict fields and an allowed status, checked on a scratch copy). The user decided on 2026-10-14, Q3, "Yes, that one case only (Recommended)", and confirmed on 2026-10-15 "Proceed with Option 1". The user's Bash permission rule is in place in the local, untracked `.claude/settings.local.json` (read-only `cat` of `case.yaml`, `brief.md`, `expect.py` and `grep` on `case.yaml` under `tests/golden/held-out/*/`). If a further command on the held-out directory (copy, delete, write) is denied, stop and report it; do not work around the denial. Item 11 stays excluded (T627 is not merged).
**Priority:** P1
**Tier:** judgment
**Depends on:** T625, T626
**Affects:** —
**Created:** 2026-10-14
**Completed:** 2026-10-15
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T628)
- `docs/artifacts/promotion-and-golden-realignment-plan-v1.md` §4 (classification), §6.3 (grant G-1: the 12 items, the not-authorized list and the controls), §8 (scorecard expectations), §9 (held-out hygiene); this brief carries the grant text by reference to that table
- `docs/artifacts/protected-paths-v1.md` §5, `docs/decisions/ADR-007-command-contract-authority.md`
- The user's approval of G-1 and baseline v21 on 2026-10-14 (verbatim option label): "Approve G-1 and baseline v21 (Recommended)"; and on 2026-10-09: "approving baseline v21 - plan re-evaluation and steps to bring them out of experimental"
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

**This task is authorized to modify the protected paths of `docs/artifacts/protected-paths-v1.md` §5, and only the files of grant G-1 listed in the plan's §6.3 table (items 1-10 always; item 11 only if the `/skillify` skill from T627 is merged; item 12 only if the orchestrator has recorded in this brief's Status note that the held-out read S-HO-1 allowed it and the user's permission rule is in place).** Nothing else under `tests/golden/**` may be touched; `scripts/scorecard.py`, `evaluator_hash.py` and `evaluator-hash-known-good-v*.json` are not authorized. Apply the items exactly as the table states them. Controls (report each): every `expect.py` `check()` is byte-identical (for item 3 only the path lines differ), with before/after `check()` results per affected case; discrimination probes on scratch copies outside the repo (the new fixture returns the expected value; one required element removed returns False; a wrong value returns False); the scorecard before (`34 / 26 / 0`, matching the committed artifact) and after (expected counts in the plan's §8; regenerate `docs/benchmarks/scorecard-v6.12.0.{json,md}` after a status flip); the floor check (find every test or script that encodes the 'at least 5 known_failing' floor before any status flip; if one would fail at the resulting count, stop and report; do not edit it); gates, expecting exactly the two evaluator-hash test failures and no others, named; held-out hygiene (no held-out id anywhere; do not paste `check-maturity.py` output for `tech-lead`; prune `tests/golden/held-out` from every traversal; item 12 only: open only the six held-out `case.yaml` files to find the predicate match, then only that one directory). One local Conventional Commit. Do NOT refresh the baseline.

## 2. Output

The golden changes of the authorized items, a report following the controls, the regenerated scorecard files, one local commit.

## 3. Constraints

- Work in your own worktree/branch; do not push or merge; do not edit ledgers or brief Status lines; no root refresh. Gates: `test_golden_held_out_isolation`, `test_golden_suite_format`, `docs/tasks/validate-tasks.py`, then `python3 tests/run.py` redirected to a file.
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Only authorized files changed (`git diff --stat` shown); `check()` sources byte-identical as stated.
2. Expected results: items 3-6 `check()` stays False; items 7-12 False becomes True; the suite fails in exactly the two evaluator-hash tests.
3. No held-out id appears anywhere.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
