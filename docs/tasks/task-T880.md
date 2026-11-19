# T880 — CI lock opentelemetry-api fix, CI-lock audit scope, Node floor note

**ID:** T880
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-182-next-release.md` (Addendum 2)
- The user's answers of 2026-11-19, verbatim: "release plan go"; "Approve (Recommended)"; "v12.0.0, MAJOR (Recommended)"

## 1. What and why

Carry out plan-182 Addendum 2, T880.

## 2. Output

The commits on `agent/tech-lead/T869` (the wave-1 branch).

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 50k.

## 4. Acceptance criteria

See plan-182 Addendum 2. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
