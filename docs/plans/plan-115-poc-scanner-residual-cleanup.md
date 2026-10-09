# plan-115 — PoC scanner residual cleanup (T605 and T609-10..T609-13)

**Created:** 2026-10-09
**Based on:** the user's instruction of 2026-10-09, "Continue as suggested" (after the orchestrator suggested batching the unscheduled scanner residuals into one cleanup task);
`docs/artifacts/security-review-poc-security-audit-code-v2.md` (SEV-1..SEV-6 and three pins, called T605 there);
`docs/artifacts/security-review-t609-template-label-v1.md` (T609-10..T609-13).
**Scopes:** `T611`.

## 1. Why now

The queue is empty. Every residual below is LOW, fails closed and was left unscheduled by decision, but they touch the same
files (`poc_scan.py`, `poc_audit_server.py`, their tests and contract v3) and can be fixed in one pass.

## 2. Sequence

1. **T611** (backend-developer, P2): implement, with gates and the full suite.
2. Orchestrator verification and probes; a Security Engineer reviews the change before merge (scanner code).
3. One root refresh afterwards only if the agent-text wording fix (T609-13) projects (it does: user approval needed).

## 3. Not in scope

The other plan-112 §2 notes, the held-out grep, the stale quote in one open golden case's brief.

## 4. Outcome (2026-10-09)

T611 is done (MR !544). Security Engineer: PASS with 5 LOW (`security-review-t611-scanner-residuals-v1.md`); the cheap items were fixed in one round. Tracked and unscheduled: T611-2 (altered path should not be flaggable; contract v5 delta), T611-3 (regex-library portability self-test), R-1. One user-approved root refresh follows for the 6 `poc-security-engineer` projections.
