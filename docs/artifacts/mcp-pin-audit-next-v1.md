# Artifact: mcp-pin-audit-next-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: devops-engineer (T870). **Date**: 2026-11-19. **Owner**: devops-engineer.
- **Task**: T870 (`docs/tasks/task-T870.md`), plan `docs/plans/plan-182-next-release.md` (wave 1, item 2), release v12.0.0 (MAJOR; user: "release plan go", "Approve (Recommended)", "v12.0.0, MAJOR (Recommended)").
- **Based on**: `implementation/knowledge/mcp/servers.yaml`, `scripts/audit-mcp-pins.py`, `scripts/check-ca-chains.sh`, `.gitlab-ci.yml`, `ci/requirements-{ci,gate,release}.txt` and `implementation/runtime/{security,memory}/requirements-mcp-server.lock.txt` at `2fec9af8` (develop `9b9a31f0` plus the plan-182 commit); `docs/wiki/mcp-pin-bump-checklist.md` § 1 to § 5; `docs/artifacts/mcp-pin-audit-v11-v1.md` (shape and method).
- **Scope**: report only. No pin, `servers.yaml` entry, lock file, CI image, gate, acceptance or test was changed. No `docker` command was run, no MCP server was started, no audited package was executed, and no GitLab job log was read.

## 1. Summary

- **No HIGH, no acceptance, nothing that blocks the release.** All four npm commands exit 0; the release-gate command (`audit --audit-level high --signatures`) passes with no `--accept`, as checklist § 4 requires. No `--accept` entry exists any more (the seven of `brave-audit-acceptance-v4.md` were retired by the bump to Brave 2.1.5, T851), so no pin acceptance can be expired or void.
- **npm audit at `low`: no known vulnerabilities** for the 8 npm pins. The two `server-filesystem` moderates of v11 (`GHSA-3g3m-2fjr-6pw4`, `GHSA-g3hv-75wg-m249`, SEC-T756-07) no longer appear: `server-filesystem@2.4.0` does not resolve the affected `glob`/`minimatch`.
- **Signatures**: 193 packages with verified registry signatures, 39 with verified attestations.
- **Pin age**: two pins are still younger than 7 days, exactly the two recorded exceptions of checklist § 1: `@brave/brave-search-mcp-server@2.1.5` (2 days) and `@modelcontextprotocol/server-filesystem@2.4.0` (1 day). Without exceptions `age` exits 1; with both exits 0. Both stay needed until 2026-11-24 (Brave) and 2026-11-25 (filesystem); a tag on or after 2026-11-25 needs neither.
- **Provenance**: 7 of 8 pinned versions carry provenance; `toolradar-mcp@2.1.0` does not (known; its newest, 2.4.0, does). `provenance` without `--require` exits 0.
- **Newer upstream releases (section 5)** exist for 7 of 8 npm pins, among them **`@brave/brave-search-mcp-server` 2.2.0, published today 17:17 UTC**. None fixes a known advisory of the pinned version (the pinned set audits clean). Nothing was bumped.
- **Python (section 6)**: `mcp-server-git` and both runtime locks: no known vulnerabilities. **New finding below HIGH: `ci/requirements-ci.txt` pins `opentelemetry-api==1.45.1`** (via `mcp==2.2.0`), affected by `CVE-2026-126360` / `GHSA-mf5v-w3w3-f6cg` (GitHub severity medium, CVSS 3.1 5.3, availability only), fixed in 1.45.2. v11 fixed it in the runtime locks (SEC-T814-01, T824) but the CI lock was not audited then. Grade proposal `SECURITY:LOW` (A06), for the Security Engineer to confirm. Not a release blocker (not HIGH).
- **Images (section 7)**: neither pin is stale for amd64. `node:24-alpine` still resolves to the pinned index `116b800c…` (Node 24.22.3, the newest 24.x and a security release of 2026-11-10). `python:3.12-alpine` resolves to `c5ba3dee…`, but its linux/amd64 manifest `a61cbd76…` is the pinned one (Python 3.12.16, the newest 3.12).
- **CA chains (section 8)**: run locally, without Docker, on the CA stores extracted from the pinned amd64 layers: `--ca-release` and `--cafile` PASS for both images, `--capath` PASS for python; node ships no hashed directory, which the CI job skips by design.

## 2. Commands run

All runs on 2026-11-19 from 18:05 UTC, in the worktree, scratch under the session scratchpad `t870/`. npm used an empty user and global configuration and `https://registry.npmjs.org/`.

