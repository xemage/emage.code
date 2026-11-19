# Security Review: T881, the CI lock fix for `opentelemetry-api` (T880)

## Metadata
- **Task:** T881 (plan-182 Addendum 2)
- **Reviewer:** security-engineer (read-only)
- **Date:** 2026-11-19
- **Tree:** worktree `agent-tech-lead-T869`, branch `agent/tech-lead/T869` at `34549b6f`. Commits `669728c1` (CI lock), `8c9b4c54` (checklist § 2 and § 5, test), `4c70536b` (PREREQUISITES).
- **Based on:** `docs/plans/plan-182-next-release.md` (Addendum 2), `docs/tasks/task-T881.md`, `docs/artifacts/mcp-pin-audit-next-v1.md` (C10), `docs/artifacts/release-next-audit-v1.md` (TL-T869-01), `docs/artifacts/security-review-t825-v11-prep-v1.md` and `security-review-t820-release-v11-v1.md` (SEC-T825-01 precedent)
- **User's words (verbatim):** "release plan go", "Approve (Recommended)", "v12.0.0, MAJOR (Recommended)". For SEC-T660-01 and SEC-T665-01: "Accept for v12.0.0 (Recommended)". LOW policy: "Track LOW items as debt, stop chasing (Recommended)".

## Scope
I read these files in the worktree:
- `ci/requirements-ci.in`
- `ci/requirements-ci.txt` (header lines 1-6; the `opentelemetry-api` entry at lines 423-426)
- `ci/requirements-release.txt`
- `docs/wiki/mcp-pin-bump-checklist.md` § 2
- `tests/functional/test_pin_bump_checklist.py` (`AUDITED_LOCKS`, `audit_scope_problems`, the new mutation test)
- `implementation/PREREQUISITES.md` line 4

I also read the npx pins in `implementation/knowledge/mcp/servers.yaml`. For comparison I read the develop copy of `ci/requirements-ci.txt`, where line 421 has `opentelemetry-api==1.45.1` and the cut-off is `2026-10-22T12:00:00Z`.

What I could not do (no shell, and the audit tools failed on the worktree path):
- I did not diff the commits.
- I did not run `pip-audit` myself. `run_pip_audit` returned a tool error on the worktree path.
- I did not fetch PyPI or npm metadata.

Every statement below that rests on those steps is marked **(unverified)**.

## Assessment

### 1. Grade of the finding: SEC-T881-01, SECURITY:LOW (A06). Fixed by T880.
- **The advisory.** Per the brief, CVE-2026-126360 / GHSA-mf5v-w3w3-f6cg is GitHub medium, CVSS 5.3, and affects availability only. It is fixed in 1.45.2. I did not trace the advisory text or the vulnerable code path **(unverified)**.
- **Who is exposed.** Only the `unit-tests` CI job, which installs `ci/requirements-ci.txt`. `opentelemetry-api` arrives as a transitive dependency (`# via mcp`). No user install path uses this lock: users get the runtime locks, which SEC-T825-01 / T824 already moved to 1.45.2.
- **The worst case.** A denial of service in a pipeline job: the job hangs or fails. An attacker would have to feed hostile input to the vulnerable code path inside the job. Nothing in the advisory class suggests code execution, so the Docker-socket binding of `unit-tests` does not raise the grade. A crash there cannot reach the socket.
- **Grade.** No confidentiality or integrity impact, CI-only reach, and a precondition that is unlikely to hold. That makes it LOW under the agent definitions, which matches T870's proposal. A MEDIUM would need at least a defence-in-depth gap with plausible reach. This finding has neither.
- **v11.0.0.** According to the brief, the v11.0.0 pipeline installed 1.45.1 **(unverified: I read no job log, by constraint)**. That affects only past pipeline runs. It ships nothing to users, so v11.0.0 users need no action.
- **Status.** Fixed in T880. The lock pins `opentelemetry-api==1.45.2` with hashes `2cbd7373…` (wheel) and `d7b0008e…` (sdist), which I read at lines 423-426. The orchestrator matched these against PyPI's JSON **(unverified by me)**, and the orchestrator's `pip-audit` run is clean **(unverified by me)**. The fix takes effect when the branch merges.

