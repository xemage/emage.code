# Artifact: security-review-t646-dependency-audit-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no execute tool; the `security-audit` tools failed to run, so advisory databases, registry manifests and source reading were used). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security (dependency audit, audit D-7). **Date**: 2026-10-15.
- **Target**: T646: the 11 pinned `npx`/`uvx`/`docker` entries of `implementation/knowledge/mcp/servers.yaml` and the Python requirements under `implementation/`, at develop `5bdf81c`.
- **Based on**: `docs/tasks/task-T646.md`, `docs/plans/plan-122-release-v8-wave-3.md`, `docs/artifacts/release-v8-audit-v2.md` (D-7, C-6, K-13), `docs/artifacts/mcp-server-packages-v1.md`, `docs/artifacts/security-review-t638-mcp-packages-v1.md`.

## Verdict: CONDITIONAL_PASS

0 critical, 0 high, 1 medium, 5 low. No pinned package has a published advisory that affects its exact pinned version. A medium security finding gives at best CONDITIONAL_PASS; at the Release gate it is fixed (or re-graded on evidence) before the release ships. No automated audit ran (limit L-1): the results are advisory-database queries (GitHub Advisory Database `affects=` with positive controls, PyPI `vulnerabilities`) plus registry and source reading.

## Findings

| ID | Grade | OWASP | Location | Finding | Disposition |
|---|---|---|---|---|---|
| SEC-T646-01 | SECURITY:MEDIUM | A10, A06 | `servers.yaml` `mcp-fetch-server@1.1.2` (core, enabled everywhere) | GHSA-8fxj-2g9q-8fjw (SSRF private-IP bypass) is recorded as `<= 1.0.2` with no fixed version, so 1.1.2 is outside the range but no fix is named. Source read at gitHead `4080fd2`: `_fetch` follows redirects and checks `response.url` only after the request was sent (blind GET to loopback or link-local targets is possible; the body is not returned); the resolve-then-fetch gap allows DNS rebinding; the guard depends on `private-ip@3.0.2`, which has an unpatched high advisory (GHSA-9h3q-32c7-r533, multicast ranges, all versions). The server fetches model-chosen URLs and the caller can set request headers. | **Condition, due before T652.** The user chose "Test first, then decide": task T653 runs a loopback redirect test against the pinned version; no second-listener request means LOW + tracked debt, a request means MEDIUM stands and fix options (move to extended, remove, replace) go to the user |
| SEC-T646-02 | SECURITY:LOW | A06 (record accuracy) | K-13 of `release-v8-audit-v2.md` §4; `security-review-t638-mcp-packages-v1.md` L-3; `mcp-server-packages-v1.md` §2.3 | They call GHSA-w4q6-qw23-4rg7 (CVE-2026-47427, `completion/complete` nil-pointer DoS) unpatched for the GitHub container. The database now lists `< 1.1.0` as vulnerable, patched in v1.1.0; the pinned image is v2.0.2 and is not affected (control query: `@1.0.0` returned it, `@2.0.2` did not). | Condition before T651: drop that clause from the release document's Known issues; keep the no-signature-verification and default-toolset points |
| SEC-T646-03 | SECURITY:LOW | A08, A06 | `fetch`, `brave`, `toolradar` entries; `@playwright/mcp@0.0.83` | `mcp-fetch-server`, `@brave/brave-search-mcp-server` and `toolradar-mcp` have no npm provenance attestation (registry signatures only). `toolradar-mcp@2.1.0` is a 750 KB bundle with no runtime dependencies, so a dependency audit cannot see inlined code. `@playwright/mcp@0.0.83` pins exact alpha `playwright` builds (Microsoft release process, no advisory found, but alpha builds are rarely covered). Toolradar ownership is better corroborated than in T637 (site links the npm package and `github.com/Nadeus/toolradar-mcp`); the legal operator is still unnamed. | Tracked debt (extends T638 L-8): prefer versions with provenance at each pin bump |
| SEC-T646-04 | SECURITY:LOW | A06, A08 | `implementation/runtime/security/requirements-mcp-server.txt:23`, `implementation/runtime/memory/requirements-mcp-server.txt:27` | `mcp==2.2.0` is clean but requires floating transitives: `httpx2>=2.5.0` permits versions before 2.12.0 (GHSA-8xx6-hgc6-gc2m, decompression memory amplification). A fresh install resolves 2.13.1; a stale mirror could resolve a vulnerable one. The servers are local stdio servers; impact low. No hash pinning (SEC-014 of T633). | Tracked debt: add `httpx2>=2.12.0` or a constraints file; longer term `--require-hashes` |
| SEC-T646-05 | SECURITY:LOW | A06 (process) | `security-audit` MCP server; no `package.json` or lockfile in the repository | `run_pip_audit`, `run_npm_audit` and `grep_content` returned a bare "Error executing tool" (third report in a row: T633, T640, T646). `npm audit` cannot apply to `npx` entries without a manifest. | Tracked debt: diagnose the audit server (a throwaway `package.json` generated from the pins is a cheap path); until then the manual advisory-database path used here is the record |
| SEC-T646-06 | SECURITY:LOW | A06 | `memory`, `sequential-thinking`, `filesystem` entries | The three reference servers moved from calendar versions (`2026.8.31`) to `1.0.0`; advisory ranges in calendar form (GHSA-hc55-p739-j48w, GHSA-q66q-fx2p-7w4m, `>= 2025.1.14, < 2025.7.1`) sort `1.0.0` below them. No advisory matches `1.0.0` today. | Tracked debt: read advisory ranges manually for these three at each pin bump |

## Per-package results

