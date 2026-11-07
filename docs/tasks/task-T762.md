# T762 — Security re-check for v10.0.0

**ID:** T762
**Owner:** security-engineer
**Status:** pending
**Priority:** P0
**Tier:** standard
**Depends on:** T758
**Affects:** —
**Created:** 2026-11-06
**Based on:**
- `docs/plans/plan-145-release-v10.md` (task T762)
- The user's answers of 2026-11-06, verbatim: "release go"; "Approve (Recommended)"

## 1. What and why

Security re-check for v10.0.0, as `docs/plans/plan-145-release-v10.md` § Task Decomposition specifies.

## 2. Output

A gate verdict and `docs/artifacts/security-review-release-v10-v1.md`, returned as text; the orchestrator commits it.

## 3. Constraints

- As in the plan, § Constraints. Do not push, merge, tag or release unless this task's owner is the orchestrator. Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's local `.claude/settings*.json` or `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.
- No `docker` command.
- Token budget: 120k, counting context.

## 4. Acceptance criteria

As in the plan, § Task Decomposition, T762.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
