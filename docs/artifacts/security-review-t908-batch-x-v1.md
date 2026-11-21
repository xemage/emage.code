# Security Review: T908 batch X (plan-199, SEC-T897-01 fix)

Based on: docs/plans/plan-199-batch-x-sec-t897-01.md; docs/artifacts/security-review-t897-batch-x-v1.md (row SEC-T897-01); diff of commit 069c8f14 on agent/devops-engineer/T908 (scratchpad t908.diff); the worktree files tests/functional/test_ci_hash_pins.py, .gitlab-ci.yml (ca-chain-check-python lines 169-187, main-develop-drift-gate lines 308-332) and scripts/audit-mcp-pins.py lines 535-618.
Reviewer: security-engineer, read-only. Nothing was executed (no shell). Statements marked \"(reasoned, not run)\" are read from the code; the engineer's run results (141 tests OK, 7 of 8 new cases fail on old code) were not re-run by me. The full suite and the pipeline are outside this review.
Scope: tests/functional/test_ci_hash_pins.py and docs/wiki/mcp-pin-bump-checklist.md only. No job, digest or pin change (confirmed from the diff).

## Per-id status

| Id | Status | Basis |
|----|--------|-------|
| SEC-T897-01 (apk pairing ignored non-`apk add` forms) | Fixed | `apk_adds` now looks at every before_script and script line whose raw text has the token `apk`. A line counts as a normal add only if its unwrapped words begin `apk add`, contain no later `apk` word, no word has a shell metacharacter, and no spaced word re-splits to contain `apk`. Everything else is returned as a stray and fails the pairing check (fail closed). Option before add, `env`/`command` prefix, `sh -c`, `;`/`&&` chains, `/sbin/apk`, `busybox apk`, here-docs and multi-line items are all refused (reasoned, not run). Two-space and tab forms parse to a plain `apk add` and are counted as one, which is equivalent. Residual forms are tracked as SEC-T909-01 (LOW). |
| SEC-T891-02 checklist wording | Fixed | The new sentence \"`--allow-young` cannot override the refusal of a future time\" is true: audit-mcp-pins.py:555-557 raises AuditError before `allowed` is read; :613-615 returns exit 2. |

## Answers to the review points

1. Closure of the listed forms: all closed (see the status row). Forms still missed are in SEC-T909-01: a quote-split token such as `ap\"\"k add x` (the raw-text gate finds no `apk`, `continue` skips the line, and it never reaches the words check); the command held in a variable (`variables: PM: apk` and `$PM add x`, which contains no `apk` token on the install line); and `after_script` (not scanned; also not scanned before). An install through `pip`/`npm` is outside the apk-pairing claim.
2. False positives: none on today's file, since the only matching line in each job is the one standard add line. Possible plausible future refusal: a version constraint written with a comparison operator, for example `'git>=2.54'` (valid apk syntax), has `>` in a word and is refused as a stray, although it is a pure pairing edit. The message does not say why, so a maintainer may be tempted to loosen the character set or the check. See SEC-T909-02. `$` in a package word is also refused, which is the right default.
3. No existing assertion weakened or dropped. The `not a or a != b` condition and its message are unchanged; the new check is an additional problem entry. The 13 original cases remain; eight are added.
4. Checklist sentence: true against scripts/audit-mcp-pins.py (see the status row).
5. Nothing else changed: two files in the diff; in the checklist only line 10 differs.

## New findings

| Id | Severity | OWASP | Location | Finding | Remediation |
|----|----------|-------|----------|---------|-------------|
| SEC-T909-01 | SECURITY:LOW | A08 Data Integrity Failures (CI pipeline integrity) | tests/functional/test_ci_hash_pins.py `apk_adds` (line 1485 raw-text gate); `before_script`/`script` only | The raw-text test `\\bapk\\b` runs before shlex parsing, so a quote- or escape-split token (`ap\"\"k add x`, `a\\pk add x`) is skipped entirely, and an install through a variable naming the program is not seen. `after_script` is not scanned. No current exposure: nothing uses these forms and both jobs are equal. | Test the parsed words as well as the raw text: strays if any word, after shlex, equals or ends with `/apk` or contains `apk`; or refuse any quote, backslash or `$` outside the standard add line. Also scan `after_script` or add a case that the jobs have none. Add one mutation case for `ap\"\"k add x`. |
| SEC-T909-02 | SECURITY:LOW | A08 (maintainability of the control) | tests/functional/test_ci_hash_pins.py line 1493 (`[;&\\|\\`$()<>\
]`) | `<` and `>` in a word refuse a legitimate constraint such as `'git>=2.54'` as a stray, with a message that names only \"not exactly an `apk add` line\". A maintainer may weaken the check to get the bump through. | Drop `<` and `>` from the character set (they are inert inside a quoted word), or say in the message and the docstring which characters are refused. Add a case that `'git>=2.54'` in both jobs is accepted. |

## Verdict

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 2 (SEC-T909-01, SEC-T909-02) | 0 | 2 (tracked as technical debt) |

### Justification
SEC-T897-01 is fixed for every listed form and several more; the current CI file still passes; no assertion was weakened; the checklist sentence is true; nothing else changed. The two remaining findings are LOW with no current exposure and are tracked as technical debt in the next register. No Immutable Security Constraint is breached and no required control is weakened.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01-A05, A07, A09, A10 | No (not in scope of this diff) | 0 |
| A06: Vulnerable Components | Yes (age-check wording only) | 0 |
| A08: Data Integrity Failures | Yes | 2 (LOW) |

## What stays open
- SEC-T909-01 and SEC-T909-02 (LOW, new).
- SEC-T881-02 and SEC-T756-02: out of scope, unchanged.
- Pending outside my review: the full clean-worktree suite, the pipeline and the merge.

## Orchestrator addendum (2026-11-21)

- Verdict stands: PASS. Both new findings are LOW and are tracked as debt under the user's LOW policy; they go to register v34 in batch X (SEC-T909-01, SEC-T909-02).
- The engineer ran the old-versus-new check on a copy (7 of the 8 new cases fail on the old code; the semicolon chain was already refused). I read the diff, ran the two test files (141 tests OK) and the ledger, link-integrity and release-document gates. The full suite on the pushed head is recorded in the merge request.
- The reviewer's row named the checklist sentence under SEC-T891-02; the wording gap belongs to SEC-T897-01 (register v31). The register keeps SEC-T897-01 as the id.
