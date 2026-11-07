# Artifact: mcp-pin-audit-v10-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: devops-engineer (T755). **Date**: 2026-11-06. **Owner**: devops-engineer.
- **Task**: T755 (`docs/tasks/task-T755.md`), plan `docs/plans/plan-145-release-v10.md` (wave 1, item 3).
- **Based on**: `implementation/knowledge/mcp/servers.yaml` and `scripts/audit-mcp-pins.py` at `16ea3418` (both unchanged since `6d4abc1b`: `git diff` is empty); `docs/artifacts/brave-audit-acceptance-v3.md`; `docs/artifacts/mcp-pin-audit-v9-v1.md` (shape and method); ADR-011.
- **Scope**: report only. No pin, `servers.yaml`, CI image or acceptance was changed or renewed. No `docker` command was run and no image layer was pulled.

## 1. Summary

- **MCP pin set: no new HIGH, no expired acceptance.** Without `--accept` the audit exits 1; with the seven `--accept` entries of `brave-audit-acceptance-v3.md` it exits 0. The ids npm reports through the Brave pin are exactly those seven, and the negative control fails as it should.
- **Brave**: `npm view @brave/brave-search-mcp-server version` gives **2.1.4** on 2026-11-06, so condition (a) of the expiry has not happened. Condition (b), 2027-01-30, is 85 days away.
- **The moderates through `@modelcontextprotocol/server-filesystem` are covered by nothing** (`GHSA-3g3m-2fjr-6pw4`, `GHSA-g3hv-75wg-m249`; section 4). They pass the gate only because they are below `--audit-level high`.
- **Changed since v9**: a clean path for those moderates now exists. `server-filesystem@2.2.0` audits at zero findings in a scratch lock tree (section 4). It is not applied; a pin bump is not part of this task.
- **Python**: `pip-audit` was really run this time and finds nothing (section 5).
- **Manual reads**: no advisory covers `server-memory@1.0.0`, `server-sequential-thinking@1.0.0` or `server-filesystem@1.0.0` (section 6).
- **Images: BLOCKER CANDIDATE, for the orchestrator (section 7).** `servers.yaml` has no docker pin, so the script's docker notice has no target. The only digest-pinned images in the repository are the two CI images, and I checked those instead. The pinned `python:3.12-alpine` digest holds Python 3.12.15, and 3.12.16 is a security release with four non-Windows CVEs, computed CVSS 4.0 up to 9.4. These are new and in no acceptance. Nobody has graded them for this project, and they are not MCP pins. Whether they count as a "new HIGH" under the plan is not decided here.
- **Pending**: Node.js announces security releases for 2026-11-11, highest severity in 24.x HIGH (section 7).

## 2. Commands run

Date of all runs: 2026-11-06 (from 22:18 UTC). npm 11.17.0, node 24.19.0, Python 3.12.3. Registry `https://registry.npmjs.org/`, with empty user and global npm configuration. Every npm install used `--package-lock-only --ignore-scripts`. No audited package was executed.

| # | Command | Purpose |
|---|---------|---------|
| C1 | `python3 scripts/audit-mcp-pins.py audit --audit-level high` | The gate, no `--accept` |
| C2 | The same with the seven `--accept` entries of the acceptance | The gate as the acceptance names it |
| C3 | C2 without `GHSA-f897-62hf-6gxq` | Negative control |
| C4 | Per pin: a one-dependency `package.json`, `npm install --package-lock-only --ignore-scripts --no-audit --no-fund`, `npm audit --json` | Attribution per package (the script has no per-package mode) |
| C5 | `npm view` of `version`, `dist-tags`, `versions`, `time` | Newest versions and dates |
| C6 | `python3 scripts/audit-mcp-pins.py generate DIR`, then `pip-audit -r requirements-uvx.txt --no-deps` | The Python pin, as the script asks |
| C7 | `uv pip compile` (`--only-binary :all: --universal --python-version 3.12`), then `pip-audit --no-deps` on the 34-pin tree and on the 35-entry in-repo lock, with the default source and with `-s osv` | What `--no-deps` on one line does not see |
| C8 | GitHub Advisory Database REST API (`/advisories`, types `reviewed`, `unreviewed`, `malware`, by package and by `package@version`); OSV `query` | Manual advisory reads |
| C9 | Docker Hub and registry HTTP API: tag, index, one amd64 manifest and its config JSON. No layer | Image digests, without a pull |

