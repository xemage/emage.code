# Security Review: T890 Batch X Fixes (T891)

Based on: plan-188-batch-x-round.md, task-T891.md, t891 evidence and diff (`git diff cb9961ae be9659dc`, branch `agent/devops-engineer/T890`, head `be9659dc`), security-review-t885-batch-v-v1.md (SEC-T885-04), security-review-t867-batch-x-text-v1.md (SEC-T867-01, -02), tech-lead-release-v12-v1.md (TL-T876-04), tech-lead-release-v10-v1.md and security-review-t860-batch-x-v1.md (TL-T761-11), security-review-t881-ci-lock-v1.md (SEC-T881-02), checkpoint-044-release-v12.0.0.md.
User words: "X go"; plan approval "Approve (Recommended)".
Scope of this review: read-only code and text review of the diff and the files it touches. The orchestrator did not re-run the clean-worktree suite for this text. I did not run `pip-audit`; the tool errored on the lock path.

## Summary
- **Risk Level**: LOW
- **Findings**: 0 CRITICAL, 0 HIGH, 0 MEDIUM, 3 LOW new (SEC-T891-01 to -03), plus SEC-T881-02 still open at LOW
- **Status**: PASS

## Per-id status

| Id | Status | Basis |
|----|--------|-------|
| SEC-T885-04 | fixed | `ca_job_pairing_problems()` loads the YAML with `yaml.safe_load` and compares the `image` of `main-develop-drift-gate` with that of `ca-chain-check-python`. It also compares the ordered list of `openssl...` tokens found on `apk add` lines in each job's `before_script`. Current CI: both images are `python:3.12-alpine@sha256:e064671c...`; the `openssl~=3.5` constraint is in both jobs. The drift gate's line is wrapped by `run-allowlisted.py -- apk add ...`; the regex `openssl[^\s'"]*` still finds `openssl~=3.5`. Bypass review: see below. Five mutation subTests are present. |
| SEC-T867-01 | fixed | `--min-age-days` uses `min_age_days()`, which refuses values below `MIN_AGE_DAYS` (7) through argparse (exit 2). It builds on `non_negative_int`, which accepts only `\d{1,4}`, so a negative, signed, empty or oversized value is refused (and there is no timedelta overflow). argparse prefix abbreviations (`--min-age`) resolve to the same action and the same type. There is no environment variable and no config file for this option. `-h` only prints help. Only a programmatic `Namespace(min_age_days=0)` could bypass it, and that is code, not an operator path. The checklist sentence and its command (`age` with up to two `--allow-young PKG@VER:reason`) stay correct, and the test now requires the phrase "the option may only raise it". Residual, unchanged by this fix: a trivial `--allow-young` reason is accepted. The checklist gates it by process (merge request record of provenance, audit, diff review). Not a regression. |
| SEC-T867-02 | fixed | Age is `now_utc - published_utc >= timedelta(days=N)` with both instants aware UTC (the publication regex requires `Z` or an offset, so `fromisoformat` returns an aware time; `astimezone(utc)` normalises it). The offset stamp case is tested. Exact 7 days passes; 6 days 23:59:59 is young (the old calendar-day difference would have said 7). There are no leap-second or DST effects in UTC arithmetic. A future publication date gives a negative difference, so it is young (fail closed), see SEC-T891-02. Duplicate refusal: the key is `(package, version)` taken from `NPM_PIN`, with exact-case comparison. A different-case spelling is not in the current-pin set and is refused as "not a current npm pin"; padded whitespace fails `NPM_PIN.match` or the pin set, so it is refused too. A true duplicate raises `AuditError` (exit 2). I found no new fail-open. The publication time is printed in UTC. |
| TL-T876-04 | fixed | Folded into SEC-T867-02: exact instant, UTC print, fixed `now` in tests (`AGE_NOW`). |
| TL-T761-11 | fixed (documentation) | The note in `CONTRIBUTING.md` and the comment in `scripts/publish-release.py` match the checklist's § 3 text and the repo's behaviour: with `FF_GIT_URLS_WITHOUT_TOKENS` on, the `release` fetch has no credential because `CI_JOB_TOKEN` is withheld. It works while the project is public and fails closed if not. It tells the reader not to widen the allowlist and to re-open A-21. The facts about the runner flag are not observed live; A-21 is closed on the user's report that the flag is absent from the runner config (checklist). The comment-only change cannot alter behaviour (the diff shows two added comment lines above `run_git`). |
| SEC-T881-02 | open (not fixed, by design) | No lock or header change, as planned. The original description (fresh compile could pick up other packages from 2026-10-22 to 2026-10-30) is confirmed. |

