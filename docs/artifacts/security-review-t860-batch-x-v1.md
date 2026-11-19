# Security Review: T860, batch X (CI images, the CA control, runner settings)

## Metadata
- **Task:** T860 (plan-177). **Reviewer:** security-engineer, read-only. I made no edits and ran no shell.
- **Date:** 2026-11-19.
- **Based on:** `docs/plans/plan-177-batch-x-ci-images-ca-runner.md` and branch `agent/devops-engineer/T859`, read at worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T859`. That branch holds commits `71d8b2ae`, `d8e24104`, `71afeec9`, `6f793834` and `108a1215`, on top of `edab01db`.
- **Also read:** `tracked-debt-register-v17.md` and `-v18.md` (grep for A-21), and the published `dist/index.js` of `@modelcontextprotocol/server-filesystem@2.4.0` on unpkg.
- **User decision (verbatim):** "X + AB go". **LOW policy (verbatim):** "Track LOW items as debt, stop chasing (Recommended)".
- **Not read** (each marked **(unverified)** where it matters):
  - `ca-check-t767-v2.md`, the tests, the drift baseline, the generated configs and the registry;
  - the 4,139-line `npm diff` and `http.js` of server-filesystem 2.4.0;
  - the frozen tag-job bodies;
  - any pipeline, job log, runner or GitLab setting.

## Scope
Every file in the brief's list of 19 changed files. I traced these in full:
- `scripts/check-ca-chains.sh`;
- the `.gitlab-ci.yml` header and the jobs `ca-chain-check-python` and `ca-chain-check-node`;
- `scripts/sync-wiki.py`;
- `tests/fixtures/ca-chains/SHA256SUMS` and `disclosure-spki.txt`;
- the `filesystem` entry in `implementation/knowledge/mcp/servers.yaml`;
- `docs/wiki/mcp-pin-bump-checklist.md` § 3.

## Assessment

### 1. Python image decision: acceptable
- **Why keeping the pin is sound:** a digest pin fixes the content that is pulled. The x86-64 runners only ever resolve the `linux/amd64` manifest `sha256:a61cbd76…`, and T859 and the orchestrator each checked that it is byte-identical under both indexes. So the old index ships the same packages and the same CA store as the new one.
- **The review date:** `ci_images_reviewed_on: 2026-11-19` records a real review, and the header comment says what was looked at. That matches the date's stated meaning: the day the image was looked at, not the day a digest was taken.
- **Residual risk:** if Docker Hub ever stops serving the old index digest, the pull fails closed. It never falls back to the tag.
- **The new standing rule:** checklist § 3 now says "A digest whose `linux/amd64` manifest is unchanged … need not be taken." I accept it on one reading: "unchanged" means the amd64 manifest digest was hashed under both indexes. That is the method in § 3 (b) and (c).

### 2. The two added rollover keys: the extension is correct, and the old gap was real but narrow
- **What the script checks:** `check_fixtures` now requires every root, every non-leaf chain certificate and every extra certificate to carry a key in `disclosure-spki.txt`. That is the right invariant.
- **Why the two keys belong on the list:** the self-issued `EM DV TLS CA - G3B` rollover certificates sit in the disclosure's own `chains.zip`. They are the same compromised issuer under rollover keys.
- **The gap:** before T859, `check_keys` would not have flagged a store certificate on `413d8778…` or `e13e260f…`. That is exactly the "re-signed copy with the same key" case the key scan exists for.
- **Why the gap was narrow:** chain validation of the two rollover fixtures would still have caught a store entry that let those chains validate. I know of no public store carrying either key **(unverified)**. The gap was real, but nothing was missed in practice.
- **Observation, not a finding:**
  - The two listed keys found in no fixture certificate (`92c063d6…` and `ec4ffa1a…`, the OV CS CA G3B/G3C code-signing keys) are protected only by the key count and by `SHA256SUMS` in the same directory.
  - So an edit that replaces one of those lines with another 64-hex value, and updates `SHA256SUMS` with it, passes the cross-check.
  - That edit would have to be deliberate, and anyone who can make it can also rewrite the script. Merge-request review covers it.
  - Accidental edits are caught by both the count and `sha256sum -c`.
- **Other properties of the new code:**
  - `spki_of` no longer hashes empty input.
  - `split_pems` counts any block that is not a certificate and fails on it. CRLs and `CERTIFICATE REQUEST` blocks also fail, which is fail-closed.
  - The unanchored `-----BEGIN ` match can only over-count, and the check `read == total` then fails, which is also fail-closed.

### 3. SEC-T756-07, server-filesystem 2.4.0: acceptable, and the HTTP transport is unreachable from our launch line
- **The launch line:** `["-y", "@modelcontextprotocol/server-filesystem@2.4.0", "."]`.
- **What the published `dist/index.js` does:**
  - the default is `transport: "stdio"`;
  - it changes only on a `--transport` or `--transport=` argument, which accepts only the values `stdio` and `streamable-http`;
  - `main()` takes the HTTP path only when the value is `streamable-http`;
  - the file itself has no `process.env` read.
- **Unverified:** `HOST` and `PORT` are read in `http.js`, inside the HTTP branch only, and I did not read that file. Whether that branch has authentication is also **(unverified)**. It is not reachable here.
- **Age of the pin:** there is no minimum-age rule, and a one-day-old release falls in the window in which most malicious npm publishes are found. This pin is acceptable without such a rule because:
  - the release has provenance;
  - `npm audit` is clean, there is no `glob`, and minimatch is 11.0.9;
  - T859 read the diff **(unverified by me)**;
  - `filesystem` is an extended, opt-in server with `denyUnlessGranted: true`, held by no agent, so the exposure is limited to user sessions that enable it.
- **The gap for future bumps:** SEC-T860-01 records it.
- **The root copies:** the root configs keep 1.0.0 until the user approves a root refresh. SEC-T756-07 is fixed in source and in the generated mirrors; at the root it is pending.

### 4. SEC-T811-05, runner steps: correct, and enough once two points are added
**What is right:**
- `services_limit = 0` is the right control.
- Keeping `privileged = false` and setting no `allowed_privileged_services` is right.
- Marking the behaviour of an empty `allowed_services = []` as **(unverified)** is honest.
- The text tells the user to read `gitlab-runner --version` first.

**What is missing (SEC-T860-02, LOW):**
- **(a) A check that the option takes effect.** A runner version that predates `services_limit` may ignore or only warn about an unknown key, so the step could give false assurance. The user should check the runner log after the restart for an unknown-key warning, and record the version.
- **(b) An out-of-cycle patch trigger.** The 120-day image-review cadence is a ceiling, not a trigger. A critical runc, Docker Engine or kernel container-escape advisory should be patched when it is published.

"Nothing else in the LXC" is correct.

### 5. SEC-T756-02: it stays LOW
- **What T859 adds:** neither (a) nor (b) closes it. They strengthen the control: three certificate forms, the fixture cross-check, two more keys and the `--capath` runs.
- **Where A-21 was closed:** the brief's correction is right in substance but cites the wrong register. Register **v17** records A-21 as *open* (lines 25, 184, 215, 244, 275). Register **v18** closes it on the user's report (lines 24, 84, 169, 182), and there `FF_GIT_URLS_WITHOUT_TOKENS` is absent from `config.toml` on `gitlab-runner-16028`. Instance variables on gitlab.com stay **(unverified)**.
- **The wrong text:** checklist § 3 line 38 says the flag's state "is still unreported". That is wrong (SEC-T860-03). The same wording may also be in `ca-check-t767-v2.md` and in the TL-T761-11 note **(unverified)**.

## Per-finding statuses
| Id | Status | Basis |
|----|--------|-------|
| SEC-T756-02 | **Open, tracked LOW** | Nothing closes it. A-21 was closed in register v18. The control is stronger. |
| SEC-T756-07 | **Fixed in source.** At the root it is pending the user-approved root refresh. | Pin 2.4.0 has no `glob` and has minimatch 11.0.9. The stdio launch line was traced. |
| SEC-T756-08 | **Fixed** | `_RefuseRedirects.redirect_request` returns `None`, so urllib raises `HTTPError` on any 3xx and `PRIVATE-TOKEN` is never re-sent. The page then counts as failed. The tests are **(unverified)**. |
| SEC-T768-01 | **Fixed** | `CERT_BEGIN_RE` takes the three forms. Any other `BEGIN` fails, and `read == total` is asserted. |
| SEC-T768-02 | **Fixed** | Counts per directory, the distinct-key count, every root, non-leaf and extra certificate on a listed key, and `sha256sum -c` in both jobs. The unanchored-key observation is in § 2. |
| SEC-T768-03 | **Fixed** | Python job: unconditional `--capath` on the shipped and the live stores. If no hashed entries exist the run exits 2, which fails closed. Node job: a guarded run. |
| SEC-T768-04 | **Open, trigger not reached** | No tag-job edit. I relied on the header comment and the brief and did not read the tag-job bodies **(unverified)**. |
| SEC-T768-05 | **Fixed** per T859: v2 says 3 extra certificates, which matches `EXPECTED_EXTRA=3` and the 3 `extra/` files in `SHA256SUMS`. | I did not read v2 **(unverified)**. |
| TL-T761-11 | **Open, LOW, note added.** Per v18 the flag is absent, so the `release` fetch keeps its current behaviour. | The note's "still unreported" is wrong (SEC-T860-03). |
| SEC-T811-05 | **Open, LOW, user action** | The steps are correct; add SEC-T860-02 (a) and (b). |

## Findings
| Id | Severity | OWASP | Location | Description | Remediation | Owner / deadline |
|----|----------|-------|----------|-------------|-------------|------------------|
| SEC-T860-01 | SECURITY:LOW | A06/A08 | `docs/wiki/mcp-pin-bump-checklist.md` § 1 | No minimum release age for an `npx` pin bump. This bump took a release published one day earlier. | Add a cooldown, for example 7 days after publication. A younger pin then needs a recorded exception naming the provenance, the audit and the diff review. | devops-engineer; tracked debt, next batch |
| SEC-T860-02 | SECURITY:LOW | A05 | checklist § 3, "Release-gate runner hardening" | (a) No step shows that `services_limit` takes effect on the runner's unknown version. (b) Patching only every 120 days, with no out-of-cycle trigger. | (a) After the restart, check the runner log for an unknown-key warning, and record `gitlab-runner --version` in § 5. (b) Patch at once for critical runc, Docker Engine or kernel escape advisories, with 120 days as the ceiling. | devops-engineer (text); the user applies |
| SEC-T860-03 | SECURITY:LOW | A09 (record accuracy) | checklist § 3 line 38; possibly `ca-check-t767-v2.md` **(unverified)** | It says the `FF_GIT_URLS_WITHOUT_TOKENS` state "is still unreported". Register v18 records A-21 closed, with the flag absent from `config.toml`. | Restate it as "absent per the user's report (register v18, A-21 closed); instance variables unverifiable", and cite v18, not v17. | devops-engineer; **before merge** |

## OWASP coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (runner scope, the filesystem server's grant) | 0 |
| A02: Cryptographic Failures | Yes (CA store, SPKI scan) | 0 |
| A03: Injection | Yes (shell quoting in the CA script; whitespace in paths is refused) | 0 |
| A04: Insecure Design | Yes | 0 |
| A05: Security Misconfiguration | Yes | 1 (SEC-T860-02) |
| A06: Vulnerable Components | Yes (images, server-filesystem) | 1 (SEC-T860-01) |
| A07: Auth Failures | Yes (token not re-sent on redirect) | 0 |
| A08: Data Integrity Failures | Yes (digest pins, fixture checksums) | 0 (shared with SEC-T860-01) |
| A09: Logging & Monitoring | Yes | 1 (SEC-T860-03) |
| A10: SSRF | Yes (redirect refusal) | 0 |

## VERDICT: CONDITIONAL_PASS

### Findings summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 3 new + 4 carried (SEC-T756-02, SEC-T768-04, TL-T761-11, SEC-T811-05) | 0 | 7 |

### Justification
- There is no CRITICAL, HIGH or MEDIUM finding, no Immutable Constraint breach, and no required control weakened. The CA control, the redirect refusal and the stdio-only launch are all stronger than before.
- The python pin decision is sound.
- The verdict is conditional because SEC-T860-03 is an incorrect security record in a document the user acts on, and it is cheap to fix before merge.

### Conditions
- **SEC-T860-03:** owner=@devops-engineer; correct the A-21 / `FF_GIT_URLS_WITHOUT_TOKENS` wording; deadline=before the T859 merge.
- **SEC-T860-01 and SEC-T860-02:** owner=@devops-engineer (text), with the user applying the runner steps; tracked LOW debt; deadline=register v24, next batch.
- **SEC-T756-07 at the root:** the root refresh needs the user's approval at that moment. Until then the root `.mcp.json`, `.cline/mcp.json` and `.opencode/opencode.json` keep 1.0.0.