`pip-audit` was not installed. I installed 2.10.1 into a virtual environment in the scratch directory (`uv pip install`). The `cvss` library went into the same environment, only to compute the scores in section 7.

## 3. npm audit, and each finding against the acceptance

### 3.1 C1: without `--accept`, exit 1

```text
npm pins audited: 8 (audit level: high)
  high     @brave/brave-search-mcp-server (direct: True): via a dependency
  high     @modelcontextprotocol/sdk (direct: False): MCP TypeScript SDK: OAuth client could send credentials to an authorization server chosen by the MCP server [>=1.12.0 <1.31.0] https://github.com/advisories/GHSA-6qxp-vccf-f47h; MCP TypeScript SDK: Experimental tasks were not tied to the session that created them [>=1.24.0 <1.32.0] https://github.com/advisories/GHSA-22jm-h49p-29qw; MCP TypeScript SDK: One HTTP request within the default size limit could exhaust server memory during validation [>=1.3.0 <1.32.0] https://github.com/advisories/GHSA-46jr-4wx8-v453; MCP TypeScript SDK: Server bearer authentication accepted tokens issued for another service [>=1.6.0 <1.32.0] https://github.com/advisories/GHSA-rvq5-wwqv-78pq; MCP TypeScript SDK: HTTP server transports and handlers did not limit request body size or JSON-RPC batch length [>=1.10.0 <1.30.1] https://github.com/advisories/GHSA-f897-62hf-6gxq; MCP TypeScript client SDK: HTTP client transports and OAuth requests followed cross-origin redirects and re-sent custom headers and request bodies [<1.32.0] https://github.com/advisories/GHSA-6prh-2h8m-c8cw
  moderate @modelcontextprotocol/server-filesystem (direct: True): via a dependency
  moderate glob (direct: False): Glob: AbortSignal cancellation bypass allows post-timeout filesystem traversal [>=9.0.0 <=14.0.1] https://github.com/advisories/GHSA-3g3m-2fjr-6pw4
  moderate minimatch (direct: False): minimatch has potential denial of service via globparts amplification [>=7.0.0 <11.0.1] https://github.com/advisories/GHSA-g3hv-75wg-m249
  high     zod (direct: False): Zod can exhaust memory while validating oversized constrained collections [<4.6.6] https://github.com/advisories/GHSA-mrhx-c7xc-m3w5
MANUAL ADVISORY READ (SEC-T646-06): these moved from calendar versions to 1.0.0; semver sorts the
calendar-form advisory ranges ABOVE them, so the npm audit result for them is not conclusive.
Read the advisories by hand (GitHub Advisory Database, ecosystem npm) and record the date:
  - @modelcontextprotocol/server-memory@1.0.0
  - @modelcontextprotocol/server-sequential-thinking@1.0.0
  - @modelcontextprotocol/server-filesystem@1.0.0
PyPI pins are not covered by npm: run `pip-audit -r requirements-uvx.txt --no-deps` on the file written by `generate DIR`.
docker digests are not covered either: check the image's release notes and advisories by hand.
result: FINDINGS
```

### 3.2 C2: with the seven `--accept` entries, exit 0

