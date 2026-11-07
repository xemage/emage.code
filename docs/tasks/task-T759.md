# T759 — Rehearse the release job in the real CI image

**ID:** T759
**Owner:** devops-engineer
**Status:** in_progress
**Priority:** P0
**Tier:** standard
**Depends on:** T758
**Affects:** —
**Created:** 2026-11-06
**Based on:**
- `docs/plans/plan-145-release-v10.md` (task T759)
- The user's answers of 2026-11-06, verbatim: "release go"; "Approve (Recommended)"

## 1. What and why

Rehearse the release job in the real CI image, as `docs/plans/plan-145-release-v10.md` § Task Decomposition specifies.

## 2. Output

`docs/artifacts/release-rehearsal-t759-v1.md`, committed on `agent/devops-engineer/T759`.

## 3. Constraints

- As in the plan, § Constraints. Do not push, merge, tag or release unless this task's owner is the orchestrator. Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's local `.claude/settings*.json` or `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.
- No `docker` command, other than the one the plan approves for this task.
- Token budget: 80k, counting context.

## 4. Acceptance criteria

As in the plan, § Task Decomposition, T759.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
