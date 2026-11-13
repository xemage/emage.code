# Artifact: mcp-pin-audit-v11-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: devops-engineer (T814). **Date**: 2026-11-13. **Owner**: devops-engineer.
- **Task**: T814 (`docs/tasks/task-T814.md`), plan `docs/plans/plan-161-release-v11.md` (wave 1, § Task Decomposition item 2).
- **Based on**: `implementation/knowledge/mcp/servers.yaml`, `scripts/audit-mcp-pins.py` and `.gitlab-ci.yml` at `f41bb087` (no diff to `9acf84dc`, the commit of the last green develop pipeline; `servers.yaml` and the script last changed in `44e7c967`); `docs/artifacts/brave-audit-acceptance-v4.md` (the seven `--accept` entries, expiry 2027-01-30); `docs/artifacts/mcp-pin-audit-v10-v1.md` (shape and method); `docs/wiki/mcp-pin-bump-checklist.md` § 2 to § 4; `docs/artifacts/tracked-debt-register-v16.md` (§ 6.2 item 42; SEC-T786-01, batch X); `docs/artifacts/security-review-t756-accepted-mediums-v1.md` (SEC-T756-07).
- **Scope**: report only. No pin, `servers.yaml` entry, lock file, CI image, gate, acceptance or test was changed. No `docker` command was run and no image layer was pulled.

## 1. Summary

- **MCP pin set: no new HIGH, no expired or voided acceptance.** Without `--accept` the audit exits 1; with v4's seven `--accept` entries it exits 0. Every advisory at or above high is one of v4's seven. The negative control (six entries) exits 1.
- **Brave**: npm's newest `@brave/brave-search-mcp-server` is **2.1.4** on 2026-11-13, so expiry condition (a) of v4 has not occurred (§ 6.2 item 42, TD-T808-02). Condition (b), 2027-01-30, is 78 days away.
- **New finding, below HIGH (section 5)**: `opentelemetry-api==1.45.1` in `implementation/runtime/security/requirements-mcp-server.lock.txt` (also the byte-identical lock under `runtime/memory`) is affected by `GHSA-mf5v-w3w3-f6cg` / `CVE-2026-126360`, GitHub severity **medium**, CVSS 3.1 5.3 (`AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`), published **2026-11-13T16:43Z**, fixed in 1.45.2 (on PyPI since 2026-10-29). It is in no acceptance and in no register. Grade proposal: `SECURITY:LOW` (A06), for the Security Engineer to confirm. Not a release blocker under the plan's rule (not HIGH).
- **`mcp-server-git` (`uvx`)**: `pip-audit` finds nothing, on the script's one line and on the 34-pin resolved tree.
- **Manual reads**: no advisory covers `server-memory@1.0.0`, `server-sequential-thinking@1.0.0` or `server-filesystem@1.0.0` (section 6). The filesystem moderates `GHSA-3g3m-2fjr-6pw4` and `GHSA-g3hv-75wg-m249` are unchanged; since v10 they are graded SEC-T756-07, `SECURITY:LOW`.
- **CI images (section 7)**: both pinned digests resolve. `node:24-alpine@sha256:116b800c…` holds Node **24.22.3** (the security release of 2026-11-10) and is still the tag's digest. `python:3.12-alpine@sha256:e064671c…` holds Python **3.12.16**, the newest 3.12; the tag moved to `sha256:c5ba3dee…`, but only its riscv64 entry differs, the amd64 manifest is identical. Both are on Alpine 3.24.4. The v10 blocker candidate (Python 3.12.15) and the pending Node release are resolved by the current pins.
- **SEC-T786-01 (section 8)**: Alpine `v3.24/main` now ships `nodejs` **24.22.3-r0** for x86_64. The `unit-tests` job installs `nodejs~=24` unpinned with `--no-cache`, so its next run should install it; that a `unit-tests` log shows it is **(unverified)**: no job log was read.
- **CA-chain (section 9)**: `ca-chain-check-node` and `ca-chain-check-python` passed on develop pipeline 3066295917 (`9acf84dc`, 2026-11-13); the image digests have not changed since.
- **`ci_images_reviewed_on: 2026-11-11`**: last passing day **2027-03-11**, `test_ci_hash_pins` fails from **2027-03-12** (118 days ahead).
- **Nothing found here blocks the release.**

## 2. Commands run

Date of all runs: 2026-11-13, from 20:04 UTC. npm 11.17.0, node 24.19.0, Python 3.12.3. Registry `https://registry.npmjs.org/`; the `npm view` calls used an empty user and global npm configuration. The script's own runs use `--package-lock-only --ignore-scripts` (as in v10); no audited package was executed.

