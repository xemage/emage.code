# T839 — SEC-T837-03: Opencode agents no longer override the default read rules for .env

**ID:** T839
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-14
**Completed:** 2026-11-14
**Based on:**
- `docs/plans/plan-168-batch-j-opencode-permission.md` (§ Addendum 1)
- `docs/artifacts/security-review-t837-opencode-permission-v1.md` (SEC-T837-03)
- The user's words of 2026-11-14, verbatim: "SEC-T837-03: fix before root refresh." and "Once done do the root refresh"

## 1. What and why

As in plan-168 § Addendum 1.

## 2. Output

Commits on `agent/devops-engineer/T836`: `implementation/scripts/sync.mjs`, the regenerated agents and registry, tests, and documents.

## 3. Constraints

- Do not push, merge, tag or release.
- Do not edit the ledger, any brief's Status line or the plan.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

- No generated Opencode agent re-allows reading `*.env` or `*.env.*`.
- Every other allow and deny is unchanged.
- The tests fail if `read` is emitted again.

## 5. Blocker protocol

Report each blocker with its type and severity.