| # | Command | Exit | Result |
|---|---------|------|--------|
| C1 | `python3 scripts/audit-mcp-pins.py list` | 0 | 8 npm pins, 1 PyPI pin, no docker pin (section 4) |
| C2 | `python3 scripts/audit-mcp-pins.py provenance` | 0 | 7 of 8 with provenance; `toolradar-mcp@2.1.0` none ("pinned versions without provenance: 1") |
| C3 | `python3 scripts/audit-mcp-pins.py audit --audit-level low` | 0 | `no known vulnerabilities`; `result: no finding at or above the audit level` |
| C4 | `python3 scripts/audit-mcp-pins.py audit --audit-level high --signatures` (no `--accept`) | 0 | `npm audit signatures: ok`, 193 verified registry signatures, 39 verified attestations; no finding |
| C5 | `python3 scripts/audit-mcp-pins.py age` | 1 | 2 pins under 7 days without exception (Brave 2.1.5, filesystem 2.4.0) |
| C6 | C5 with the two `--allow-young` strings of checklist § 1, character for character | 0 | both `YOUNG, ALLOWED`; 0 without exception |
| C7 | `npm view <pkg> version time --json`, each of the 8 npm pins | 0 (each) | section 5 |
| C8 | GitHub Advisory Database REST API, `ecosystem=npm&affects=<pkg>`, each of the 8 npm pins (anonymous) | HTTP 200 (each) | section 3 |
| C9 | `python3 scripts/audit-mcp-pins.py generate <scratch>/gen` | 0 | `requirements-uvx.txt` = `mcp-server-git==2026.10.10` |
| C10 | `uvx --from pip-audit==2.10.1 pip-audit -r <file> --no-deps --disable-pip`, six files | see section 6 | 5 clean, 1 finding |
| C11 | Docker Hub registry HTTP API (anonymous pull token): index of each pinned digest and of each tag, amd64 manifest, config blob, layers (sha256 verified on download) | HTTP 200 | section 7 |
| C12 | `nodejs.org/dist/index.json`; `endoflife.date/api/python/3.12.json` | read | Node 24 newest v24.22.3 (2026-11-10, security); Python 3.12 newest 3.12.16 (2026-10-25) |
| C13 | `sh scripts/check-ca-chains.sh` `--ca-release`, `--cafile`, `--capath` on the extracted stores; fixtures `sha256sum -c SHA256SUMS` first | see section 8 | PASS (node `--capath`: exit 2, no hashed directory) |

`uvx` was present (`/home/emage/.local/bin/uvx`); no scratch venv was needed. pip-audit 2.10.1.

## 3. Manual advisory read (checklist § 1 step 4) and per-package advisories

Read 2026-11-19 from the GitHub Advisory Database (C8; types reviewed, ecosystem npm). Each advisory's range and fix were compared with the pinned version and its publication date.

| Package (pin) | Advisories | Affects the pin? |
|---------------|-----------|------------------|
| `@modelcontextprotocol/server-memory` (1.0.0) | none | no |
| `@modelcontextprotocol/server-sequential-thinking` (1.0.0) | none | no |
| `@modelcontextprotocol/server-filesystem` (2.4.0) | `GHSA-hc55-p739-j48w` high, `GHSA-q66q-fx2p-7w4m` high (both 2025-07-01; ranges `<= 0.6.2` and `>= 2025.1.14, < 2025.7.1`, fixed 2025.7.1) | no: 2.4.0 (published 2026-11-18) is outside both ranges by semver and was published 16 months after the fix |
| `@zereight/mcp-gitlab` (2.2.5) | `GHSA-cv3r-c5h8-f4g5`, `GHSA-2h44-8472-frjj` (critical, `< 2.1.27`), `GHSA-vmp7-252j-cwp7` (critical), `GHSA-5648-rgj9-v224` (high) (`< 2.1.30`) | no: all fixed below 2.2.5 |
| `@playwright/mcp` (0.0.83) | `GHSA-6fg3-hvw7-2fwq` high, `< 0.0.40` | no |
| `@brave/brave-search-mcp-server` (2.1.5) | none on the package itself | no |
| `@supabase/mcp-server-supabase` (0.13.0) | none | no |
| `toolradar-mcp` (2.1.0) | none | no |

Transitive advisories are covered by C3/C4 (clean at `low`).

