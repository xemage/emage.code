# Artifact: security-review-t756-accepted-mediums-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Review T756: accepted MEDIUMs and new dependency-audit findings, release v10.0.0

Based on: `docs/artifacts/mcp-pin-audit-v10-v1.md` (T755, in `/home/emage/Code/emage/worktrees/agent-devops-engineer-T755/`); `docs/plans/plan-145-release-v10.md` (read from the same worktree, it is not in the primary checkout); ADR-011; ADR-012; `tracked-debt-register-v11.md` § 2.3, § 6.1, § 6.2; `docs/releases/v8.0.0.md:250-304`; `docs/releases/v9.0.0.md:236-295`; `brave-audit-acceptance-v3.md`; `implementation/PREREQUISITES.md` (grep lines); `.gitlab-ci.yml` at `6d4abc1b`.

## Summary
- **Risk level**: HIGH
- **Findings (new)**: 0 CRITICAL, 1 HIGH, 1 MEDIUM, 6 LOW. Carried: 4 MEDIUM that v10.0.0 ships, plus 1 MEDIUM it does not ship.
- **Status**: FAIL, until SEC-T756-01 is fixed.

**Verdict on proceeding.** The user's decisions may be asked now, but T757 must not start until the Python digest is bumped. A HIGH cannot be accepted (ADR-011), so SEC-T756-01 is a fix and not a question of acceptance. The bump is small, and it belongs in wave 1 so that T759 rehearses the new image.

**Four corrections to the working assumptions:**
1. **CVE-2026-115557 is not about certifi or a Python CA store.** Python ships no CA store. The fix is a built-in denylist in `Modules/_ssl.c` that rejects the compromised keys "regardless of the SSLContext policy configuration".
2. **The compromise is real and the keys are public.** The disclosure says "anyone can recover" them from the certificates.
3. **Removing the emSign root is not enough.** Six Sectigo cross-signed intermediates chain to AAA Certificate Services. So `ca-certificates` 20261020-r0, the fixed Alpine version the disclosure lists, may not close the path. The page does not say whether it does.
4. **T755's computed 9.4 overstates this case.** Its vector has `AT:N`, but here the attacker needs an on-path network position.

## Part 1. Accepted MEDIUMs

