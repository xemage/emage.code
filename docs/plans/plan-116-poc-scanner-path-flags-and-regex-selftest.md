# plan-116 — Altered-path flags and the regex-library self-test (T611-2, T611-3)

**Created:** 2026-10-09
**Based on:** the user's instruction of 2026-10-09, "Continue with the next best step" (after the orchestrator suggested a small follow-up for the two remaining substantive scanner residuals);
`docs/artifacts/security-review-t611-scanner-residuals-v1.md` (T611-2, T611-3, R-1);
`docs/artifacts/poc-security-engineer-tool-scoping-v4.md` §12 (open residuals).
**Scopes:** `T612`.

## 1. Why now

The queue is empty. T611-2 is the most substantive open residual: a name that `safe_name` stripped or capped no longer equals
the real path, so the agent's "path in the modified-paths list" check can never void a flag on that file. T611-3 is an
availability gap: the bounded repeats of T611 may not compile on regex libraries with `RE_DUP_MAX` below 1024 (musl, some BSD),
which fails closed as `git_failed` on every scan without saying why.

## 2. Sequence

1. **T612** (backend-developer, P2): implement, gates, full suite.
2. Orchestrator verification and probes; a Security Engineer code-reviews it (scanner and flag semantics).
3. One user-approved root refresh afterwards (agent text projections).

## 3. Not in scope

R-1 (aperiodic-input cost; fails closed; documented), the plan-112 §2 parked notes, the held-out grep, the stale quote in one open golden case's brief.

## 4. Outcome (2026-10-09)

T612 is done (MR !546). Security Engineer: CONDITIONAL_PASS with one MEDIUM (non-UTF-8 names unmarked, reproduced) and four LOW, all fixed in one round (`security-review-t612-altered-paths-selftest-v1.md`). Open and unscheduled: R-1. One user-approved root refresh follows for the 12 declared projections.