## 4. Pins and age

| Pin | Published | Age (days) | Provenance | Age status |
|-----|-----------|-----------|------------|------------|
| `@zereight/mcp-gitlab@2.2.5` | 2026-10-13 | 37 | yes | ok |
| `@playwright/mcp@0.0.83` | 2026-09-28 | 52 | yes | ok |
| `@modelcontextprotocol/server-memory@1.0.0` | 2026-10-11 | 39 | yes | ok |
| `@modelcontextprotocol/server-sequential-thinking@1.0.0` | 2026-10-11 | 39 | yes | ok |
| `@brave/brave-search-mcp-server@2.1.5` | 2026-11-17 | 2 | yes | **young**, exception T851 (checklist § 1) needed until 2026-11-24 |
| `@modelcontextprotocol/server-filesystem@2.4.0` | 2026-11-18 | 1 | yes | **young**, exception T860 (checklist § 1) needed until 2026-11-25 |
| `@supabase/mcp-server-supabase@0.13.0` | 2026-09-17 | 63 | yes | ok |
| `toolradar-mcp@2.1.0` | 2026-08-21 | 90 | **no** | ok |
| `mcp-server-git==2026.10.10` (PyPI, `uvx`) | not covered by `age` | n/a | n/a | n/a |

## 5. Newer upstream releases (not bumped)

Newest on npm on 2026-11-19 (C7). "Fixes a known advisory" is judged against C3/C4 (the pinned set audits clean at `low`) and section 3 (no advisory affects a pin): none of the newer releases fixes a known advisory of the pinned version.

| Package | Pin | Newest | Newest published | Age (days) | Fixes a known advisory of the pin |
|---------|-----|--------|------------------|-----------|-----------------------------------|
| `@zereight/mcp-gitlab` | 2.2.5 | 2.3.29 | 2026-11-18T04:02Z | 1 | no |
| `@playwright/mcp` | 0.0.83 | 0.0.86 | 2026-11-18T18:54Z | 0 | no |
| `@modelcontextprotocol/server-memory` | 1.0.0 | 2.2.1 | 2026-11-18T09:18Z | 1 | no |
| `@modelcontextprotocol/server-sequential-thinking` | 1.0.0 | 2.2.0 | 2026-11-18T09:19Z | 1 | no |
| `@brave/brave-search-mcp-server` | 2.1.5 | **2.2.0** | 2026-11-19T17:17Z | 0 | no |
| `@modelcontextprotocol/server-filesystem` | 2.4.0 | 2.4.0 | (pinned) | 1 | n/a |
| `@supabase/mcp-server-supabase` | 0.13.0 | 0.18.0 | 2026-11-17T18:07Z | 2 | no |
| `toolradar-mcp` | 2.1.0 | 2.4.0 (has provenance) | 2026-11-04T16:01Z | 15 | no |

Every newer release except `toolradar-mcp@2.4.0` is under the 7-day minimum age today; a bump of any of them before v12.0.0 would need a recorded exception (checklist § 1). `toolradar-mcp@2.4.0` is the only one that is old enough and would also clear the pin's missing provenance; that is a bump candidate for a later plan, not for this task.

## 6. Python pins

| Scope | File | Exit | Result |
|-------|------|------|--------|
| `mcp-server-git` (`uvx`) | `requirements-uvx.txt` from C9 (one line) | 0 | No known vulnerabilities found |
| security-audit, poc-security-audit, context-retriever | `implementation/runtime/security/requirements-mcp-server.lock.txt` | 0 | No known vulnerabilities found (`opentelemetry-api==1.45.2`, line 244, since T824) |
| memory runtime | `implementation/runtime/memory/requirements-mcp-server.lock.txt` (byte-identical to the security lock, `cmp`) | 0 | No known vulnerabilities found |
| `unit-tests` job | `ci/requirements-ci.txt` | **1** | `opentelemetry-api 1.45.1  CVE-2026-126360  1.45.2` |
| `validation-super-gate` job | `ci/requirements-gate.txt` | 0 | No known vulnerabilities found |
| `release-docs-gate` job | `ci/requirements-release.txt` | 0 | No known vulnerabilities found |

### 6.1 New finding: `opentelemetry-api` 1.45.1 in the CI lock