| Id | What it is today, and what changed | Carried plan, exact words, source | Deadline as read; passed? | Grade; can it close? | Proposed plan (for the user to see) |
|---|---|---|---|---|---|
| **SEC-T660-01** | The tool list is not a credential boundary. All seven holders now have named sets (T667), but six hold `execute`, and a shell with the token can merge, tag, release or push (v9.0.0:232). T664/T665 (2026-10-22) added the token file, `GITLAB_PERMISSION_MODE=modify` and the check script. T689 (2026-10-31) made the in-memory file the default. | "Remediation plan: token scope and environment handling, owner devops-engineer, review tech-lead, in the sprint after v8.0.0." (v8.0.0:261). "deadline the sprint after v8.0.0" (v8.0.0:300) | **Passed.** No sprint date found; at the latest it passed when v9.0.0 shipped on 2026-11-01. v9.0.0 did not replace it: K-16 and K-24 only say "accepted", and the Conditions name Brave only (v9.0.0:294; register v5:414). The named work was delivered by T665 and T689, but no document closes the plan. | MEDIUM holds. **Cannot be closed by the harness.** It is now the same exposure as SEC-T665-01. | Shared with SEC-T665-01, see the next row. |
| **SEC-T665-01** | The residual after option D: a same-user shell reads the token file or calls the API, and `modify` does not stop that. tmpfs can swap. One shared Developer-level token is an accepted residual (DEC-T681-1, plan-123:134). | **There is a source; it is not in the release documents** (grep of `docs/**`: no hit under `docs/releases/`). "the residual the user re-accepted on 2026-10-16 ("Adopt D and re-accept the residual (Recommended)"); stays open and tracked; the three live checks are the user's; closure only by an isolated user, container or VM" (`security-review-t665-token-handling-v1.md:19`; also register v2:282, :554) | **None ever set**, so none has passed. The last cell of register v2:282 is `-` (header not read). ADR-011 now requires one. | MEDIUM holds. **Nothing more can be fixed in the harness:** "The only closure is an isolated user, container or VM ...; the harness cannot create it." (`PREREQUISITES.md:190`) | Owner: the user, for isolation; devops-engineer, for the documentation. Fix: none possible in the harness, and this should be said plainly. Record `mitigation=` "no harness fix exists; closure only by an isolated user, container or VM; review at token renewal". Deadline: a **review** by **2027-01-28** (GitLab token renewal, A-13), plus a new acceptance at the next release. |
| **SEC-T657-01 / SEC-T658-01 remainder** | **Smaller, but not gone.** Cursor IDE is out of support since v9.0.0, leaving only a frozen `.cursor/` in old targets (K-22, SEC-T678-03). Still open: Gemini CLI, where any agent can call every tool of every configured server except the six Playwright denials, GitLab write tools included; and Pi agents with no `mcp__` entry. K-23 (Opencode built-ins) is a separate user decision. | "Accept the unfixable remainder; fix the rest after v8.0.0 (Recommended)"; "The fixable parts, Opencode per-agent denies and a Cursor CLI deny list, are a tracked follow-up right after v8.0.0 (owner devops-engineer, review tech-lead)." (v8.0.0:262). "deadline right after v8.0.0" (v8.0.0:301) | **Passed**, and not replaced: v9.0.0:231 says only that the remainder "stays accepted by the user (2026-10-15)". Opencode part done by T663 (2026-10-16). Cursor CLI part is moot since the removal; I did not search for whether it was ever built **(unverified)**. | MEDIUM holds, because the Gemini exposure alone justifies it. Cannot be closed. | Owner devops-engineer, review tech-lead. Fix: re-read Gemini CLI and Pi vendor documents for per-agent scoping and implement it if it exists; evaluate a server-level `excludeTools` for GitLab merge and delete on Gemini as a partial fix. If nothing exists, record that. Deadline **2027-01-31**. |
| **SEC-T702-09** | Brave 2.1.4 ships seven advisories. T755: same seven ids, none new; stdio-only pins pass (49 tests); newest release still 2.1.4. Operators' environment **(unverified)**. | "owner devops-engineer, remediation acceptance v3 and its re-audit triggers, deadline 2027-01-30 or the first Brave release above 2.1.4." (v9.0.0:294) | **Not passed**: 85 days ahead; condition (a) not met on 2026-11-06. | MEDIUM holds (acceptance v3:31). Cannot close until upstream publishes; upstream `main` declares fixed versions, unpublished (T755 § 3.6, **unverified**). Reachability not re-derived here. | Keep as carried: owner devops-engineer; fix = bump to the first Brave release above 2.1.4 through the pin checklist; deadline **2027-01-30**. ADR-011 needs both the pin acceptance and the user's words for v10.0.0. |
| **TD-T697-07** | CWSO over plain HTTP on the LAN; the bearer travels in cleartext. **v10.0.0 does not ship it**: "A deployment acceptance, not a release-shipped finding" (register v5:411). It is not in § 6.2 item 2. | "Tie to the bearer (Recommended)" (2026-11-02): "ends when the current CWSO bearer token expires (**2027-01-29**); renewed by the user with each new token; ends at once if CWSO becomes reachable from outside the LAN, if the token's role widens beyond orchestrator, or if a token leak is suspected" (register v5:230) | **Not passed**: 2027-01-29. | MEDIUM per register v4:194, "regrade to HIGH if the orchestrator role can make the CWSO server run code or read secrets". Not checked: the CWSO repository is out of scope **(unverified)**. | No v10.0.0 question. Keep A-13: the user renews with the new token by 2027-01-29. The release document should not list it as accepted for v10.0.0. |