| # | Command | Exit |
|---|---------|------|
| C1 | `python3 scripts/audit-mcp-pins.py audit --audit-level high` | 1 |
| C2 | C1 with the seven `--accept` entries of `brave-audit-acceptance-v4.md`, character for character as its gate command | 0 |
| C3 | C2 without `--accept GHSA-f897-62hf-6gxq:…` (negative control) | 1 |
| C4 | `python3 scripts/audit-mcp-pins.py generate <scratch>` | 0 |
| C5 | `pip-audit -r requirements-uvx.txt --no-deps`, default source and `-s osv` | 0, 0 |
| C6 | `uv pip compile --only-binary :all: --universal --python-version 3.12` of that file (34 pins), then `pip-audit --no-deps` | 0, 0 |
| C7 | `pip-audit -r implementation/runtime/security/requirements-mcp-server.lock.txt --no-deps`, default source and `-s osv`; control `jinja2==2.10` | 1, 1; control 1 |
| C8 | `npm view @brave/brave-search-mcp-server version dist-tags versions time.modified` | 0 |
| C9 | GitHub Advisory Database REST API (`/advisories?affects=…`, types `reviewed`, `unreviewed`, `malware`); OSV `query` | all HTTP 200 |
| C10 | Docker Hub registry HTTP API: index, amd64 manifest, config JSON of each pinned digest and of each tag; Hub tag API. No layer | all HTTP 200 |
| C11 | `nodejs.org/dist/index.json`; `endoflife.date/api/python/3.12.json`; Alpine `APKINDEX.tar.gz` of `v3.24` and `edge`, `main` and `community`, x86_64 | all read |
| C12 | `glab ci list --ref develop`; `glab api projects/:fullpath/pipelines/<id>` and `…/jobs` (read-only; job status only, no job log) | 0 |

`pip-audit` was not installed (`python3 -m pip_audit`: "No module named pip_audit"). As in v10, I installed `pip-audit==2.10.1` into a virtual environment in the session scratch directory (`uv venv`, `uv pip install`). No system package was installed.

## 3. npm audit, and each finding against the acceptance

### 3.1 C1: without `--accept`, exit 1 (advisory titles of the sdk line shortened)

```text
npm pins audited: 8 (audit level: high)
  high     @brave/brave-search-mcp-server (direct: True): via a dependency
  high     @modelcontextprotocol/sdk (direct: False): [the six sdk ids below]
  moderate @modelcontextprotocol/server-filesystem (direct: True): via a dependency
  moderate glob (direct: False): Glob: AbortSignal cancellation bypass allows post-timeout filesystem traversal [>=9.0.0 <=14.0.1] https://github.com/advisories/GHSA-3g3m-2fjr-6pw4
  moderate minimatch (direct: False): minimatch has potential denial of service via globparts amplification [>=7.0.0 <11.0.1] https://github.com/advisories/GHSA-g3hv-75wg-m249
  high     zod (direct: False): Zod can exhaust memory while validating oversized constrained collections [<4.6.6] https://github.com/advisories/GHSA-mrhx-c7xc-m3w5
result: FINDINGS
```

Advisory ids in the output, each once: `GHSA-22jm-h49p-29qw`, `GHSA-46jr-4wx8-v453`, `GHSA-6prh-2h8m-c8cw`, `GHSA-6qxp-vccf-f47h`, `GHSA-f897-62hf-6gxq`, `GHSA-rvq5-wwqv-78pq` (sdk), `GHSA-mrhx-c7xc-m3w5` (zod), `GHSA-3g3m-2fjr-6pw4`, `GHSA-g3hv-75wg-m249` (filesystem moderates). The output also carries the script's fixed notices (manual read list, PyPI, docker); they are sections 5 to 7.

### 3.2 C2: with the seven `--accept` entries, exit 0

```text
  ACCEPTED high     @brave/brave-search-mcp-server (direct: True): via a dependency
  ACCEPTED high     @modelcontextprotocol/sdk (direct: False): [the six sdk ids]
  moderate @modelcontextprotocol/server-filesystem (direct: True): via a dependency
  moderate glob (direct: False): … GHSA-3g3m-2fjr-6pw4
  moderate minimatch (direct: False): … GHSA-g3hv-75wg-m249
  ACCEPTED high     zod (direct: False): … GHSA-mrhx-c7xc-m3w5
acceptances (reviewed, expiring):
  accepted GHSA-22jm-h49p-29qw until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-46jr-4wx8-v453 until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-6prh-2h8m-c8cw until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-6qxp-vccf-f47h until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-f897-62hf-6gxq until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-mrhx-c7xc-m3w5 until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
  accepted GHSA-rvq5-wwqv-78pq until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4
result: no finding at or above the audit level
```

