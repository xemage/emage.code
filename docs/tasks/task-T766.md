# T766 — CA-chain control in CI for SEC-T756-02

**ID:** T766
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-07
**Based on:**
- `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md` (task T766, § Task decomposition, Part A, item 1)
- The user's request of 2026-11-07, verbatim: "Plan for: Fix of SEC-T756-02, Remove PI support completely, then review and work on SEC-T657-01/SEC-T658-01"; the user's answer, AskUserQuestion, option label verbatim: "Approve (Recommended)"

## 1. What and why

As `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md` § Task decomposition specifies for T766.

## 2. Output

The fixtures, the check, the merge-request CI job and the checklist step, committed on `agent/devops-engineer/T766`.

## 3. Constraints

- As in the plan, § Constraints. Do not push, merge, tag or release unless this task's owner is the orchestrator. Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's local `.claude/settings*.json` or `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.
- No `docker` command.
- Token budget: 110k, counting context.

## 4. Acceptance criteria

As in the plan, § Task decomposition, T766.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
