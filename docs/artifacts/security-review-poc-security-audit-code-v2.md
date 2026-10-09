# Artifact: security-review-poc-security-audit-code-v2.md

> Immutable once produced; revisions bump `<N>`. Continues `security-review-poc-security-audit-code-v1.md`.

## Metadata

- **Reviewer**: security-engineer (read-only; read the code, ran nothing). The orchestrator recorded this from the
  reviewer's report, because the agent has no write tool.
- **Task**: T604 (plan-113), commit `dc87cf3`. A review of the tuned unquoted-credential rule, the untracked-name check,
  the fixes for L-1, L-2 and L-7, and the extra token formats.
- **Date**: 2026-10-09
- **User decision under review**: "Add it, tuned (Recommended)".

## Verdict: PASS

0 critical, 0 high, 0 medium, 6 low. **Condition C-1 (the unquoted `KEY=value` rule gap) is closed**, and so are L-1,
L-2 and L-7. No Immutable Security Constraint is breached, and no required control is removed or weakened.

## Findings (all `SECURITY:LOW`, tracked as technical debt)

| ID | Concerns | Orchestrator note |
|---|---|---|
| SEV-1 | Quadratic cost on keyword-dense and `eyJ`-dense single lines. Fails closed on the 60 s deadline (`timeout`, `complete: false`). | **Measured by the orchestrator:** `"password" × 100000` and `"eyJ" × 266000` each take the full 60 s and report `timeout`, never a silent pass. An 800 KB line of `a` takes 0.2 s. Only adversarial input triggers it. |
| SEV-2 | The Python name loop in `_name_scan` is not bound by the deadline (a multi-second stall at roughly 2M names). | |
| SEV-3 | Allowlisted file names are returned verbatim, so a hostile name becomes text in the reviewing agent's context (pre-existing). Strip control characters and cap the length. | |
| SEV-4 | The name-exclusion suffix match has no word boundary (`SECRET_PROFILE=` is excluded by accident). Require the ending to follow `_` or `-`. | |
| SEV-5 | False positives on type annotations and docs (`password: Optional[str]`, `args.password`). Document and pin them. | |
| SEV-6 | JWT test fixtures (the jwt.io sample) are flagged, and an unsigned token matches. | |

## Decisions recorded

- **`MAX_TOKENS=100000000`** (found by the orchestrator, an all-digit value under a name that contains "token") is a
  known false positive. The reviewer recommends against both a "not all digits" condition (it would miss
  `DB_PASSWORD=12345678` and numeric PoC defaults) and adding `tokens` to the excluded endings (`API_TOKENS=<a>,<b>` is
  a plausible real secret list). It is documented and pinned instead.
- **The `{0,31}` URL-scheme bound is sound.** The only realistic miss is a `://` preceded by 32 or more characters that
  are all digits, `+`, `.` or `-`. Upper-case schemes were never matched.
- **L-2's edge** (an empty `.git` directory that is not a repository gives `git_failed`) is acceptable.
- No regressions against F-1..F-7.

## Items to track (T605, not yet scheduled)

SEV-1..SEV-6 plus the three missing pins (`MAX_TOKENS`, `SECRET_FILE`, the type-annotation class). They are low
priority and fail closed. They need no decision from the user. Schedule T605 when convenient.
