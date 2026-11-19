# T875 — QA gate for v12.0.0

**ID:** T875
**Owner:** qa-engineer
**Status:** in_progress
**Priority:** P0
**Tier:** standard
**Depends on:** T873
**Affects:** —
**Created:** 2026-11-19
**Based on:**
- `docs/plans/plan-182-next-release.md` (§ Task Decomposition item 8; Addenda 1 to 3)
- The user's answers of 2026-11-19, verbatim: "release plan go"; "Approve (Recommended)"; "v12.0.0, MAJOR (Recommended)"; "Yes, probe first (Recommended)"; "Accept for v12.0.0 (Recommended)"; "Yes, push the probe tag (Recommended)"

## 1. What and why

Carry out plan-182 § Task Decomposition item 8, for `v12.0.0`.

## 2. Output

`docs/artifacts/qa-gate-release-v12-v1.md`

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 90k.

## 4. Acceptance criteria

See plan-182 item 8. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