### 3.3 C3: negative control, exit 1

Without the `GHSA-f897-62hf-6gxq` entry the sdk and Brave lines print `high` without `ACCEPTED` and the run ends `result: FINDINGS`; six acceptances are listed. The gate still depends on each id.

### 3.4 Findings

Severities are the GitHub Advisory Database's (C9, `affects=package@version`); "in v4" means the id is one of the seven accepted in `brave-audit-acceptance-v4.md`.

| Package | Id | Severity | Through | New? | Covered by |
|---------|----|----------|---------|------|------------|
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-6qxp-vccf-f47h` | high | Brave pin | no | **in v4** |
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-22jm-h49p-29qw` | high | Brave pin | no | **in v4** |
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-46jr-4wx8-v453` | high | Brave pin | no | **in v4** |
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-f897-62hf-6gxq` | high | Brave pin | no | **in v4** |
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-6prh-2h8m-c8cw` | medium | Brave pin | no | **in v4** |
| `@modelcontextprotocol/sdk` 1.30.0 | `GHSA-rvq5-wwqv-78pq` | medium | Brave pin | no | **in v4** |
| `zod` 4.3.6 | `GHSA-mrhx-c7xc-m3w5` | high | Brave pin | no | **in v4** |
| `glob` 13.0.7 | `GHSA-3g3m-2fjr-6pw4` | medium | `server-filesystem` | no | SEC-T756-07 (`SECURITY:LOW`); below the audit level |
| `minimatch` 10.2.6 | `GHSA-g3hv-75wg-m249` | medium | `server-filesystem` | no | SEC-T756-07 (`SECURITY:LOW`); below the audit level |

The advisory database returns exactly these sets for `zod@4.3.6` and `@modelcontextprotocol/sdk@1.30.0`, which is the positive control for the empty reads of section 6. **Every advisory at or above high is one of v4's seven; none is new.**

### 3.5 State of the acceptance (v4)

| Item | Read on 2026-11-13 | Result |
|------|--------------------|--------|
| Condition (a), first Brave release above 2.1.4 | `version` 2.1.4; `dist-tags` `{ latest: '2.1.4' }`; `versions` ends `2.1.0, 2.1.3, 2.1.4`; `time.modified` 2026-09-17T14:48:16Z | not reached |
| Condition (b), 2027-01-30 | 78 days ahead; within the script's 90-day rule (C2 accepted it) | not reached |
| Re-audit trigger: new advisory on sdk 1.30.0 or zod 4.3.6 | none beyond the seven | not triggered |
| Change to the `brave` entry of `servers.yaml` | none since `44e7c967` (v4's commit) | not triggered |
| Operators do not set `BRAVE_MCP_TRANSPORT` or `BRAVE_MCP_HOST` | not checkable from here | **(unverified)** |

The acceptance is neither expired nor voided. It still ends on the earlier of a Brave release above 2.1.4 and 2027-01-30; if v11.0.0 is tagged after either, the gate fails (v4, "The expiry and the 90-day rule").

## 4. Per pin

`python3 scripts/audit-mcp-pins.py list`: 8 npm pins and 1 PyPI pin, unchanged from v10 (`@zereight/mcp-gitlab` 2.2.5, `@playwright/mcp` 0.0.83, `server-memory` 1.0.0, `server-sequential-thinking` 1.0.0, `@brave/brave-search-mcp-server` 2.1.4, `server-filesystem` 1.0.0, `@supabase/mcp-server-supabase` 0.13.0, `toolradar-mcp` 2.1.0; `mcp-server-git` 2026.10.10). No docker pin. I did not repeat v10's one-dependency per-pin lock trees; attribution here comes from C1 and the advisory database. Newest versions of the non-Brave pins were not re-read **(unverified)**.

## 5. Python pins

| Scope | Input | Source | Result |
|-------|-------|--------|--------|
| git (`uvx`), script form | `requirements-uvx.txt` from C4: the one line `mcp-server-git==2026.10.10` | default; `-s osv` | `No known vulnerabilities found`, exit 0; both |
| git, resolved tree | 34 pins, resolved 2026-11-13, wheels only, universal, Python 3.12 (`mcp` 1.30.0, `starlette` 1.10.0, `cryptography` 50.0.2, `gitpython` 3.2.1, `pydantic` 2.14.3); no `opentelemetry-api` in it | default | `No known vulnerabilities found`, exit 0 |
| security-audit, poc-security-audit, context-retriever | `implementation/runtime/security/requirements-mcp-server.lock.txt`, 35 entries, byte-identical (`cmp`) to `implementation/runtime/memory/requirements-mcp-server.lock.txt`; last changed `44c15b49` (2026-10-22) | default; `-s osv` | **1 finding**, exit 1; both |
| Control | `jinja2==2.10` | default | `Found 12 known vulnerabilities in 1 package`, exit 1 |

C7 output (default source; `-s osv` gives the same row):

```text
opentelemetry-api 1.45.1  CVE-2026-126360 1.45.2
```

### 5.1 New finding: `opentelemetry-api` 1.45.1

| Field | Value |
|-------|-------|
| Ids | `CVE-2026-126360`, alias `GHSA-mf5v-w3w3-f6cg` |
| Title | "OpenTelemetry Python API: Denial of service through quadratic-time traceparent parsing" |
| GitHub severity | medium; CVSS 3.1 5.3, `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`; no CVSS 4.0 vector |
| Published | 2026-11-13T16:43:18Z (about three hours before this run); not withdrawn |
| Range, fix | `<= 1.45.1`; fixed 1.45.2 (on PyPI since 2026-10-29T17:29Z, the newest release) |
| In the lock | line 244, `# via mcp` (`mcp==2.2.0`) |
| In an acceptance or register | no (`grep` over `docs`, `implementation`, `scripts`: no match for either id) |

