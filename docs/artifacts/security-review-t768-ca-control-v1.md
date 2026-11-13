# Artifact: security-review-t768-ca-control-v1.md

# Security Review T768: plan-146 Part A (CA-chain control) and re-grade of SEC-T756-02

**Based on:** worktree `agent/devops-engineer/T766`, commits `1db94420` (T766) and `1f3af21a` (T767): `scripts/check-ca-chains.sh`, `tests/functional/test_ca_chain_check.py`, `tests/fixtures/ca-chains/README.md`, `.gitlab-ci.yml:92-192`, `docs/wiki/mcp-pin-bump-checklist.md` § 3, `docs/artifacts/ca-check-t767-v1.md`, `docs/artifacts/security-review-t756-accepted-mediums-v1.md` (Part 2 row and §§ 2-3).
**Reviewer:** security-engineer (read-only; no shell). Recorded by the orchestrator from the reviewer's final message, 2026-11-07; the wording is the reviewer's, shortened only where marked.
**Method:** files read directly. The reviewer ran nothing; the `grep_content` tool returned errors on every call. `ca-check-t765-v1.md` and `security-review-release-v10-v1.md` were not opened (budget); their facts come through T767 and the T756 review.

## Summary
- **Risk level:** LOW, once the condition below is met. Until then SEC-T756-02 stays MEDIUM.
- **New findings:** 0 CRITICAL, 0 HIGH, 0 MEDIUM, 6 LOW (SEC-T768-01 to -06).
- **SEC-T756-02:** MEDIUM → **LOW**, taking effect only when MR !658's pipeline passes both new jobs and the MR merges.
- **Status:** CONDITIONAL_PASS.

## Answers to the review questions

**1. Script logic: sound.** No way was found for the script to pass while libcurl/git or Python's default context would trust a disclosed chain in the store under test.
- Isolation: `env -i` with `-no-CAfile`, `-no-CApath`, `-no-CAstore`; only the store under test is read.
- `-partial_chain` makes the verifier at least as accepting as libcurl's; `-purpose sslserver` matches git's use; the fixed `-attime` stops expiry from turning a refusal into a vacuous pass.
- No empty pass: a refusal counts only if the same file validates against the disclosure roots; the counts (19, controls ≥ 1, 12 keys) fail closed.
- The SPKI check closes the logic: a forged chain is trusted only if (a) the store holds a certificate on one of the 12 keys, caught by the scan (re-signed copies included), or (b) an uncompromised root cross-signed a compromised key; T767's crt.sh search by key found no case of (b) for any bundle root, and the AAA key has only its self-signed certificate.
- Residual: an unlogged cross-sign (stated limit); minor gaps SEC-T768-01, -02.
- `--ca-release`: 8-digit release strings compared after a length check; a missing `ca-certificates-bundle` fails.

**2. CI wiring: sound.** Store copied with `cp -L` and `--ca-release` run before `apk add`; copied and live stores checked after; the python job also checks the hashed directory; the node job takes the default image (a structural test asserts no `image:` key). No tag rule, no `allow_failure`. Nothing prints or sends the job token (no `set -x`, `openssl` under `env -i`, no network call but `apk`, no artifacts, `sha256sum` of public files only). The `openssl~=3.5` and `git~=2.54` pins follow the fuzzy-pin policy; `apk` signature checking is from knowledge **(unverified)**; the checking openssl comes from the same repository as the store (circular, no worse than other jobs). Gaps: tag pipeline not covered (SEC-T768-04); node job checks no hashed directory (SEC-T768-03).

**3. Fixtures: acceptable.** Source, fetch date and archive hash stated; `SHA256SUMS` checked by `unit-tests`, which also checks that no file contains `PRIVATE KEY`; everything vendored is public certificates and SPKI hashes. `SHA256SUMS` protects against accidental corruption, not a coordinated edit; against tampering, MR review is the only control (SEC-T768-02).

**4. T767: points 1-3 and 5 settled well enough for LOW.** Point 1 by the NSS 3.131.1 / `certdata.txt` diff (an image older than `ca-certificates` 20261020 is now caught by `--ca-release` and the SPKI check); point 2 settled (same 118 certificates, hash names match); point 3 settled as far as CT shows (the "4" vs 3 listed: SEC-T768-05); point 5 partly. The live connection stays open, acceptable because store selection is established from source and `-partial_chain` path verification is the more accepting test. A-21 is the right residue: the CA-override variables (`SSL_CERT_*`, `CURL_CA_BUNDLE`, `GIT_SSL_*`, above all `GIT_SSL_NO_VERIFY`) and `helper_image` are the only open points that could change the result. `FF_GIT_URLS_WITHOUT_TOKENS` does not change this grade: by T765's source reading the job's own `git` on Docker is unpinned whether the flag is on or off.