**Passed deadlines (SEC-T735-08).** Under ADR-012 a passed deadline counts as moved later, which needs the user's new acceptance. ADR-011's one-release rule requires that acceptance anyway. **No text settles whether a new acceptance cures a passed deadline**, so the two questions below state this and do not present it as cured. The old plans should be recorded as done or moot, with a new plan shown beside them.

## Part 2. New findings

| Id | Grade | Location | Description and reachability | Smallest fix; is the fix a risk? | Blocks? |
|---|---|---|---|---|---|
| **SEC-T756-01** | **SECURITY:HIGH** (A02, A06) | `.gitlab-ci.yml:51,92,134,145,180,198,222,245`; `scripts/publish-release.py:619,665-673`; `scripts/sync-wiki.py:65,71` | CVE-2026-115557. Python 3.12.15 has no denylist, per the 3.12.16 notes. **Traced:** `release` sends `CI_JOB_TOKEN` in `JOB-TOKEN` over the default urllib HTTPS handler, and `wiki-sync` sends `WIKI_TOKEN`, a stored CI variable, in `PRIVATE-TOKEN` the same way. Neither sets a CA file. **Not CRITICAL:** it needs an on-path position between runner and GitLab. Why HIGH: anyone can recover the keys, and this client checks neither CT nor revocation. | Bump the digest in all eight places. See "The fix" below. Low risk. | **Yes.** It cannot be accepted. |
| **SEC-T756-02** | **SECURITY:MEDIUM**, provisional (A02) | `.gitlab-ci.yml:232-235`, `:109,151-152`; runner clone | OpenSSL clients have no denylist, so `git` depends on the CA bundle. Whether the AAA-chained cross-signs validate against the bundle **(unverified)**. Lower than -01 because the runner normally pins git to the server's chain (`http.<host>.sslCAInfo`, `CI_SERVER_TLS_CA_FILE`): from my memory of runner source **(unverified)**. If that pin is absent and the chains validate, regrade to HIGH. | Check, no Docker: take `/etc/ssl/cert.pem` from the new digest's layers and run `openssl verify` on the disclosure's `chains.zip`. Read `.gitlab-runner.ext.conf` handling. No code risk. | **Yes until checked:** then a fix or the user. |
| **SEC-T756-03** | SECURITY:LOW (A06) | Python image | CVE-2026-77214 and CVE-2026-102633 (Expat). T755's 8.3 and 8.2 do not apply here. No XML parser import in `scripts/`, `implementation/` or `tests/functional/` (grep, with positive controls). -102633 is 32-bit only per OSV; T755 read amd64 only. The upstream Dockerfile has no `--with-system-expat`, so the bundled copy is implied. Dependencies not analysed **(unverified)**. | Fixed by the same bump. | No |
| **SEC-T756-04** | SECURITY:LOW (A06) | `tests/functional/test_install_cursor_removal.py:352-353` | CVE-2026-114583 needs `filter="tar"` on an untrusted archive. The only `extractall` found uses `filter="data"`, on a `git archive` of this repository's own tag, in `unit-tests` only. `pip` runs with `--only-binary=:all:`. Whether 3.12.15 has the `data` counterpart, CVE-2026-7774, not read **(unverified)**. | Fixed by the same bump. | No |
| **SEC-T756-05** | SECURITY:LOW, provisional (A06) | `.gitlab-ci.yml:40,99,103-104,124-130,158-175` | Node security release, content unpublished. Node image: `verify-knowledge-drift` and `sync-no-diff`, both with branch or MR rules, so **no tag job uses Node**. `unit-tests` installs Alpine's `nodejs~=24`, another version, unread. Input is repository content. `verify.mjs` and `sync.mjs` show no network call (grep); `npm ci --ignore-scripts` is locked by sha512. | **Do not wait for it.** Re-read the advisory at T762 if published; bump at the next image review, no later than 2027-02-19. Regrade if it reaches these inputs. | No |
| **SEC-T756-06** | SECURITY:LOW, provisional (A06) | both images | Alpine 3.24.4: **the announcement could not be read** (two URLs returned 404). Known only: branch v3.24 has `ca-certificates-bundle` 20261020-r0. Whether the new digest is on 3.24.4 **(unverified)**. | Comes with the bump if its base is 3.24.4; read the notes in that task. | No |
| **SEC-T756-07** | SECURITY:LOW (A06) | `implementation/knowledge/mcp/servers.yaml:241-246` | `GHSA-3g3m-2fjr-6pw4`, `GHSA-g3hv-75wg-m249`. **Extended, but not per-server opt-in:** it is generated for every platform whose manifest opts in. No agent lists it; `denyUnlessGranted: true`. On Gemini CLI any agent can reach it. `glob` is not imported (T755). `minimatch` needs `optimizationLevel >= 2` and the default is 1 (T755); level 1 not analysed **(unverified)**. Worst case: an attacker-controlled pattern hangs a local stdio process. | `server-filesystem@2.2.0` through the checklist, after the release: owner devops-engineer, next sprint. Not before the tag: a semver major with unchecked behaviour. | No. **The user need not accept a LOW**; tell them. |
| **SEC-T756-08** | SECURITY:LOW (A07) | `scripts/sync-wiki.py:65,71` | Found while tracing -01: plain `urlopen` follows redirects with `PRIVATE-TOKEN`. `publish-release.py:612-616` refuses redirects for this reason. I did not search the registers, so this may already be tracked. | Reuse the refuse-redirects opener, next sprint. | No |

