# Artifact: mcp-server-packages-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T637 (plan-121 Addendum 2): verify the MCP server packages the shipped configs launch; propose corrected, pinned entries (audit SEC-002).
- **Owner**: devops-engineer (research only; no file other than this artifact was changed; no package was installed or executed).
- **Based on**: `docs/tasks/task-T637.md`, `docs/artifacts/security-review-release-v8-v1.md` (SEC-002), `implementation/knowledge/mcp/servers.yaml` (develop `30ef8ba`), `implementation/.mcp.json` and the six other generated projections, `implementation/scripts/sync.mjs`, `scripts/merge-mcp-json.py`.
- **Research date**: 2026-10-14 (all "age" figures are relative to this date, about 21:35 UTC).
- **Sources used** (all read-only): npm registry JSON (`registry.npmjs.org/<pkg>`, `/-/org/<scope>/package`), npm download counts (`api.npmjs.org`), PyPI JSON and PyPI provenance API, OSV (`api.osv.dev`), GitHub REST API and raw README/source files of the upstream repositories, one WebFetch of a GitHub advisory page, `uvx --help`, the `ctx7` CLI for uv and npm documentation, and the local npx cache (package.json version fields only, to see which versions this machine resolves today).
- **Status**: Proposal. Names and pins go to the user for approval; a later task applies them.

## 1. Verdict summary (one line per server)

| Server key | Launcher today | Verdict |
|---|---|---|
| `gitlab` | `npx -y @zereight/mcp-gitlab` | Exists; third-party, single maintainer, receives the GitLab PAT. Four published advisories (two CRITICAL) fixed only in `>= 2.1.30`. Pin `2.2.5`. |
| `playwright` | `npx -y @playwright/mcp@latest` | Exists; Microsoft. Replace `@latest` with `0.0.83`. |
| `fetch` | `npx -y mcp-fetch-server` | Exists; third-party personal repo, 2 npm maintainers. SSRF advisory against `<= 1.0.2`. Pin `1.1.2`. |
| `memory` | `npx -y @modelcontextprotocol/server-memory` | Exists; official reference server. Pin `1.0.0`. |
| `sequential-thinking` | `npx -y @modelcontextprotocol/server-sequential-thinking` | Exists; official reference server. Pin `1.0.0`. |
| `brave` | `npx -y @brave/brave-search-mcp-server` | Exists; Brave's own org. Pin `2.1.4`. |
| `filesystem` | `npx -y @anthropic/mcp-filesystem` | **Nonexistent (404). The `@anthropic` npm scope belongs to an unrelated individual account, not Anthropic PBC (grade HIGH, see 3.1).** Replace with `@modelcontextprotocol/server-filesystem@1.0.0` plus an allowed directory. |
| `github` | `npx -y @github/mcp-github` | **Nonexistent (404).** GitHub's official server is not an npm package (Go binary, container image `ghcr.io/github/github-mcp-server`, hosted endpoint). Replace with the container pinned by digest (recommended) or the hosted endpoint (alternative). |
| `git` | `npx -y @modelcontextprotocol/mcp-git` | **Nonexistent (404).** The reference git server is the PyPI package `mcp-server-git`. Replace with `uvx mcp-server-git@2026.10.10 --repository .`. |
| `supabase` | `npx -y @supabase/mcp` | **Nonexistent (404).** Real package: `@supabase/mcp-server-supabase`. Replace; pin `0.13.0` (0.14.0 is hours old). |
| `docker` | `npx -y docker-mcp` | Exists; 1 release ever, 0 stars, about 2.2k downloads a month, single maintainer, can control the Docker daemon. Pin `1.0.0` or remove (user decision). |
| `postgresql` | `npx -y postgres-mcp` | Exists; unrelated to any database vendor, last release 2025-04-20, 0 stars, about 670 downloads a month, single maintainer. As configured it cannot work (needs `.env`-style DB configuration). Pin `1.0.4` or remove (user decision, removal recommended). |
| `toolradar` | `npx -y toolradar-mcp` | Exists; 4 stars, about 205 downloads a month, single maintainer, receives `TOOLRADAR_API_KEY`. Pin `2.1.0`. |

