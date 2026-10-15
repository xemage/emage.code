# T648 — QA release gate

**ID:** T648
**Owner:** qa-engineer
**Status:** pending
**Priority:** P1
**Tier:** judgment
**Depends on:** T644, T645, T647
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Task Decomposition item for T648)
- `docs/artifacts/release-v8-audit-v2.md`, `docs/artifacts/release-documents-ruling-v1.md`
- The user's approval of plan-122 on 2026-10-15 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"; the decisions quoted in the plan's header.

## 1. What and why

On the `release/v8.0.0` tip: the full suite, golden suite and scorecard, `verify-release-docs.py`, `check-version-consistency.py`, `check-main-develop-drift.py` (offline), a clean install into a scratch target (plain and `--projections-only`), and the Migration steps of the release document replayed on a scratch v7.x-shaped target. Output: a gate verdict (`PASS | CONDITIONAL_PASS | FAIL`) with Executor, Date, Target and a findings table, as a text for the orchestrator to record (test files only for any write).

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or a release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