```text
npm pins audited: 8 (audit level: high)
  ACCEPTED high     @brave/brave-search-mcp-server (direct: True): via a dependency
  ACCEPTED high     @modelcontextprotocol/sdk (direct: False): MCP TypeScript SDK: OAuth client could send credentials to an authorization server chosen by the MCP server [>=1.12.0 <1.31.0] https://github.com/advisories/GHSA-6qxp-vccf-f47h; MCP TypeScript SDK: Experimental tasks were not tied to the session that created them [>=1.24.0 <1.32.0] https://github.com/advisories/GHSA-22jm-h49p-29qw; MCP TypeScript SDK: One HTTP request within the default size limit could exhaust server memory during validation [>=1.3.0 <1.32.0] https://github.com/advisories/GHSA-46jr-4wx8-v453; MCP TypeScript SDK: Server bearer authentication accepted tokens issued for another service [>=1.6.0 <1.32.0] https://github.com/advisories/GHSA-rvq5-wwqv-78pq; MCP TypeScript SDK: HTTP server transports and handlers did not limit request body size or JSON-RPC batch length [>=1.10.0 <1.30.1] https://github.com/advisories/GHSA-f897-62hf-6gxq; MCP TypeScript client SDK: HTTP client transports and OAuth requests followed cross-origin redirects and re-sent custom headers and request bodies [<1.32.0] https://github.com/advisories/GHSA-6prh-2h8m-c8cw
  moderate @modelcontextprotocol/server-filesystem (direct: True): via a dependency
  moderate glob (direct: False): Glob: AbortSignal cancellation bypass allows post-timeout filesystem traversal [>=9.0.0 <=14.0.1] https://github.com/advisories/GHSA-3g3m-2fjr-6pw4
  moderate minimatch (direct: False): minimatch has potential denial of service via globparts amplification [>=7.0.0 <11.0.1] https://github.com/advisories/GHSA-g3hv-75wg-m249
  ACCEPTED high     zod (direct: False): Zod can exhaust memory while validating oversized constrained collections [<4.6.6] https://github.com/advisories/GHSA-mrhx-c7xc-m3w5
acceptances (reviewed, expiring):
  accepted GHSA-22jm-h49p-29qw until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-46jr-4wx8-v453 until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-6prh-2h8m-c8cw until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-6qxp-vccf-f47h until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-f897-62hf-6gxq until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-mrhx-c7xc-m3w5 until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-rvq5-wwqv-78pq until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
MANUAL ADVISORY READ (SEC-T646-06): these moved from calendar versions to 1.0.0; semver sorts the
calendar-form advisory ranges ABOVE them, so the npm audit result for them is not conclusive.
Read the advisories by hand (GitHub Advisory Database, ecosystem npm) and record the date:
  - @modelcontextprotocol/server-memory@1.0.0
  - @modelcontextprotocol/server-sequential-thinking@1.0.0
  - @modelcontextprotocol/server-filesystem@1.0.0
PyPI pins are not covered by npm: run `pip-audit -r requirements-uvx.txt --no-deps` on the file written by `generate DIR`.
docker digests are not covered either: check the image's release notes and advisories by hand.
result: no finding at or above the audit level
```

### 3.3 C3: negative control, exit 1

The six-entry command ends in `result: FINDINGS`, with two lines at `high` that are not `ACCEPTED`. The acceptance therefore still depends on each id.

### 3.4 Findings

"Named" means that the id is in the accepted table of `brave-audit-acceptance-v3.md`. Severities are npm's.