## Findings

| Id | Grade | OWASP | Location | Description | Fix | Blocks? |
|---|---|---|---|---|---|---|
| SEC-T768-01 | SECURITY:LOW | A02 | `scripts/check-ca-chains.sh:122-126` (`split_store`) | The SPKI scan reads only `-----BEGIN CERTIFICATE-----` blocks; OpenSSL's CAfile loader also accepts `TRUSTED CERTIFICATE` and `X509 CERTIFICATE` **(unverified on 3.5)**. A compromised root in that form escapes the key scan (chain checks still catch the listed chains, not an unlisted cross-sign). Alpine's bundles do not use these forms. | Match `BEGIN (TRUSTED \|X509 )?CERTIFICATE`, fail on any other `BEGIN` type, assert certificates read = PEM blocks. | No |
| SEC-T768-02 | SECURITY:LOW | A08 | `check-ca-chains.sh:131-132, 168-171`; the CI jobs | Fixtures not cross-checked: `disclosure-spki.txt` checked only for its count, not that the roots and non-leaf certificates carry those keys; 16+3 counted as one sum; the CI jobs do not run `sha256sum -c`. A coordinated edit could hollow out the check. | Assert every root and non-leaf certificate's SPKI is listed; count per directory; optionally `sha256sum -c SHA256SUMS` in both jobs. | No |
| SEC-T768-03 | SECURITY:LOW | A05 | `.gitlab-ci.yml:184-189` | After `apk add`, the node job checks only `--cafile`; if a future install creates hashed `/etc/ssl/certs` entries, libcurl would read them unchecked. Today libcurl depends only on `ca-certificates-bundle` **(unverified for future index states)**. | Add a guarded `--capath /etc/ssl/certs` run when hashed entries exist. | No |
| SEC-T768-04 | SECURITY:LOW | A08 | `.gitlab-ci.yml` tag jobs | The check does not run in tag pipelines; the tag jobs' `apk add git` happens later than the last checked pipeline. Short window; a regression needs Mozilla to re-add the root or the index to roll back. | None now (tag jobs frozen); at the next tag-job change add `--ca-release` and the SPKI check, or run it in a release-candidate tag pipeline. Track as debt. | No |
| SEC-T768-05 | SECURITY:LOW | A08 | `docs/artifacts/ca-check-t767-v1.md:16, 77, 132` | T767 says "4 certificates" beyond the JSON; its table, the README and the script have 3. **(unverified)** which is right. | Re-count; issue `ca-check-t767-v2.md` with "3", or vendor the fourth and set `EXPECTED_EXTRA=4`. | No |
| SEC-T768-06 | SECURITY:LOW | A06 | `docs/wiki/mcp-pin-bump-checklist.md:30` (§ 3) | Still names `python:3.12-alpine sha256:92abd2ba...` (2026-10-22); the pipeline pins `sha256:e064671c...`. Stale procedure text. | Update digest, date and version line. | No |

## Re-grade of SEC-T756-02

**New grade: SECURITY:LOW (A02), effective when MR !658's pipeline has passed both `ca-chain-check-python` and `ca-chain-check-node` and the MR is merged. Until then MEDIUM.**

A passing pipeline must show, for each store run (copied and live; file and hashed directory for python, file for node): `compromised chains and certificates validating: 0 of 19; controls validating: 1 of 1`, `store certificates on a compromised key: 0 of N`, `RESULT: PASS`; and `--ca-release` PASS before and after `apk`. That run is the first proof under busybox ash and OpenSSL 3.5.9. A job failing because a chain validates or a key is found makes the finding **HIGH** (blocks); a failure for a script or compatibility reason keeps MEDIUM until the fix passes.

Why it drops: the T756 reviewer's LOW criteria are met (root absence explained, `/etc/ssl/certs` targets, other cross-signs by key, the executor), and the re-check is a real control: a blocking script against each pinned image's own store, by key, with a release floor and a positive control. The known way back to 8 validating chains now fails the MR. The bundle is still the only runtime control for the job's own `git`, monitored at every change point except tag time (SEC-T768-04).

Conditions for keeping LOW:
- **A-21** (owner: the user; before the next tag or by 2027-02-19, whichever is first): any of `SSL_CERT_FILE`, `SSL_CERT_DIR`, `CURL_CA_BUNDLE`, `GIT_SSL_CAINFO`, `GIT_SSL_CAPATH` set as a CI variable, or `helper_image` overridden to an unchecked image, returns the grade to MEDIUM; `GIT_SSL_NO_VERIFY` set is HIGH, as a separate finding.
- Residual LOW, tracked as debt: unlogged cross-signs, no live connection test, non-amd64 images not read, helper image pinned by tag only.