Remote and local-Python entries are out of scope: `context7`, `hindsight`, `cwso`, `hf-mcp-server` (remote URLs, not packages; not pinnable, not verified here) and `context-retriever`, `security-audit`, `poc-security-audit` (repository code launched with `python3 -m`).

## 2. Per-server evidence

Owner column: scope or account that owns the name. "Maint." is the npm maintainer list at research time. "Prov." means the latest version carries npm provenance (trusted publishing by GitHub Actions). Downloads are npm "last month" (`api.npmjs.org`, 2026-10-14). Advisories come from OSV, which aggregates GitHub advisories; an empty result means none were found there, not that none exist.

### 2.1 Entries that exist today

| Package | Owner / vendor's own? | Latest (published) | Repository | Maintenance signals | Advisories (OSV) |
|---|---|---|---|---|---|
| `@zereight/mcp-gitlab` | Personal scope of user `zereight`; **not GitLab's**. Third-party. | 2.2.6 (2026-10-14 18:49Z); 2.2.5 (2026-10-13 23:10Z); 172 versions, 2.1.70 (2026-10-08), 2.2.0 (2026-10-08) | github.com/zereight/gitlab-mcp (User-owned; 2041 stars; 358 forks; 23 open issues; pushed 2026-10-14) | 1 npm maintainer (`zereight`). About 564k downloads a month. Releases almost daily. Prov.: yes (OIDC). MIT. | GHSA-2h44-8472-frjj / CVE-2026-61559 SSRF (CRITICAL, fixed 2.1.27); GHSA-cv3r-c5h8-f4g5 / CVE-2026-61560 arbitrary file read via `upload_markdown`, PAT exfiltration (CRITICAL, fixed 2.1.27); GHSA-5648-rgj9-v224 `execute_graphql` read-only bypass and unauthenticated transports (HIGH, fixed 2.1.30); GHSA-vmp7-252j-cwp7 / CVE-2026-61568 DNS rebinding (fixed 2.1.30). All published 2026-09-15/16. **None affect 2.2.5.** |
| `@playwright/mcp` | `@playwright` scope, Microsoft. Vendor's own. | 0.0.83 (2026-09-28) | github.com/microsoft/playwright-mcp (Org: microsoft; 38k stars; pushed 2026-10-08) | 5 npm maintainers incl. `microsoft-oss-releases`. About 31M downloads a month. Prov.: yes. Apache-2.0. Pre-1.0 versions. | GHSA-8rgw-6xp9-2fg3 / CVE-2025-9611 DNS rebinding, fixed 0.0.40. None affect 0.0.83. |
| `mcp-fetch-server` | Unscoped name; account `zachcaceres` (repo owner `zcaceres`). Third-party. | 1.1.2 (2026-03-09) | github.com/zcaceres/fetch-mcp (User-owned; 827 stars; pushed 2026-03-12). `package.json` name matches. | 2 npm maintainers (`zachcaceres`, `ilintar`; the second is unverified). About 26k downloads a month. Prov.: no (manual publish). 6 versions. MIT. No release for 7 months. | GHSA-8fxj-2g9q-8fjw / CVE-2025-65513 SSRF, private-IP validation bypass; affected range recorded as `<= 1.0.2`, no fixed version stated. 1.1.2 is outside the recorded range; whether the code fix is complete was **not verified**. |
| `@modelcontextprotocol/server-memory` | `@modelcontextprotocol` org (54 packages; the MCP project's reference servers, Anthropic-sponsored). Vendor's own. | 1.0.0 (2026-10-11); previous 2026.8.31 | github.com/modelcontextprotocol/servers (91k stars; pushed 2026-10-13) | 6 npm maintainers. About 717k downloads a month. Prov.: yes. | None. |
| `@modelcontextprotocol/server-sequential-thinking` | same | 1.0.0 (2026-10-11); previous 2026.8.31 | same | same; about 618k downloads a month | None. |
| `@brave/brave-search-mcp-server` | `@brave` scope, Brave Software. Vendor's own. | 2.1.4 (2026-09-17) | github.com/brave/brave-search-mcp-server (Org: brave; 1497 stars; pushed 2026-10-14) | 10 npm maintainers (brave.com addresses). About 105k downloads a month. Prov.: no (manual publish). MIT. | None. |
| `docker-mcp` | Unscoped; account `sondt2709`. Third-party individual. | 1.0.0 (2025-07-13), the only release | github.com/sondt2709/docker-mcp (0 stars; pushed 2025-07-13) | 1 maintainer. About 2.2k downloads a month. No updates for 15 months. Prov.: no. README needs `DOCKER_MCP_LOCAL=true` for a local daemon; the shipped entry sets no env. | None found. |
| `postgres-mcp` (npm) | Unscoped; account `alvamind`, repo org `llm-graph`. Third-party, no relation to PostgreSQL or any vendor. **Not** the PyPI `postgres-mcp` of Crystal DBA. | 1.0.4 (2025-04-20); 5 versions in 4 days; `package.json` on repo main says 1.0.3 | github.com/llm-graph/postgres-mcp (0 stars; 1 open issue; pushed 2025-04-20) | 1 maintainer. About 670 downloads a month. No updates for 18 months. Prov.: no. Configured through `DB_ALIASES`, `DB_*_HOST` etc. loaded from `.env` files in its working directory. | None found. |
| `toolradar-mcp` | Unscoped; account `louiscorneloup`, repo owner `Nadeus`. Whether this is the toolradar.com operator is **unverified**. | 2.1.0 (2026-08-21); repo main says 2.1.1 (unpublished) | github.com/Nadeus/toolradar-mcp (4 stars; pushed 2026-08-25) | 1 maintainer. About 205 downloads a month. 3 versions, zero dependencies. Prov.: no. | None found. |

Installed-version cross-check (local npx cache, version fields only): this machine currently resolves `@zereight/mcp-gitlab` 2.2.5, `@playwright/mcp` 0.0.83, `mcp-fetch-server` 1.1.2, `@brave/brave-search-mcp-server` 2.1.4, and the two reference servers 1.0.0. The proposed pins equal what is running now, so they change no behaviour on this machine.

### 2.2 The four nonexistent names

All four return HTTP 404 from `registry.npmjs.org` (2026-10-14 21:35 UTC). A 404 also hides a package that was unpublished; the registry gives no history for it, and that is **not verified** either way.

| Name | Scope ownership (from `registry.npmjs.org/-/org/<scope>/package`) | Squat exposure |
|---|---|---|
| `@anthropic/mcp-filesystem` | The `anthropic` name is an **individual npm user**, not Anthropic PBC: 4 packages, all unrelated and from 2022 (`angular-schema-form` and three siblings; maintainer address is a Gmail account). Anthropic PBC publishes under `@anthropic-ai` (36 packages, 15 maintainers; no filesystem server). | **The owner of the `anthropic` account can publish `@anthropic/mcp-filesystem` at any time, and every `npx -y` launch of the extended profile would then run it with the user's file access.** This is the "scope registrable by a third party" case that SEC-002 grades HIGH. I cannot prove who holds the account; I can show it is not Anthropic PBC's. |
| `@github/mcp-github` | `@github` is GitHub's org (153 packages, 88 scoped, e.g. `@github/copilot` published by GitHub Actions). | Only GitHub org members can publish. Low squat exposure. |
| `@modelcontextprotocol/mcp-git` | `@modelcontextprotocol` org (54 packages). The git server was never an npm package; the org has no `server-git`. | Only org members can publish. Low squat exposure. |
| `@supabase/mcp` | `@supabase` org (66 packages, all scoped; includes `@supabase/mcp-server-supabase`, `@supabase/mcp-utils`, `@supabase/mcp-server-postgrest`). | Only org members can publish. Low squat exposure. |

### 2.3 Replacements (documented by the vendor)

| Server | Replacement | Evidence |
|---|---|---|
| filesystem | `@modelcontextprotocol/server-filesystem` 1.0.0 (2026-10-11); prev 2026.8.31 (2026-08-31). Prov.: yes (GitHub Actions OIDC). About 2.56M downloads a month. 6 npm maintainers. | Documented in the server's README (`npx -y @modelcontextprotocol/server-filesystem <dir>...`). **Needs at least one allowed directory** (argument or client Roots); with neither it exits with status 1. Source resolves a relative path against the working directory (`path.resolve`), so `.` is the launch directory. Old CVEs (GHSA-hc55-p739-j48w, GHSA-q66q-fx2p-7w4m) are fixed in 2025.7.1; none affect 1.0.0 or 2026.8.31. |
| git | PyPI `mcp-server-git` 2026.10.10 (2026-10-11); prev 2026.8.18. Author "Anthropic, PBC.", repo `modelcontextprotocol/servers/src/git`, MIT, not yanked. PyPI provenance attestation present (GitHub trusted publisher, `modelcontextprotocol/servers`, `release.yml`). sha256 of the wheel: `5bd3dc5736d67ab01b664363055001b2ce84e945c17af98875e5e04b5823d335`. Dependencies float: `mcp<2,>=1.29.0`, `gitpython>=3.1.60`, `click`, `pydantic`. | README documents `uvx mcp-server-git --repository <path>`; `--repository .` works from any subdirectory of the working tree. Four CVEs (CVE-2025-68143/68144/68145, CVE-2026-27735) are fixed in `>= 2026.1.14`; none affect 2026.10.10. |
| github | Not an npm package. GitHub's official server `github/github-mcp-server` (MIT, 33.6k stars, pushed 2026-10-14): container `ghcr.io/github/github-mcp-server` (public), release `v2.0.2` (2026-10-08; 2.0.0 was 2026-10-06), and a hosted endpoint `https://api.githubcopilot.com/mcp/` that accepts `Authorization: Bearer <PAT>`. The npm package `@modelcontextprotocol/server-github` is the deprecated predecessor (last release 2025.4.8, npm deprecation notice "no longer supported"): do not use. | Image `ghcr.io/github/github-mcp-server:v2.0.2` resolves anonymously to manifest digest `sha256:ffced0d76e77428532a2ced185516992d77fd146d69eec2f244e6237d1a97796` (read from the registry 2026-10-14). The image signature and attestations were **not verified**. Advisories on the Go server: GHSA-pjp5-fpmr-3349 (medium, HTTP-server mode, fixed 1.1.2), GHSA-w4q6-qw23-4rg7 / CVE-2026-47427 (high, availability only: a malformed `completion/complete` request crashes the process; "patched versions: none" and "also affects latest main" per the advisory page, read via WebFetch summary, not independently confirmed). |
| supabase | `@supabase/mcp-server-supabase` 0.14.0 (**2026-10-14 15:29Z, hours old**); 0.13.0 (2026-09-17); 62 versions. Prov.: yes. About 416k downloads a month. 2 npm maintainers (`gregnr`, `mattrossman`) under Supabase's org; repo `supabase/mcp` (Org-owned, 2951 stars, pushed 2026-10-14). Binary `mcp-server-supabase`. | Package has a stdio CLI. From its source: token via `--access-token` **or** env `SUPABASE_ACCESS_TOKEN` (use the env form; argv would leak the token), plus `--read-only`, `--project-ref`, `--features`. Supabase's own README now leads with the hosted endpoint `https://mcp.supabase.com/mcp` (OAuth), which needs no package. No OSV advisories. 0.13.0 carries a breaking change for destructive-SQL confirmation (elicitation), which makes clients without elicitation support behave differently; **not tested**. |

## 3. Findings that change SEC-002's grade or scope

1. **SEC-002 is HIGH for `@anthropic/mcp-filesystem` alone.** SEC-002 said "HIGH if an unclaimed scope can be registered". The scope is not unclaimed; it is held by an unrelated individual account, which has the same effect (a third party can make the name resolve). The other three names are LOW exposure (vendor org scopes).
2. **`@zereight/mcp-gitlab` was unpinned while carrying four advisories, two CRITICAL, that include PAT exfiltration.** Anything below 2.1.30 is unsafe. `npx -y` with no version resolved the latest, so current users are fine, but a stale npx cache or a registry mirror could serve an old build. The pin must be at least 2.1.30.
3. **`mcp-fetch-server` had an SSRF advisory (`<= 1.0.2`).** Pinning 1.1.2 keeps users out of the affected range. The server is an SSRF-shaped tool by design (fetches arbitrary URLs); residual risk stays.
4. **Transitive dependencies are not pinned by any proposed entry** (`npx pkg@x` and `uvx pkg@x` pin only the top package). Hash-pinning would need a lockfile or `--require-hashes`, which the current generator cannot express. Not solved by this proposal.

## 4. Proposed `servers.yaml` entries (exact)

Pin policy: every `npx` entry carries an exact `name@x.y.z` (no `@latest`, no ranges). `-y` **stays**: the servers are launched over stdio by a client with no terminal to answer npm's install confirmation, and `-y` only skips that confirmation; with an exact pin it no longer lets a newer, unreviewed version in. (The exact non-interactive behaviour of `npx` without `-y` was not tested; the npm documentation retrieved only states that the flag skips the download prompt.) Remote entries and `python3 -m` entries are unchanged and not shown.

Pins chosen: the vendor's newest version that is not under a day old and has no advisory, except where the machine already runs a newer one (listed in 2.1). Conservative fallbacks, if a longer soak is wanted, are given in the table in section 5.

```yaml
  gitlab:
    tags: [core]
    transport: stdio
    command: npx
    args: ["-y", "@zereight/mcp-gitlab@2.2.5"]
    env:
      GITLAB_PERSONAL_ACCESS_TOKEN: { fromEnv: GITLAB_PERSONAL_ACCESS_TOKEN, secret: true }
      GITLAB_API_URL: { fromEnv: GITLAB_API_URL }

  playwright:
    tags: [core]
    transport: stdio
    command: npx
    args: ["-y", "@playwright/mcp@0.0.83"]

  fetch:
    tags: [core]
    transport: stdio
    command: npx
    args: ["-y", "mcp-fetch-server@1.1.2"]

  memory:
    tags: [core]
    transport: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-memory@1.0.0"]

  sequential-thinking:
    tags: [core]
    transport: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-sequential-thinking@1.0.0"]

  brave:
    tags: [core]
    transport: stdio
    command: npx
    args: ["-y", "@brave/brave-search-mcp-server@2.1.4"]
    env:
      BRAVE_API_KEY: { fromEnv: BRAVE_API_KEY, secret: true }

  filesystem:
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem@1.0.0", "."]

  github:
    # Official GitHub MCP server, container pinned by digest (tag v2.0.2). Token is passed by
    # name (-e VAR), never in argv.
    tags: [extended]
    transport: stdio
    command: docker
    args: ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server@sha256:ffced0d76e77428532a2ced185516992d77fd146d69eec2f244e6237d1a97796"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: { fromEnv: GITHUB_PERSONAL_ACCESS_TOKEN, secret: true }

  git:
    # PyPI package, not npm. Requires uv on PATH.
    tags: [extended]
    transport: stdio
    command: uvx
    args: ["mcp-server-git@2026.10.10", "--repository", "."]

  supabase:
    # Token comes from the environment (the CLI also accepts --access-token; do not use it).
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "@supabase/mcp-server-supabase@0.13.0", "--read-only"]
    env:
      SUPABASE_ACCESS_TOKEN: { fromEnv: SUPABASE_ACCESS_TOKEN, secret: true }

  docker:
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "docker-mcp@1.0.0"]

  postgresql:
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "postgres-mcp@1.0.4"]

  toolradar:
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "toolradar-mcp@2.1.0"]
    env:
      # SECURITY: never inline a real key here. Set TOOLRADAR_API_KEY in your shell
      # or your platform's secret store. v1 leaked a live key — do not repeat.
      TOOLRADAR_API_KEY: { fromEnv: TOOLRADAR_API_KEY, secret: true }
```

Notes on the entries:

- The generator's YAML reader (`parseServersYaml` in `sync.mjs`) splits inline arrays on commas, so no argument may contain a comma; none of the above does. It does not need a change for `command: docker` or `command: uvx` (`command` is copied verbatim; opencode gets `[command, ...args]`).
- `supabase` gains `--read-only` (writes disabled) as a safe default; this is a behaviour decision for the user (the old entry could not start at all, so there is no existing behaviour to preserve). Drop the flag to allow writes.
- `github` as a digest is the only immutable pin available here; a tag is mutable. Docker becomes a prerequisite for this opt-in server, as it already is for the `docker` server's purpose.
- Hosted alternative for `github` (no local code, no pin, vendor-controlled; **not recommended as a drop-in because of the merge behaviour in section 6**):

```yaml
  github:
    tags: [extended]
    transport: remote
    url: "https://api.githubcopilot.com/mcp/"
    headers:
      Authorization: { fromEnv: GITHUB_PERSONAL_ACCESS_TOKEN, secret: true, wrap: "Bearer {VAR}" }
```

- Hosted alternative for `supabase`: `transport: remote`, `url: "https://mcp.supabase.com/mcp"` (OAuth, no secret in the config); the same merge caveat applies on already-installed targets.

## 5. Pin choices, soak alternatives and single-maintainer flags

| Entry | Proposed pin (age at 2026-10-14) | More conservative alternative | Single-maintainer upstream? |
|---|---|---|---|
| gitlab | 2.2.5 (about 22 h; what this machine runs) | 2.2.1 (2026-10-09) or 2.1.70 (2026-10-08, last 2.1.x; both satisfy the `>= 2.1.30` floor, but 2.2.x behaviour changes were not diffed) | **Yes** (one npm maintainer, one personal repo; high release cadence, provenance present) |
| playwright | 0.0.83 (16 days) | 0.0.82 (2026-09-18) | No (Microsoft) |
| fetch | 1.1.2 (7 months) | none newer | **Partly**: personal repo, 2 npm maintainers (one unverified), no provenance |
| memory | 1.0.0 (3 days) | 2026.8.31 (6 weeks) | No (MCP org) |
| sequential-thinking | 1.0.0 (3 days) | 2026.8.31 | No |
| brave | 2.1.4 (4 weeks) | 2.1.3 (2026-08-20) | No (Brave org) |
| filesystem | 1.0.0 (3 days) | 2026.8.31 (6 weeks) | No |
| git | 2026.10.10 (3 days) | 2026.8.18 (8 weeks) | No (MCP org; PyPI attested) |
| github | v2.0.2 (6 days; 2.0.0 is 8 days) | v1.14.0 (2026-10-02) pre-major | No (GitHub) |
| supabase | 0.13.0 (4 weeks) | 0.12.0 (2026-09-04) | No (Supabase org; 2 npm maintainers) |
| docker | 1.0.0 | none | **Yes**, abandoned, 0 stars |
| postgresql | 1.0.4 | none | **Yes**, abandoned, 0 stars |
| toolradar | 2.1.0 (7 weeks) | 2.0.x does not exist (1.0.1 is the prior release) | **Yes**, 4 stars |

The two reference servers jumped from calendar versions (`2026.8.31`) to `1.0.0` on 2026-10-11 (release note: "release v1.0.0, sdk1"). Numerically `2026.8.31` sorts above `1.0.0`, which only matters for tooling that compares versions; an exact pin is unaffected.

Recommendation on the three weak upstreams (user decision): remove `postgresql` (it cannot work as configured, reads `.env` files from the launch directory, and is abandoned); remove or replace `docker` (container control through an unreviewed single-release package); keep `toolradar` pinned (it is the service operator's own tool as far as the README shows; ownership unverified). Candidate replacements that exist, not evaluated beyond existence: PyPI `postgres-mcp` (Crystal DBA, 0.3.0, 3.4k stars on GitHub) and PyPI `mcp-server-docker` (0.3.0, 2026-08-07, 748 stars). If removed, the entries leave `servers.yaml` and `generatorOwnedKeys` shrinks.

## 6. Impact on platform projections and on the root refresh

- **Generated files that change.** Core npx pins (`gitlab`, `playwright`, `fetch`, `memory`, `sequential-thinking`, `brave`) appear in all seven projections: `.mcp.json` (claude-code), `.gemini/settings.json`, `.opencode/opencode.json`, `.cursor/mcp.json`, `.cline/mcp.json`, `.pi/mcp.json`, `.vscode/mcp.json` (github/Copilot; core tags only). The seven extended entries (`filesystem`, `github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`) appear in six: all of the above except `.vscode/mcp.json`. Each exists twice: under `implementation/` and as a root copy (root `.mcp.json`, `.gemini/`, `.opencode/`, `.cursor/`, `.cline/`, `.pi/`, `.vscode/mcp.json.provenance.json` are tracked; the root and `implementation/` JSON compared identical for the six non-vscode files; the root `.vscode/mcp.json` is gitignored and was deliberately not compared). That is up to 14 JSON files, plus provenance sidecars only if a server key is added or removed (the proposal keeps all 20 keys, so sidecars stay unchanged unless `docker` or `postgresql` is removed; then 12 sidecars change).
- **Per-format shape.** opencode: `"command": ["npx","-y","pkg@x"]` / `["uvx","pkg@x","--repository","."]` / `["docker","run",...]` and `environment` with `{env:VAR}`; gemini and cursor/pi/cline/claude-code: `command` + `args` + `env` with that platform's placeholder syntax. The `supabase` and `github` entries add a secret `env` entry that each projection renders as a platform-native reference, never a value.
- **Unset variables.** `SUPABASE_ACCESS_TOKEN` and `GITHUB_PERSONAL_ACCESS_TOKEN` are new variables. Per `mcp-header-url-templating-design-v2.md` §9, an unset `${VAR}` in claude-code format loads the config with a warning, and only that server fails to start. Same behaviour as the existing `BRAVE_API_KEY`.
- **Already-installed targets (`install.sh --update`) and `merge-mcp-json.py`.** The merge is recursive: arrays and scalars from the source win, but keys present only in the destination object survive. Consequences: (a) `args` array pins overwrite old args, good; (b) `command` changes (`npx`→`docker`/`uvx`) overwrite, good; (c) a **transport change stdio→remote leaves the old `command` and `args` in place next to the new `url`**, producing a hybrid object that can still try to launch the unpinned 404 package; `--force-prune-keys` only removes dest-only server names, not stale keys inside a name that still exists. This is why the container form is the recommended `github` replacement and why the hosted alternatives should wait for a merge-script change; (d) removed servers are pruned via the provenance sidecar's retired keys (checked by reading the script; not run); (e) `env` objects merge, so dest-only env keys persist (SEC-007).
- **Registry generator.** `implementation/registry/index.json` contains no `mcp` entries (0 matches), so `generate-registry.py` should not change; I did not run its `--check`.
- **Commands the applying task runs** (not run here): `node implementation/scripts/sync.mjs --root implementation`, then `--check`, then the root refresh (re-install of the projections to the repository root), then `python3 implementation/scripts/generate-registry.py --check`. CI job `sync-no-diff` regenerates and diffs.
- **Tests that pin the defect.** `tests/functional/test_audit_server.py::ServersYamlEntryTests::test_other_entries_untouched_sample` asserts `filesystem` args `["-y","@anthropic/mcp-filesystem"]` and `git` args `["-y","@modelcontextprotocol/mcp-git"]` ("disclosed defects must remain as-is"), so it **fails after the fix and must be updated in the same change**. `tests/functional/test_mcp_secret_guard.py`, `test_mcp_platform_conformance.py`, `test_mcp_schema_validation.py` and `test_sync_determinism.py` should keep passing (new secret entries use the existing `${VAR}`/`{env:VAR}` placeholder families), but I did not run them. A new test that every `npx` arg carries an exact `@x.y.z` and no `@latest` would lock the pin policy in.
- **Prerequisites.** `implementation/PREREQUISITES.md` lists only Node 18+. The fix adds `uv` (for `git`) and Docker (for `github`; optional extended servers). `uv` is present on this machine (0.11.9). Both belong in `PREREQUISITES.md`.
- **Agent tool grants.** `.claude/agents` contains no `mcp__git__*`, `mcp__github__*`, `mcp__filesystem__*` or `mcp__supabase__*` grants (grep), so server-key names remain valid and no agent file needs to change. The tool names the new servers expose differ from the (never working) old ones; nothing depends on them.

## 7. Biggest risks

1. **`@anthropic/mcp-filesystem` is a live squat opportunity** held by an unrelated account (3.1). Until the entry is replaced, every extended-profile install is exposed. This is the one finding that justifies not waiting for the next sprint.
2. **Stale installs keep the bad launchers.** A target that already merged the old config keeps old keys unless the new object overrides them (6). Replacements that stay on `command`+`args` override cleanly; the hosted forms do not. Releasing the fix without a changelog note leaves existing users on the old entries until they run `--update`.
3. **`@zereight/mcp-gitlab` carries the GitLab PAT, has one maintainer and ships almost daily.** Pinned 2.2.5 is clean in OSV today, but this is the most security-sensitive third-party dependency (shown by four advisories in one fortnight) and needs a deliberate, reviewed bump process.
4. **Fresh majors as pins.** `1.0.0` of the reference servers (3 days), `mcp-server-git` 2026.10.10 (3 days) and `github-mcp-server` 2.0.x (6-8 days) are new. They are vendor-published with provenance, but a longer soak is possible (section 5).
5. **Abandoned single-maintainer packages with powerful capabilities** (`docker-mcp`, `postgres-mcp`): no advisories exist because nobody is looking. Pinning does not make them reviewed.
6. **Transitive dependencies float** (3, point 4).

## 8. What I could not verify

- Who operates the npm account `anthropic` and whether it is unrelated to Anthropic PBC beyond the evidence in 2.2 (unrelated 2022 packages, Gmail address). Source: npm registry JSON, 2026-10-14.
- Whether the `404` of the four names is "never existed" versus "unpublished". The registry does not say.
- npm `-/org/<scope>/package` shows packages visible to the public; a scope can be held with no public package. For `@github`, `@modelcontextprotocol` and `@supabase` the presence of many vendor packages is strong evidence of ownership, not proof. `www.npmjs.com` returned HTTP 403 to non-browser requests, so org pages were not read.
- Advisory completeness: OSV only. GitHub advisory pages were read for `github-mcp-server` GHSA-w4q6-qw23-4rg7 (via WebFetch summary, not re-checked). No `npm audit` / `pip-audit` was run on the resolved dependency trees (nothing was installed).
- Whether `mcp-fetch-server` 1.1.2 truly fixes CVE-2025-65513 (the advisory has no fixed version).
- Supabase 0.13.0 versus 0.14.0 behaviour on a given client, and the effect of `--read-only` on features users rely on. Not tested; no package was run.
- That `.` is accepted by `@modelcontextprotocol/server-filesystem@1.0.0` as an allowed directory: confirmed from the `main` branch source (`path.resolve`), not from the 1.0.0 tag. Likewise `--repository .` for `mcp-server-git@2026.10.10` is from the README on `main`.
- The container image's signature and attestations; the digest was read from `ghcr.io` anonymously on 2026-10-14 only.
- Exact `npx` behaviour without `-y` in a non-interactive launch.
- The identity of npm co-maintainer `ilintar` on `mcp-fetch-server`, and whether `Nadeus`/`louiscorneloup` is the operator of toolradar.com.
- Which of the tests listed in 6 pass after the change (nothing was run), and how each client (Cursor, Cline, Gemini, opencode, pi, Copilot) treats the pinned and `docker`/`uvx` launchers. Only the generator code was read.
- Remote entries (`context7`, `hindsight`, `cwso`, `hf-mcp-server`): not examined.

Process disclosures: the `ctx7` CLI (user rule) was run through `npx` twice for uv and npm documentation, so `ctx7@0.6.1` sits in the npx cache; no MCP server package was installed or run. A structural `jq` comparison of the worktree's gitignored `.vscode/mcp.json` against the generated one was run with its output discarded (only the exit status was seen; the file's content was not read or displayed).

## 9. Decisions requested from the user

1. Approve the five replacements: `filesystem` -> `@modelcontextprotocol/server-filesystem@1.0.0 .`; `git` -> `uvx mcp-server-git@2026.10.10 --repository .`; `github` -> the digest-pinned container (or the hosted endpoint, accepting the merge-script change); `supabase` -> `@supabase/mcp-server-supabase@0.13.0 --read-only` (or hosted, same caveat).
2. Approve the pins (section 4) or choose the soaked alternatives (section 5), especially `@zereight/mcp-gitlab` 2.2.5 versus 2.2.1.
3. Decide whether `postgresql` and `docker` are removed or kept pinned.
4. Confirm that SEC-002 is regraded HIGH for the `@anthropic` scope.
