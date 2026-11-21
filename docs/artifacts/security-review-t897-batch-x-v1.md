# Security Review: T897 batch X small round (T896 fixes for SEC-T891-01 and SEC-T891-02)

Based on: docs/artifacts/security-review-t891-batch-x-v1.md (rows SEC-T891-01, SEC-T891-02, SEC-T885-04 bypass review); docs/plans/plan-192-batch-x-small-round.md; docs/tasks/task-T897.md; branch agent/devops-engineer/T896 head 887b6bcc (= plan 7fac9ed2 + 44da9174 + 887b6bcc), diff `git diff 7fac9ed2 887b6bcc`; the T896 head tree and the orchestrator's evidence note t897-evidence.md.
Reviewer: security-engineer, read-only. Nothing was executed (no shell). Statements marked "(reasoned, not run)" are read from the code; the agent's own run results were not re-run by me.
Scope: four files only (scripts/audit-mcp-pins.py, docs/wiki/mcp-pin-bump-checklist.md, tests/functional/test_audit_mcp_pins_hardening.py, tests/functional/test_ci_hash_pins.py). .gitlab-ci.yml and ci/ are unchanged (orchestrator evidence). SEC-T756-02 and SEC-T881-02 ("Keep the lock") are out of scope and untouched.

## Per-id status

| Id | Status | Basis |
|----|--------|-------|
| SEC-T891-01 (the pairing check compared only the openssl tokens) | Fixed for the stated gap; a residue in matching form is tracked as SEC-T897-01 (LOW) | `ca_job_pairing_problems` now compares the whole ordered `apk add` argument list of every matching line in `before_script` then `script`, wrapper dropped by `unwrapped()`. Both jobs hold `apk add --no-cache 'openssl~=3.5' 'git~=2.54'` today (ca-chain-check-python .gitlab-ci.yml:172, drift gate :321 through run-allowlisted). Changed package constraint, added or dropped package, a different option or `--repository`, and a reordering all make the lists differ (reasoned, not run; the agent reports eight mutation cases refused, plus the old openssl case kept). |
| SEC-T891-02 (a future publication time counted as "young", so `--allow-young` could hide it) | Fixed | `command_age` raises AuditError when `published_utc > now`, before the age line and before the allowance is consulted, so an exception cannot cover it. Exactly `now` is still age 0, rc 1 "YOUNG", unchanged. Checklist sentence matches the code. |

## Answers to the specific questions

1. SEC-T891-01 bypass analysis (all reasoned, not run).
   - Second `apk add` line in one job only: caught if it has the form `apk add ...` (after unwrapping), because the list of lists then differs in length. Fail-closed.
   - A job with no `apk add` on one side, or on both: `not a or a != b` gives a problem. Fail-closed.
   - A different `--repository` option, a different package, a different constraint, a reorder: all caught (whole ordered list is compared, options included).
   - Not caught (SEC-T897-01): the selector is `"apk add" in line and words[:2] == ["apk","add"]`. A line that does not start with exactly `apk add` is silently ignored, so an extra install in one job escapes in these forms: `apk --no-cache add pkg` (options before `add`; the substring test fails too), `apk  add` (two spaces), `env X=1 apk add pkg`, `sh -c 'apk add pkg'` (also under the run-allowlisted wrapper, because only the wrapper is stripped), `command apk add`, and a `;` or `&&` chain with `apk add` in a later position. If both jobs use such a form for the same install, the lists are both empty and `not a` fires, which is fail-closed; the hole is only the extra, one-sided install in a non-matching form while the standard `apk add` line stays equal.
   - A package given by a variable: `$PKGS` is compared as a literal word, so two jobs with the same literal pass even if each job's `variables:` gives it a different value. Today nothing uses a variable.
   - `image:` mapping form: the whole value is compared with `!=`, so a mapping with a different `name`, `entrypoint` or `docker` options differs from a string form. Fail-closed. A job taking its image through `extends` or `default` is read as raw YAML by the test helper and would be flagged as missing (fail-closed).
   - Residual: position of the `apk add` relative to the store copy and the check lines is not compared, and a line moved between `before_script` and `script` still passes because the two fields are concatenated. LOW.
