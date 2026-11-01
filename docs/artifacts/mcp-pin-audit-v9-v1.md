# Artifact: mcp-pin-audit-v9-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: devops-engineer (T702). **Date**: 2026-11-01. **Owner**: devops-engineer.
- **Task**: T702 (`docs/tasks/task-T702.md`), plan `docs/plans/plan-124-release-v9.md` (wave 1, item 3), user action A-6 of `docs/artifacts/tracked-debt-register-v3.md`.
- **Based on**: `implementation/knowledge/mcp/servers.yaml` and `scripts/audit-mcp-pins.py` at commit `3394229a`; `docs/artifacts/brave-audit-acceptance-v2.md` (SEC-T676-02, expires 2026-11-21 or at the first brave release above 2.1.4).
- **Scope**: report only. No pin, `servers.yaml`, generated configuration or acceptance was changed or renewed. No `--accept` option was used anywhere.

## 1. Summary

- `python3 scripts/audit-mcp-pins.py audit --audit-level high` **without `--accept`** exits 1 (`result: FINDINGS`).
- Every HIGH finding comes from **`@brave/brave-search-mcp-server@2.1.4`**. The per-package audit (section 3) gives no HIGH or CRITICAL for any other pinned package.
- **Brave is still affected.** 2.1.4 is still the newest published release (`npm view`, 2026-11-01), so the acceptance has not yet expired through a new release. It expires on 2026-11-21.
- **The finding is wider than what was accepted.** Two HIGH advisories that are **not** in the acceptance list of SEC-T676-02 now apply to brave 2.1.4:
  - `GHSA-f897-62hf-6gxq` (`@modelcontextprotocol/sdk`, `>=1.10.0 <1.30.1`, high)
  - `GHSA-mrhx-c7xc-m3w5` (`zod`, `<4.6.6`, high)

  Even the full v2 gate command with all five `--accept` options would therefore fail today. This was inferred from the acceptance list and the script's per-advisory scoping. The command with `--accept` was not run (brief: no `--accept`).
- No CRITICAL anywhere. One package has MODERATE findings: `@modelcontextprotocol/server-filesystem` (section 3).
- Python: `mcp-server-git@2026.10.10` and the pinned lock file of the in-repo Python MCP servers return no advisory from PyPI or OSV (section 4).

## 2. Commands run

All runs were in scratch directories outside the repository. Every npm install used `--package-lock-only --ignore-scripts`. npm got an empty user and global `.npmrc`, the public registry and an environment with only `PATH` and a scratch `HOME`. No audited package was executed.

| # | Command | Purpose |
|---|---------|---------|
| C1 | `python3 scripts/audit-mcp-pins.py audit --audit-level high` | The release gate, whole npm set as one throwaway project, no `--accept` |
| C2 | per pin: a one-dependency `package.json`, `npm install --package-lock-only --ignore-scripts --no-audit --no-fund`, `npm audit --json` | Per-package attribution (the script offers no per-package mode; `generate`/`list` only write or list the set) |
| C3 | `npm view <pkg> version dist-tags.latest time versions --json` | Newest published versions (read-only) |
| C4 | `uv pip compile` of `mcp-server-git==2026.10.10` with `--only-binary :all:` (wheel metadata only, no build), `--universal --python-version 3.12` | Resolve the Python dependency tree without running package code |
| C5 | stdlib script: PyPI JSON API `vulnerabilities` field (the default source of `pip-audit`) and OSV `querybatch` for every `name==version` | Python advisory lookup. `pip-audit` is not installed here, so the same data sources were queried directly. A positive control (`jinja2==2.10`, `mcp==1.9.0`) returned advisories from both sources. |
| C6 | OSV `query` (npm ecosystem, all versions) for each npm pin | The manual advisory read that C1 asks for (SEC-T646-06, calendar-version packages) |

## 3. npm pins: results without `--accept`

"High" and "critical" count npm's vulnerable package entries in the one-package audit (C2). Advisory ids and their severities are as npm reported them on 2026-11-01. Dependency ranges were resolved on 2026-11-01. `npx` resolves them again at launch, so a later run can differ for every package that does not pin its dependencies exactly.

