# T682 — Installer and generator residuals of the T672 review (N-1..N-8)

**ID:** T682
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T672
**Affects:** —
**Created:** 2026-10-22
**Completed:** 2026-10-22
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-22: T682)
- `docs/artifacts/security-review-t672-installer-robustness-v1.md` (delta re-review, N-1..N-8)

## 1. What and why

Fix the eight LOW findings of the T672 delta re-review (`docs/artifacts/security-review-t672-installer-robustness-v1.md`), in the reviewer's priority order: N-2 (apply the old directory mode to `$build` after the copy, not before; a 555/500/600 destination must not break the update), N-1 (print key, server and permission names of the user file `ascii`-escaped or `repr`ed when not printable), N-4 (`path.resolve` of an absolute `--root`), N-5 (refuse an `outRoot` that equals, contains or is contained by `knowledge`, `platforms`, `_extras`, `scripts`, `runtime` or `__dirname` or another manifest\'s `outRoot`; assert `extras.from` against `_extras`), N-3 (first line of `swap_cleanup`: `trap \'\' HUP INT QUIT TERM`; N-3b `mv -T` where available), N-7 (warn or refuse when a `*.emage-old.*` or `*.emage-new.*` sibling of a managed tree exists at start), N-6 (schema `relPath` pattern that also rejects a newline: `^(?!/)(?!([^/]*/)*\\.\\.?(/|$))[^\\\\]+$`), N-8 (catch `OSError`, `ValueError` and `RecursionError` in `merge-task-docs.py` `main()` with a one-line message; consider an up-front check). Every fix gets a test and a mutation proof (store the mutation log). *Acceptance:* the eight findings closed; all gates and the suite pass; a Security Engineer delta review follows.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief\'s Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; do not modify `tests/golden/**`. No `.env*` or credential files; do not read the user\'s local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
