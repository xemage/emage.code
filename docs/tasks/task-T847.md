# T847 — Security review of T846 (SEC-T837-01)

**ID:** T847
**Owner:** security-engineer
**Status:** done
**Priority:** P2
**Tier:** judgment
**Depends on:** T846
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-170-sec-t837-01-opencode-live-check.md`
- The user's answer of 2026-11-19, verbatim: "SEC-T837-01 go"

## 1. What and why

Review the T846 evidence against SEC-T837-01, as plan-170 § Task Decomposition item 2 describes.

## 2. Output

The text of `docs/artifacts/security-review-t847-opencode-live-v1.md`. The orchestrator commits it.

## 3. Constraints

- Read-only.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 40k.

## 4. Acceptance criteria

- A verdict: PASS, CONDITIONAL_PASS or FAIL.
- A status for SEC-T837-01.
- A decision for each of these "unverified" notes on live runs: SEC-T663-02, SEC-T837-03, SEC-T840-01 and SEC-T842-01.

## 5. Blocker protocol

Report each blocker with its type and severity.