| Server | Package | Pinned | Audit tool | High | Critical | Advisory ids | Fixed in | Clean upgrade path |
|--------|---------|--------|------------|------|----------|--------------|----------|--------------------|
| gitlab | `@zereight/mcp-gitlab` | 2.2.5 | npm audit (C1, C2); OSV (C6) | 0 | 0 | none in the tree. Package-level advisories in OSV (`GHSA-2h44-8472-frjj`, `GHSA-cv3r-c5h8-f4g5` fixed in 2.1.27; `GHSA-5648-rgj9-v224`, `GHSA-vmp7-252j-cwp7` fixed in 2.1.30) do not cover 2.2.5 | n/a | not needed (newest is 2.3.19) |
| playwright | `@playwright/mcp` | 0.0.83 | npm audit (C1, C2); OSV (C6) | 0 | 0 | none. `GHSA-6fg3-hvw7-2fwq` is fixed in 0.0.40 and does not cover 0.0.83 | n/a | not needed (newest is 0.0.84). The browser binaries Playwright downloads at run time are **not covered** by npm audit |
| memory | `@modelcontextprotocol/server-memory` | 1.0.0 | npm audit (C1, C2); OSV (C6) | 0 | 0 | none. OSV lists no advisory for any version, so the calendar-range concern of SEC-T646-06 does not apply | n/a | not needed (newest is 2.0.1) |
| sequential-thinking | `@modelcontextprotocol/server-sequential-thinking` | 1.0.0 | npm audit (C1, C2); OSV (C6) | 0 | 0 | none. OSV lists no advisory for any version | n/a | not needed (newest is 2.0.0) |
| **brave** | **`@brave/brave-search-mcp-server`** | **2.1.4** | npm audit (C1, C2) | **3** | 0 | see section 3.1 | sdk 1.32.0 (all six), zod 4.6.6 | **none**: 2.1.4 is the newest release and pins `@modelcontextprotocol/sdk` `1.30.0` and `zod` `4.3.6` exactly |
| filesystem | `@modelcontextprotocol/server-filesystem` | 1.0.0 | npm audit (C1, C2); OSV (C6) | 0 | 0 | moderate only: `GHSA-3g3m-2fjr-6pw4` (`glob` `>=9.0.0 <=14.0.1`), `GHSA-g3hv-75wg-m249` (`minimatch` `<11.0.1`). Calendar-range advisories `GHSA-hc55-p739-j48w` and `GHSA-q66q-fx2p-7w4m` (`2025.1.14` to `<2025.7.1`) do not cover 1.0.0, which was published on 2026-10-11, after the fixed 2025.7.1 | not given by npm (`fixAvailable: false`) | none for the moderates: newest 2.1.0 gives the same three moderate entries (C2) |
| supabase | `@supabase/mcp-server-supabase` | 0.13.0 | npm audit (C1, C2); OSV (C6) | 0 | 0 | none | n/a | not needed (newest is 0.15.0) |
| toolradar | `toolradar-mcp` | 2.1.0 | npm audit (C1, C2); OSV (C6) | 0 | 0 | none. The lock tree has one entry, the package itself | n/a | not needed (newest is 2.2.0) |

### 3.1 Brave in detail

From the one-package audit of `@brave/brave-search-mcp-server@2.1.4`:

| Vulnerable entry | Resolved | Advisory | npm severity | Range | In SEC-T676-02 acceptance |
|------------------|----------|----------|--------------|-------|---------------------------|
| `@modelcontextprotocol/sdk` | 1.30.0 | `GHSA-6qxp-vccf-f47h` | high | `>=1.12.0 <1.31.0` | yes |
| `@modelcontextprotocol/sdk` | 1.30.0 | `GHSA-22jm-h49p-29qw` | high | `>=1.24.0 <1.32.0` | yes |
| `@modelcontextprotocol/sdk` | 1.30.0 | `GHSA-46jr-4wx8-v453` | high | `>=1.3.0 <1.32.0` | yes |
| `@modelcontextprotocol/sdk` | 1.30.0 | `GHSA-6prh-2h8m-c8cw` | moderate | `<1.32.0` | yes |
| `@modelcontextprotocol/sdk` | 1.30.0 | `GHSA-rvq5-wwqv-78pq` | moderate | `>=1.6.0 <1.32.0` | yes |
| `@modelcontextprotocol/sdk` | 1.30.0 | **`GHSA-f897-62hf-6gxq`** | high | `>=1.10.0 <1.30.1` | **no** |
| `zod` | 4.3.6 | **`GHSA-mrhx-c7xc-m3w5`** | high | `<4.6.6` | **no** |

