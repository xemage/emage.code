# T636 — Refuse symlinked and escaping managed paths in the installer and the merge scripts (audit SEC-001)

**ID:** T636
**Owner:** backend-developer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Addendum 2: T636)
- `docs/artifacts/security-review-release-v8-v1.md` (SEC-001, with the file:line list and the orchestrator's reproduction)
- `scripts/install.sh`, `scripts/merge-mcp-json.py`, `scripts/merge-task-docs.py`, `scripts/render_installed_agents.py`, the existing installer tests (`tests/functional/test_install_script.py`, `test_install_projections_only.py`, `test_merge_task_docs.py`)
- The user's decisions of 2026-10-14 on the T633 audit (AskUserQuestion, verbatim option labels): SEC-001 "Yes, fix before the release (Recommended)"; SEC-002 "Fix before the release (Recommended)"; SEC-003 "I'll check; both are set (grade drops to LOW)".

## 1. What and why

The installer follows symlinks at managed target paths: with `<target>/.claude` a symlink to an outside directory, `install.sh --update` deletes files there (rsync `--delete`) and writes the harness files into it; the same holds for `docs`, `implementation`, `.vscode` and single-file writes (`.mcp.json`, `CLAUDE.md`, ledgers). Add one guard, run before the first write of any mode (including `--dry-run` reporting, `--update` and `--projections-only`): refuse (exit non-zero with a clear message, nothing written) any managed path (and the managed ancestors `docs`, `implementation`, `implementation/runtime`, `.vscode`) that is itself a symlink or whose physical path resolves outside the physical target. Implement it once in `install.sh` and call it from `copy_tree_into`, `sync_tree_into`, `merge_tree_preserve_existing` and before each single-file write; in the three Python scripts, refuse a symlinked destination (`is_symlink()` check or `O_NOFOLLOW`) before writing. A symlink INSIDE a shipped tree that the installer copies verbatim is a separate matter and out of scope (the shipped tree has none today: add a test that asserts `find implementation -type l` is empty). Existing behaviour for ordinary targets must not change (rsync and no-rsync paths keep parity). Reproduce first: a scratch target whose `.claude` links to a scratch directory holding a canary file must show the canary deleted before the fix and intact after it, with the install refused.

## 2. Output

The guard, the Python-script checks, tests (symlinked `.claude`, `docs`, `implementation`, `.vscode`, `.mcp.json`, `CLAUDE.md`, a symlinked ledger; the canary test; no-op on ordinary targets), and a report with before/after of the reproduction, gate results and the suite summary line.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line; do not edit generated platform folders by hand; no root refresh.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `docs/tasks/validate-tasks.py`, the evaluator hash (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere. No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.

## 4. Acceptance criteria

1. The reproduction is deleted-before, intact-after, with a clear refusal message and exit status.
2. No behaviour change for ordinary targets; all existing installer tests pass.
3. A Security Engineer reviews the diff (the orchestrator dispatches it).

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