Method: GitHub Advisory Database `GET /advisories?ecosystem=<eco>&affects=<pkg>@<exact version>` with a positive control per ecosystem (`@zereight/mcp-gitlab@2.1.0` and `mcp-fetch-server@1.0.2` for npm, `mcp@1.8.0` for pip, `github-mcp-server@1.0.0` for go); unfiltered lists for the gitlab, playwright and filesystem packages; PyPI version JSON; `registry.npmjs.org/<pkg>/<version>` read 2026-10-15. OSV was not queried directly (POST-only API).

| # | Package, exact pin | Result | Signals |
|---|---|---|---|
| 1 | `@zereight/mcp-gitlab@2.2.5` | No advisory affects 2.2.5 (four existing advisories fixed in 2.1.27 or 2.1.30) | Provenance present; one maintainer; `prepare` script only; latest is 2.3.0; holds the GitLab PAT |
| 2 | `@playwright/mcp@0.0.83` | None (only CVE-2025-9611, `< 0.0.40`; see the note below the table) | Provenance present; 5 maintainers incl. `microsoft-oss-releases`; exact alpha `playwright` dependency (SEC-T646-03) |
| 3 | `mcp-fetch-server@1.1.2` | No advisory lists 1.1.2; SEC-T646-01 | No provenance; maintainers `zachcaceres`, `ilintar` (second unverified); latest equals the pin |
| 4 | `@modelcontextprotocol/server-memory@1.0.0` | None | Provenance present; MCP org maintainers |
| 5 | `@modelcontextprotocol/server-sequential-thinking@1.0.0` | None | as #4 |
| 6 | `@modelcontextprotocol/server-filesystem@1.0.0` | None for 1.0.0 (two older advisories `<= 0.6.2` and `>= 2025.1.14, < 2025.7.1`; SEC-T646-06) | as #4 |
| 7 | `@brave/brave-search-mcp-server@2.1.4` | None | No provenance (SEC-T646-03); Brave maintainers; runtime dependencies exact-pinned |
| 8 | `toolradar-mcp@2.1.0` | None | No provenance; one maintainer; bundled, no runtime dependencies |
| 9 | `@supabase/mcp-server-supabase@0.13.0` | None | Provenance present; latest is 0.14.0 |
| 10 | `mcp-server-git@2026.10.10` (PyPI via `uvx`) | None; PyPI `vulnerabilities` is `[]` | Uploaded 2026-10-11; author Anthropic, PBC; lower-bound transitives (`mcp@1.29.0`, `gitpython@3.1.60`) clean; PyPI attestation from T637 not re-checked |
| 11 | `ghcr.io/github/github-mcp-server@sha256:ffced0d7...97796` (v2.0.2) | No advisory affects 2.0.2 (SEC-T646-02); the digest resolves anonymously as an OCI index (amd64 and arm64) identical to tag `v2.0.2` | Signatures and attestation content not verified; image layers not scanned |
| 12 | `mcp==2.2.0` (both requirement files) | None; `vulnerabilities: []`, not yanked, uploaded 2026-09-07 | `httpx2` floor (SEC-T646-04); `starlette`, `pyjwt`, `python-multipart` clean |
| 13 | `fastembed==0.8.0`, `tree-sitter==0.26.0`, `tree-sitter-python==0.25.0`, `tree-sitter-javascript==0.25.0`, `tree-sitter-bash==0.25.1` | No advisory in the DB; fastembed PyPI `vulnerabilities: []` | fastembed transitives not covered |

Note on row 2: the reviewer reported that T637 and the database give different GHSA ids for the same CVE-2025-9611; the CVE number is what this record relies on. Sampled npm transitives with no advisory: `@modelcontextprotocol/sdk@1.32.1`, `express@5.3.0`, `undici@6.29.0`, `jsdom@28.1.0`, `diff@8.0.3`, `glob@13.0.6`, `minimatch@10.2.6`, `tough-cookie@5.1.2`; `private-ip@3.0.2` has the unpatched high advisory of SEC-T646-01. All other transitives are not covered. No other requirement file under `implementation/` was found; the set was not exhaustively enumerated (no working grep or glob tool).

## Conditions

- SEC-T646-01: fix or evidence-based re-grade before T652 (owner devops-engineer for the change and the test, the user for the option choice, tech-lead for review). The Release Manager records the outcome in the release document's Gate Verdicts.
- SEC-T646-02: correct K-13 in the v8.0.0 Known issues (owner release-manager, T645, before T651).
- SEC-T646-03 to -06: tracked LOW debt, due at the next pin bump.

## Blockers

None on CRITICAL/HIGH grounds. Tooling blocker T646-B1 (type technical, severity minor): the `security-audit` MCP tools return a bare error; retry 1; escalated to the orchestrator; workaround: advisory-database queries.

## Limits

L-1 no `npm audit`, `pip-audit`, container scan, `cosign` or signature verification ran (no shell); L-2 an empty advisory result means "no known advisory", and the `affects=` filter was trusted only where a positive control worked (not for the calendar-to-1.0.0 reference servers); L-3 SEC-T646-01 comes from source reading at the gitHead, not from the published tarball's bundled `dist`, and nothing was executed; L-4 transitive dependencies are sampled, not enumerated; L-5 registry facts reflect 2026-10-15, maintainer identity and the legal operator of toolradar are unverified; L-6 the GitHub container image was checked at manifest level only; L-7 the user's local settings files, `.env*` files and `tests/golden/held-out/` were not opened; L-8 the four CVEs fixed in `mcp-server-git >= 2026.1.14` and its PyPI attestation were not re-checked from T637.
