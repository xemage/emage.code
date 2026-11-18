# T844 — Security review of T843

**ID:** T844
**Owner:** security-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T843
**Affects:** —
**Created:** 2026-11-14
**Completed:** 2026-11-14
**Based on:**
- `docs/plans/plan-168-batch-j-opencode-permission.md` (§ Addendum 3)
- `docs/artifacts/security-review-t842-opencode-deny-v1.md` (SEC-T842-01)
- The user's answer of 2026-11-14 (question dialog, option label verbatim): "Fix now, then refresh (Recommended)"

## 1. What and why

As in plan-168 § Addendum 3.

## 2. Output

`docs/artifacts/security-review-t844-opencode-task-v1.md` (text returned to the orchestrator).

## 3. Constraints

- Do not push, merge, tag or release.
- Do not edit the ledger, any brief's Status line or the plan.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

- Every agent whose source line has no `agent` denies `task` on Opencode.
- `orchestrator` and `poc-orchestrator` keep the default.
- No allow is added.
- Every existing entry is kept, in its order.
- A dropped deny fails the tests.

## 5. Blocker protocol

Report each blocker with its type and severity.