### SEC-T885-04 bypass review

- YAML anchors and merge keys (`<<`): `safe_load` resolves them, so the resolved values are compared.
- `extends`: not resolved by the function. A job using `extends` for the image has no `image` key of its own. For `ca-chain-check-python` the `not mr.get("image")` test refuses; if only the gate used `extends`, the images differ and it is refused. Fail closed.
- `image:` as a mapping with `name:`: the two values are compared as whole objects, so any difference (including an `entrypoint`) is refused, and equal mappings pass. Correct.
- Different `apk add` spelling (`apk --no-cache add`) or an `apk add` moved to `script`: `openssl` list empty on one side, so refused. Fail closed, though it also refuses harmless moves.
- A second `apk add` line, or a second package group on one line: all tokens are collected in order and compared as lists, so an extra, differently pinned or unpinned `openssl` token makes the lists differ. Refused.
- Nested list entries (non-string) in `before_script` are skipped; if that empties one side it is refused.
- The check proves equality only. It does not prove the pinned digest is the intended one, and it does not look at the `git~=` constraint (see SEC-T891-01).

## New findings

| Id | Severity | Category | Location | Description | Remediation |
|----|----------|----------|----------|-------------|-------------|
| SEC-T891-01 | SECURITY:LOW | A04 / A05 | `tests/functional/test_ci_hash_pins.py` `ca_job_pairing_problems` | The pairing check covers only the image and the `openssl` constraint, and only in `before_script`. The `git~=` constraint and the other tags/variables of the two jobs are not paired. Structural changes fail closed, so it is a coverage gap, not a bypass. | Extend the helper to compare the whole ordered `apk add` argument list of both jobs (after dropping the wrapper). Track as debt. |
| SEC-T891-02 | SECURITY:LOW | A08 | `scripts/audit-mcp-pins.py` `command_age` | A publication time in the future is treated as "young" and printed as a negative day count. It fails closed, but an `--allow-young` exception would let an anomalous timestamp through silently. | Treat `published > now` as an `AuditError` (exit 2). Track as debt. |
| SEC-T891-03 | SECURITY:LOW | A08 | `ci/requirements-ci.txt:2-6` (restates SEC-T881-02 with the count) | Six pins differ between the committed lock and a fresh compile with the header command (see below). The agent's count of 7 does not match the two pin lists. | See the recommendation below. Track together with SEC-T881-02. |

Test and scope review: no assertion on the 7-day default or on exit 1 for a young pin was removed. The replaced lines (6-day boundary pair, `--min-age-days 6` exit 0) tested the behaviour that SEC-T867-01 and -02 deliberately remove. They are replaced by a stricter exact-instant boundary, a refusal test (0, 1, 6 give exit 2), a duplicate test and a mutation test covering floor, duplicate and calendar-day difference. The checklist test gains one required phrase. The diff is limited to `CONTRIBUTING.md`, `docs/wiki/mcp-pin-bump-checklist.md`, `scripts/audit-mcp-pins.py`, `scripts/publish-release.py` (comments only) and three test files. `.gitlab-ci.yml`, `ci/`, the lock, images and pins are untouched (per the evidence file). Nothing outside the stated scope.

## SEC-T881-02: count and recommendation

Count from the two pin files (`committed.pins` against `fresh.pins`, 38 lines each, same package set): **6** differ.

| Package | Committed | Fresh |
|---------|-----------|-------|
| certifi | 2026.10.19 | 2026.10.23 |
| pycparser | 3.11 | 3.12 |
| pydantic | 2.14.1 | 2.14.2 |
| pydantic-core | 2.50.1 | 2.50.2 |
| sse-starlette | 3.5.0 | 3.6.0 |
| starlette | 1.9.0 | 1.10.0 |

The agent's figure of 7 is not reproducible from these two files; the orchestrator's 6 stands. The package set is the same, so the difference is versions only.

