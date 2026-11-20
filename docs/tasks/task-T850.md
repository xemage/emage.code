# T850 — Security review of the Brave upstream report draft (T849)

**ID:** T850
**Owner:** security-engineer
**Status:** done
**Priority:** P2
**Tier:** judgment
**Depends on:** T849
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-172-batch-p-brave-upstream-report.md`
- The user's answer of 2026-11-19, verbatim: "P go"

## 1. What and why

Carry out plan-172 § Task Decomposition item 2.

## 2. Output

The text of `docs/artifacts/security-review-t850-brave-report-v1.md`. The orchestrator commits it.

## 3. Constraints

- Read-only.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.
- Token budget: 30k.

## 4. Acceptance criteria

- A verdict.
- A ruling on the accuracy of the finding, on disclosure and on the channel.

## 5. Blocker protocol

Report each blocker with its type and severity.