- The three high entries are `@brave/brave-search-mcp-server` itself (via both libraries), `@modelcontextprotocol/sdk` and `zod`. With C1 (the whole set) the same two libraries show up as high. The other pins resolve `@modelcontextprotocol/sdk` 1.32.2 and `zod` 4.6.7 in their own trees (C2), so brave 2.1.4 is the only pin that pulls the vulnerable versions.
- Titles reported by npm: GHSA-f897, "HTTP server transports and handlers did not limit request body size or JSON-RPC batch length"; GHSA-mrhx, "Zod can exhaust memory while validating oversized constrained collections". Whether either one is reachable in brave's default stdio transport was **not analysed** (out of scope for T702; it is a security-engineer review item).
- npm reports `fixAvailable: true` for `zod`. Brave declares `zod` exactly `4.3.6`, so only an `overrides` entry could apply that fix, and the pinned `npx` launch has no project manifest to carry one. (reasoning, not tested)
- Newest version: **2.1.4** (published 2026-09-17; `npm view ... versions` ends at 2.1.4; `dist-tags.latest` 2.1.4). No newer release exists to audit in a scratch directory.
- Upstream: the `package.json` on the default branch of `github.com/brave/brave-search-mcp-server` still says version 2.1.4 but declares `@modelcontextprotocol/sdk` `1.32.2` and `zod` `4.6.7`, so a fix exists in the source but has not been published. (unverified: read once through a web fetch, not from a clone or a tag.)
- **Upgrade path:** none today. A brave release above 2.1.4 would end the acceptance (condition (a)) and would need its own audit.

## 4. Python pins

| Server / scope | Package | Pinned | Audit tool | High | Critical | Advisory ids | Fixed in | Clean upgrade path |
|----------------|---------|--------|------------|------|----------|--------------|----------|--------------------|
| git (`uvx`) | `mcp-server-git` | 2026.10.10 | PyPI JSON + OSV (C4, C5) over the 34-pin tree resolved on 2026-11-01 (wheels only, `--universal`, Python 3.12) | 0 | 0 | none on any of the 34 pins (including `mcp` 1.30.0, `starlette` 1.10.0, `cryptography` 50.0.2, `gitpython` 3.2.1) | n/a | not needed |
| security-audit, poc-security-audit, context-retriever (in-repo, `python3 -m ...`) | `implementation/runtime/security/requirements-mcp-server.lock.txt` (byte-identical to `implementation/runtime/memory/requirements-mcp-server.lock.txt`) | `mcp==2.2.0`, `httpx2` 2.14.0 / 2.16.0 and 31 more (35 entries) | PyPI JSON + OSV (C5) | 0 | 0 | none | n/a | not needed |

Limits of the Python results:
- `uvx` resolves the dependencies of `mcp-server-git` again at launch, without a lock file. The result covers the tree resolved on 2026-11-01 for Python 3.12 with wheels only. Another interpreter or a later date can resolve a different tree.
- `pip-audit` itself was not run (not installed; installing and executing it was avoided). C5 queries the PyPI advisory data that `pip-audit` uses by default, plus OSV. Treat this as a substitute for a `pip-audit` run. (unverified that the two give identical output)
- `implementation/runtime/memory/requirements.txt` (`fastembed`, `tree-sitter*`) belongs to the index builder, not to an MCP server pin, and was not audited.

## 5. Not covered

- **Remote servers** (`context7`, `hindsight`, `cwso`, `hf-mcp-server`): URL entries, with no package pin to audit. No result is claimed for them.
- **Docker digests**: `servers.yaml` at `3394229a` has no docker entry (`audit-mcp-pins.py list` shows none).
- **`npm audit signatures`** (`--signatures`, full install) was not run. It is outside the T702 brief.
- **Runtime downloads** (Playwright browsers) are not in any lock tree.

## 6. Consequence for the release (for the user's decision, question 3 of plan-124)

- The two Brave HIGH findings of SEC-T676-02 (the `@brave/brave-search-mcp-server` and `@modelcontextprotocol/sdk` entries) **remain**. Two further HIGH advisories that were never accepted (`GHSA-f897-62hf-6gxq`, `GHSA-mrhx-c7xc-m3w5`) now also apply to the same pin.
- Under plan-124 T702, "any other `SECURITY:HIGH` blocks". Whether these two new advisories count as "other" or as part of the Brave decision is for the user and the security engineer to decide. This artifact does not rule on that.
- There is no clean upgrade path: no newer brave release exists. The available options are the user's decision (for example: renew an acceptance in a new acceptance version that also covers the two new ids, wait for an upstream release, or drop or replace the pin). Nothing was changed.