### 2. The lock change is sound, and the cooldown still holds.
- **Cut-off and age.**
  - The cut-off is `2026-10-30T00:00:00Z`, 20 days before the run on 2026-11-19. The rule needs at least 7 days, so it holds.
  - 1.45.2 was uploaded at 2026-10-29T17:29Z, before the cut-off, and is 21 days old. The new-package rule needs at least 14 days, so it holds.
  - The upload time comes from the orchestrator's PyPI check **(unverified by me)**.
- **Only one package moved.** `--upgrade-package` with the previous lock as the preference changes only the named package. That matches the orchestrator's diff finding (header plus one entry, two hashes). A newer `opentelemetry-api` could pull in new dependencies. The diff shows none, and `--require-hashes` would reject any unlisted package at install time anyway.
- **The other locks.** The gate and release locks keep `2026-10-22T12:00:00Z`, which is correct. `ci/requirements-release.txt` only reworded line 4. Its two entries are unchanged, and its `mdurl` hashes still equal those in the CI lock (read). `test_ci_hash_pins.py` enforces that the two locks stay equal. The reworded line is accurate ("moved to 2026-10-30 by T880 for opentelemetry-api only").
- **Residual (SEC-T881-02, LOW).** Header line 2 shows the `uv pip compile … --exclude-newer 2026-10-30T00:00:00Z` command as if it produced the whole lock. Run fresh, without the previous lock as the preference, that command could also pick up other packages published between 2026-10-22 and 2026-10-30. So line 2 alone does not reproduce the lock. Lines 3-6 and checklist § 2 explain the real procedure, which makes this a documentation precision issue and not a vulnerability. Tracked as debt.

### 3. A floor in `ci/requirements-ci.in` is not needed. No finding.
- The runtime floor of SEC-T825-01 exists because the documented runtime install is an unhashed `pip install -r requirements-mcp-server.txt`, which resolves loosely. The CI job installs only the hashed lock (`--require-hashes --only-binary=:all:`, as stated in the `.in` header and checklist § 2), so a floor in the `.in` file changes nothing that gets installed.
- The only thing a floor would add is protection against a future full regeneration picking a version below 1.45.2. With any cut-off after 2026-10-29, uv resolves the newest allowed version, and `pip-audit` now covers every CI lock (point 4), so a regression would be caught at the next audit.
- Adding `opentelemetry-api>=1.45.2` is optional hardening. Leaving it out is acceptable, and it does not need a debt row.

### 4. The other two edits are correct and not overstated.
- **Audit scope (checklist § 2).**
  - The item names all five locks and pins `pip-audit==2.10.1` with `--no-deps --disable-pip`, which is correct for a fully locked file. It requires a per-file record in § 5.
  - `audit_scope_problems` takes the union of a fixed list (both runtime locks and the three CI locks) and a glob of `ci/requirements-*.txt` on disk, so a future CI lock must also be named. The mutation test removes each CI lock name and expects a failure.
  - The test enforces the scope as written in the document. It does not prove that an audit was run; the per-file record in § 5 does that. The checklist does not claim more. "Enforced by a test" is accurate as long as it is read as "the documented scope is enforced".
  - The historical sentence (CI locks were not in the routine audit until 2026-11-19) is honest and correct.
- **The PREREQUISITES Node note (TL-T869-01).**
  - The general floor (Node 22, 24 or 26) is unchanged.
  - The exception for `@modelcontextprotocol/server-filesystem@2.4.0` (`engines.node >=24`) is worded as advice ("use Node 24 or 26 if you enable it").
  - The behaviour of `npx` on Node 22 is explicitly marked unverified. The parenthetical "npm only warns about `engines` unless `engine-strict` is set" matches npm's documented behaviour.
  - The list covers all eight npx pins in `servers.yaml`: gitlab, playwright, memory, sequential-thinking, brave, filesystem, supabase and toolradar. Nothing is missing.
  - The `engines` values themselves come from T880's `npm view` run **(unverified by me)**.
  - Nothing is overstated.

