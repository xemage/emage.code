# T831 — SEC-T829-01 timeout and SEC-T829-02 redaction fixes

**ID:** T831
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-14
**Completed:** 2026-11-14
**Based on:**
- `docs/plans/plan-165-batch-i-followups.md` (§ Goal)
- The user's answer of 2026-11-14, verbatim: "Batch I follow-ups go"

## 1. What and why

As in plan-165 § Goal.

## 2. Output

Commits on `agent/backend-developer/T831`: `implementation/runtime/memory/context_retriever.py`, `implementation/runtime/memory/build.py` if needed, and their tests.

## 3. Constraints

- Do not push, merge, tag or release. Do not edit the ledger, any brief's Status line or the plan. No `docker`.
- Never open `tests/golden/held-out/`. Never read secrets or the user's settings files. Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

As in plan-165 § Goal; each fix has a test that fails without it.

## 5. Blocker protocol

Report each blocker with its type and severity.
