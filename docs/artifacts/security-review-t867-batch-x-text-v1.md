# Security review T867: batch X text items and SEC-T862-02 (T866)

## Metadata
- **Task:** T867 (plan-180), security-engineer, read-only
- **Date:** 2026-11-19
- **Reviewed tree:** worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T866`, branch `agent/devops-engineer/T866`, commits `611c55b6` (a), `84e14c21` (b), `6f445234` (c), on `39d74f32`
- **Based on:** `docs/plans/plan-180-batch-x-text-and-sec-t862-02.md`, `docs/tasks/task-T867.md`, `docs/artifacts/security-review-t860-batch-x-v1.md`, `docs/artifacts/security-review-t862-batch-ab-v1.md`, `docs/artifacts/security-review-t852-brave-2-1-5-v1.md`, `docs/artifacts/mcp-agent-denials-evidence-v4.md`
- **User decision (verbatim):** "X + SEC-T862-02 go"
- **LOW policy (verbatim):** "Track LOW items as debt, stop chasing (Recommended)"
- **Gate:** security
- **Budget:** 35k tokens. Because of it, I could not read every changed file in full; I mark those parts **(unverified)**.

## Scope
**Read in full (worktree):**
- `scripts/audit-mcp-pins.py`: lines 60-99 and 196-218, plus the whole new `age` code at lines 485-590.
- `docs/wiki/mcp-pin-bump-checklist.md`: §§ 1, 3 and 5.

**Checked against the vendor docs:**
- https://docs.gitlab.com/runner/commands/, for `gitlab-runner lint` and `gitlab-runner restart`.

**Not read (unverified):**
- the diffs of `tests/functional/test_audit_mcp_pins_hardening.py`, `tests/functional/test_mcp_agent_denials.py` and `tests/functional/test_pin_bump_checklist.py`;
- the diff of `docs/wiki/mcp-servers.md`;
- the input artifacts T852, T860 and T862, and the evidence v4. I rely on the brief's summary of them.

**Taken from the orchestrator's runs, not re-run by me (no shell):**
- `age` without exceptions exits 1.
- With both exceptions it exits 0.
- With `left-pad@1.3.0` it exits 2.
- The gates pass and the drift is `[]`.

## Assessment

### 1. SEC-T860-01: minimum release age

**The `age` subcommand is sound.**
- **It fails closed** (`published_on`, lines 509-521). A non-zero `npm view` exit is an error. So is a missing entry for the pinned version, a non-string value, a timestamp that does not fit the strict ISO-8601 pattern, and a `fromisoformat` failure. Each raises `AuditError`, which exits 2.
  - `main()` turns any unexpected exception into exit 2 too.
  - A publication time in the future gives a negative age, which counts as YOUNG and exits 1.
  - So no doubt ever yields "old enough".
- **It reuses the hardened `run_npm`.** That is the default runner (line 534). It runs with:
  - an empty user and global `.npmrc`;
  - a fixed `--registry https://registry.npmjs.org/`;
  - `clean_env`, which drops names that look like secrets;
  - `shell=False` and a timeout;
  - a fresh `TemporaryDirectory` as cwd.

  `npm view … time --json` runs no package script.
- **It refuses an exception for a version that is not pinned.** `check_allowances` (lines 524-531) raises `AuditError` (exit 2) unless the exception's `package@version` is a current npm pin. A bump therefore voids the exception.
- **It requires a reason.** `parse_allow_young` (lines 494-500):
  - requires the `:` separator;
  - requires a valid `NPM_PIN` spec;
  - requires a non-empty reason, and refuses one that matches `UNSAFE_TEXT_RE`;
  - prints the reason through `safe_text`.
- **Minor points (SEC-T867-01, SEC-T867-02):**
  - `--min-age-days` accepts 0-9999, so the floor can be lowered without a recorded reason.
  - The age is a difference of UTC calendar days, so "7 days" can mean a little over 6 × 24 h.
  - A second `--allow-young` for the same pin silently replaces the first. That is harmless, because both name the same pin.
  - An exception that is no longer needed is printed as "(ok; --allow-young not needed)". That keeps a stale entry visible, which is good.