| Finding | Id | npm severity | Comes through | New? | In the acceptance |
|---------|----|--------------|---------------|------|-------------------|
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-6qxp-vccf-f47h` | high | Brave pin | no | **accepted** |
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-22jm-h49p-29qw` | high | Brave pin | no | **accepted** |
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-46jr-4wx8-v453` | high | Brave pin | no | **accepted** |
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-f897-62hf-6gxq` | high | Brave pin | no | **accepted** |
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-6prh-2h8m-c8cw` | moderate | Brave pin | no | **accepted** |
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-rvq5-wwqv-78pq` | moderate | Brave pin | no | **accepted** |
| `zod` 4.3.6 | `GHSA-mrhx-c7xc-m3w5` | high | Brave pin | no | **accepted** |
| `@brave/brave-search-mcp-server` 2.1.4 | none of its own: "via a dependency" (the sdk and zod above) | high | the pin itself | no | covered by the seven; printed `ACCEPTED` in C2 |
| `glob` 13.0.7 | `GHSA-3g3m-2fjr-6pw4` | moderate | `server-filesystem` | no (in the v9 audit) | **not accepted**: mentioned in its T712 run as "not part of this decision" |
| `minimatch` 10.2.6 | `GHSA-g3hv-75wg-m249` | moderate | `server-filesystem`, also through `glob` | no (in the v9 audit) | **not accepted**: same |
| `@modelcontextprotocol/server-filesystem` 1.0.0 | none of its own: "via a dependency" (`glob`, `minimatch`) | moderate | the pin itself | no | **not accepted** |

The GitHub Advisory Database agrees on the Brave side (C8): `affects=zod@4.3.6` returns exactly `GHSA-mrhx-c7xc-m3w5`, and `affects=@modelcontextprotocol/sdk@1.30.0` returns exactly the six sdk ids. This is also the positive control for the empty results in section 6.

### 3.5 Per pin (C4)

| Server | Package | Pinned | High | Moderate | sdk / zod resolved | Newest |
|--------|---------|--------|------|----------|--------------------|--------|
| gitlab | `@zereight/mcp-gitlab` | 2.2.5 | 0 | 0 | 1.32.2 / 4.6.7 | 2.3.22 |
| playwright | `@playwright/mcp` | 0.0.83 | 0 | 0 | none / none | 0.0.84 |
| memory | `@modelcontextprotocol/server-memory` | 1.0.0 | 0 | 0 | 1.32.2 / 4.6.7 | 2.1.0 |
| sequential-thinking | `@modelcontextprotocol/server-sequential-thinking` | 1.0.0 | 0 | 0 | 1.32.2 / 4.6.7 | 2.1.1 |
| **brave** | **`@brave/brave-search-mcp-server`** | **2.1.4** | **3** | 0 | **1.30.0 / 4.3.6** | **2.1.4** |
| filesystem | `@modelcontextprotocol/server-filesystem` | 1.0.0 | 0 | 3 | 1.32.2 / 4.6.7 | 2.2.0 |
| supabase | `@supabase/mcp-server-supabase` | 0.13.0 | 0 | 0 | none / 4.6.7 | 0.16.1 |
| toolradar | `toolradar-mcp` | 2.1.0 | 0 | 0 | none / none | 2.4.0 |

High and moderate count npm's vulnerable package entries, not advisories. Brave 2.1.4 is still the only pin that pulls the vulnerable sdk and zod, which is the scoping that the acceptance requires. `npx` resolves ranges again at launch, so a later date can differ for any package that does not pin exactly.

### 3.6 State of the acceptance

| Item | Read on 2026-11-06 | Result |
|------|--------------------|--------|
| Condition (a), first release above 2.1.4 | `version` and `dist-tags.latest` are 2.1.4; `versions` ends `2.1.0, 2.1.3, 2.1.4`; `latest` is the only dist-tag; 2.1.4 was published 2026-09-17T14:48:15Z | not reached |
| Condition (b), 2027-01-30 | 85 days ahead; the script accepted the date | not reached |
| Stdio-only launch | `python3 -m unittest tests.functional.test_mcp_package_pins`: 49 tests, OK | holds |
| Operators do not set `BRAVE_MCP_TRANSPORT` or `BRAVE_MCP_HOST` | not checkable from here | **(unverified)** |
| A re-audit trigger: new advisory on sdk 1.30.0 or zod 4.3.6 | none beyond the seven (section 3.4) | not triggered |