**The fix for SEC-T756-01.**
- **Target.** `python:3.12-alpine@sha256:e064671ca452259bab50e8e2c7bd896e39e9a343bb06ca25234adf6fe18d0fc7`, which T755 read as `3.12.16-alpine`. Re-read and re-hash it at bump time, per `.gitlab-ci.yml:23-25`.
- **Tests.** `PINNED_IMAGE` (`test_ci_hash_pins.py:93`) accepts any digest, and no test under `tests/functional/` names `3.12.15` or `3.24.3`. This supports item 19; I did not run the suite.
- **Risks.**
  - If the base moved to 3.24.4, each `apk` pin must still resolve (`.gitlab-ci.yml:99,103,149,162,232,251`). A miss fails closed.
  - MR pipelines do not run the tag jobs. T759 covers `release`; `release-docs-gate`'s install stays on item 14's watch list.
  - Header lines 15-18 and `ci_images_reviewed_on` need editing by hand.
- **Timing.** Before T757, or T759 and the gates would test an image that does not ship the fix. T759's Docker approval says "the pinned image", so name the new digest to the user.
- **What it does not fix.** SEC-T756-02, the runner's helper image, or the operator's own Python on `scripts/check-gitlab-token.py`. I suggest a known-limitation line in the release document.
- **Past runs.** I found no evidence of exploitation and did not investigate past runs. I do not recommend rotating tokens on this alone.

**Which job uses what for TLS:**

| Job | TLS client | Carries a credential? | Status |
|---|---|---|---|
| `release` | stdlib `ssl`, then OpenSSL default paths, then Alpine's store. **No certifi**: it runs no `pip`. | `CI_JOB_TOKEN` | Script traced; default-context behaviour from CPython knowledge, not run |
| `wiki-sync` | same | `WIKI_TOKEN` | same |
| `release-docs-gate` | pip's own (truststore or vendored certifi) **(unverified)** | No: allowlisted, `.git` removed; hash-locked | Read |
| `validation-super-gate`, `unit-tests` | pip's own; `unit-tests` also has `certifi==2026.10.19` for `requests` (`ci/requirements-ci.txt:23`), the version the disclosure lists as patched | Job token in the environment, not sent by pip | Which tests reach the network not traced |
| `main-develop-drift-gate` | `git` over libcurl; `apk`; its Python scripts import no urllib | Job token, git only | apk signature protection from knowledge **(unverified)** |

## Questions for the user

