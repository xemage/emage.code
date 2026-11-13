# Artifact: security-review-t784-node-advisory-v1.md

> Immutable once produced; revisions bump <N>.

Based on: `docs/plans/plan-148-node-image-bump.md` (§ Facts, § Task Decomposition); `docs/tasks/task-T784.md`; `docs/artifacts/tracked-debt-register-v12.md` (§ 1, § 5 batch X, § 6.2); `docs/artifacts/security-review-t756-accepted-mediums-v1.md` (Part 2 rows SEC-T756-05 and -06, § Re-grade after T765); `.gitlab-ci.yml` lines 1-273 on `agent/security-engineer/T784`; `implementation/knowledge/mcp/servers.yaml` (whole file); `implementation/scripts/verify.mjs:1-40`; `implementation/scripts/sync.mjs:1-40`; `scripts/check-ca-chains.sh:1-40`. External sources, all read on 2026-11-11: the Node.js advisory "November 11, 2026 Security Releases"; `https://nodejs.org/dist/index.json` (first 100k characters); `docker-library/official-images` `library/node` (master); the Alpine announcement "Alpine 3.21.10, 3.22.8, 3.23.8 and 3.24.4 released"; pkgs.alpinelinux.org `nodejs` v3.24 x86_64. Task: T784 (plan-148; the user's words: "Re-grade now, bump later (Recommended)"). Producer: security-engineer, read-only. I changed no file.

## Summary
- **Risk level**: LOW
- **Findings**: 0 CRITICAL, 0 HIGH, 0 MEDIUM, 3 LOW. Two are re-graded (SEC-T756-05, SEC-T756-06) and one is new (SEC-T784-01).
- **Status**: CONDITIONAL_PASS. The only condition is that SEC-T784-01 gets entered as tracked debt.

**Main points:**
- **No CI job reaches any of the 16 CVEs.** No CI job runs Node as a server, as a TLS endpoint, with HTTP/2, with a proxy or with the permission model.
- **The shipped `npx` entries reach none of the server-side CVEs.** Each is a stdio process. Two client-side MEDIUMs, and the undici and llhttp updates, can reach a user's own Node, but only under conditions this repository does not set.
- **24.22.2 is not a security release.** `index.json` flags v24.22.2 (2026-10-27) `security: false`. The pinned v24.22.1 (2026-10-20) was the last security release before v24.22.3. So taking 24.22.2 now would gain no Node fix.

**Facts read today:**
- **Node.** The advisory's fixed versions are 22.23.5, 24.22.3 and 26.13.1. `index.json` lists v24.22.3 dated 2026-11-10, `security: true`, npm 11.19.1, OpenSSL 3.5.9.
- **Image.** `library/node` tags `24-alpine` and `24-alpine3.24` as `24.22.2-alpine3.24` (GitCommit `e994dfe1…`). No stanza carries 24.22.3. This matches plan-148 § Facts.
- **Alpine package for `unit-tests`.** The v3.24 `nodejs` package is `24.22.1-r1`, built 2026-10-30. So `unit-tests` still runs 24.22.1, and the fuzzy pin `nodejs~=24` takes a fixed package automatically once Alpine publishes one.
- **`ca-chain-check-node` runs no Node at all.** It uses POSIX sh and the openssl CLI only (`scripts/check-ca-chains.sh:25`). For it, the Node image matters only for its CA store, OpenSSL and apk-tools.

## 1. The advisory, one row per CVE

Key:
- **(a)** CI: `verify-knowledge-drift` and `sync-no-diff` run `node verify.mjs` / `sync.mjs` on the Node image; `ca-chain-check-node` runs no Node; `unit-tests` runs Alpine's `nodejs` 24.22.1 with `npm ci --ignore-scripts --prefix ci/js` (sha512-locked) and `tests/run.py`.
- **(b)** What this repository ships: the `npx` entries in `servers.yaml` (gitlab :74-75, playwright :111-112, memory :123-124, sequential-thinking :130-131, brave :138-142, filesystem :235-236, supabase :252-253, toolradar :262-263). Each is `transport: stdio`, and brave forces `--transport stdio`. Node is the user's own version. gitlab, brave, supabase and toolradar are HTTPS clients that carry a credential; `npx -y` is an npm client.

**What `verify.mjs` and `sync.mjs` import:**
- `verify.mjs` imports `node:child_process`, `node:url` and `node:path`. It spawns `process.execPath` with `sync.mjs` and nothing else.
- `sync.mjs`'s static imports in lines 1-40 are `node:fs`, `node:path` and `node:url`.
- I read no `http`, `https`, `http2`, `tls`, `net`, `zlib`, `sqlite` or `fetch` use. Review T756 had already found no network call by grep. I could not re-grep the rest of `sync.mjs` (see § 8).

| CVE | Sev | Area / side | (a) CI reached? | (b) Shipped / user reached? | Reason |
|---|---|---|---|---|---|
| CVE-2026-123863 | HIGH | http2 server | No | No | No job or entry runs an `http2` server. Every MCP entry is stdio. |
| CVE-2026-123864 | HIGH | https server (`flushHeaders` + `end(chunk)`) | No | No | No HTTPS server anywhere. |
| CVE-2026-123865 | HIGH | http2 server, GOAWAY then protocol error | No | No | No http2 server. |
| CVE-2026-123866 | HIGH | http2 server, stream teardown UAF | No | No | No http2 server. |
| CVE-2026-126051 | HIGH | tls server (SNICallback, OCSP, session hooks, `addContext`) | No | No | No TLS server. |
| CVE-2026-123872 | HIGH | tls server, TLS 1.2 renegotiation and per-host client-cert policy | No | No | No TLS server and no mTLS. |
| CVE-2026-123874 | HIGH | http2 server, `respondWithFile`/`respondWithFD` | No | No | No http2 server. |
| CVE-2026-123828 | MEDIUM | http2 server, `altsvc()` | No | No | No http2 server. |
| CVE-2026-123867 | MEDIUM | tls server, CA-only `addContext` | No | No | No TLS server. |
| CVE-2026-123868 | MEDIUM | http2 server memory budget | No | No | No http2 server. |
| CVE-2026-123871 | MEDIUM | Node's own proxy config: credentials in `ERR_PROXY_INVALID_CONFIG` messages | No | **Conditional** | (a) `verify.mjs` and `sync.mjs` make no request, so no proxy config is built. npm uses its own agent stack, not Node's `ProxyConfig` (from knowledge, **(unverified)**). (b) Reached only if the user turns on Node's built-in env proxy with a proxy URL that holds credentials, and the config is invalid. A stdio server's stderr then lands in the MCP client's logs. The repository sets no proxy. That Node's built-in proxy is opt-in on 24.x (`NODE_USE_ENV_PROXY` / `--use-env-proxy`) is from knowledge **(unverified)**. → SEC-T784-01 |
| CVE-2026-123877 | MEDIUM | `https.Agent` client: omitted `ca` and `ca: []` share a session key | No | **Unlikely; conditional** | Needs one Agent that serves both an omitted `ca` and `ca: []`. (a) No Node HTTPS client in the drift and sync jobs. `npm ci` passes no `ca: []`, and its install is sha512-locked, so a swapped tarball fails anyway. (b) Whether any pinned package uses `https.Agent` with `ca: []` was not read **(unverified)**. `fetch` (undici) does not go through `https.Agent`. |
| CVE-2026-123875 | MEDIUM | http2 server, cancelled `respondWithFile` | No | No | No http2 server. |
| CVE-2026-123829 | LOW | Permission Model, recursive `fs.watch` (macOS and Windows) | No | No | No job or entry runs `--permission`. CI is Linux. |
| CVE-2026-123862 | LOW | zlib `params()` + `destroy()` | No | Unlikely | Not imported by the scripts read. Use in the pinned packages was not read **(unverified)**. The advisory calls it uncommon. |
| CVE-2026-106071 | LOW | Permission Model, wildcard `--allow-fs-read` over-grant | No | No | No `--permission` or `--allow-fs-*` flag in any job or entry. |

**The dependency updates** (the advisory gives no versions and no CVE ids):

| Update | (a) CI | (b) User | Reason |
|---|---|---|---|
| llhttp | No | Possible | It is the parser of `node:http` and `node:https`, server and client. No CI Node process makes a request or serves one. A user's `npx` server that uses `node:https` parses responses from GitLab, Brave, Supabase, toolradar or the npm registry, so exploiting it needs a malicious or on-path server behind TLS. The reason for the update was not read **(unverified)**. |
| undici | No | Possible | It is the engine behind global `fetch`. No CI script uses `fetch`. Whether any test under `tests/` does was not traced **(unverified)**. The `npx` servers probably use `fetch` **(unverified)**. Same attacker position as llhttp. |
| sqlite | No | No | No `node:sqlite` import in the scripts read. None expected in the stdio servers **(unverified)**. |

**What this means:**
- **CI:** nothing reached. The inputs are repository content and no Node process opens a socket.
- **Shipped:** the 11 server-side CVEs and the two Permission Model CVEs cannot be reached through these entries. CVE-2026-123871, and in principle CVE-2026-123877, llhttp and undici, can reach a user's own unpatched Node only under user-side conditions. The repository does not pin the user's Node, so the repository's part is to tell users which versions are fixed (SEC-T784-01).

## 2. The Alpine 3.24.4 notes

The announcement was published 2026-11-05 and covers 3.21.10, 3.22.8, 3.23.8 and 3.24.4. It names two fixes and no CVE ids. It says the releases "include security fixes across core components" and points to the git log for the full list, which I did not read **(unverified)**.

- **openssh: "Fixes a password authentication bypass in `openssh-server`."** This does not matter to CI. Neither CI image runs `sshd`, and no `apk add` line installs `openssh-server`. That neither image's base contains it is from knowledge of the official images, not read from their layers **(unverified)**.
- **apk-tools: "A security fix in apk-tools 3.0.9 and 2.14.13 to prevent crashing on certain malformed data."** This matters a little. Every Node-image job except `verify-knowledge-drift` runs `apk add` (`ca-chain-check-node`, `sync-no-diff`), and so do the Python-image jobs.
  - The impact is a crash, so the job fails closed. That is availability, not integrity.
  - The Python digest is already on 3.24.4 (`.gitlab-ci.yml:16`). The pinned Node digest is on 3.24.3 (`.gitlab-ci.yml:17`), so it lacks this fix.
  - Which apk-tools version 3.24 ships, and whether the malformed data is parsed before the index signature is checked, were not read **(unverified)**.
- **Not named:** openssl, ca-certificates, musl, busybox, nodejs. The CA store question stays under the CA-chain jobs (SEC-T756-02 and the T768 ids).

## 3. Grades

| Id | Grade now | Provisional? | Reason |
|---|---|---|---|
| **SEC-T756-05** | **SECURITY:LOW** (A06) | **No, final** | **Why it is not higher:** the advisory is now published and § 1 maps every CVE. None is reached by a CI job. The 11 server-side CVEs need an http2, https or TLS server, and no job runs one. The two Permission Model CVEs need `--permission`, which no job uses. The two client CVEs need a Node HTTP client with a proxy or a mixed `ca` policy, and the drift and sync jobs make no request. `npm ci` is integrity-locked. No tag job uses Node. **Why it is not closed:** the pinned image and Alpine's `nodejs` (24.22.1-r1) still run a Node line with known HIGH CVEs, a best-practice gap. The undici and llhttp update contents are unread. **What would raise it:** a Node job gains a network client or server, or the v24.22.3 notes show an undici or llhttp client bug on a path `npm ci` takes. **Closes when:** T785 lands the 24.22.3 image and T786 confirms it. Alpine's `nodejs` in `unit-tests` stays a residual until Alpine ships a fixed package, which T786 records. |
| **SEC-T756-06** | **SECURITY:LOW** (A06) | **No, final for what was read** | **What changed:** the notes are now read. Their only fix that touches CI is the apk-tools crash, a fail-closed DoS. The Node digest lacks it; the Python digest has it. The openssh fix does not apply. **Why the unread part does not keep it open:** the git-log "core components" are unread **(unverified)**, but T785 closes them anyway because it moves the Node base to 3.24.4 or later. **What would raise it:** an Alpine 3.24.4 fix to openssl, ca-certificates, musl or busybox that a Node-image job reaches. **Closes when:** T786 confirms the new Node base is 3.24.4 or later. The Python half is already done. |

## 4. The bump: wait for 24.22.3 (the plan stands)

**Ruling: wait for an official `node:24-alpine` image that carries 24.22.3. Do not take 24.22.2 or the 2026-11-05 digest now.**

**Why:**
- **24.22.2 brings no Node security fix.** The pinned 24.22.1 is the last security release before 24.22.3.
- **No CVE in the advisory is reached by CI**, so waiting leaves no reachable exposure open.
- **The only CI-relevant Alpine 3.24.4 fix is a crash that fails closed.** Whether the 2026-11-05 digest is even on 3.24.4 is **(unverified)**: the same-day timing suggests it, but I read no layer.
- **An interim bump costs a full cycle twice within days:** digest re-hash, pins, both CA-chain jobs, a security review.

**Upper bound on the wait (my suggestion, for the orchestrator and the user):**
- If no official image carries 24.22.3 by **2026-12-11**, or by the start of v11.0.0 release preparation if that comes first, the orchestrator asks the user whether to take the newest official digest anyway.
- The hard limit stays the image-review test: `ci_images_reviewed_on: 2026-11-06` plus 120 days fails after **2027-03-06** (register v12 § 4.3).
- On security grounds the v11.0.0 tag need not wait, because no tag job uses Node. Register v12 § 6.2 makes "both CA-chain jobs pass after the Node bump" a v11.0.0 checklist item, and that stays the release's rule.

## 5. What T785 must prove

1. **Digest.** Read the multi-arch index for `24.22.3-alpine3.24` and for `24-alpine` from the registry API, and show that both resolve to the same digest. Re-fetch the index body; its SHA-256 must equal the digest. Record the tag, the digest and the date read. Confirm the index has the runner's architecture (amd64; the runner arch itself is **(unverified)** here).
2. **Node version in the image.** Read the image config blob of the runner's architecture: `NODE_VERSION=24.22.3`. **Recommended:** also have one Node-image job print `node --version` in its log, so the MR pipeline shows the version that actually ran, not only the metadata. That is a CI change; it is the devops-engineer's call.
3. **Alpine version.** Read `/etc/alpine-release` from the base layer, or the `alpine3.24` directory and its `FROM` in the docker-library Dockerfile at the stanza's GitCommit. It must be 3.24.4 or later, which closes SEC-T756-06's Node half. Also record the installed `apk-tools` version from `/lib/apk/db/installed`, which must be at least the fixed 3.0.9 (or 2.14.13 for the 2.x line).
4. **`apk` pins.** Re-read the v3.24 APKINDEX (main and community) and show that each pinned package resolves:
   - `openssl~=3.5` and `git~=2.54` in `ca-chain-check-node` and `sync-no-diff`;
   - the Python-image pins, which are unchanged but run against the same branch index.
   - For `unit-tests`: report Alpine's `nodejs` and `npm` versions on v3.24 (today `nodejs` 24.22.1-r1). Change `nodejs~=24` / `npm~=11` only if the major or minor version moved. Do not wait for Alpine.
5. **CA control.**
   - Both `ca-chain-check-python` and `ca-chain-check-node` must pass in the MR pipeline on the new digest.
   - `--ca-release` must pass before and after `apk add`, and the node job must log the `sha256sum` of the shipped and live stores.
   - Report whether the new image now ships hashed `/etc/ssl/certs` entries. If it does, the node job's `--cafile`-only check (SEC-T768-03) misses a store that OpenSSL reads, and T785 must say so.
6. **The real Node consumers.** `verify-knowledge-drift` and `sync-no-diff` must pass on the new image.
7. **Text and tests.**
   - Update `.gitlab-ci.yml:13-20` and `ci_images_reviewed_on` in the same change. Line 17's "a Node security release is announced for 2026-11-11" becomes the 24.22.3 record.
   - `test_ci_hash_pins` and `test_publish_release` must pass, and the full suite must pass in a clean worktree.
   - The old digest `06d7adf3…` must appear nowhere afterwards (search the whole tree, including `docs/wiki/mcp-pin-bump-checklist.md`; compare SEC-T768-06).
   - The digest changes in one place only, the `default:` image at `.gitlab-ci.yml:42`.
8. **Scope.** No new job, no rule that matches a tag, and no runner, CI variable or project setting changed (plan-148 § Constraints).

## 6. New finding

| Id | Grade | OWASP | Location | Description | Remediation |
|---|---|---|---|---|---|
| **SEC-T784-01** | **SECURITY:LOW** | A06 | `implementation/knowledge/mcp/servers.yaml:74-75, 111-112, 123-124, 130-131, 138-142, 235-236, 252-253, 262-263`; the user-facing Node requirement in `implementation/PREREQUISITES.md` (line not found, see § 8) and the v11.0.0 release document | The eight `npx` entries run on the user's own Node, outside every pin in this repository. On an unpatched Node 22, 24 or 26, CVE-2026-123871 can write a proxy credential into an error message that lands in the MCP client's logs, if the user enables Node's built-in env proxy with credentials. CVE-2026-123877 and the undici and llhttp fixes are client-side and need a malicious or on-path server. The gitlab, brave, supabase and toolradar entries carry credentials over those clients. **Why LOW:** user-side conditions, and no server-side exposure. | Name the fixed Node versions (≥ 22.23.5, ≥ 24.22.3, ≥ 26.13.1) as the minimum for the MCP entries, in `PREREQUISITES.md` and in the v11.0.0 release document. Owner: technical-writer, routed with batch Q or Y. Window: the v11.0.0 release document. **Do not add a version check to the generated entries**: that changes the pinned argv form that `test_mcp_package_pins.py` approves, a larger change than this finding warrants. |

Example wording (a docs addition; nothing is removed):
```
Before: Node.js 24 (or another supported line) is required for the npx MCP servers.
After:  Node.js 22.23.5, 24.22.3 or 26.13.1 or later is required for the npx MCP servers
        (November 2026 Node security release). Older patch versions carry known
        HIGH CVEs and a proxy-credential disclosure (CVE-2026-123871).
```
The "Before" line is illustrative, because the current text was not read **(unverified)**.

## 7. Verdict

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
| LOW | 3 | 0 | 3 |

### Justification
- No CRITICAL, HIGH or MEDIUM finding exists. No Immutable Security Constraint is breached. No required control is omitted or weakened: this is a docs-only re-grade, with no change under review.
- SEC-T756-05 and SEC-T756-06 are final LOW. Both are already tracked in batch X, owner devops-engineer, triggered by the Node bump (T785/T786).
- SEC-T784-01 is new and not yet tracked, so the verdict is CONDITIONAL_PASS rather than PASS.

### Conditions (if CONDITIONAL_PASS)
- SEC-T784-01: owner=@technical-writer (routed by the orchestrator), remediation=state the fixed Node minimums in `PREREQUISITES.md` and the v11.0.0 release document, deadline=the v11.0.0 release document. Enter it as tracked-LOW in the next register (batch Q or Y).
- SEC-T756-05, SEC-T756-06: owner=@devops-engineer, remediation=T785 as § 5 describes, then T786 review, deadline=as § 4 (ask the user by 2026-12-11 if no official image exists; hard limit 2027-03-06).

### Blockers (if FAIL)
Not applicable. The non-blocking blockers are listed at the end.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | No (out of scope) | 0 |
| A02: Cryptographic Failures | Partial (TLS client and server CVEs mapped; CA store left to the CA jobs) | 0 |
| A03: Injection | No | 0 |
| A04: Insecure Design | No | 0 |
| A05: Security Misconfiguration | Partial (proxy, permission model) | 0 |
| A06: Vulnerable Components | Yes | 3 |
| A07: Auth Failures | Partial (CVE-2026-123872 and -123867, not reached) | 0 |
| A08: Data Integrity Failures | Partial (digest pins, the `npm ci` lock, apk-tools) | 0 |
| A09: Logging & Monitoring | Partial (CVE-2026-123871 log sink) | 0, counted under A06 as SEC-T784-01 |
| A10: SSRF | No | 0 |

### Compliance Checklist (scope: T784 only)
- [ ] OWASP Top 10 reviewed: partial, see the table above
- [x] Dependencies audited: the Node advisory and the Alpine 3.24.4 notes are mapped
- [ ] Authentication, authorization, input validation, headers, secrets: not in scope

## 8. Not verified **(unverified)**
1. **The `grep_content` tool failed on every call** (4 attempts). So I could not grep:
   - the rest of `sync.mjs` past line 40, for later imports, dynamic `import()`, `fetch`, `zlib` or `sqlite`. I rely on T756's earlier grep and on the static imports I read;
   - `tests/` for a Node server, a `fetch` call or a test that starts an `npx` server. A test-only localhost server would not change the grade, because no attacker reaches it;
   - `PREREQUISITES.md` for an existing Node version floor.
2. The versions and reasons of the llhttp, undici and sqlite updates. The v24.22.3 release notes were not read.
3. Whether the Docker Hub `24-alpine` digest of 2026-11-05 (`a34ab6d7…`) is built on Alpine 3.24.4. I read no layer.
4. The Alpine git log behind "security fixes across core components". Which apk-tools version 3.24 ships, and whether the malformed data is parsed before the signature check.
5. That `openssh-server` is absent from both bases, and that `git` on Alpine pulls it in neither (from knowledge).
6. That Node's built-in env proxy is opt-in on 24.x. That npm does not use Node's `ProxyConfig`. Whether the runner sets proxy variables (A-21's area; no runner setting was read).
7. Whether any pinned `npx` package uses `https.Agent` with `ca: []`, Node's built-in proxy, `zlib.params()` or `node:sqlite`, or opens a listening socket. For Playwright, its browser link was not read.
8. That the pinned digest `06d7adf3…` is Alpine 3.24.3 with Node 24.22.1. This comes from the 2026-10-22 record (`.gitlab-ci.yml:17`) and was not re-hashed or re-read here.
9. `index.json` was read only up to character 100,000. The entries I used were inside that range.
10. The runner's architecture (amd64 assumed).

## Blockers
- `BLK-T784-01`: the `security-audit` `grep_content` tool errors on every call. Type `technical`, severity `minor`. Effect: the items in § 8.1 stayed unverified; no grade depends on them. Suggestion: the orchestrator checks the server (ripgrep on PATH, the `root_dir` handling) before T786, which needs grep for the old-digest sweep.
- `BLK-T784-02`: no official image with 24.22.3 exists. Type `external`, severity `minor`. It blocks T785's start only, as plan-148 already records.

## Task completion
- **Artifact:** this text, for the orchestrator to commit as `docs/artifacts/security-review-t784-node-advisory-v1.md`. No file was changed.
- **Acceptance criteria:**
  - Every CVE is mapped to reached or not, with a reason: met (§ 1).
  - Each id has a grade and its reason: met (§ 3).
  - The bump ruling and T785's proof obligations are stated: met (§ 4, § 5).
- **Follow-up:** enter SEC-T784-01 in the next register. Before T786, check BLK-T784-01.

Sources:
- [Node.js November 2026 security releases](https://nodejs.org/en/blog/vulnerability/november-2026-security-releases)
- [Node.js dist index.json](https://nodejs.org/dist/index.json)
- [docker-library official-images, library/node](https://raw.githubusercontent.com/docker-library/official-images/master/library/node)
- [Alpine 3.21.10, 3.22.8, 3.23.8 and 3.24.4 released](https://alpinelinux.org/posts/alpine-3.21.10-3.22.8-3.23.8-3.24.4-released/)
- [Alpine package index, nodejs v3.24](https://pkgs.alpinelinux.org/packages?name=nodejs&branch=v3.24&arch=x86_64)
