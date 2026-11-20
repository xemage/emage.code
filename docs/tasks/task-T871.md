# T871 — Dated confirmation of SEC-T660-01 and SEC-T665-01 for v12.0.0

**ID:** T871
**Owner:** security-engineer
**Status:** done
**Priority:** P0
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-182-next-release.md` (§ Task Decomposition; Addendum 1)
- The user's answers of 2026-11-19, verbatim: "release plan go"; "Approve (Recommended)"; "v12.0.0, MAJOR (Recommended)"; "Yes, probe first (Recommended)"

## 1. What and why

Carry out plan-182 § Task Decomposition item 3.

## 2. Output

The text of `docs/artifacts/security-confirmation-t871-sec-t660-t665-v1.md`. The orchestrator commits it.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 40k.

## 4. Acceptance criteria

See plan-182 § Task Decomposition, item T8710. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
