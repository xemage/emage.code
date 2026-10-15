---
title: MCP Servers
---
# MCP Servers

emage.code uses [Model Context Protocol](https://modelcontextprotocol.io) servers as the integration layer between agents and external tools.

All servers are declared once in [`implementation/knowledge/mcp/servers.yaml`](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/knowledge/mcp/servers.yaml) and projected to platform-specific config files.

## Tag system

| Tag | Behaviour |
|-----|-----------|
| `core` | Emitted to **every** platform, always available |
| `extended` | Emitted only to platforms that opt in via their manifest (all except `github`: `cursor`, `gemini`, `opencode`, `pi`, `claude-code`, `cline`) |

## Core servers (always available)

| Server | Purpose | Used by |
|--------|---------|---------|
| `gitlab` | Repository, issues, MRs, pipelines | Orchestrator, Scrum Master, DevOps, Release Manager |
| `playwright` | Browser automation, E2E testing | QA, Frontend, Demo Agent |
| `memory` | Persistent knowledge graph | Orchestrator (team memory) |
| `sequential-thinking` | Complex problem decomposition | Architect, Orchestrator |
| `brave` | Technology discovery (web search) | Technology Scout, Feasibility |
| `context7` | Framework / API documentation lookup | Technology Scout, Integration |
| `hindsight` | Remote MCP endpoint; its URL is read from `HINDSIGHT_MCP_URL` | Not stated in `servers.yaml` |

The `fetch` server was removed in v8.0.0 (audit SEC-T646-01). Agents read web pages with the platform `web` tool; no agent is granted a fetch tool any more, and no agent was given Playwright in its place. See [Migrating an existing install](#migrating-an-existing-install-from-v7x).

## Extended servers (opt-in)

`cwso`, `hf-mcp-server`, `context-retriever`, `security-audit`, `poc-security-audit`, `filesystem`, `github`, `git`, `supabase`, `toolradar`.

The `docker` and `postgresql` servers were removed in v8.0.0 (audit SEC-002); see [Migrating an existing install](#migrating-an-existing-install-from-v7x).

Most require additional credentials — see [`servers.yaml`](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/knowledge/mcp/servers.yaml) for the full env-var contract. The two Python servers `security-audit` and `poc-security-audit` need no credentials; `poc-security-audit` is described [below](#poc-security-scan-server-poc-security-audit).

## Required environment variables

| Variable | Server | Notes |
|----------|--------|-------|
| `GITLAB_PERSONAL_ACCESS_TOKEN` | `gitlab` | Scopes: `api`, `read_repository`, `write_repository` |
| `GITLAB_API_URL` | `gitlab` | Not a secret |
| `BRAVE_API_KEY` | `brave` | Free tier: 2000 queries/month |
| `HINDSIGHT_MCP_URL` | `hindsight` | URL of the remote endpoint |
| `CWSO_MCP_URL` | `cwso` (extended) | URL of the remote endpoint |
| `CWSO_BEARER_TOKEN` | `cwso` (extended) | Sent as `Authorization: Bearer <value>` |
| `CWSO_ORIGIN` | `cwso` (extended) | Sent as the `Origin` header |
| `TOOLRADAR_API_KEY` | `toolradar` (extended) | API key |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | `github` (extended) | Classic PAT or fine-grained. Passed into the container by name (`-e`), never on the command line |
| `SUPABASE_ACCESS_TOKEN` | `supabase` (extended) | Project access token. Read from the environment, never from argv. The server starts with `--read-only` |

Claude Code's `.mcp.json` references these as `${VAR}`; the other platforms use `${env:VAR}` (Opencode: `{env:VAR}`). Claude Code reports an unset variable in `claude mcp list` and uses the literal `${VAR}` text. Export the variables for the servers you use in the environment that starts your assistant.

> **Never commit these.** Use environment variables or a secret vault. See [`SECURITY.md`](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/SECURITY.md) for the full rules.

## Playwright server (`playwright`)

The `playwright` entry (`@playwright/mcp@0.0.83`) is a `core` server for browser automation and E2E testing. It is launched with `--headless --isolated --browser chromium --sandbox --block-service-workers --no-webmcp` and a `--blocked-origins` list that names loopback, link-local, private and carrier-grade-NAT address ranges, `localhost` forms, IPv6 loopback and mapped forms, and user-information URLs. The list is one argument made of semicolon-separated glob patterns (`*` is a wildcard and `{a,b}` is brace alternation, so `172.{16,...,31}.*` covers 172.16 to 172.31). Do not split it, quote it again or expand it. In the T654 and T655 tests the entry was started by a driver that spawned the server directly, without a shell, on Linux; clients that route `args` through a shell, and Windows, are unverified, and a shell would treat the `;` and `*` in this value specially.

It needs a browser that is not installed by `npx`: see [`implementation/PREREQUISITES.md`](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/PREREQUISITES.md). Output files (snapshots, downloads from visited pages) are written to `.playwright-mcp/` in the launch directory. This repository's `.gitignore` excludes it, but `install.sh` does not edit the `.gitignore` of a project that installs emage.code: add `.playwright-mcp/` to that project's `.gitignore`, or point `--output-dir` at an ignored path in a user-owned entry, so page content is not committed by accident.

**Local apps are blocked.** The same list denies `localhost`, `127.*`, `*.localhost`, `10.*`, `192.168.*` and `172.16` to `172.31`, which are the addresses of a local dev server. With the shipped entry the first request to a local app fails with `net::ERR_BLOCKED_BY_CLIENT`, so **the shipped `playwright` entry cannot be used for E2E testing of a local app**. Do not edit its arguments: they are generator-owned and `install.sh --update` restores them. To test a local app, add a second, user-owned entry named `playwright-local` that has the same arguments without `--blocked-origins` (the JSON is in `implementation/PREREQUISITES.md`, section "Local apps are blocked by the shipped entry"). It has no origin restriction at all, so a page it opens can reach every address your host reaches, including internal services and cloud metadata endpoints; use it only on a development machine, for your own pages, and remove it afterwards. `scripts/merge-mcp-json.py` keeps keys that exist only in your file and prunes a name only if the old provenance sidecar lists it as generator-owned or you pass it to `--force-prune-keys`, so `playwright-local` survives `install.sh --update` (a test pins this). The generated agent tool lines name `mcp__playwright`, not `mcp__playwright-local`, so subagents do not receive the second server's tools; use it from your own session (how each platform matches server names is unverified).

**Limits. This is not a security boundary.** The origin flags block a direct navigation or sub-request to a listed origin. They do not cover redirects (an allowed page that answers `302` to a blocked address still reaches it, and the page content is returned to the model), WebSockets, a DNS name that resolves to an internal address, or the `browser_run_code_unsafe` tool, which runs code on the host. The flags only narrow what the entry reaches; the Playwright `--help` text says the same. Four agents (`qa-engineer`, `frontend-developer`, `poc-qa-engineer`, `demo-agent`) list the whole `mcp__playwright` server and so keep that tool; narrowing them to named tools is not shipped, because the generated tool names are not honoured by every platform (see `docs/artifacts/security-review-t655-fetch-removal-v1.md`, SEC-T655-01, and the T656 report). Pages the agent opens can contain prompt-injection text, and nothing here filters it. Evidence: `docs/artifacts/fetch-replacement-evaluation-v1.md`.

## Package pins and runtime requirements of the extended servers

Every `npx`, `uvx` and `docker` entry in `servers.yaml` is pinned to an exact version or digest (audit SEC-002); `@latest` and ranges are not used.

| Server | Launcher | Needs |
|--------|----------|-------|
| `filesystem` | `npx -y @modelcontextprotocol/server-filesystem@1.0.0 .` | Node.js |
| `git` | `uvx mcp-server-git@2026.10.10 --repository .` | `uv` on `PATH` |
| `github` | `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server@sha256:<digest>` | Docker, daemon running, able to pull from `ghcr.io` |
| `supabase` | `npx -y @supabase/mcp-server-supabase@0.13.0 --read-only` | Node.js |

**Pin maintenance.** The devops-engineer bumps the pins at every release and at least monthly; there is no automated scheduler. Each bump is a reviewed change that edits `servers.yaml` and the `APPROVED_NPX_PINS` dict in `tests/functional/test_mcp_package_pins.py` together. Before a bump, check the package with `npm audit` or OSV, and check the registry's latest version and its provenance. `@zereight/mcp-gitlab` holds the GitLab token, has a single maintainer, and releases often with published advisories, so it is reviewed at every release.

### Launch directory and what the extended servers can reach

- `filesystem` (`.`) and `git` (`--repository .`) resolve the path against the directory the assistant was started from. Start the assistant from the project root. Cline's configuration is global: replace `.` with the absolute path of your project there.
- The `filesystem` server can read every file under that directory, including `.env*` files and `.git`. Keep secrets out of the project directory or do not enable the server.
- The `git` server exposes write tools (for example commit and branch operations), not only read tools.

## PoC security scan server (`poc-security-audit`)

A fixed-command, stdio MCP server for the PoC security reviewer (`@poc-security-engineer`). It runs only `git` with fixed argument lists, needs no environment variable or API key, and makes no network call.

It is declared in `servers.yaml` as `tags: [extended]`, `command: python3`, `args: ["-m", "implementation.runtime.security.poc_audit_server", "--allowed-root", "."]`. The Python source is installed into your project's `implementation/runtime/security/` by `scripts/install.sh` (a full install or `--update`; `--projections-only` does not copy it).

### Tools

| Tool | Arguments | Returns |
|------|-----------|---------|
| `scan_secrets` | `root_dir` (the repository top level), `scope` (`worktree`, `index`, `stashes`, `history` or `tracked_names`), `rev_range` (optional, `history` only) | Rule ids, paths (shown as `<redacted-by-rule:ID>` when the name itself matches a rule), line numbers and commits. Never the matched text. |
| `ref_containment` | `root_dir`, `commit` (40 hex characters) | The remote-tracking refs, tags and local branches that contain the commit, `pushed` and `last_fetch_time`. `pushed` is `true` only when a remote-tracking ref contains the commit, otherwise `"unknown"`, never `false`. It reads local refs only. |

No result contains matched text, `stderr` or the command line, and the server has no free-form command tool.

### What a clean result means

A clean result means **no match for the fixed rule set at the scanned refs. It is not proof that no secret exists.** A secret in a format the rule table does not list, a short or unusual value (the agent text lists the blind spots), a dangling object or a reflog-only commit is not found. Always read `complete` and `truncated` first: a scan with `complete: false` proves nothing. The reviewer treats a scan that did not complete (tool unavailable, error, timeout or `truncated`) as a blocker with the verdict `FAIL`, never `PASS`.

### Requirements

| Requirement | Detail |
|-------------|--------|
| Python package `mcp` | Pinned `mcp==2.2.0` in `implementation/runtime/security/requirements-mcp-server.txt`, the same pin as the memory server. That release declares Python 3.10 or newer on PyPI; the repository itself states no minimum. Without it the client shows a generic "Connection closed" error. |
| `git` 2.40 or newer on `PATH` | The scanner reads attributes from git's empty tree with `--attr-source`; an older git exits non-zero and every call fails closed as `git_failed`. |
| A regex library with `RE_DUP_MAX` of at least 1024 | Used by `git grep -E` and `git log -G`. glibc has 32767. Where it is lower (some musl and BSD builds), every scope except `tracked_names` ends `regex_unsupported` with `complete: false`. |
| Launch from the project root | The configs start the server with `--allowed-root .` and an `implementation.…` module path, both relative to its launch directory. The server accepts only repositories inside that directory. |
| POSIX host | Paths such as `/dev/null` are assumed. Windows is not verified. |

Install the dependency once per project, from the project root; the installer prints this command after a full install or `--update`:

```bash
python3 -m venv .venv-mcp && source .venv-mcp/bin/activate && pip install -r implementation/runtime/security/requirements-mcp-server.txt
```

The configs run plain `python3`, so start your assistant from an environment where that `python3` can import `mcp`. To check the dependency, run `python3 -m implementation.runtime.security.poc_audit_server --help` from the project root: it prints a usage message when `mcp` is importable and a Python `ImportError` otherwise.

Cost: in the worst measured shape the `jwt` rule scales linearly with line length, about 2 microseconds per byte on the measured host (git 2.43.0, glibc). Each call has a 60 second deadline, so one file with a single line of roughly 30 MB or more of that shape (an extrapolation from a 10 MB measurement) can end the scan as `timeout` with `complete: false`. That is an incomplete scan, not a clean one.

### Client-owned permission (Claude Code)

The installer never writes `.claude/settings.json`. For Claude Code, add this to your own `.claude/settings.json` so the two tools are pre-approved:

```json
{
  "permissions": {
    "allow": ["mcp__poc-security-audit__*"]
  }
}
```

`mcp__<server>__*` matches every tool of one server. The PoC security reviewer's tool grant also names `mcp__security-audit__grep_content` from the separate `security-audit` server, so the same form (`mcp__security-audit__*`) applies there. Claude Code applies `permissions.allow` rules from a project's `.claude/settings.json` only after you accept the workspace trust dialog, and it asks for approval before using a project-scoped server from `.mcp.json`, so approve `poc-security-audit` when prompted. Other platforms: grant the platform's equivalent permission if it asks for one; the harness cannot do this for you.

### Platform availability

The entry is generated into `.mcp.json` (Claude Code), `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json` and `.cline/mcp.json`. It is **not** in GitHub Copilot's `.vscode/mcp.json`, because `extended` servers are not emitted to the `github` platform. On Copilot the reviewer's scan has no server to call; see the `FAIL` rule above.

## Per-platform output

| Platform | Output file |
|----------|-------------|
| GitHub Copilot | `.vscode/mcp.json` |
| Gemini CLI | `.gemini/settings.json` |
| Opencode | `.opencode/opencode.json` |
| Cursor | `.cursor/mcp.json` |
| Pi | `.pi/mcp.json` |
| Claude Code | `.mcp.json` (repo root) |
| Cline | `.cline/mcp.json` (staging file — see [Cline Setup](cline-setup)) |

All platform configs are regenerated by `node implementation/scripts/sync.mjs --root implementation`.

## Provenance-aware merge on `--update`

Every platform's generated MCP/settings file is accompanied by a `<mcpfile>.provenance.json`
sidecar recording the exact set of server keys the generator owned at that generation. On
`scripts/install.sh --update`, this sidecar lets the merge (`scripts/merge-mcp-json.py`)
distinguish two cases that used to be indistinguishable:

- A key present only in the installed file that the generator has **never** claimed (e.g. a
  hand-added server, or this repo's own `.vscode/mcp.json` `cwso` block) — always preserved,
  forever, regardless of provenance history.
- A key present only in the installed file that **was** generator-owned at some prior generation
  (per an existing sidecar) and is **no longer** emitted by the current source — pruned
  automatically, since it is safe to assume the registry retired it deliberately.

A key the current source still emits is never pruned, no matter what any sidecar claims — only
genuinely dest-only, previously-owned, now-retired keys are ever removed.

**Bootstrap limitation, stated honestly:** a project with no prior sidecar (every project on its
first `--update` after this mechanism shipped, including this repo's own root before its own
first post-fix update) has no history to diff against, so the automatic mechanism prunes
**nothing** on that first run — behavior is identical to before this mechanism existed. That
run also writes the new sidecar over the (missing) old one, so the retired keys are never
recorded as owned: a later automatic prune cannot remove a key that the first run left
behind. Remove such keys by hand or with `--force-prune-keys` (below). Automatic pruning only
takes effect for keys retired after a sidecar exists.

**One-time bootstrap bridge:** `scripts/merge-mcp-json.py --force-prune-keys <name1,name2,...>`
prunes exactly the named dest-only keys, with no dependency on sidecar history — used only once,
explicitly, by `docs/tasks/task-T382.md` to close the already-decided `e2b`/`redis`/`figma`/
`notion` removal gap for already-installed roots. It is not invoked automatically by `--update`
anywhere in this codebase, and is not a general-purpose "prune whatever" convention — every
invocation names an explicit, already-reviewed list.

## Migrating an existing install from v7.x

v8.0.0 corrects and pins the MCP server entries (audit SEC-002). Four extended entries named npm packages that do not exist (the `@anthropic/mcp-filesystem` name belonged to an unrelated npm account, so a third party could have published under it); every `npx` server is now pinned to an exact version; `docker` and `postgresql` are removed. After upgrading:

1. Run `scripts/install.sh --update` in your project.
2. The `filesystem`, `git`, `github` and `supabase` entries are overwritten in place: `command` and `args` are replaced and the new `env` entry is added. A key you added yourself inside one of those entries (for example an extra `env` variable) is kept; delete it if you no longer want it. Your own server entries with other names are kept.
3. `docker` and `postgresql` are removed automatically only if the installed file's `<file>.provenance.json` sidecar lists them as generator-owned. If the install has no sidecar (v6.9.0 or earlier), or the sidecar no longer lists them, remove both server objects from every installed MCP config by hand, or run once per file and once per name: `python3 scripts/merge-mcp-json.py --source <generated file> --dest <your file> --force-prune-keys docker`, then the same with `postgresql`. Use one name per call: the script refuses, and writes nothing, if any named key is missing from the destination or still present in the source, so the combined `--force-prune-keys docker,postgresql` fails as soon as one of the two is already gone. `install.sh` does not pass this option, so this is a direct call. The files are `.mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.cursor/mcp.json`, `.cline/mcp.json`, `.pi/mcp.json` and `.vscode/mcp.json`. Cline's real configuration is global (see [Cline Setup](cline-setup)): remove the two entries from it directly.
4. If you had your own server entry named `docker` or `postgresql` and the old sidecar lists those names, the update removes it as well, because only the name is compared. Re-add it under another name.
5. Set `GITHUB_PERSONAL_ACCESS_TOKEN` (`github`) and `SUPABASE_ACCESS_TOKEN` (`supabase`) in the environment that starts your assistant, install `uv` if you use `git`, and install Docker if you use `github`. An unset variable stops only that server.
6. The `fetch` server is removed the same way as `docker` and `postgresql` (step 3): automatically when the installed file's `<file>.provenance.json` sidecar lists it, otherwise delete the `fetch` object by hand or run the step 3 command with `--force-prune-keys fetch` (a separate call, not combined with the other names). The `playwright` entry is overwritten with the hardened arguments and needs Chrome for Testing, installed with the pinned command in `implementation/PREREQUISITES.md`; that file also explains how to test a local app (`playwright-local`).
7. Your client may ask you to approve the changed servers again (Claude Code asks before using a project-scoped server from `.mcp.json`). Approve the new entries after checking them.

## Remote-server transport encoding differs per platform

Two servers in this registry use `transport: remote` (`context7`, `hf-mcp-server` — both
hosted, streamable-HTTP MCP endpoints with no local process). Every other server uses
`transport: stdio` and is emitted as a `command`/`args` block, which **is** consistent across
every platform.

Remote servers are **not** encoded identically across platforms. Each platform's own config
schema determines the field name(s) used for the server URL and whether a `type`/transport
discriminator field is required at all, and getting this wrong doesn't always fail loudly — on
some platforms an unrecognized or missing field silently falls back to a different (often
deprecated) transport instead of erroring. Do not assume a shape that is correct for one
platform is portable to another; always verify against the target platform's own current
documentation.

| Platform | Remote-server JSON shape | Notes |
|----------|---------------------------|-------|
| GitHub Copilot (VS Code) | `{ "type": "http", "url": "…" }` | `type` is a **required** field in VS Code's MCP schema for HTTP/SSE servers; a config missing it is invalid. |
| Cursor | `{ "url": "…" }` | No `type` field — Cursor's remote-server schema doesn't use one. |
| Pi | `{ "url": "…" }` | **Closed decision (T385): keep the Cursor-format assumption.** T360's web search left this inconclusive; T385 re-attempted via `context7` (a new angle) and confirmed Pi is [pi.dev](https://pi.dev), a real terminal coding-agent product (`context7` library `/websites/pi_dev`), built on the open-source `@earendil-works/pi-coding-agent` package — whose own docs state it "intentionally does not include built-in MCP... build or install those workflows as extensions or packages" (`https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/usage.md`). MCP support for Pi is therefore provided by third-party extensions rather than a single first-party spec; the `@spences10/pi-mcp` extension (part of the `my-pi` distribution, `context7` library `/spences10/my-pi`) documents `mcp.json` loaded from `~/.pi/agent/mcp.json` using the standard `mcpServers: { name: {...} }` wrapper for stdio servers, but its README provides no JSON example for a remote/HTTP server shape. Since Pi ships no native MCP support, there is no single canonical "Pi" remote-transport shape to confirm against — the actual shape depends on whichever third-party extension a given user installs, which this repo cannot target definitively. Retaining the Cursor-derived `{ "url": ... }` (no `"type"`) shape as the least-risky default; this closes the question rather than leaving it open for a third research pass. |
| Gemini CLI | `{ "httpUrl": "…" }` | **Different key name**, not just a different shape. Gemini reserves the `"url"` key for the legacy SSE transport — using `"url"` for a streamable-HTTP server silently selects the deprecated SSE path instead of failing. |
| Opencode | `{ "type": "remote", "url": "…" }` | Both fields are required. |
| Claude Code | `{ "type": "http", "url": "…" }` | Same shape as VS Code's here, but that's confirmed independently against Claude Code's own docs — it is not assumed or derived from VS Code's. |
| Cline | `{ "type": "streamableHttp", "url": "…" }` | Cline does **not** accept `"http"` as a `type` value. Omitting `type`, or supplying an unrecognized value such as `"http"`, silently falls back to the deprecated `sse` transport rather than failing. An earlier release shipped `"http"` here, which caused a real runtime failure — see the release changelog for the fix. |

All shapes above are generated by `emitMcp()` in `implementation/scripts/sync.mjs` and
regenerated by `make sync` — never hand-edit the platform output files directly.

## Runtime verification checklist

`tests/functional/test_platform_projections.py` proves the generator is internally
consistent and deterministic (exact-shape assertions against `sync.mjs`'s own expected
output) — it does **not** prove a generated config actually loads and works in a
platform's real tooling. The only place that has ever happened is a one-time manual
spot-check for Cline (T365: a real, already-installed
`~/.cline/data/settings/cline_mcp_settings.json` on that host compared byte-identical to
the corrected `implementation/.cline/mcp.json`). The table below extends that same
discipline to all 7 platforms: **automated (schema-backed)** where live research
(2026-08-10) confirmed the platform publishes a genuine, citable JSON Schema for the
exact config file this repo generates, **documented manual check** everywhere else — no
platform is left silently unaddressed.

| Platform | Verification method | Basis |
|----------|---------------------|-------|
| GitHub Copilot (VS Code) | Documented manual check | No officially published, standalone-fetchable JSON Schema found for `.vscode/mcp.json` — see below. |
| Cursor | Documented manual check | Confirmed **not** published — see below. |
| Gemini CLI | **Automated (schema-backed)** | [`schemas/settings.schema.json`](https://raw.githubusercontent.com/google-gemini/gemini-cli/main/schemas/settings.schema.json) in the official `google-gemini/gemini-cli` repo. |
| Opencode | **Automated (schema-backed)** | [`https://opencode.ai/config.json`](https://opencode.ai/config.json), the vendor's own published config schema — already referenced via the `"$schema"` field this repo's generator emits in `implementation/.opencode/opencode.json`. |
| Pi | Documented manual check | No officially published pi.dev schema found — see below. |
| Claude Code | Documented manual check | No officially published schema found for `.mcp.json` — see below. |
| Cline | Documented manual check | Cline validates its settings file internally with Zod, not a published JSON Schema document — see below. |

### Automated (schema-backed)

**Gemini CLI.** The official `google-gemini/gemini-cli` GitHub repository publishes
`schemas/settings.schema.json` (fetched live 2026-08-10:
`https://raw.githubusercontent.com/google-gemini/gemini-cli/main/schemas/settings.schema.json`).
Its `mcpServers` property (`$defs.MCPServerConfig`) explicitly defines the `httpUrl`
field this repo's generator emits for remote (`context7`, `hf-mcp-server`) servers in
`implementation/.gemini/settings.json`, plus `command`/`args`/`env` for stdio servers —
the exact shape `emitMcp()` produces, not an inferred or sibling-platform shape.
`tests/functional/test_mcp_schema_validation.py` validates the live-generated
`implementation/.gemini/settings.json` against this schema.

**Opencode.** The official `opencode.ai/config.json` schema (fetched live 2026-08-10) is
already the schema this repo's own generated `implementation/.opencode/opencode.json`
references via its `"$schema"` field. Its `mcp` property (`$defs.McpLocalConfig` /
`$defs.McpRemoteConfig`) matches this repo's generated shape exactly: local servers as
`{"type": "local", "command": [...]}`, remote servers as `{"type": "remote", "url": "…"}`
— confirmed against the actual fetched schema, not assumed. `tests/functional/
test_mcp_schema_validation.py` validates the live-generated
`implementation/.opencode/opencode.json` against this schema.

### Documented manual check

For every platform without a confirmed, citable schema, this is the literal spot-check to
run — mirroring the Cline (T365) precedent of comparing the generated file against the
platform's real installed config and confirming the server(s) show as connected in the
platform's own UI or CLI status output.

**GitHub Copilot (VS Code).**
1. Copy `implementation/.vscode/mcp.json` into a real VS Code workspace's
   `.vscode/mcp.json` (or reload the window if it's already there).
2. Open the Command Palette → `MCP: List Servers`. Select a server (e.g. `context7`) to
   inspect its status; a failure surfaces a "Show Output" option that opens the server
   log.
3. Alternatively, check the MCP status indicator in the bottom status bar, or the **MCP
   SERVERS - INSTALLED** section of the Extensions view (`Ctrl+Shift+X`) for a
   running/stopped/error state per server.

No official, standalone-fetchable JSON Schema document for `.vscode/mcp.json` was found
during live research (VS Code registers schema validation internally via its own
`jsonValidation` extension contribution point for editor IntelliSense, not as a publicly
citable schema URL; see e.g. `microsoft/vscode` issue #252907, "User mcp.json should
follow standard mcp.json schema") — manual check is the correct outcome, not an
oversight.

**Cursor.**
1. Copy `implementation/.cursor/mcp.json` into a real Cursor workspace's
   `.cursor/mcp.json`.
2. Open **Cursor Settings → MCP** tab. Each configured server shows a status dot: green
   means connected (MCP handshake completed) with a discovered-tool count; red means
   disconnected/error, with an expandable error message.

Cursor explicitly does **not** publish a schema document for `mcp.json` to a webserver
(confirmed via a Cursor Community Forum bug report: "Two flaws with mcp.json" —
`$schema` validation does not work in Cursor's `mcp.json` for this reason) — manual check
is the correct, sourced outcome.

**Pi.**
1. Copy `implementation/.pi/mcp.json` into Pi's real config location. No single,
   officially pi.dev-documented canonical path was confirmed during this research (this
   file's own "Remote-server transport encoding" table above already flags Pi as lacking
   an independently confirmed official doc source, and that status is not resolved by
   this checklist); community-sourced setup guides describe `~/.pi/agent/mcp.json` as the
   per-agent global path — treat this as unverified-but-best-available, not as a
   confirmed official location.
2. Run `/mcp status` (or the interactive `/mcp` panel) from within Pi to confirm each
   server shows as connected, and `/mcp tools [name]` to confirm its tools are
   discoverable.

**Claude Code.**
1. Compare `implementation/.mcp.json` (repo root) directly against a real project's
   `.mcp.json` — Claude Code reads project-scoped MCP servers straight from that file, so
   no copy step is even required if this repo itself is opened in Claude Code.
2. Run `claude mcp list` from a terminal in the project root. Each server appears with a
   `✔ Connected` status (or a failure status plus the underlying error/status code).

No official, standalone-published JSON Schema for `.mcp.json` was found during live
research — manual check is the correct outcome.

**Cline.**
1. Cline's MCP configuration is global, not per-project (see [Cline Setup](cline-setup) §
   "MCP server setup"): merge `implementation/.cline/mcp.json`'s entries into the real
   global config. The standalone CLI reads `~/.cline/mcp.json`; the IDE extension reads
   its own per-OS global storage path (e.g. on Linux,
   `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`,
   or `~/.cline/data/settings/cline_mcp_settings.json` for a standalone CLI install on
   this host, as used in T365's original spot-check).
2. Confirm, via the IDE's MCP Servers icon → Configure panel or the CLI's own
   server-status output, that each merged server shows as connected/available.

Cline validates this file internally against a Zod schema, not a published JSON Schema
document, so no automated `jsonschema`-library check applies here — this reconfirms,
rather than repeats, T365's original one-time manual precedent.