Upstream: the GitHub tag list and the releases list both start at `v2.1.4` (2026-09-17). The `package.json` on `main` still says version 2.1.4 and declares `@modelcontextprotocol/sdk` 1.32.2 and `zod` 4.6.7. The fix therefore still looks unpublished. **(unverified)**: read once over HTTP, not from a clone.

ADR-011 is a separate clock. The acceptance's date above is the script's per-advisory mechanism, which ADR-011 leaves unchanged. The overall finding SEC-T702-09 is a `SECURITY:MEDIUM` that the user accepted for v9.0.0 only, so it needs the user again for v10.0.0 (register v11, MEDIUM end dates). That belongs to T756 and is not an expiry in the sense of this audit.

## 4. The moderates through `server-filesystem`: what covers them

**Nothing covers them.**

- `brave-audit-acceptance-v3.md` names both ids only in its run log, as "not part of this decision". No `--accept` exists for them, and one could not name them under the Brave pin.
- The ids appear in only two documents under `docs`, `implementation` and `scripts`: that acceptance and `mcp-pin-audit-v9-v1.md`. `docs/wiki/mcp-pin-bump-checklist.md` mentions the moderates by package name in a log line. `tracked-debt-register-v11.md` has neither the ids nor `server-filesystem`, and they are not among its five MEDIUMs.
- They have no `SEC-*` id and no Security Engineer grade. npm's "moderate" is not a `SECURITY:*` grade.
- The gate passes them only through `--audit-level high`.

For the Security Engineer: if these are graded `SECURITY:MEDIUM`, ADR-011 requires a fix before the release or the user's acceptance for v10.0.0. I do not grade them here.

| Id | GitHub Advisory Database | Range and fix | Resolved here |
|----|--------------------------|---------------|---------------|
| `GHSA-3g3m-2fjr-6pw4` | medium, published 2026-10-30, not withdrawn. "Glob: AbortSignal cancellation bypass allows post-timeout filesystem traversal" | `>= 9.0.0, <= 14.0.1`; fixed 14.0.2 | `glob` 13.0.7 |
| `GHSA-g3hv-75wg-m249` | medium, published 2026-10-30, updated 2026-11-04, not withdrawn. "minimatch has potential denial of service via globparts amplification" | `>= 7.0.0, < 11.0.1`; fixed 11.0.1 | `minimatch` 10.2.6 |

Input for the grading, from a read of the `server-filesystem@1.0.0` tarball and `minimatch@10.2.6` (text search, read, not run, no call-graph analysis):

- `glob`: `package.json` declares it (`^13.0.6`), but `dist/*.js` has no import of it and no use of `signal` or `AbortSignal`. The advisory needs a caller that relies on abort.
- `minimatch`: `dist/lib.js:471,475` and `dist/server.js:478-484` call it with `{ dot: true }`, on patterns from tool arguments. The advisory describes `optimizationLevel >= 2`; `minimatch@10.2.6` defaults to `optimizationLevel = 1` (`dist/esm/index.js:332,652`), and the calls set no level. Whether another path in the advisory applies at level 1 was not analysed **(unverified)**.
- Exposure: `filesystem` is an `extended` server that no agent lists (`AGENTS.md`). It still ships in the generated configurations of the platforms that opt in.

**Upgrade path.** npm now reports `fixAvailable` as `server-filesystem@2.2.0`, semver major; the v9 audit reported `false`. A one-dependency scratch audit of 2.2.0 (lock tree only, not run) gives zero findings at every level, with `minimatch` 11.0.5 and no `glob` in the tree. Whether 2.2.0 behaves the same as 1.0.0 was not checked, and a bump would need the pin-bump checklist and a root refresh.

## 5. Python pins

