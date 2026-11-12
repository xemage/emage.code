# Artifact: security-review-t786-node-bump-v1.md

> Immutable once produced; revisions bump <N>.

Based on:
- `docs/artifacts/security-review-t784-node-advisory-v1.md` (§ 3, § 5, § 6, § 8)
- `docs/plans/plan-148-node-image-bump.md` (§ Facts, § Constraints, § Progress, the orchestrator's rulings)
- `docs/tasks/task-T785.md`, `docs/tasks/task-T786.md`
- `.gitlab-ci.yml` lines 1-319, read whole in the worktree `agent-devops-engineer-T785` at the reviewed sha `50520592`
- `docs/wiki/mcp-pin-bump-checklist.md` lines 15-44
- `tests/functional/test_pin_bump_checklist.py` lines 80-114
- `docs/artifacts/security-review-t768-ca-control-v1.md` (SEC-T768-03 row, read by grep on develop)
- `docs/artifacts/tracked-debt-register-v12.md` (the SEC-T756-05/-06 rows, the batch X row, the unverified list; read by grep on develop)
- The orchestrator's evidence file: script-output lines of the jobs of pipeline 3056919066 on `50520592` (MR !667, 7 of 7 jobs success), the `unit-tests` nodejs and npm lines, a registry re-read, the clean-worktree suite result and the digest sweep
- T785's report as relayed in the T786 brief (model output; checked against the evidence where possible)

Task: T786 (plan-148; the user's words: "Re-grade now, bump later (Recommended)"). Producer: security-engineer, read-only. I changed no file.

## Summary
- **Risk level**: LOW
- **Findings**:
  - 0 CRITICAL, 0 HIGH, 0 MEDIUM.
  - 6 LOW in scope: 2 resolved (SEC-T756-05, SEC-T756-06), 2 carried open (SEC-T784-01, SEC-T768-03) and 2 new (SEC-T786-01, SEC-T786-02).
- **Status**: CONDITIONAL_PASS. The only condition is that the open LOW items are entered as tracked debt.

**The change is sound:**
- The default image is now the official multi-arch index `sha256:116b800c…`: Node 24.22.3 on Alpine 3.24.4.
- Every job that runs on it pulled exactly that digest and printed `v24.22.3`.
- Both CA-chain jobs pass on it.
- No pin, job, rule or tag job changed, apart from one added `node --version` line.
- The control the plan requires for an image bump (both CA jobs pass) is in place and enforced. No security control is removed or weakened.

## 1. Proof obligations (T784 § 5)

| # | Obligation | Result | Evidence |
|---|---|---|---|
| 1 | **Digest.** Same index for `24.22.3-alpine3.24` and `24-alpine`; body re-hash equals the digest; tag, digest and date recorded; runner's architecture present. | **Met** | Orchestrator registry reads at 23:42Z and about 23:50Z: `24-alpine` = `24.22.3-alpine` = `24.22.3-alpine3.24` = `sha256:116b800c3754b440…f6e85f5`, body re-hash agrees (prefix recorded). T785 gives the same digest for all three tags at 23:43-23:45Z, bodies equal, architectures amd64, arm64/v8 and s390x. Record and date are in `.gitlab-ci.yml:17-19`. The CI pull is itself content-addressed: each Node job logs `Using docker image sha256:116b800c… for node:24-alpine@sha256:116b800c…`. **Runner architecture is now shown.** Jobs 17951936902, -899 and -903 log `Running on CPU: AMD Ryzen 7 2700X`, an x86-64 CPU, so the amd64 manifest `d8d97e47…` is the one that runs. That manifest's config history holds `alpine-minirootfs-3.24.4-x86_64.tar.gz`. This closes T784 § 8 item 10 and the "non-amd64 images" point of register v12 for this image. The runner's platform setting itself was not read (A-21 area); no grade depends on it. |
| 2 | **Node version.** Config `NODE_VERSION=24.22.3`; recommended `node --version` in a job log. | **Met** | Config Env `NODE_VERSION=24.22.3` (orchestrator and T785). `verify-knowledge-drift` (job 17951936899) runs the new line `.gitlab-ci.yml:134` and logs `v24.22.3`. That is the version that actually ran, independent of the metadata. |
| 3 | **Alpine version and apk-tools.** Base 3.24.4 or later; apk-tools at least 3.0.9. | **Met** | Orchestrator: minirootfs 3.24.4 in the amd64 config history. T785: `/etc/alpine-release` = 3.24.4 and apk-tools 3.0.9-r0 from the layers. That apk-tools version comes from T785's layer read only. It matches the fix version named in the Alpine 3.24.4 announcement that T784 read. |
| 4 | **apk pins.** `openssl~=3.5` and `git~=2.54` resolve; Python-image pins resolve; report `nodejs` and `npm` for `unit-tests`; change them only if the version moved. | **Met** | Jobs install `openssl (3.5.9-r0)` and `git (2.54.1-r0)`: 17951936902 (node CA job), 17951936901 (python CA job) and 17951936903 (`sync-no-diff`, git only). `unit-tests` (17951936898) installs every pinned package and logs `nodejs (24.22.1-r1)` and `npm (11.12.1-r0)`. `~=24` and `~=11` are major-only pins and the majors did not move, so leaving the pins unchanged is correct (`.gitlab-ci.yml:102, 104, 108`). The Node 24.22.1 in `unit-tests` is a residual, ruled in § 3 (SEC-T786-01). |
| 5 | **CA control.** Both CA jobs pass on the new digest; `--ca-release` passes before and after `apk add`; the node job logs `sha256sum` of the shipped and live stores; report hashed `/etc/ssl/certs`. | **Met** | Node job: `--ca-release` PASS before and after `apk add`. `sha256sum` gives `5961c0a3…` for both `/tmp/ca-shipped/cert.pem` and `/etc/ssl/cert.pem`, so `apk add` did not change the store. Both `--cafile` runs give `0 of 118`, `0 of 19; controls validating: 1 of 1`, `RESULT: PASS`. Python job: all four store runs (cafile and capath, shipped and live) give the same result. **Hashed entries:** the node job's `--ca-release` lists only `ca-certificates-bundle 20261020-r0`, both before and after `apk add`. The python job lists `ca-certificates` as well. So the `ca-certificates` package, which writes the hashed directory, is absent from the new Node image and is not pulled in by `openssl` or `git`. T785 also read no hashed entries in the layers. See § 3 for SEC-T768-03. |
| 6 | **Real Node consumers.** `verify-knowledge-drift` and `sync-no-diff` pass on the new image. | **Met** | Job 17951936899: `OK - no drift across 314 files.` Job 17951936903: `Done - 314 files written.`, then `Sync output matches committed platform folders.` Both pulled `116b800c…`. |
| 7 | **Text and tests.** `.gitlab-ci.yml:13-20` and `ci_images_reviewed_on` in the same change; line 17 becomes the 24.22.3 record; `test_ci_hash_pins` and `test_publish_release` pass; full suite in a clean worktree; old digest `06d7adf3…` absent from live files; digest changes in one place only. | **Met** | Lines 16-21 now hold the 24.22.3 record and `ci_images_reviewed_on: 2026-11-11`; the block grew by one line, so the image moved from line 42 to line 43. The orchestrator ran `test_ci_hash_pins` and `test_pin_bump_checklist` (OK) and the full suite at `50520592` in a clean detached worktree: 2707 tests OK, 24 skipped, no FAIL or ERROR. That run includes `test_publish_release`, which the evidence does not list separately. **Old digest:** the sweep finds `06d7adf3` only in immutable records (`mcp-pin-audit-v10-v1.md`, `ca-check-t765-v1.md`, `ca-check-t767-v1.md`, `security-review-t784-node-advisory-v1.md`) and in plan-148, all under the orchestrator's ruling. `test_pin_bump_checklist.py:97` now uses the neutral `sha256:0a1b2c3d...`. The new sample has the same shape as the old one (8 hex digits and an ellipsis), so the test that the scanner does not flag short digest prefixes is unchanged. The superseded index `eb37f586` is only in the do-not-pin note of `task-T785.md`. **One pin:** the sweep finds `116b800c` as a pin only at `.gitlab-ci.yml:43`. `ca-chain-check-node` and `sync-no-diff` have no `image:` key and take the default. The wiki line 30 mention is a record, not a pin. |
| 8 | **Scope.** No new job, no rule that matches a tag, no runner, CI variable or project setting changed. | **Met** (on the files read) | The MR pipeline has the same 7 jobs as before: markdown-links, unit-tests, verify-knowledge-drift, validation-super-gate, both CA jobs, sync-no-diff. The CA, drift and sync jobs keep only the `merge_request_event` and `CI_COMMIT_BRANCH` rules. The three tag jobs (`.gitlab-ci.yml:252-318`) all name the python digest and do not use the default image. Runner tags (`docker`, `dind`) are unchanged in the text. The only script change is `node --version` (`:134`), which prints a public version string and reads no variable. **Not read by me:** the git diff's file list, because I have no git tool, and the project or runner settings, which are not in the repository. The orchestrator's merge check of the changed-file list covers the first. |

## 2. Final status of each id

| Id | Grade | Final status | Reason |
|---|---|---|---|
| **SEC-T756-05** | SECURITY:LOW (A06) | **Fixed: closes** | The closing condition from T784 § 3 is met: "T785 lands the 24.22.3 image and T786 confirms it". All three Node-image jobs (`ca-chain-check-node`, `verify-knowledge-drift`, `sync-no-diff`) run Node 24.22.3 (obligations 1, 2, 6). The Alpine `nodejs` package in `unit-tests` was named a separate residual in T784. It moves to its own id, SEC-T786-01, so this id can close on its own condition. |
| **SEC-T756-06** | SECURITY:LOW (A06) | **Fixed: closes** | T784's closing condition, "T786 confirms the new Node base is 3.24.4 or later", is met (obligation 3). The apk-tools crash fix (3.0.9) is now in both bases. The Python half was already done (T765). Alpine's unread git-log "core components" are covered because both bases are on 3.24.4. |
| **SEC-T784-01** | SECURITY:LOW (A06) | **Open, tracked-LOW (unchanged)** | T785 changes CI only. The user-side Node behind the eight `npx` entries is not touched. `implementation/PREREQUISITES.md:4` and `:227` still say Node 18+, per plan-148 § Progress. Remediation is unchanged: state the minimums (≥ 22.23.5, ≥ 24.22.3, ≥ 26.13.1) in `PREREQUISITES.md` and in the v11.0.0 release document, and replace the end-of-life "18+" floor. Owner technical-writer, deadline the v11.0.0 release document, register v13 (batch Q or Y). |
| **SEC-T768-03** | SECURITY:LOW (A05) | **Open, tracked-LOW (unchanged); its trigger did not fire** | The evidence bears on it. The finding is about a future install that creates hashed `/etc/ssl/certs` entries, which the node job's `--cafile`-only check would miss. At the new digest the image is still bundle-only, before and after `apk add`: `--ca-release` lists only `ca-certificates-bundle`, and the shipped and live `sha256sum` are equal (obligation 5). So today the job checks every store that OpenSSL reads. The finding stays open because nothing yet guards a future index state. The remediation (a guarded `--capath` run when hashed entries exist) is unchanged, in batch X. |

## 3. Residuals and new findings

**Residual: `unit-tests` runs Alpine's Node 24.22.1.**
- It is out of SEC-T756-05's closing scope, as T784 § 3 set it. It is in scope of the same advisory, so I give it its own id below rather than keeping SEC-T756-05 open.
- **Why it is not higher than LOW:**
  - `tests/run.py` and the tests start no Node server. Per plan-148 § Progress, no `.js` or `.mjs` under `tests/` holds `createServer`, `http2.`, `node:https` or `fetch(`.
  - The only Node network client in the job is `npm ci` against the public registry over TLS. Its install is sha512-locked and runs `--ignore-scripts`.
- **What weighs against it:**
  - The job binds the host Docker socket (`.gitlab-ci.yml:96-100`). If an unpatched Node client bug (the llhttp or undici updates, or CVE-2026-123877) became code execution, it would reach the host's Docker daemon.
  - Exploitation still needs a malicious registry or an attacker who can pass TLS, and those updates' content is unread **(unverified)**.
- **Self-healing:** the fuzzy pin `nodejs~=24` takes Alpine's fixed package automatically.

**Runner architecture:** resolved by the CPU line (obligation 1). It is no longer an open point for this image.

**SEC-T784-01:** stays open for the docs task, as § 2 says.

| Id | Grade | OWASP | Location | Description | Remediation |
|---|---|---|---|---|---|
| **SEC-T786-01** | **SECURITY:LOW** | A06 | `.gitlab-ci.yml:102` (`'nodejs~=24'`), `:108-109` (`npm ci`); job log 17951936898 `Installing nodejs (24.22.1-r1)` | The `unit-tests` job runs Alpine's `nodejs` 24.22.1-r1. That line carries the November 2026 Node CVEs because Alpine v3.24 has no 24.22.3 package yet. The job also binds the host Docker socket. No server-side CVE is reached. The client-side items (llhttp, undici, CVE-2026-123877) are reachable only through `npm ci` against a TLS-protected, integrity-locked registry. | No code change is needed: `nodejs~=24` takes the fixed package once Alpine publishes it. **Closes when** a `unit-tests` log shows `Installing nodejs (24.22.3-*)` or later. Owner devops-engineer, batch X. Check it at v11.0.0 preparation (register § 6.2): if Alpine still has no fixed package then, record it in the release document and re-grade. Raise it if the v24.22.3 notes show an llhttp or undici client memory-safety bug on a path `npm ci` takes. Do not move `npm ci` or the Node install into a job without the Docker socket only for this. That is out of proportion at LOW and is a separate design question. |
| **SEC-T786-02** | **SECURITY:LOW** | A05 | `docs/wiki/mcp-pin-bump-checklist.md:30` ("run the image to read its Alpine and runtime versions"; "the first real pipeline is still the proof **(unverified until it runs)**"); `:26` (`docker run` against "a remote Docker host") | The image-bump procedure tells the maintainer or an agent to run the image. That conflicts with the project rule against `docker` in agent work: the configured Docker host is a remote production host (plan-148 § Constraints). An agent following the checklist could start a container on that host. The method this bump actually used, the registry API and the image layers (the method in `ca-check-t765-v1.md`), is safe and is already named in the same section for the CA check. The "unverified until it runs" note is stale, because pipelines now run these jobs. T785 flagged the conflict; the text predates T785. | Docs change only. In § 3, replace "run the image to read its Alpine and runtime versions" with reading `/etc/alpine-release`, `/lib/apk/db/installed` and the config `Env` from the registry layers (no Docker). Name the `node --version` line of `verify-knowledge-drift` as the runtime proof, and drop the stale note. In § 2, mark the `docker run` musl check as a maintainer-only step on a non-production Docker host, never an agent step. Owner technical-writer, register v13 (batch Q or Y), window: next sprint. |

Example wording for SEC-T786-02:
```
Before: ... confirm the body hashes to the digest, run the image to read its Alpine and runtime versions, re-read ...
After:  ... confirm the body hashes to the digest, read the Alpine version (/etc/alpine-release), apk-tools
        (/lib/apk/db/installed) and the runtime version (config Env) from the registry layers (no Docker;
        method in docs/artifacts/ca-check-t765-v1.md), re-read ... The MR pipeline's `node --version` line in
        verify-knowledge-drift is the proof of the Node that ran.
```

## 4. Recommendations (priority order)
1. Merge MR !667 at `50520592` after the orchestrator's own checks. Nothing in this review blocks it.
2. Register v13:
   - close SEC-T756-05 and SEC-T756-06 as fixed (T785/T786);
   - add SEC-T784-01, SEC-T786-01 and SEC-T786-02 as tracked-LOW;
   - keep SEC-T768-03 tracked-LOW, noting that its trigger did not fire at `116b800c…`;
   - mark the "non-amd64 images" unverified point as answered for the runner (x86-64 CPU line).
3. Before committing, confirm one point in T785's report: that `python:3.12-alpine` was in fact re-read on 2026-11-11, as `.gitlab-ci.yml:19` says. The evidence file holds no python registry read. If it was not re-read, line 19 should say so, because `ci_images_reviewed_on` is a single date for both images. This changes no grade: the python digest was read on 2026-11-06, five days earlier.
4. v11.0.0 preparation: check SEC-T786-01, which needs Alpine's `nodejs` 24.22.3 or later in a `unit-tests` log.

## 5. Verdict

## Gate Verdict
**Gate:** security
**Status:** CONDITIONAL_PASS

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 6 | 2 | 4 |

### Justification
- All 8 obligations from T784 § 5 are met (§ 1), with pipeline evidence for the image that actually ran: the digest pulled, `node --version`, both CA jobs, drift and sync.
- SEC-T756-05 and SEC-T756-06 close on their stated conditions.
- No CRITICAL, HIGH or MEDIUM finding. No Immutable Security Constraint is breached: no secret, no PII, nothing bypassed or disabled, no new input path, no privilege change, no data at rest.
- The control that plan-148 and the register require for this bump, both CA-chain jobs passing on the new digest, is present and passing. No other control is removed or weakened: the only script change prints a version, and the test edit keeps its assertion's strength.
- It is not a PASS, because four LOW items are not yet tracked as debt: SEC-T784-01 (new since register v12), SEC-T786-01 and SEC-T786-02 (new here), and SEC-T768-03 (tracked, carried).

### Conditions (if CONDITIONAL_PASS)
- SEC-T786-01: owner=@devops-engineer, remediation=none needed in code; confirm Alpine `nodejs` ≥ 24.22.3 in a `unit-tests` log; re-grade if absent at release, deadline=v11.0.0 release preparation; enter as tracked-LOW in register v13 (batch X).
- SEC-T786-02: owner=@technical-writer, remediation=§ 3 wording (no Docker in the bump procedure; drop the stale note), deadline=next sprint; enter as tracked-LOW in register v13.
- SEC-T784-01: owner=@technical-writer, remediation=as T784 § 6, also replacing the "Node.js 18+" floor at `PREREQUISITES.md:4` and `:227`, deadline=the v11.0.0 release document; enter as tracked-LOW in register v13.
- SEC-T768-03: owner=@devops-engineer, unchanged, stays in batch X.

### Blockers (if FAIL)
Not applicable.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | No (out of scope) | 0 |
| A02: Cryptographic Failures | Partial (CA store at the new digest) | 0 |
| A03: Injection | Partial (the one new CI line takes no input) | 0 |
| A04: Insecure Design | No | 0 |
| A05: Security Misconfiguration | Yes (CI wiring, procedure text) | 2 (SEC-T768-03 carried, SEC-T786-02) |
| A06: Vulnerable Components | Yes | 4 (SEC-T756-05 and -06 resolved, SEC-T784-01, SEC-T786-01) |
| A07: Auth Failures | No | 0 |
| A08: Data Integrity Failures | Yes (digest pin, content-addressed pull, `npm ci` lock, apk pins) | 0 |
| A09: Logging & Monitoring | Partial (new log line prints no secret) | 0 |
| A10: SSRF | No | 0 |

### Compliance Checklist (scope: T786 only)
- [ ] OWASP Top 10 reviewed: partial, see the table above
- [x] Dependencies audited: image digest, Node, Alpine, apk-tools, apk pins
- [x] Secrets management verified for the change: no secret added; the new line reads no variable
- [ ] Authentication, authorization, input validation, headers: not in scope

## 6. Not verified **(unverified)**
1. The git diff's file list (no git tool). I read the named files and relied on the orchestrator's sweep and the unchanged 7-job set.
2. apk-tools 3.0.9-r0, `/etc/alpine-release` and the absence of hashed `/etc/ssl/certs` entries come from T785's layer read. The CI log backs up the last point (bundle-only `--ca-release`, equal `sha256sum`).
3. The index body re-hash: the orchestrator recorded a prefix match; T785 reports full equality.
4. The arm64/v8 and s390x manifests: not read, and not used by the runner.
5. The runner's configured platform and the project or runner settings (A-21).
6. The python re-read claim at `.gitlab-ci.yml:19` (Recommendation 3).
7. The v24.22.3 notes for the llhttp, undici and sqlite updates, still unread (bears on SEC-T786-01's raise trigger).
8. When Alpine will ship `nodejs` 24.22.3 for v3.24.

## Blockers
None. BLK-T784-01 is answered: `grep_content` worked in this review with `root_dir "."` on the main checkout, so the T784 failure was a scoping limit, as plan-148 § Progress said. For the worktree I used the orchestrator's sweep and direct reads.

## Task completion
- **Artifact:** this text, committed by the orchestrator as `docs/artifacts/security-review-t786-node-bump-v1.md`. No file was changed by the reviewer.
- **Acceptance criteria:**
  - Every T784 proof obligation is checked against the diff or the pipeline: met (§ 1).
  - Each id has its final status: met (§ 2; new ids in § 3).
- **Follow-ups:**
  - register v13 entries (§ 4.2);
  - the python re-read confirmation (§ 4.3);
  - the SEC-T786-02 docs fix, which T785 flagged too.