## CA-pin recommendation
Do not add a CA pin for the job's own `git` now. With the check in place the residual is LOW; a pin would change the frozen tag jobs, provable only in a tag pipeline, and would fail closed at release time if gitlab.com rotates CA, as it has before. If wanted anyway: scope it to the host (`http.https://gitlab.com/.sslCAInfo`), use a small set of roots (USERTrust/Sectigo RSA and ECC), and prove it first in a release-candidate tag pipeline, never next to a real tag.

## Compliance Checklist (scope T768)
- [x] OWASP Top 10 reviewed: A02, A05, A06, A08 in scope.
- [ ] Authentication secure: not in scope.
- [ ] Authorization enforced: not in scope.
- [x] Input validation complete (script arguments: whitespace, missing and empty store refused).
- [x] Secrets management verified for the new jobs and fixtures.
- [x] Dependencies audited: new `apk` pins follow the fuzzy-pin policy; no new npm or pip dependency.
- [ ] Security headers configured: not applicable.
- [x] Logging appropriate: job output holds only hashes and certificate names.

## Gate Verdict
**Gate:** security
**Status:** CONDITIONAL_PASS

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 (SEC-T756-02, carried) | 0 | 1 until the condition is met |
| LOW | 6 (SEC-T768-01 to -06) | 0 | 6 |

### Justification
No CRITICAL or HIGH open; no Immutable Security Constraint breached (fixtures are public certificates, no secret exposed); no required control weakened (the change adds one). SEC-T756-02 drops to LOW only after the MR pipeline proves the jobs. The six new findings are LOW and are tracked as debt.

### Conditions
- **SEC-T756-02:** owner devops-engineer; remediation: MR !658's pipeline passes both CA jobs with the outputs above, then the MR merges; deadline before that merge. Any later image bump must also pass both jobs.
- **A-21:** owner the user; presence only, as T767 describes; before the next tag or 2027-02-19, whichever is first.
- **SEC-T768-01, -02, -03, -05, -06:** owner devops-engineer, next sprint; debt in register v12.
- **SEC-T768-04:** owner devops-engineer, at the next tag-job change; debt.

### Blockers
None. If the MR pipeline fails: BLK-T768-01, type `technical`, severity `major` (`critical` if a chain validates), escalation to the orchestrator.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01 Broken Access Control | No | 0 |
| A02 Cryptographic Failures | Yes | 1 (+ SEC-T756-02) |
| A03 Injection | Partial (script arguments) | 0 |
| A04 Insecure Design | Partial | 0 |
| A05 Security Misconfiguration | Yes | 1 |
| A06 Vulnerable Components | Yes | 1 |
| A07 Auth Failures | No | 0 |
| A08 Data Integrity Failures | Yes | 3 |
| A09 Logging & Monitoring | Partial (output content) | 0 |
| A10 SSRF | No (no network calls added) | 0 |

## Not verified
- The reviewer ran nothing; the 16 passing tests, the real-bundle result and the mutation exit are the orchestrator's observations. The MR !658 pipeline result was unknown to the reviewer; the grade depends on it as stated.
- OpenSSL 3.5's loading of `TRUSTED CERTIFICATE` / `X509 CERTIFICATE` blocks (SEC-T768-01); `apk` signature verification and transport; whether a future Alpine libcurl pulls the full `ca-certificates`; T767's "4 vs 3"; the A-21 values and the helper image actually used.

## Orchestrator's record of the condition
MR !658 pipeline 3040148068 (commit `1f3af21a`, runner 19.5.3), read by the orchestrator on 2026-11-07:
- `ca-chain-check-python` (job 17832613605) **success**: `--ca-release` PASS before and after `apk add` (`ca-certificates` and `ca-certificates-bundle` 20261020-r0); four store runs (copied and live, file and hashed directory), each `store certificates on a compromised key: 0 of 118`, `compromised chains and certificates validating: 0 of 19; controls validating: 1 of 1`, `RESULT: PASS`. This is the first run under busybox ash and the image's OpenSSL.
- `ca-chain-check-node` (job 17832613606) **success**: `--ca-release` PASS before and after (`ca-certificates-bundle` 20261020-r0); two file-store runs (copied and live), each `0 of 118`, `0 of 19; controls validating: 1 of 1`, `RESULT: PASS`.
- `unit-tests` failed on one test of `test_ca_chain_check.py` that matched OpenSSL 3.0's default subject format (`CN = …`), which OpenSSL 3.5 in CI prints differently. Neither CA job nor the check script is affected; the fix is a test-only change, and the condition's last part (the merge) waits for it.

The outputs this review requires are met. SEC-T756-02 becomes LOW when MR !658 merges.