**Q1. SEC-T756-01, for your information; it needs a task.** "Python 3.12.15 in the CI image lacks the block on the compromised eMudhra keys, and the job publishing v10.0.0 sends its token through it. I graded it `SECURITY:HIGH`, which cannot be accepted, so it blocks the release. Plan: devops-engineer bumps the digest to 3.12.16 in all jobs, before `release/v10.0.0` opens; the T759 rehearsal then uses the new digest. Approve this task?"

**Q2. SEC-T756-02, ask only after its check.** "For release v10.0.0: `git` in CI has no such block and depends on the CA bundle and the runner's pin. [Result of the check.] Fix it, or accept it for v10.0.0? Plan: owner devops-engineer; fix: take the newest CA bundle and re-check at each image bump; deadline 2027-02-19." If the check shows it reachable, it returns as HIGH and this question is withdrawn.

**Q3. SEC-T660-01 and SEC-T665-01, `SECURITY:MEDIUM`.** "For release v10.0.0: an agent shell running as you can read the GitLab token. **No harness fix exists**; closure needs an isolated user, container or VM. The old plan's deadline ('the sprint after v8.0.0') has passed, though its work was done by T665 and T689; SEC-T665-01 never had a deadline. **The rules do not say whether a new acceptance cures a passed deadline.** Plan shown: owner you (isolation) and devops-engineer (documentation); fix: none possible in the harness; deadline: review at token renewal, 2027-01-28, and a new acceptance at the next release. Accept for v10.0.0, or isolate the agents first? Separately: may the register mark SEC-T660-01 as superseded by SEC-T665-01 after the release?"

**Q4. SEC-T657-01/SEC-T658-01 remainder, `SECURITY:MEDIUM`.** "For release v10.0.0: on Gemini CLI any agent can call every configured MCP tool except six Playwright tools, GitLab writes included; on Pi, agents without an `mcp__` entry stay open. Cursor IDE is gone from support. The old deadline ('right after v8.0.0') has passed; Opencode was done and the Cursor part is moot. **The rules do not say whether a new acceptance cures a passed deadline.** Plan shown: owner devops-engineer, review tech-lead; fix: re-check vendor scoping and evaluate a server-level GitLab deny on Gemini; deadline 2027-01-31. Accept for v10.0.0, or fix first?"

**Q5. SEC-T702-09, `SECURITY:MEDIUM`.** "For release v10.0.0: Brave 2.1.4 still ships the same seven advisories, and no newer release exists. Plan shown: owner devops-engineer; fix: bump to the first Brave release above 2.1.4; deadline 2027-01-30 or that release, whichever is first. Accept for v10.0.0?"

**For information, no decision:** TD-T697-07 is not shipped by v10.0.0 and stays on its own date, 2027-01-29. The `filesystem` moderates are graded LOW and tracked.

## Blockers
- `BLK-T756-01`: SEC-T756-01. Type `technical`, severity `critical`, assets: all Python-image jobs, owner devops-engineer, retry 0, escalation orchestrator.
- `BLK-T756-02`: SEC-T756-02 unverified. Type `technical`, severity `major`, owner devops-engineer, retry 0, escalation orchestrator.
- `BLK-T756-03`: does a new acceptance cure a passed deadline, and may a plan's fix be "none possible"? Type `unclear_requirements`, severity `major`, escalation the user. No rule states either. I also found no rule that a CI-image CVE counts at the Release gate: I count SEC-T756-01 because the publishing job runs in that image, which is my reading.
- `BLK-T756-04`: Node advisory unpublished. Type `external`, severity `minor`; does not hold the tag.

## Not verified or not read
- No image layer read, no container run, no test run. The CA bundle in either digest and the runner's location and host are unknown; the grade does not rely on the runner being safe.
- `security-review-t702-brave-reachability-v1.md`, `task-T665.md` and `task-T689.md` were not opened. I used acceptance v3, the T665 and T689 reviews and `completed-tasks.md` instead.
- The eMudhra facts come from the disclosure page, OSV, a Python issue and secondary press. I did not read the Mozilla thread.
- I did not read the `validation-gates` skill's verdict format, so `## Gate Verdict` below follows the fields this agent's instructions name.

