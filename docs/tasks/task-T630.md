# T630 — Promote tech-lead to stable

**ID:** T630
**Owner:** backend-developer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T629
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T630)
- `docs/artifacts/promotion-and-golden-realignment-plan-v1.md` §10 (promotion steps), `docs/artifacts/maturity-promotion-criteria-v2.md` §3.1
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

Only if T629 cleared `tech-lead`'s blocker: set `maturity: stable` in `implementation/knowledge/agents/tech-lead.md`, update the maturity distribution snapshot in `tests/functional/test_check_maturity.py`, regenerate the registry and mirrors, declare the root drift. Run `check-maturity.py --root implementation` (0 failing) and do not paste its output for any component that names a held-out id. An independent re-run by a reviewer other than `tech-lead` (the orchestrator or `solution-architect`) is mandatory because `tech-lead` authored its own exit artifact (T625). If the blocker is not cleared, stop and report; do not promote.

## 2. Output

The edited agent file, test snapshot, mirrors, registry, drift baseline, gate results.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `.claude/` (outside the generated `implementation/.claude` mirror), `.github/` or other derived top-level folders, `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py` when a projected file changes; declare the root drift in `tests/_baselines/root-install-drift.json` (sorted `--print-drift` paths plus one comment line starting "Declared <date> by <task> ("); do NOT refresh the root install.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0 unless the brief says otherwise), `docs/tasks/validate-tasks.py`, the evaluator hash via `implementation/runtime/golden_harness/evaluator_hash.py` (baseline v20 unchanged unless the brief says otherwise), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. `check-maturity.py` reports 0 failing with `tech-lead` stable.
2. The independent re-run is recorded.
3. No other component's maturity changed.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
