# T642 — Exclude tests/golden/ from the version-consistency scan (audit v2 decision D-1)

**ID:** T642
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** T641
**Affects:** —
**Created:** 2026-10-15
**Completed:** 2026-10-15
**Based on:**
- `docs/artifacts/release-v8-audit-v2.md` (C-1 and decision D-1, option 1; the 18-finding measurement)
- `scripts/check-version-consistency.py` (`EXCLUDED_PREFIXES` and its comment citing `docs/tasks/task-T400.md`), `tests/functional/test_check_version_consistency.py`, `docs/decisions/ADR-007-command-contract-authority.md` §5
- The user's decision of 2026-10-15 (AskUserQuestion, verbatim option label): "Exclude tests/golden/ (Recommended)"

## 1. What and why

T628 added a frozen copy of `docs/releases/v7.0.1.md` and brief text naming v7.0.1 under `tests/golden/open/prepare-release-real-verdict-missing/`. When the README marker moves to v8.0.0, `scripts/check-version-consistency.py` reports those as stale claims (7 of the 18 findings), which would fail Gate G0 and `release-docs-gate`. The user decided: add `tests/golden/` to `EXCLUDED_PREFIXES` (golden fixtures are frozen evidence by design, like `docs/releases/`, `docs/checkpoints/` and `docs/artifacts/`, which are already excluded). Implement exactly that: one new prefix `"tests/golden/"` in `EXCLUDED_PREFIXES`, the comment above it extended with one sentence citing this task, the user's decision and the reason; add tests to `tests/functional/test_check_version_consistency.py` that pin it: (a) a stale `Latest release: v7.0.1`-style claim under `tests/golden/open/<case>/fixture/` and in a `brief.md` there is NOT reported when the marker is v8.0.0; (b) the same stale claim in a non-excluded path (for example `docs/wiki/x.md`) IS still reported; (c) a path that merely contains the string `tests/golden` but does not start with it (for example `docs/tests/golden/x.md`) is still scanned. No other change to the script or its logic. Do not touch `tests/golden/**` (protected) or `scripts/scorecard.py`.

## 2. Output

The edited script, the new tests, one local commit.

## 3. Constraints

- Work in your own worktree/branch (`agent/devops-engineer/T642`); one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit ledgers or any brief's Status line.
- Gates: the version-consistency test module, `tests.functional.test_golden_held_out_isolation`, `python3 docs/tasks/validate-tasks.py`, then `python3 tests/run.py` redirected to a file (summary lines only). Also run `scripts/check-version-consistency.py` on a scratch copy of `git archive HEAD` (exclude `tests/golden/held-out`) with only the README marker bumped to v8.0.0 and report which findings remain (the expected remainder is the non-golden stale lines listed in audit v2 C-1 rows 1-9, to be fixed in release preparation).
- Never open `tests/golden/held-out/`; never write a held-out case id; no `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`.

## 4. Acceptance criteria

1. Only `scripts/check-version-consistency.py` and its test module changed.
2. The three new tests pass and fail when the prefix is removed (show the mutation).
3. On the scratch copy no finding remains under `tests/golden/`; the other findings are reported unchanged.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