## Compliance Checklist
Scope is T756, not a full audit.
- [ ] OWASP Top 10 reviewed: partial, see the coverage table
- [ ] Authentication secure: not in scope
- [ ] Authorization enforced: not in scope, except the carried GitLab findings
- [ ] Input validation complete: not in scope
- [ ] Secrets management verified: not verified; the token paths were traced for TLS only
- [x] Dependencies audited: T755's results graded
- [ ] Security headers configured: not applicable to this review
- [ ] Logging appropriate: not in scope

## Gate Verdict
**Gate:** security
**Status:** FAIL

## VERDICT: FAIL

### Findings Summary
Carried MEDIUMs: 5, counted separately in Part 1 (accepted earlier, not resolved).

| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 1 | 0 | 1 |
| MEDIUM | 1 | 0 | 1 |
| LOW | 6 | 0 | 6 |

### Justification
SEC-T756-01 is an unresolved HIGH on the job that publishes this release, so the verdict is FAIL (§ Security Gate Protocol item 2). After the bump, and with SEC-T756-02 checked, the best available verdict is CONDITIONAL_PASS. That also needs the user's acceptances for v10.0.0 of the four carried MEDIUMs and owners for the LOW findings.

### Conditions (if CONDITIONAL_PASS)
Not applicable while FAIL. Proposed plans are in Part 1 and the questions.