Supply-chain assessment: all six fresh versions were published between the older 2026-10-22 cut-off and the 2026-10-30 cut-off, so on 2026-11-20 they are about 21 to 29 days old and already meet the 14-day rule. The committed pins are older, were reviewed at their own regeneration, and were not touched by T880 except the single targeted `--upgrade-package`. Keeping the committed pins therefore carries no new supply-chain exposure. Regenerating would move six packages (including `certifi`, whose newer root list matters for TLS trust, and `starlette`/`pydantic`, which are network-facing) and would be a lock change that needs the checklist's review: 14-day age, provenance where available, advisory audit with hashes, diff read.

Recommendation: **keep lines 3-6 of the lock header as the record** and change nothing now. The header states honestly that line 2 alone does not reproduce the lock, and the risk is documentation precision, not a vulnerability. Do the one-cut-off regeneration at the next scheduled full regeneration, with the checklist's 14-day review, and run the advisory audit on the result before adopting it. Regenerate sooner only if an advisory names one of the six committed pins. This is advice only; I recommend no lock change without that review.

## Verdict

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 4 (SEC-T881-02, SEC-T891-01, -02, -03) | 0 | 4 |

### Justification
SEC-T885-04, SEC-T867-01, SEC-T867-02, TL-T876-04 and TL-T761-11 are fixed as described. No weakened test, no out-of-scope change, no Immutable Security Constraint breach, no required control removed or weakened. Only LOW items remain and each is tracked as technical debt; none is a merge blocker. PASS is subject to the clean-worktree suite passing at the merge commit (not run by this review).

### Conditions
None (no CONDITIONAL_PASS).

### Blockers
None.

## What stays open (tracked LOW debt)
- SEC-T881-02 and SEC-T891-03: lock header reproducibility; owner devops-engineer; next full regeneration of `ci/requirements-ci.txt` with the checklist's 14-day review. Not fixed by design in plan-188.
- SEC-T891-01: pair the whole `apk add` argument list in the CI test; owner devops-engineer.
- SEC-T891-02: refuse a publication time in the future in `command_age`; owner devops-engineer.
- Unchanged residual: a trivial `--allow-young` reason is accepted; mitigated by the checklist's merge-request record.
- The `FF_GIT_URLS_WITHOUT_TOKENS` behaviour is documented, not observed live (A-21 closed on the user's report).

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes | 0 |
| A02: Cryptographic Failures | Yes (CA/openssl pairing) | 0 |
| A03: Injection | Yes (argparse inputs, regex) | 0 |
| A04: Insecure Design | Yes | 1 (SEC-T891-01) |
| A05: Security Misconfiguration | Yes | 0 (SEC-T891-01 also touches it) |
| A06: Vulnerable Components | Yes (lock comparison; `pip-audit` not run) | 0 |
| A07: Auth Failures | Yes (release fetch credential note) | 0 |
| A08: Data Integrity Failures | Yes | 2 (SEC-T891-02, -03) plus open SEC-T881-02 |
| A09: Logging & Monitoring | Yes (UTC print) | 0 |
| A10: SSRF | Yes (not applicable) | 0 |

## Compliance Checklist
- [x] OWASP Top 10 reviewed
- [x] Authentication secure (no credential widening)
- [x] Authorization enforced (no change)
- [x] Input validation complete (`--min-age-days`, `--allow-young`)
- [x] Secrets management verified (none read or added)
- [ ] Dependencies audited (comparison only; `pip-audit` errored)
- [x] Security headers configured (not applicable)
- [x] Logging appropriate

## Addendum — orchestrator notes (2026-11-20)

- **The pin count.** T890 reported 7 differing pins. The orchestrator's `diff` of `committed.pins` and `fresh.pins` shows 6, and T891 confirms it. The six are certifi, pycparser, pydantic, pydantic-core, sse-starlette and starlette.
- **The ages in the supply-chain assessment** (21 to 29 days on 2026-11-20) are the reviewer's own arithmetic from the cut-off dates, not a measured publication time **(unverified)**. They do not change the recommendation, which makes no lock change without the checklist's review.
- **The user decides SEC-T881-02:** keep header lines 3-6 as the record (T891's recommendation), or a full regeneration with the 14-day review.
