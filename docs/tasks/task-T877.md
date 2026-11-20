# T877 — Release-level security re-check for v12.0.0

**ID:** T877
**Owner:** security-engineer
**Status:** done
**Priority:** P0
**Tier:** judgment
**Depends on:** T873
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-182-next-release.md` (§ Task Decomposition item 10; Addenda 1 to 3)
- The user's answers of 2026-11-19, verbatim: "release plan go"; "Approve (Recommended)"; "v12.0.0, MAJOR (Recommended)"; "Yes, probe first (Recommended)"; "Accept for v12.0.0 (Recommended)"; "Yes, push the probe tag (Recommended)"

## 1. What and why

Carry out plan-182 § Task Decomposition item 10, for `v12.0.0`.

## 2. Output

The text of `docs/artifacts/security-review-t877-release-v12-v1.md`. The orchestrator commits it.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 60k.

## 4. Acceptance criteria

See plan-182 item 10. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