## Per-finding statuses
- **SEC-T881-01** (new): LOW, A06. Fixed by T880 and closes on merge. No user action. The v11.0.0 exposure was CI-only and in the past.
- **SEC-T881-02** (new): LOW, A08 (reproducibility of the lock record). Open, tracked as debt under the user's LOW policy.
- **SEC-T825-01** (existing): unchanged. Part (a), the runtime `.txt` floor, stays open as tracked-LOW. T880 does not touch it.

## Findings

| ID | Severity | OWASP | Location | Description | Remediation | Status |
|----|----------|-------|----------|-------------|-------------|--------|
| SEC-T881-01 | SECURITY:LOW | A06 | `ci/requirements-ci.txt:423-426` (develop: line 421) | `opentelemetry-api==1.45.1` (GHSA-mf5v-w3w3-f6cg / CVE-2026-126360, availability only, CVSS 5.3) was locked for the `unit-tests` job. The audit did not cover CI locks, so this survived the runtime fix | Lock 1.45.2 with its hashes (done in T880). Keep every `ci/requirements-*.txt` in the routine `pip-audit` scope (done, test-enforced) | Fixed in T880, closes on merge |
| SEC-T881-02 | SECURITY:LOW | A08 | `ci/requirements-ci.txt:2` | The `uv pip compile` command in the header, with cut-off 2026-10-30, does not reproduce the lock alone. Lines 4-6 show that other packages were held at the 2026-10-22 state through `--upgrade-package` from the previous lock | At the next full regeneration (which the checklist already schedules for when an input changes), run with one cut-off for all packages so line 2 becomes reproducible again. Until then lines 3-6 are the record | Open, tracked-LOW |

Code example for SEC-T881-02, the next full regeneration (maintainer-only, not an agent step):
```
# Before: line 2 lists the 10-30 cut-off, but most packages come from the 10-22 lock
# After: a single cut-off, at least 7 days before the run, every changed package at least 14 days old
uv pip compile ci/requirements-ci.in --universal --python-version 3.12 --generate-hashes --exclude-newer <run day minus 7 or more days>T00:00:00Z -o ci/requirements-ci.txt
uvx pip-audit==2.10.1 -r ci/requirements-ci.txt --no-deps --disable-pip
```

## OWASP coverage

| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | No (out of scope: no access-control code changed) | 0 |
| A02: Cryptographic Failures | Yes (lock hashes are sha256; hash values read) | 0 |
| A03: Injection | No (out of scope) | 0 |
| A04: Insecure Design | Yes (cooldown and age rule) | 0 |
| A05: Security Misconfiguration | Yes (Node floor note) | 0 |
| A06: Vulnerable Components | Yes | 1 (SEC-T881-01, fixed) |
| A07: Auth Failures | No (out of scope) | 0 |
| A08: Data Integrity Failures | Yes (hash lock, `--require-hashes`, reproducibility) | 1 (SEC-T881-02) |
| A09: Logging & Monitoring | No (out of scope) | 0 |
| A10: SSRF | No (out of scope) | 0 |

## Gate Verdict
**Gate:** security
**Verdict:** PASS

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 2 | 1 | 1 |

### Justification
- No finding is CRITICAL, HIGH or MEDIUM.
- No Immutable Security Constraint is breached. No required control is omitted or weakened: `--require-hashes --only-binary=:all:` and the cooldown rules are unchanged, and the audit scope got wider.
- SEC-T881-01 is fixed by T880.
- SEC-T881-02 is LOW and goes to the debt register under the user's LOW policy.
- Nothing goes to the user.

### Conditions
None. For the debt register: SEC-T881-02 (owner devops-engineer; next full regeneration of `ci/requirements-ci.txt`). The orchestrator records SEC-T881-01 as minted and fixed in the next register.

### Unverified points
- I made no diff of the three commits.
- I ran no `pip-audit` of my own (tool error on the worktree path).
- The PyPI hashes and upload time come from the orchestrator's check.
- The npm `engines` values come from T880.
- The vulnerable code path of the advisory is not traced.
- That the v11.0.0 CI installed 1.45.1 is not checked (no job logs, by constraint).
