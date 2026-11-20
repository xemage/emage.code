# T834 — SEC-T832-01 query/fragment redaction and SEC-T832-02 decode refusal

**ID:** T834
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-14
**Completed:** 2026-11-14
**Based on:**
- `docs/plans/plan-167-batch-i-sec-t832.md` (§ Goal)
- The user's answer of 2026-11-14, verbatim: "Continue with one of the LOW batches" (the orchestrator chose batch I's SEC-T832-01 and SEC-T832-02)

## 1. What and why

As in plan-167 § Goal.

## 2. Output

Commits on `agent/backend-developer/T834`: `implementation/runtime/memory/context_retriever.py` and its tests.

## 3. Constraints

- Do not push, merge, tag or release.
- Do not edit the ledger, any brief's Status line or the plan.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

As in plan-167 § Goal. Each fix has a test that fails without it.

## 5. Blocker protocol

Report each blocker with its type and severity.