| Scope | Input | Source | Result |
|-------|-------|--------|--------|
| git (`uvx`), script form | `requirements-uvx.txt` written by `generate DIR`: the one line `mcp-server-git==2026.10.10` | `pip-audit` default; `-s osv` | `No known vulnerabilities found`, exit 0; both |
| git, resolved tree | 34 pins, resolved 2026-11-06, wheels only, `--universal`, Python 3.12 (including `mcp` 1.30.0, `starlette` 1.10.0, `cryptography` 50.0.2, `gitpython` 3.2.1, `pydantic` 2.14.3) | `pip-audit` default; `-s osv` | `No known vulnerabilities found`, exit 0; both |
| security-audit, poc-security-audit, context-retriever | `implementation/runtime/security/requirements-mcp-server.lock.txt`, 35 entries, byte-identical to the one under `runtime/memory` | `pip-audit` default; `-s osv` | `No known vulnerabilities found`, exit 0; both |
| Control | `jinja2==2.10` | `pip-audit` default | `Found 12 known vulnerabilities in 1 package`, exit 1 |

Every `pip-audit --no-deps` run also printed the tool's warning that it encourages hashed pins. The GitHub Advisory Database (`ecosystem=pip`, `mcp-server-git@2026.10.10`) returns nothing either.

Limits: the script form audits one line only, so its result alone says nothing about dependencies. `uvx` resolves again at launch without a lock file, so another interpreter or date can give another tree.

## 6. Manual advisory reads (SEC-T646-06)

Read on **2026-11-06** (22:19 UTC) from the GitHub Advisory Database REST API, `ecosystem=npm`, with OSV as the second source.

| Package | Advisories for any version | `affects=` the pin, reviewed / unreviewed / malware | OSV for the pin | 1.0.0 published | Conclusion |
|---------|----------------------------|-----------------------------------------------------|-----------------|-----------------|------------|
| `@modelcontextprotocol/server-memory@1.0.0` | none | none / none / none | none | 2026-10-11 | no advisory |
| `@modelcontextprotocol/server-sequential-thinking@1.0.0` | none | none / none / none | none | 2026-10-11 | no advisory |
| `@modelcontextprotocol/server-filesystem@1.0.0` | `GHSA-hc55-p739-j48w`, `GHSA-q66q-fx2p-7w4m`, both high | none / none / none | none | 2026-10-11 | neither covers 1.0.0 |

For `server-filesystem`, both advisories have the ranges `<= 0.6.2` and `>= 2025.1.14, < 2025.7.1` (fixed 2025.7.1, published 2025-07-01). The v9 audit listed only the calendar range. Version 1.0.0 is in neither range, and it was published 15 months after the fix, which is the case the script warns about. As a further check, its tarball has the corresponding code: the allowed-directory check compares with a trailing separator (`dist/path-validation.js:86`, the prefix-match issue), and `dist/lib.js:141-143` checks the real path (the symlink issue). That was read, not run, and I matched the code to the advisories by their titles, not against the upstream patches. Neither is a finding for this pin.

The same `package@version` query for the other five npm pins also returns nothing from the advisory database or OSV. The Brave result is about the pin itself; its advisories are on the dependencies (section 3.4).

## 7. Images, checked by hand

`python3 scripts/audit-mcp-pins.py list` shows no docker pin, and `servers.yaml` has no `command: docker`. The script's line "docker digests are not covered either" is printed unconditionally (`audit-mcp-pins.py:420`). **For the MCP pin set there is no image to check**, the same as in the v9 audit.

I widened the check to the only digest-pinned images in the repository, the CI images in `.gitlab-ci.yml` (`ci_images_reviewed_on: 2026-10-22`). That is my reading of the brief, not the script's scope. Read over HTTP on 2026-11-06; the versions come from the amd64 config JSON only.

