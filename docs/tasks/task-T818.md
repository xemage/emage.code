# T818 — QA gate for v11.0.0

**ID:** T818
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-13
**Completed:** 2026-11-13
**Based on:**
- `docs/plans/plan-161-release-v11.md` (§ Task Decomposition item 6; § Addenda 1 to 3)
- `docs/releases/v11.0.0.md` (T816); `docs/artifacts/release-v11-audit-v1.md` (T813)
- The user's answers of 2026-11-13 (question dialog, option labels verbatim): plan-161 "Approve (Recommended)"; version "v11.0.0, MAJOR (Recommended)"; probe tag "Yes, probe first (Recommended)".

## 1. What and why

As in plan-161 § Task Decomposition item 6: wave 3, a gate of the v11.0.0 release on `release/v11.0.0`.

## 2. Output

`docs/artifacts/qa-gate-release-v11-v1.md`, with a VERDICT (PASS | CONDITIONAL_PASS | FAIL).

## 3. Constraints

- Review agents do not modify code or the release files during review.
- Do not push, merge, tag or release. Do not edit the ledger, briefs or plan. No `docker`.
- Never open `tests/golden/held-out/`. Never read secrets or the user's settings files. Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

As in plan-161 § Task Decomposition item 6.

## 5. Blocker protocol

Report each blocker with its type and severity.
