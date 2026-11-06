# T746 — Tracked-debt register v10

**ID:** T746
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-06
**Completed:** 2026-11-06
**Based on:**
- `docs/plans/plan-141-tracked-debt-register-v10.md` (task T746)
- The user's answer of 2026-11-06, verbatim: "1. Delete, 2. v10 go"
- `docs/artifacts/tracked-debt-register-v9.md`; `docs/plans/plan-140-batch-s-release-gate.md`; `docs/artifacts/security-review-t745-batch-s-v1.md`

## 1. What and why

Write `docs/artifacts/tracked-debt-register-v10.md`, as `docs/plans/plan-141-tracked-debt-register-v10.md` § Task Decomposition specifies. That plan's § Facts since plan-140 is the source for the variable, the two settings and the gate probe.

## 2. Output

`docs/artifacts/tracked-debt-register-v10.md`, committed on `agent/tech-lead/T746`. No other file changes.

## 3. Constraints

- Work in your own worktree on branch `agent/tech-lead/T746`. Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; a recursive search over `tests/` needs `--exclude-dir=held-out`. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Do not read the CWSO repository. Mark anything you did not verify **(unverified)**.
- Run no mutation and no full suite. Put a `timeout` on any test run.
- Token budget: 120k, counting context. The delta is small: read v9 and the sources above, and do not re-read v1 to v8.

## 4. Acceptance criteria

As in the plan: every v9 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row; each status claim can be traced, or is marked **(unverified)**; the counts add up and no open item is above LOW, or the register says so; `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity` and `python3 -m unittest discover -s tests -p 'test_team_health*.py'` pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
