# T842 — Security review of T841

**ID:** T842
**Owner:** security-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T841
**Affects:** —
**Created:** 2026-11-14
**Completed:** 2026-11-14
**Based on:**
- `docs/plans/plan-168-batch-j-opencode-permission.md` (§ Addendum 2)
- `docs/artifacts/security-review-t840-opencode-read-v1.md` (SEC-T840-01, SEC-T840-02)
- The user's answer of 2026-11-14 (question dialog, option label verbatim): "Fix now, then refresh (Recommended)"

## 1. What and why

As in plan-168 § Addendum 2.

## 2. Output

`docs/artifacts/security-review-t842-opencode-deny-v1.md` (text returned to the orchestrator).

## 3. Constraints

- Do not push, merge, tag or release.
- Do not edit the ledger, any brief's Status line or the plan.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

- Every agent without `execute`, `edit` or `web` in its source line denies `bash`, `edit`, and `webfetch` plus `websearch` respectively on Opencode.
- No allow is added.
- Every existing entry is kept, in the same order.
- The tests fail for each class if the denial is lost.

## 5. Blocker protocol

Report each blocker with its type and severity.