From the advisory text: `TraceContextTextMapPropagator.extract()` backtracks quadratically on a crafted `traceparent` value, so an application that extracts trace context from an untrusted carrier can spend excessive CPU. Input for the grading (read, not run, no call-graph analysis): the three servers that use this lock are stdio entrypoints (`implementation/runtime/security/audit_server.py:1,9`), and no file under `implementation/runtime/security` or `implementation/runtime/memory` names `opentelemetry`, `traceparent` or `TraceContext` outside the lock. Whether `mcp` 2.2.0 calls `extract()` on a stdio transport, and on what input, was not analysed **(unverified)**.

**Grade proposal**: `SECURITY:LOW` (A06, vulnerable component): availability only, local stdio servers, fix available as a lock bump. For the Security Engineer to grade; not a release blocker under plan-161's rule. Not applied: a lock change is out of this task's scope.

Every `pip-audit --no-deps` run printed the tool's warning that it encourages hashed pins. The advisory database (`ecosystem=pip`) returns nothing for `mcp-server-git@2026.10.10`.

## 6. Manual advisory reads (SEC-T646-06)

Read on **2026-11-13** (20:06 UTC), GitHub Advisory Database REST API, `ecosystem=npm`, OSV as the second source.

| Package | Advisories for any version | `affects=` the pin: reviewed / unreviewed / malware | OSV for the pin | Conclusion |
|---------|----------------------------|-----------------------------------------------------|-----------------|------------|
| `@modelcontextprotocol/server-memory@1.0.0` | none | 0 / 0 / 0 | none | no advisory |
| `@modelcontextprotocol/server-sequential-thinking@1.0.0` | none | 0 / 0 / 0 | none | no advisory |
| `@modelcontextprotocol/server-filesystem@1.0.0` | `GHSA-hc55-p739-j48w`, `GHSA-q66q-fx2p-7w4m` | 0 / 0 / 0 | none | neither covers 1.0.0 (ranges `<= 0.6.2` and `>= 2025.1.14, < 2025.7.1`, as read in v10) |

The `affects=package@version` query for the other five npm pins (`@zereight/mcp-gitlab@2.2.5`, `@playwright/mcp@0.0.83`, `@brave/brave-search-mcp-server@2.1.4`, `@supabase/mcp-server-supabase@0.13.0`, `toolradar-mcp@2.1.0`) also returns nothing. The ranges of the two filesystem advisories were not re-read today; they are v10's reading **(unverified today)**.

## 7. Images, checked by hand

`servers.yaml` has no docker pin, so the script's docker notice has no MCP target (as in v9 and v10). Following v10 and the checklist, I checked the two digest-pinned CI images of `.gitlab-ci.yml` over the registry HTTP API (C10). No `docker` command, no layer. Versions come from the amd64 config JSON; the Alpine version from the first history entry (`ADD alpine-minirootfs-<version>-x86_64.tar.gz`).

