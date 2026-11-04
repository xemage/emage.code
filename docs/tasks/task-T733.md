# T733 — Tracked-debt register v6

**ID:** T733
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-04
**Completed:** 2026-11-04
**Based on:**
- `docs/plans/plan-132-tracked-debt-register-v6.md` (task T733)
- The user's answer of 2026-11-04, verbatim: "Register v6"
- `docs/artifacts/tracked-debt-register-v5.md`; `docs/plans/plan-131-batch-g-release-tooling.md` § Outcome; `docs/artifacts/security-review-t730-t732-batch-g-v1.md`

## 1. What and why

Write `docs/artifacts/tracked-debt-register-v6.md`, as `docs/plans/plan-132-tracked-debt-register-v6.md` § Task Decomposition specifies.

## 2. Output

`docs/artifacts/tracked-debt-register-v6.md`, committed on `agent/tech-lead/T733`. No other file changes.

## 3. Constraints

- Work in your own worktree on branch `agent/tech-lead/T733`. Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Do not read the CWSO repository. Mark anything you did not verify **(unverified)**.
- Token budget: 60k. The delta is small: do not re-read v1 to v4.

## 4. Acceptance criteria

As in the plan: every v5 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row; each status claim can be traced, or is marked **(unverified)**; the counts add up and no open item is above LOW, or the register says so; `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity` and `python3 -m unittest discover -s tests -p 'test_team_health*.py'` pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
