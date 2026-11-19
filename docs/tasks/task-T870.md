# T870 — Pin and image audit for v12.0.0

**ID:** T870
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-182-next-release.md` (§ Task Decomposition; Addendum 1)
- The user's answers of 2026-11-19, verbatim: "release plan go"; "Approve (Recommended)"; "v12.0.0, MAJOR (Recommended)"; "Yes, probe first (Recommended)"

## 1. What and why

Carry out plan-182 § Task Decomposition item 2.

## 2. Output

`docs/artifacts/mcp-pin-audit-next-v1.md`, committed on `agent/devops-engineer/T870`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 60k.

## 4. Acceptance criteria

See plan-182 § Task Decomposition, item T8700. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