| Image | Pinned digest | Resolves | amd64 built | Holds | Tag now |
|-------|---------------|----------|-------------|-------|---------|
| `node:24-alpine` (`.gitlab-ci.yml:43`) | `sha256:116b800c3754b440ee0aa3ed2f20f5bf3d99a554bfd9adeea09ea8017f6e85f5` | yes, HTTP 200, `Docker-Content-Digest` equal, OCI index | 2026-11-11T20:16Z | Node 24.22.3, Yarn 1.22.22, Alpine 3.24.4 | the same digest |
| `python:3.12-alpine` (`.gitlab-ci.yml:54,95,142,162,201,236,254,281,305`) | `sha256:e064671ca452259bab50e8e2c7bd896e39e9a343bb06ca25234adf6fe18d0fc7` | yes, HTTP 200, `Docker-Content-Digest` equal, OCI index | 2026-11-05T19:31Z | Python 3.12.16, Alpine 3.24.4 | `sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89` (Hub `last_updated` 2026-11-12T08:07Z; same digest as `3.12.16-alpine3.24`) |

**The python tag move**: comparing the two indexes per platform, every platform manifest is the same except riscv64 (`a45d1fb29b01…` to `4da05f748cd6…`). The amd64 manifest is `a61cbd76a882…` in both, and its config (built 2026-11-05T19:31Z, Python 3.12.16) is the same. All CI jobs run on x86-64 (register v13), so the move changes nothing the pipeline runs. Not a finding; a digest bump is not needed for it.

**Upstream releases** (C11): newest Node 24.x is 24.22.3 (2026-11-10, marked `security`), which is in the pin; 24.22.1 (2026-10-20) was the previous security release. Newest Python 3.12 is 3.12.16 (2026-10-25), which is in the pin. So the v10 blocker candidate (Python 3.12.15 with four CVEs fixed in 3.12.16) and v10's pending Node security release are both covered by the current digests.

**Not checked**: Alpine package CVEs inside either digest (no scanner, no layer read); platforms other than amd64; the tag-only images that v10 § 7.2 lists (not digest-pinned, not re-read).

## 8. SEC-T786-01: Alpine `nodejs` for `unit-tests`

`unit-tests` runs on the `python:3.12-alpine` digest (Alpine 3.24.4, branch `v3.24`) and installs `'nodejs~=24'` with `apk add --no-cache` (`.gitlab-ci.yml:102`).

| APKINDEX (x86_64) | `nodejs` |
|-------------------|----------|
| `v3.24/main` | **`24.22.3-r0`** |
| `v3.24/community` | absent |
| `edge/main` | `24.22.3-r0` |

So Alpine now ships 24.22.3 on the image's branch. The closing trigger as register v16 states it is "Alpine `nodejs` 24.22.3 in a `unit-tests` log". I did not read any job log (C12 reads job status only), so that the `unit-tests` run of pipeline 3066295917 (finished 2026-11-13T19:56Z) installed 24.22.3 is **(unverified)**; the CDN mirror the runner reaches and its cache state were not checked. No pin was changed.

## 9. CA-chain check

| Pipeline | Commit | Created | `ca-chain-check-node` | `ca-chain-check-python` | `unit-tests` |
|----------|--------|---------|-----------------------|-------------------------|--------------|
| 3066295917 (newest on develop) | `9acf84dc` | 2026-11-13T19:39Z | success | success | success |
| 3066133118 | `5de6fbb7` | 2026-11-13T19:06Z | success | success | success |

Read with `glab ci list --ref develop` and `glab api …/pipelines/<id>/jobs` (read-only). The digests in `.gitlab-ci.yml` are unchanged since that run: `git diff 9acf84dc f41bb087 -- .gitlab-ci.yml` is empty, the python digest dates from `4ab4a5b6` and the node digest from `4b7d5c5d`, both older than `9acf84dc`. Since the python tag move touches only riscv64 (section 7), the jobs ran on the same amd64 images that a run today would pull **(unverified: the runner's architecture was taken from register v13, not read from the job)**.

## 10. `ci_images_reviewed_on`

`.gitlab-ci.yml:21`: `# ci_images_reviewed_on: 2026-11-11`. `tests/functional/test_ci_hash_pins.py` (`MAX_REVIEW_AGE_DAYS = 120`, `review_problems`) fails when `(today - reviewed).days > 120`: **last passing day 2027-03-11, fails from 2027-03-12**, 118 days after this run. This audit does not move the date.

## 11. Not covered

- Remote servers (`context7`, `hindsight`, `cwso`, `hf-mcp-server`): URL entries, no package pin.
- `npm audit signatures` and the script's `provenance` command: outside the brief.
- Runtime downloads (Playwright browsers): in no lock tree.
- `implementation/runtime/memory/requirements.txt` (index builder, not an MCP pin).
- Reachability of the accepted advisories was not re-derived; the grades in v4 are the Security Engineer's.
- Per-pin lock trees and newest versions of the non-Brave pins (section 4).
