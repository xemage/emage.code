# T737 — Tracked-debt register v7

**ID:** T737
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-05
**Completed:** 2026-11-05
**Based on:**
- `docs/plans/plan-134-tracked-debt-register-v7.md` (task T737)
- The user's answer of 2026-11-05, verbatim: "v7 go"
- `docs/artifacts/tracked-debt-register-v6.md`; `docs/plans/plan-133-batch-h-release-gate-text.md`; `docs/artifacts/security-review-t734-t736-batch-h-v1.md`; `docs/decisions/ADR-012-medium-acceptance-record.md`

## 1. What and why

Write `docs/artifacts/tracked-debt-register-v7.md`, as `docs/plans/plan-134-tracked-debt-register-v7.md` § Task Decomposition specifies.

## 2. Output

`docs/artifacts/tracked-debt-register-v7.md`, committed on `agent/tech-lead/T737`. No other file changes.

## 3. Constraints

- Work in your own worktree on branch `agent/tech-lead/T737`. Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Do not read the CWSO repository. Mark anything you did not verify **(unverified)**.
- Token budget: 60k. The delta is small: read v6 and the three plan-133 sources, and do not re-read v1 to v5.

## 4. Acceptance criteria

As in the plan: every v6 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row; each status claim can be traced, or is marked **(unverified)**; the counts add up and no open item is above LOW, or the register says so; `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity` and `python3 -m unittest discover -s tests -p 'test_team_health*.py'` pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