**The 7-day rule with exceptions recorded in the MR is adequate** as a supply-chain cooldown for stdio `npx` pins.
- It matches the lock cooldowns of § 2: 7 days for `--exclude-newer`, and 14 days for a new CI package.
- The three-part exception record (provenance, audit, diff review) is the right content.
- Provenance proves the build origin, not that the source is clean, so the diff read is the part that matters. The rule requires it.

**The second exception, `@brave/brave-search-mcp-server@2.1.5`, is CONFIRMED.**
- It is a pre-existing pin (T851, before this rule existed), so recording it is a correction, not a widening.
- The reasons are strong:
  - the first brave release with SLSA provenance v1;
  - `audit --audit-level high --signatures` with no `--accept` exits 0;
  - the full `npm diff` and the extra review were read, and found no new network, process, file or environment access (§ 5, T851 row);
  - the bump retires seven high advisories of 2.1.4 (SEC-T702-09).
- Holding 2.1.4 for five more days would keep known highs to guard against a hypothetical compromise. The diff read has already lowered that risk.
- The exception lapses by itself on 2026-11-24, and the next bump voids it.

### 2. SEC-T860-02: runner steps in checklist § 3

**The claims are correct**, checked against docs.gitlab.com/runner/commands/ on 2026-11-19:
- `gitlab-runner lint --config /etc/gitlab-runner/config.toml` exists. It "validates a configuration file without starting the runner".
- It reports misspelled or unknown keys, which "the TOML decoder otherwise silently ignores".
- It exits non-zero on any problem or on a missing file.
- `gitlab-runner restart` "stops and then starts the GitLab Runner service".

**The method is right.** T866's point is valid: a clean log proves nothing about an unknown key. Lint, with the docs at the exact version tag as the fallback, is the correct proof.
- `journalctl -u gitlab-runner --since "-10 min"` is valid syntax. The `--syslog` caveat is noted.
- The version in which `services_limit` and `lint` were introduced is not documented, and the page says so itself **(unverified)**.
- I did not check `services_limit` in the `[runners.docker]` docs myself. It rests on T866's Context7 and docs read **(unverified by me)**.

**The out-of-cycle trigger is sufficient.**
- It covers runc, containerd, Docker Engine, GitLab Runner and the kernel. In an LXC that is the Proxmox host kernel, and the step says "reboot the host".
- Its sources are named: the runc and moby GHSAs, GitLab Runner security releases, Proxmox kernel updates and CISA KEV.
- "No release tag until patched" is an effective hold, because the tag jobs are the only jobs on that runner.
- The 120-day review is stated as the ceiling, not the cadence.

**The user can apply these steps as written.** The only residual risk is the one T866 states: an old runner version that has neither `lint` nor the option. In that case step (d) tells the user to stop and report.

### 3. SEC-T862-02: redaction test
**The ruling: acceptable, with a better form tracked as LOW (SEC-T867-03).**
- A real leak needs a user-name segment after the prefix, for example `/home/<user>`, `/Users/<user>`, `/var/folders/xy/…` or `C:\Users\<user>`. Every such leak has a path-segment character right after the prefix, so the rule still catches it.
- What the rule skips is a bare prefix followed by a space, a backtick, a quote or the end of the line. That shows the prefix only, which discloses nothing.
- **Residual class:** a prefix in prose with a leaking name later on the same line, separated by a quote or space (for example `` `/home/` + `emage` ``). It is unlikely and needs deliberate formatting.
- **Better form:** exclude only the exact Redaction line, matched by its whole text or by a fixed marker such as `Redaction:`, and apply the strict any-occurrence rule everywhere else in the `.md`.
- I did not read the test code itself. That the scan of `.md` files after v3, the three new prefixes and the mutations exist rests on the brief and the orchestrator's checks **(unverified by me)**.

### 4. Widening
**I found no weakening or widening in what I read.**
- The `age` subcommand is additive and changes no exit path of `audit` or `provenance`.
- The two exceptions are pins that already existed.
- The runner steps add checks and change nothing an agent does.
- I did not review the test-file diffs or the diff of `mcp-servers.md` for weakened assertions **(unverified)**.

