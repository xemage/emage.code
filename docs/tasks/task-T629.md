# T629 — Evaluator baseline v21

**ID:** T629
**Owner:** orchestrator
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T628
**Affects:** —
**Created:** 2026-10-14
**Completed:** 2026-10-15
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T629)
- `docs/artifacts/promotion-and-golden-realignment-plan-v1.md` §7 (the exact procedure and checks), `docs/artifacts/evaluator-hash-check-v1.md`, `docs/artifacts/evaluator-hash-known-good-v20.json`, `implementation/runtime/golden_harness/evaluator_hash.py`
- The user's authorization of baseline v21 (2026-10-09 and 2026-10-14, quoted in plan-121)
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

Follow §7 of the plan step by step: confirm exactly the two red evaluator-hash tests; confirm the changed files; confirm `tests_golden` differs from v20 and `scripts_scorecard` equals v20; compute the payload; verify it with an independent second computation in a fresh worktree; write `docs/artifacts/evaluator-hash-known-good-v21.json` as a NEW file; repoint `DEFAULT_KNOWN_GOOD_PATH` and the docstring in `evaluator_hash.py` (update only live pointers found by a repository search that prunes `tests/golden/held-out`); write a `reason` that names no held-out id; re-run the suite. Commit v21, the repointed module and the regenerated scorecard files on one MR branch so `develop` never carries a red hash test.

## 2. Output

`evaluator-hash-known-good-v21.json`, the repointed module, the report of every check in §7.

## 3. Constraints

- Orchestrator executes this; commit on its own branch; MR after independent verification.
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. `check_evaluator_hash()` reports no drift at v21 and detects a tampered copy.
2. The suite is green; the scorecard counts are as expected.
3. v1-v20 are untouched; the `reason` text contains no held-out id.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
