# T784 — Re-grade SEC-T756-05 and SEC-T756-06 against the Node advisory

**ID:** T784
**Owner:** security-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-11
**Completed:** 2026-11-11
**Based on:**
- `docs/plans/plan-148-node-image-bump.md` (task T784; § Facts)
- The user's answer of 2026-11-11, verbatim: "Re-grade now, bump later (Recommended)"
- `docs/artifacts/tracked-debt-register-v12.md` (SEC-T756-05, -06); `docs/artifacts/security-review-t756-accepted-mediums-v1.md`

## 1. What and why

Re-grade SEC-T756-05 and SEC-T756-06 against the published advisory and Alpine 3.24.4's notes, as plan-148 § Task Decomposition item 1 specifies.

## 2. Output

The review text, returned to the orchestrator. The orchestrator commits it as `docs/artifacts/security-review-t784-node-advisory-v1.md`.

## 3. Constraints

- Read-only. Never read any `.env*` or credential file or the user's settings files.
- Never open `tests/golden/held-out/`.
- Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

- Every CVE in the advisory is mapped to reached or not reached, with the reason.
- Each id has a grade, with its reason.
- The bump ruling and T785's proof obligations are stated.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
