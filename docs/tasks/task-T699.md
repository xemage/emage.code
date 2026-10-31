# T699 — Twenty-first repo-root refresh (`--projections-only`)

**ID:** T699
**Owner:** orchestrator
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-31
**Completed:** 2026-10-31
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-31: T697 to T699)
- The user's explicit approval of 2026-10-31: "1 2 go, refresh yes"
- `docs/tasks/task-T679.md` (the procedure of the twentieth refresh)

## 1. What and why

The root drift is 23 declared paths (mainly from T690 and T693). Run `scripts/install.sh --target <clean worktree> --platform all --projections-only` on the tip of `origin/develop` (touch the sources' mtimes first: rsync's quick check skips equal-size files), then empty the drift list in `tests/_baselines/root-install-drift.json` and add the 'Emptied' line.

## 2. Output

One commit `chore(self-install): twenty-first repo-root refresh with --projections-only (T699)`.

## 3. Constraints

- Only generated platform folders and `tests/_baselines/root-install-drift.json` change; client-owned paths (`.claude/settings.json`, `.claude/settings.local.json`) are not touched.

## 4. Acceptance criteria

- `python3 -m tests.functional.test_root_install_parity --print-drift` prints `[]`; the suite passes; no file under `docs/` or `implementation/` is changed by the refresh; a Security Engineer review of the diff follows.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
