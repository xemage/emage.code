# T861 — Batch AB: Opencode permission, third round

**ID:** T861
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-178-batch-ab-opencode-third-round.md`
- The user's answer of 2026-11-19, verbatim: "X + AB go"

## 1. What and why

Carry out plan-178 § Task Decomposition item 1.

## 2. Output

The commits on `agent/devops-engineer/T861`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 90k.

## 4. Acceptance criteria

See plan-178 § Task Decomposition. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