### Blockers (if FAIL)
- BLK-T756-01: Python CI image lacks the denylist on token-bearing TLS, severity=HIGH, affected_assets=[`.gitlab-ci.yml` Python-image jobs, `release`, `wiki-sync`], escalation=orchestrator
- BLK-T756-02: `git` TLS trust unverified, severity=MEDIUM (provisional), affected_assets=[tag jobs' `git fetch`, runner clone], escalation=orchestrator

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | No | 0 |
| A02: Cryptographic Failures | Yes | 2 |
| A03: Injection | No | 0 |
| A04: Insecure Design | No | 0 |
| A05: Security Misconfiguration | No | 0 |
| A06: Vulnerable Components | Yes | 5 |
| A07: Auth Failures | Partial, carried GitLab findings and SEC-T756-08 | 1 |
| A08: Data Integrity Failures | Partial, CI pins | 0 |
| A09: Logging & Monitoring | No | 0 |
| A10: SSRF | No | 0 |

SEC-T756-01 and -02 are counted under A02 only.

## Task completion
- **Artifact:** this text, for you to commit as `docs/artifacts/security-review-t756-accepted-mediums-v1.md`. No file was changed.
- **Acceptance criteria:** one row each, with the deadline as read from its source: met. Each new finding has an id, a grade and a blocks-or-not: met. Questions carry a plan and a deadline ahead: met, except Q2, which waits for its check.
- **Follow-up:** add these ids to register v12 and check SEC-T756-08 against the registers.

Sources:
- [OSV CVE-2026-115557](https://api.osv.dev/v1/vulns/CVE-2026-115557)
- [CPython issue 160040](https://github.com/python/cpython/issues/160040)
- [Python 3.12.16 release page](https://www.python.org/downloads/release/python-31216/)
- [eMudhra disclosure](https://emudhra.we-have-a-problem.com)
- [Google, Mozilla revoke eMudhra intermediates (CSO)](https://www.csoonline.com/article/4238338/google-mozilla-revoke-emudhra-intermediates-after-private-key-compromise.html)
- [OSV CVE-2026-77214](https://api.osv.dev/v1/vulns/CVE-2026-77214)
- [OSV CVE-2026-102633](https://api.osv.dev/v1/vulns/CVE-2026-102633)
- [OSV CVE-2026-114583](https://api.osv.dev/v1/vulns/CVE-2026-114583)
- [Node.js November 2026 security releases](https://nodejs.org/en/blog/vulnerability/november-2026-security-releases)
- [Alpine package index, ca-certificates-bundle](https://pkgs.alpinelinux.org/packages?name=ca-certificates-bundle&branch=v3.24&arch=x86_64)
- [docker-library python 3.12 alpine3.24 Dockerfile](https://github.com/docker-library/python/blob/master/3.12/alpine3.24/Dockerfile)
- [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249)

## Orchestrator's check of SEC-T756-01 (2026-11-06)

The reviewer ran no code. The orchestrator read these sources directly: OSV has `CVE-2026-115557`, "Distrust compromised intermediate certificates in ssl module", published 2026-10-24. Python's 3.12.16 release page lists it under its security content ("gh-160040: Distrust compromised eMudhra intermediate CA keys"), with the Expat and `tarfile` CVEs. The registry resolves both `3.12.16-alpine` and `3.12-alpine` to `sha256:e064671ca452259bab50e8e2c7bd896e39e9a343bb06ca25234adf6fe18d0fc7`, and `.gitlab-ci.yml` holds the old digest in 8 places. The fix is T765.

## Re-grade after T765 (the reviewer's words)

Based on: `/home/emage/Code/emage/worktrees/plan-145/docs/artifacts/ca-check-t765-v1.md`; `.gitlab-ci.yml:13-20` on that branch. I read T765's artifact and its method looks sound, but I ran nothing. Your summary of it matches the artifact.

**Two corrections to my review:**
- The runner-pin reason for SEC-T756-02's lower grade is wrong for the job's own `git` on Docker (T765, source reading). I withdraw it.
- SEC-T756-01 rested on the same bundle question, and my row did not say so. I marked that question unverified only under -02. The disclosed chains fail on the old digest too (0 of 16), so the Python path was not reachable through them either. Correction 3 in my report ("may not close the path") is also answered: `AAA Certificate Services` is absent from this bundle.

## 1. SEC-T756-01: closed pending T759's check
- **Status:** fixed on the branch, not closed. Closing needs the merge to `develop` and T759's check of the built `_ssl`. Today's evidence is `PYTHON_VERSION=3.12.16` plus the release notes; the binary was neither read nor run.
- **Grade:** the record stays HIGH as raised, with a note that T765 found the disclosed chains rejected at both digests.
- **If T759 finds no denylist:** the bump did not deliver this control and -01 reopens. It would not block as HIGH, because the disclosed chains still fail. It becomes the same single-control MEDIUM as -02, on Python's token paths.
- **The check itself:** print the version, then search the `_ssl` `.so` for one denylisted key hash as PR #160042 stores it. I have not read how the PR stores it **(unverified)**. No key material or `proof.zip` is needed.
- **Approval:** T759's approval names the job's `before_script` and `script`, so name this extra read-only command to the user.

## 2. SEC-T756-02: final grade `SECURITY:MEDIUM`, for a new reason
- **Not HIGH:** my condition needed both an absent pin and validating chains. The chains do not validate.
- **Why MEDIUM:** this is a defense-in-depth gap. On the job's own `git` the bundle is the only control, with no denylist and no pin, and a token-reachable path sits behind it. T765 treats the token as reachable by anyone who passes certificate validation, and I agree. There is also a known way to reopen it: if a later bundle carries `emSign ECC Root CA - G3`, 8 of 16 chains validate, and nobody knows why that root is absent today.
- **Not LOW yet:** other cross-signs, the targets behind `/etc/ssl/certs`, a live `git` connection, and the executor and flag are all unverified. The digest pin limits how the bundle can change, but it does not settle these.
- **What would justify LOW:** those points settled, plus the re-check in the bump procedure. That would be a new grading, not something to assume now.
- **T750's allowlist:** with the flag on, it removes the path to the pin. I do not count this as a weakened required control, because `security-guidelines.md` requires no such pin and certificate validation stays on. The flag's value is unverified. This is my reading, so it stays in this finding.

**Plan for the user to see:**
- **Owner:** devops-engineer; review security-engineer.
- **Fix:**
  - (a) Add T765's command as a step in `docs/wiki/mcp-pin-bump-checklist.md`, run at every Python or Node digest bump: 0 of 16 must validate, and the `gitlab.com` control must pass.
  - (b) Settle the open points: a crt.sh search by key from a host with network, the `/etc/ssl/certs` targets, why the emSign root is absent, and the deployed executor and flag.
- **Deadline:** 2027-02-19, and before any earlier image bump.
- **Possibly a test, but not a text pin alone.** A test that the checklist contains the words is a reminder, not a control, and should not be recorded as one. A real control is a script that runs the check against the image's bundle. That is optional and after the release, because it does not fit next to a tag.
- **Not now:** adding a CA pin to the job's `git`. It changes pinned commands that have not been proved in a tag pipeline.

## 3. Questions, verdict, and wording

**Verdict:** still FAIL until the bump merges. Once it merges, no HIGH stays open and the security verdict is **CONDITIONAL_PASS**, with T759's `_ssl` check as a condition. Separately, the Release gate blocks until the user fixes or accepts, for v10.0.0, each of SEC-T660-01, SEC-T665-01, the remainder, SEC-T702-09 and SEC-T756-02 (ADR-011). So the verdict does not depend on those decisions, but shipping does. The LOW findings still need owners.

**Blockers:** BLK-T756-01 is fixed, pending merge and T759. BLK-T756-02 is resolved: the check ran, and -02 now goes to the user as a normal MEDIUM.

**Questions:**
- **Q1** becomes a status note: fixed on the branch, closing after the merge and T759.
- **Q2** can now be asked, replacing the earlier text: "For release v10.0.0: `git` in CI has one control against the compromised eMudhra certificates, the image's CA bundle. Today it rejects all 16 disclosed chains, but the runner's pin does not cover this `git` on Docker, and a later bundle could reopen 8 of them. Some points are unverified, including other cross-signs and the deployed runner settings. Plan: [as above], deadline 2027-02-19. Accept for v10.0.0, or fix first?"
- **Q3** gets one added sentence: "The acceptance rule asks for a fix, and here none exists in the harness. Do you accept on this record, knowing it returns at every release?" Grade, plan and date are unchanged.
- **Q4 and Q5:** no change.

**Wording for a fix that is "none possible".** Record it literally, for example:

> `mitigation=` "Fix: none possible in the harness; none is planned. This plan does not end the finding. Remaining exposure: a same-user agent shell can read the GitLab token. Closure only by an isolated user, container or VM, which the operator must set up. Current owner: the user."
>
> `deadline=` "Review date 2027-01-28, not a fix date. The finding stays open after it unless the operator isolates the agents. A missed review counts as a passed deadline (ADR-012). A new acceptance is needed at the next release."

Four rules for that record:
- Never call the date a fix date.
- Never write "mitigated" without "not closed".
- List what T665 and T689 delivered as done work, separate from this plan.
- Whether this record satisfies ADR-011's "fix" field stays the user's ruling, which is why Q3 asks it.

**Changed rows:**

| Id | Grade | Status |
|---|---|---|
| SEC-T756-01 | HIGH, as raised | Fixed on the branch; closes after the merge and T759's `_ssl` check. Disclosed chains rejected at both digests. |
| SEC-T756-02 | MEDIUM, final | Bundle is the only control on the job's `git`. Fix or user acceptance, plan above. |
| SEC-T756-03, -04 | LOW | Fixed by the same bump, subject to T759. |
| SEC-T756-06 | LOW | Python image now on Alpine 3.24.4; Node image still on 3.24.3; I still have not read the notes. |

**One text fix on that branch:** `.gitlab-ci.yml:17` says "review T756: no security release to wait for". That misquotes me. A Node security release is announced for 2026-11-11. My finding was that the tag need not wait for it, because no tag job uses Node. Please reword the line and bump the Node image as SEC-T756-05 says.