2. SEC-T891-02.
   - Correct and fail-closed: strict `>` against the UTC `now`; `published_utc` is converted from any offset (the regex requires `Z` or an explicit offset, so no naive time reaches the comparison); a negative age can no longer be printed (before, `.days` of a negative delta printed a misleading age).
   - Clock skew: the publication time is set by the registry. A runner clock lagging by seconds would see a version published a few seconds ago as in the future. Such a pin is minutes old, so it would already be refused as young; the new outcome is exit 2 instead of exit 1, both blocking. No realistic case is newly blocked.
   - Refusing even with `--allow-young` is the right call: an exception exists for a known-young pin and must not mask an impossible timestamp. Time zones are handled by the UTC conversion.
   - The two recorded exceptions (server-filesystem 2.4.0 published 2026-11-18, brave 2.1.5 published 2026-11-17) are days in the past on 2026-11-21, so the documented fixed command in § 1 is not blocked by this check.
   - Exactly `now`: `>` not `>=`, so age 0 and "YOUNG" as before; the test pins this and a mutation to `>=` is detected.
   - Exit code: AuditError is the existing path for a missing or unparseable time and I take it to map to exit 2 as documented; I did not re-read the handler, so this is unconfirmed.
3. Checklist § 1 sentence ("a missing or unparseable publication time, or one later than now, is an error, exit 2, never 'old enough' and never 'young' (SEC-T891-02)") is accurate against the code. Observation only: it does not say that `--allow-young` cannot override it; the code and test do, so this is a wording gap, not an error.
4. Tests and scope. No assertion was dropped or weakened. The old "drift gate without openssl" case stays and eight cases are added (git constraint, extra package, dropped package, reorder, each for both jobs). The age test covers two future stamps with and without `--allow-young`, exact `now`, and two mutations (check removed, `>` changed to `>=`) that fail it. No test covers the SEC-T897-01 forms (no test documents the gap). The diff is limited to the four stated files.

## New findings

| Id | Severity | OWASP | Location | Finding | Remediation |
|----|----------|-------|----------|---------|-------------|
| SEC-T897-01 | SECURITY:LOW | A08 Data Integrity Failures (CI pipeline integrity) | tests/functional/test_ci_hash_pins.py, `ca_job_pairing_problems` / `apk_adds` (line ~1477-1480) | The pairing check recognises only lines whose words start with `apk add`; an extra install in `apk --no-cache add`, `sh -c`, `env`, or multi-space form in one job only is ignored. Today both jobs are equal and nothing uses these forms, so no current exposure; the control is weaker than its docstring claims against a deliberate or careless edit. | Select every line whose unwrapped words, or the `sh -c` payload re-split with shlex, contain the token `apk`, and treat any such line that is not exactly `apk add ...` as a problem (fail closed), or compare all lines after the first `apk` token. Add one mutation case each for `apk --no-cache add x` and `sh -c 'apk add x'` in one job. Code sketch: `words = unwrapped(line); if "apk" in words or "apk add" in line: collect, and flag if words[:2] != ["apk","add"]`. |

No other new findings. Grade of SEC-T891-01 was and stays at its earlier grade; the residue is carried by SEC-T897-01 (LOW).

## Verdict

## VERDICT: PASS

| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 1 (SEC-T897-01) | 0 | 1 (tracked as technical debt) |

Justification: SEC-T891-02 is fixed. SEC-T891-01 closes the stated gap (every package and option now compared, ordered, fail-closed when a side has none). The remaining non-matching-form hole is LOW, with no current exposure, and is tracked as technical debt; no Immutable Security Constraint is breached and no required control is weakened. Pass condition: the LOW is recorded in the next tracked-debt register (batch X remainder).

OWASP coverage: A08 reviewed (1 finding, LOW); A06 reviewed (age check, 0 findings); A01-A05, A07, A09, A10 not in scope of this diff (0 findings).

## What stays open
- SEC-T897-01 (LOW, new): non-`apk add` forms ignored by the pairing check.
- SEC-T756-02 and SEC-T881-02: out of scope, unchanged (the user kept the lock).
- Pending outside my review: the full clean-worktree suite the orchestrator is running; the merge and the live CI results are not covered by this review.

## Addendum — the orchestrator's check (2026-11-21)

- **The exit code.** The reviewer could not confirm that an `AuditError` ends in exit 2. `scripts/audit-mcp-pins.py:613-615` (`except AuditError` prints `error: ...` and returns 2) confirms it, so a publication time in the future is exit 2.
- **The checklist wording.** The reviewer notes that § 1 does not say `--allow-young` cannot override the refusal. The code and the test do. This is a wording gap only; it is tracked with SEC-T897-01 rather than edited here.
