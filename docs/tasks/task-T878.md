# T878 — Release-document corrections and the v12.0.0 release verdict

**ID:** T878
**Owner:** release-manager
**Status:** in_progress
**Priority:** P0
**Tier:** judgment
**Depends on:** T875, T876, T877
**Affects:** —
**Created:** 2026-11-19
**Based on:**
- `docs/plans/plan-182-next-release.md` (§ Task Decomposition item 11; Addendum 4)
- The user's answers of 2026-11-19, verbatim: "release plan go"; "Approve (Recommended)"; "v12.0.0, MAJOR (Recommended)"; "Yes, probe first (Recommended)"; "Accept for v12.0.0 (Recommended)"; "Yes, push the probe tag (Recommended)"

## 1. What and why

Correct the release document for the gate conditions, then write `## Gate Verdicts` and `## RELEASE VERDICT` (plan-182 item 11). The independent check is `@tech-lead`.

## 2. Output

`docs/releases/v12.0.0.md`, and the one wiki line, on `release/v12.0.0`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No push, merge, tag or release.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 70k.

## 4. Acceptance criteria

- `verify-release-docs.py --tag v12.0.0` exits 0.
- These pass: `validate-tasks.py`, `test_link_integrity` and `test_team_health*`.

## 5. Blocker protocol

Report each blocker with its type and severity.