## Per-finding status
| Id | Status | Basis |
|---|---|---|
| SEC-T860-01 | **Fixed** | 7-day rule in § 1 step 1. `age` check fails closed. Exceptions are scoped to a current pin and need a reason. Both exceptions recorded; the brave one is confirmed here. |
| SEC-T860-02 | **Fixed (text)** | § 3 verification steps (a)-(e) are correct per the GitLab docs, and the out-of-cycle trigger is complete. The user still has to apply them (SEC-T811-05 stays a user action). |
| SEC-T862-02 | **Fixed** | `.md` scan after v3 and the three new prefixes, per the brief and the orchestrator's checks; test code not read by me **(unverified)**. The path-segment exception is accepted, with SEC-T867-03 as LOW debt. |

## Findings
| Id | Severity | OWASP | Location | Description | Remediation |
|---|---|---|---|---|---|
| SEC-T867-01 | SECURITY:LOW | A08 | `scripts/audit-mcp-pins.py:503-506, 586` | `--min-age-days` accepts 0-9999. Passing `--min-age-days 0` (or 1) gives exit 0 for every young pin, with no recorded reason, and the checklist does not forbid it. | Refuse values below `MIN_AGE_DAYS` (exit 2), or print `floor lowered below 7 days` and count it as a finding. Say in § 1 that the default is the rule. |
| SEC-T867-02 | SECURITY:LOW | A08 | `scripts/audit-mcp-pins.py:542` | The age is a difference of UTC calendar days (`today - published.date()`). A version published at 23:59Z counts as 7 days old after about 6 days and 1 minute. A duplicate `--allow-young` silently replaces the earlier one. | Compute `(now_utc - published) >= timedelta(days=min_age)` from a fixed `now` in tests, and refuse a duplicate exception. |
| SEC-T867-03 | SECURITY:LOW | A09 | `tests/functional/test_mcp_agent_denials.py`, `T861EvidenceRedactionTests` **(unverified, not read)** | In the `.md` scan, a prefix counts only when a path-segment character follows it. A leaked name separated from its prefix by a quote or space on a prose line would pass. | Exclude only the exact v4 Redaction line, by its full text or a fixed marker, and apply the strict any-occurrence rule to every other line. Add a mutation that puts `` `/home/` emage `` on a prose line. |

Owner of all three: devops-engineer. All are tracked as debt for the next register, per the LOW policy.

## OWASP coverage
| Category | Reviewed | Findings |
|---|---|---|
| A01: Broken Access Control | Yes (runner LXC isolation, tag hold) | 0 |
| A02: Cryptographic Failures | Yes (provenance and signatures as basis of exceptions) | 0 |
| A03: Injection | Yes (`shell=False`, validated spec, `safe_text` on the reason) | 0 |
| A04: Insecure Design | Yes (cooldown design, exception scoping) | 0 |
| A05: Security Misconfiguration | Yes (`services_limit` verification, lint) | 0 |
| A06: Vulnerable Components | Yes (patch trigger, brave highs retired) | 0 |
| A07: Auth Failures | Yes (empty `.npmrc`, `clean_env`: no token reaches npm) | 0 |
| A08: Data Integrity Failures | Yes | 2 (SEC-T867-01, -02) |
| A09: Logging & Monitoring | Yes (redaction test, § 5 records) | 1 (SEC-T867-03) |
| A10: SSRF | Yes (fixed registry; `npm view` only) | 0 |

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 3 | 0 | 3 (tracked as debt) |

### Justification
- No CRITICAL, HIGH or MEDIUM finding.
- No Immutable Security Constraint is breached.
- No required control is omitted, removed, disabled or weakened in what I read.
- All three target ids are fixed.
- The brave 2.1.5 exception is confirmed.
- The three new LOWs are tracked as technical debt, as `validation-gates` § Verdict Rules requires for PASS.
- The unread test and doc diffs are marked (unverified) above. The orchestrator's gate runs cover them.

### Conditions
None. SEC-T867-01 to -03 go to the next register as tracked LOW.

## Gate Verdict
**Gate:** security
**Verdict:** PASS