| Image | Pinned digest | Built | Holds | Tag now points to | Used at |
|-------|---------------|-------|-------|-------------------|---------|
| `node:24-alpine` | `sha256:06d7adf3e0ef61a13f1d28682726366f97a15aa1888c934d3ecec86c33918b53` | 2026-10-21 | Node 24.22.1, Alpine 3.24.3 | `sha256:a34ab6d7f6f4813f4d0c5469d74685604b962fbdbf5793a7bc7b4998ecb867c8` (2026-11-05) | `.gitlab-ci.yml:40` |
| `python:3.12-alpine` | `sha256:92abd2ba1bdfb48b1e2ac224b582dd1558d0d4bb11c903b126b5bf9c448fd656` | 2026-10-21 | Python 3.12.15, Alpine 3.24.3 | `sha256:e064671ca452259bab50e8e2c7bd896e39e9a343bb06ca25234adf6fe18d0fc7` (2026-11-06; the same digest as `3.12.16-alpine`) | `.gitlab-ci.yml:51,92,134,145,180,198,222,245` |

### 7.1 Findings: all new, none in the acceptance

| Finding | Id | Severity as read | Status |
|---------|----|------------------|--------|
| Python 3.12.16 (a security release, 2026-10-25) distrusts compromised eMudhra intermediate CA keys | `CVE-2026-115557` | computed CVSS 4.0 **9.4 Critical** | **new** |
| Bundled Expat updated to 2.9.0 | `CVE-2026-77214` | computed **8.3 High** | **new** |
| Bundled Expat updated to 2.9.0 | `CVE-2026-102633` | computed **8.2 High** | **new** |
| `tarfile.tar_filter`: links replacing the destination | `CVE-2026-114583` | computed 6.9 Medium | **new** |
| Node.js security releases announced for 2026-11-11 | no id published | the announcement: highest in 24.x is **HIGH** | **new, pending**: nothing to apply yet |
| Alpine 3.24.4, released 2026-11-05; the digests hold 3.24.3 | not read | **(unverified)** | **new**: content not read |

The release notes also list `CVE-2024-3220`, which they scope to Windows, so it does not apply to an Alpine image.

How to read those scores: I computed them with the `cvss` library from the CVSS 4.0 vectors on OSV. They are not grades that an advisory states, and none is a `SECURITY:*` grade. Applicability is **(unverified)**:

- That each CVE is present in the pinned 3.12.15 is inferred from the 3.12.16 notes.
- Whether the image uses the bundled Expat or a system one was not checked.
- Whether any CI job reaches the affected code was not analysed.

These images run CI jobs. They are not MCP pins and are not in the launch configuration. Node 24.22.2 (2026-10-28), the newest 24.x, shows no CVE or security marker in its notes. Node 24.22.1, in the pin, is itself a security release.

**This goes to the orchestrator, undecided.** The plan's rule is "a new HIGH blocks", and the plan's T755 line includes the image digests. Whether a CVE in a CI image counts, and who grades it, is for the orchestrator, the Security Engineer and the user.

### 7.2 Not checked

- Alpine package CVEs inside either digest: no scanner was run and no layer was read.
- Platforms other than amd64.
- The tag-only images, which are not digest-pinned: `deploy/docker-compose-t226.yml` (CWSO `v0.5.2` images, `python:3.11-slim`), `deploy/docker-compose-context-retriever.yml` (`python:3.12-slim`), `implementation/adapters/sia-target/Dockerfile` (`python:3.12-slim-bookworm`). `deploy/docker-compose-t226.build.yml` was not opened.

## 8. Not covered

- **Remote servers** (`context7`, `hindsight`, `cwso`, `hf-mcp-server`): URL entries with no package pin. No result is claimed.
- **`npm audit signatures`** (`--signatures`) and the script's `provenance` command were not run; they are outside the brief.
- **Runtime downloads** (Playwright browsers) are in no lock tree.
- **`implementation/runtime/memory/requirements.txt`** belongs to the index builder, not to an MCP pin, and was not audited.
- **Reachability** of the accepted advisories was not re-derived. The grades in the acceptance are the Security Engineer's of 2026-11-01.
