# T778 — Gemini removal step S1, code

**ID:** T778
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T777
**Affects:** —
**Created:** 2026-11-07
**Based on:**
- `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md` (§ Addendum (2026-11-07): Part C becomes the Gemini removal, task T778)
- The user's request of 2026-11-07, verbatim: "then review and work on SEC-T657-01/SEC-T658-01"; the user's answer, AskUserQuestion, option label verbatim: "Drop Gemini instead of fixing (Recommended)"

## 1. What and why

As `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md` § Addendum specifies for T778.

## 2. Output

The S1 removal, committed on `agent/devops-engineer/T778`; starts only after the user accepts ADR-014.

## 3. Constraints

- As in the plan, § Constraints. Do not push, merge, tag or release unless this task's owner is the orchestrator. Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's local `.claude/settings*.json` or `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.
- No `docker` command.
- Token budget: 150k, counting context.

## 4. Acceptance criteria

As in the plan, § Addendum, T778, and the matching step of ADR-014 once accepted.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
