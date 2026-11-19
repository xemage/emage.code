# T872 — Open release/v12.0.0 and bump the version markers

**ID:** T872
**Owner:** release-manager
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** T869, T870, T871
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-182-next-release.md` (§ Task Decomposition item 5; Addenda 1 to 3)
- The user's answers of 2026-11-19, verbatim: "release plan go"; "Approve (Recommended)"; "v12.0.0, MAJOR (Recommended)"; "Yes, probe first (Recommended)"; "Accept for v12.0.0 (Recommended)"

## 1. What and why

Carry out plan-182 § Task Decomposition item 5, for `v12.0.0`.

## 2. Output

The version-marker commits, on `release/v12.0.0`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 40k.

## 4. Acceptance criteria

See plan-182 item 5. These must pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
