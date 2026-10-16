# T669 — Evaluator baseline v22

**ID:** T669
**Owner:** orchestrator
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T668
**Affects:** —
**Created:** 2026-10-16
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Task Decomposition item for T669; the section "Grant G-2" for T668 and T669)
- `docs/checkpoints/checkpoint-038-release-v8.0.0.md` (section 3), `docs/releases/v8.0.0.md` (Known issues), the review artifacts named in the item
- The user's words of 2026-10-16: "I want to drop Cursor support completely" (T661, T662); "Regarding baseline v22: approving it" (T668 to T670); the approval of plan-123 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"

## 1. What and why

Evaluator baseline **v22** (orchestrator): the procedure of the promotion plan §7 with every "21" read as "22" (two independent digest computations, a new `evaluator-hash-known-good-v22.json`, `DEFAULT_KNOWN_GOOD_PATH` repointed, a `reason` without held-out ids). Depends on T668. *Acceptance:* hash check passes at v22 and fails on a tampered copy; scorecard counts as expected; the suite passes.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift unless the brief says otherwise), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths plus one comment line starting `Declared <date> by <task> (`); do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; only T668 may modify `tests/golden/**` (grant G-2). No `.env*` or credential files (the primary checkout has an untracked local `.env` that must not be read or grepped); do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