| Field | Value |
|-------|-------|
| Ids | `CVE-2026-126360`, alias `GHSA-mf5v-w3w3-f6cg` (same advisory as SEC-T814-01) |
| Severity | GitHub medium, CVSS 3.1 5.3 (`AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`), quadratic-time `traceparent` parsing, availability only |
| Where | `ci/requirements-ci.txt` line 421, `# via mcp` (`mcp==2.2.0`, line 409); lock generated 2026-11-02 with `--exclude-newer 2026-10-22T12:00:00Z`, last changed `913a8de7` |
| Fix | 1.45.2 (on PyPI since 2026-10-29); regenerate the CI lock with `--upgrade-package opentelemetry-api==1.45.2`, as T824 did for the runtime locks (checklist § 2) |
| Tracked? | SEC-T814-01 names only the runtime locks and is closed as fixed; the CI lock is in no acceptance or register entry |
| Why v11 missed it | `mcp-pin-audit-v11-v1.md` audited the runtime locks only, not `ci/requirements-*.txt` |

Grading input (read, not run): the lock is installed only in the `unit-tests` CI job, which runs the project's own tests on a project-controlled runner; no step there extracts trace context from an untrusted carrier. Proposal: `SECURITY:LOW` (A06), track and fix in the next CI-lock regeneration. For the Security Engineer to confirm; **not a release blocker** under plan-182's rule (not HIGH).

## 7. CI images

Read through the Docker Hub registry API with an anonymous pull token (C11). No Docker.

| Pin | Pinned index | Tag's index today | linux/amd64 manifest (pin / tag) | Contents (amd64 config) | Stale for amd64? |
|-----|--------------|-------------------|-----------------------------------|-------------------------|------------------|
| `node:24-alpine` | `sha256:116b800c3754…` | `sha256:116b800c3754…` (same) | `sha256:d8d97e479cdc…` / same | created 2026-11-11T20:16Z, `NODE_VERSION=24.22.3` | no; 24.22.3 is the newest 24.x |
| `python:3.12-alpine` | `sha256:e064671ca452…` | `sha256:c5ba3deef00c…` (moved) | `sha256:a61cbd76a882…` / same | created 2026-11-05T19:31Z, `PYTHON_VERSION=3.12.16` | no; the index moved only outside amd64 (as recorded in `.gitlab-ci.yml`), and 3.12.16 is the newest 3.12 |

`ci_images_reviewed_on: 2026-11-19`: `test_ci_hash_pins` passes through 2027-03-19 and fails from 2027-03-20.

## 8. CA chains, locally, without Docker

Method: the amd64 layers of each pinned image were downloaded through the registry API into their own scratch directory, each checked against its digest, and only `etc/ssl/*` and `lib/apk/db/installed` were extracted (no owner or permission bits restored; nothing from the image executed). The fixtures passed `sha256sum -c SHA256SUMS` first. Local OpenSSL is 3.0.13 (the CI job uses the image's `openssl~=3.5`), so this is supporting evidence; the MR pipeline's `ca-chain-check-node` and `ca-chain-check-python` jobs remain the gate.

| Image | Store (`cert.pem` sha256) | `ca-certificates` packages | `--ca-release` | `--cafile cert.pem` | `--capath certs` |
|-------|---------------------------|----------------------------|----------------|---------------------|------------------|
| node | `5961c0a3…` | `ca-certificates-bundle` 20261020-r0 | exit 0, PASS | exit 0, PASS (20 lines PASS) | exit 2, "no hashed certificate in the CA directory": the image ships no hashed directory; the CI job (`.gitlab-ci.yml` near line 205) skips `--capath` in that case by design |
| python | `5961c0a3…` (identical bundle) | `ca-certificates` and `-bundle` 20261020-r0 | exit 0, PASS | exit 0, PASS | exit 0, PASS |

## 9. Blockers

None. No finding at or above high, no `--accept` in use, so no acceptance to expire or be void. The only new item (section 6.1) is below HIGH.

## 10. Follow-ups (not done here)

1. Grade the CI-lock `opentelemetry-api` finding (section 6.1) and schedule the `ci/requirements-ci.txt` regeneration; extend checklist § 2 and the next audit to always include `ci/requirements-*.txt` (they were added in this audit).
2. If v12.0.0 is tagged before 2026-11-25, the release gate's `age` run needs the two checklist § 1 `--allow-young` exceptions (one of them until 2026-11-24).
3. Newer upstream releases (section 5), notably Brave 2.2.0 (published today) and `toolradar-mcp@2.4.0` (old enough, has provenance), are bump candidates for a later plan.
