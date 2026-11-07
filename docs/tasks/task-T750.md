# T750 — Batch S rest: the pipeline and the pins

**ID:** T750
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T749
**Affects:** —
**Created:** 2026-11-06
**Completed:** 2026-11-06
**Based on:**
- `docs/plans/plan-143-batch-s-rest.md` (task T750)
- The user's answer of 2026-11-06, verbatim: "Sgo"
- `docs/artifacts/security-review-t745-batch-s-v1.md` § 4

## 1. What and why

The pipeline half of `docs/plans/plan-143-batch-s-rest.md` § Design: `scripts/run-allowlisted.py`, the job changes, the timeout, `GIT_STRATEGY: clone` on `release`, and the pins.

## 2. Output

Changes committed on `agent/devops-engineer/T750`.

## 3. Constraints

- Work in your own worktree on branch `agent/devops-engineer/T750`. Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.
- Mutation and timing runs only as the plan says. An uncapped run has already crashed this machine once. No full suite. Put a `timeout` on any test run.
- Token budget: 120k, counting context.

## 4. Acceptance criteria

As in the plan, § Task Decomposition, T750.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
