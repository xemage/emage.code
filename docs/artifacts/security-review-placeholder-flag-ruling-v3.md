# Artifact: security-review-placeholder-flag-ruling-v3.md

> Immutable once produced; revisions bump `<N>`. Continues `security-review-placeholder-flag-ruling-v2.md`.

## Metadata

- **Reviewer**: security-engineer (read-only; no write tool). Recorded by the orchestrator from the reviewer's report.
- **Task**: T606 (plan-114). **Reviewed**: `placeholder-flag-ruling-v3.md`. **Date**: 2026-10-09.
- **Read**: v3, the v1/v2 reviews, `poc_scan.py:80-160` and `:255-345`, `poc-security-engineer.md`, `poc-orchestrator.md:40-114`.
  The `Before:` anchors of E-P1 (`poc-security-engineer.md:25`) and E-O1 (`poc-orchestrator.md:68`) each match once.
  Not read or run: the tests, `poc_audit_server.py`, the contract v2.

## Verdict: CONDITIONAL_PASS

0 critical, 0 high, 3 medium, 5 low. All nine v2 findings are resolved in substance; SEC-1 is not reintroduced. The new
findings are drafting gaps, not design flaws.

| ID | Grade | Concern | Fix (carried into the implementation task) |
|---|---|---|---|
| V3-1 | MEDIUM | An unresolved hit has no orchestrator route: the `blocked` task, stop-delegation, no-close and task-before-archival mechanisms attach to a "blocking finding", so the PoC can reach timebox, close or user silence with a FAIL verdict and no tracked item. | One sentence each in E-P1 and E-O1: for progression control an unresolved hit is treated as an open blocking finding (task `blocked`, no continue/demo/evaluate/close, a task "awaiting user: placeholder flag" before archival). Exposed-secret steps start only when the hit is classified real or the user declines. An unresolved hit left at timebox, escalation or close becomes an open blocking finding. |
| V3-2 | MEDIUM (Option A only) | E-S2's label is not limited to rules; `https://<real-token>:${PASS}@host` would be labelled non-blocking because only the password is judged. | Restrict `template-ref` and `bare-dollar-name` to `credential-assignment` and `unquoted-credential-assignment`. URL hits become ordinary unlabelled hits (or require the username to be an exact shape too). |
| V3-3 | MEDIUM | "Paths modified since `flag_commit`" is undefined for uncommitted state; a value swap in the working tree is missed by `flag_commit..HEAD`. | E-O1 defines the list as paths that differ from `flag_commit` in committed, staged and working-tree state plus untracked files, with deletions and renames. In E-P1, an unavailable or unstated list voids the flags. |
| V3-4 | LOW | The register schema is duplicated three times and has drifted (E-O1 omits `rule_id`, `path`, `hit_count`, `class`). | List all fields in E-O1 or point to one schema; add a text test. |
| V3-5 | LOW | "Looks like a placeholder" is undefined; a synthetic fixture password that authenticates nowhere cannot be flagged (fail closed, but a dead end). | State the criteria: real at once only for key material, a redacted path, a provider-token format without a user-stated example source, or a user decline; otherwise unresolved with a `user-attested` proposal. |
| V3-6 | LOW | Option A's implementation list is incomplete against E-S1's (contract v3, the hit-key pin at `test_poc_audit_server.py:374`, the server key allow-list, value extraction, the exact `<word>` regex). | Add them; pin the regexes (for example `<[a-z]+([ _-][a-z]+)+>`); add reverse-order and three-match tests. |
| V3-7 | LOW | `template-ref` hits have no grade or debt-handoff entry; the totals omit their count; the standing decision has no recorded place. | Grade `SECURITY:LOW` for debt handoff; add a template-ref count to the totals; record the user's quoted standing decision in the task brief or a decision note. |
| V3-8 | LOW | Blind-spot statements are inexact (E-P2 omits the URL-scheme clause; the Option A headline says the space skip is removed but E-S2 keeps it for the unquoted and URL rules; "blocks" for `bare-dollar-name` means unresolved; `dummy-word` is vacuous for `bearer-token`). | Correct each. |

## Conditions for CONDITIONAL_PASS (owner: solution-architect; deadline: before the implementation MR is merged)

- V3-1 and V3-3 are written into the E-P1 and E-O1 text with the sentences above.
- V3-2 is applied in E-S2 if Option A is chosen.
- V3-4..V3-8 are applied as listed.
- The Security Engineer reviews the final applied diff of E-P1, E-O1 and E-P2 (and the E-S2 code if Option A). That review is the gate, not a new ruling.

## Can the remainder ride without a v4? Yes

Only MEDIUM and LOW findings remain and every fix is a bounded text or spec addition with no open design choice. The
implementation brief must quote V3-1..V3-8 verbatim. The user's two answers do not depend on these fixes.

## Recommendation (reviewer)

- **Question 1: Option 1** (user confirms each flag, no code); Option 3 can follow later.
- **Question 2: Option A, with V3-2 applied and E-P2 applied now as the interim.** If the user does not want a standing exception to Constraint 1's strictness even for exact shapes, Option B. Option C only as the interim.
- Accepted prompt-level residuals: RA-1, RA-2, RA-3, RA-5, RA-8, RA-9. RA-7 (`${ABC}`, `<correct-horse-battery>` and `{{ lower }}` secrets hidden under Option A) is a real hostile-commit bypass the user must accept in plain words.
