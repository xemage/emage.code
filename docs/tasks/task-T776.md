# T776 — Gemini removal inventory

**ID:** T776
**Owner:** tech-lead
**Status:** in_progress
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-07
**Based on:**
- `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md` (§ Addendum (2026-11-07): Part C becomes the Gemini removal, task T776)
- The user's request of 2026-11-07, verbatim: "then review and work on SEC-T657-01/SEC-T658-01"; the user's answer, AskUserQuestion, option label verbatim: "Drop Gemini instead of fixing (Recommended)"

## 1. What and why

As `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md` § Addendum specifies for T776.

## 2. Output

`docs/artifacts/gemini-removal-inventory-v1.md`, committed on `agent/tech-lead/T776`. Read-only otherwise.

## 3. Constraints

- As in the plan, § Constraints. Do not push, merge, tag or release unless this task's owner is the orchestrator. Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's local `.claude/settings*.json` or `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.
- No `docker` command.
- Token budget: 120k, counting context.

## 4. Acceptance criteria

As in the plan, § Addendum, T776, and the matching step of ADR-014 once accepted.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
