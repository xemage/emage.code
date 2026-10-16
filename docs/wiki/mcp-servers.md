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
| `gitlab` | Repository, issues, MRs, pipelines | Whole server: Orchestrator, DevOps, Release Manager, PoC Orchestrator, PoC DevOps. Named tools only: Scrum Master, QA Engineer |
| `playwright` | Browser automation, E2E testing | Named tools only: QA, Frontend, Demo Agent, PoC QA |
| `memory` | Persistent knowledge graph | Orchestrator, PoC Orchestrator (team memory) |
| `sequential-thinking` | Complex problem decomposition | Solution Architect, Orchestrator, PoC Orchestrator |
| `brave` | Technology discovery (web search) | No agent lists its tools (Technology Scout and Feasibility hold no token); available to the session |
| `context7` | Framework / API documentation lookup | No agent lists its tools (Technology Scout and Integration hold no token); available to the session |
| `hindsight` | Remote MCP endpoint; its URL is read from `HINDSIGHT_MCP_URL` | No agent lists its tools; available to the session |

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

**Local apps are blocked.** The same list denies `localhost`, `127.*`, `*.localhost`, `10.*`, `192.168.*` and `172.16` to `172.31`, which are the addresses of a local dev server. With the shipped entry the first request to a local app fails with `net::ERR_BLOCKED_BY_CLIENT`, so **the shipped `playwright` entry cannot be used for E2E testing of a local app**. Do not edit its arguments: they are generator-owned and `install.sh --update` restores them. To test a local app, add a second, user-owned entry named `playwright-local` that has the same arguments without `--blocked-origins` (the JSON is in `implementation/PREREQUISITES.md`, section "Local apps are blocked by the shipped entry"). It has no origin restriction at all, so a page it opens can reach every address your host reaches, including internal services and cloud metadata endpoints; use it only on a development machine, for your own pages, and remove it afterwards. `scripts/merge-mcp-json.py` keeps keys that exist only in your file and prunes a name only if the old provenance sidecar lists it as generator-owned or you pass it to `--force-prune-keys`, so `playwright-local` survives `install.sh --update` (a test pins this). The generated agent tool lines name the `playwright` server's tools, not `playwright-local`'s, so on Claude Code, GitHub Copilot/VS Code and Pi (for an agent that lists an `mcp__` tool) subagents do not receive the second server's tools; on Opencode, Gemini CLI and Cursor an agent's tool list does not restrict MCP tools, so any agent can call them. The server-level denial of six tools ([below](#server-level-denial-of-six-playwright-tools)) covers the `playwright` server only: `playwright-local` is another server name and is not denied, on any platform. The entry has no origin restriction and includes `browser_run_code_unsafe`: use it from your own session on a development machine, and remove it when you are done.

**Limits. This is not a security boundary.** The origin flags block a direct navigation or sub-request to a listed origin. They do not cover redirects (an allowed page that answers `302` to a blocked address still reaches it, and the page content is returned to the model), WebSockets, a DNS name that resolves to an internal address, or the `browser_run_code_unsafe` tool, which runs code on the host. The flags only narrow what the entry reaches; the Playwright `--help` text says the same. Four agents (`qa-engineer`, `frontend-developer`, `poc-qa-engineer`, `demo-agent`) hold named Playwright tools only (T657, SEC-T655-01): none holds the whole server or `browser_run_code_unsafe`, `browser_evaluate` or `browser_file_upload`. Where that narrowing is in force depends on the platform; see [MCP tool names per platform](#mcp-tool-names-per-platform). On the platforms where it is not in force (Opencode, Gemini CLI, Cursor, and Pi for agents that list no `mcp__` tool) an agent's tool list does not restrict MCP tools: every agent, not only these four, can call every tool of every configured MCP server that is not denied server-wide or, on Opencode since T663, per agent ([Per-agent denial](#per-agent-denial-on-opencode-t663-sec-t658-01): the six tools for every agent and `<server>_*` for every non-exempt server an agent holds no token of), including the GitLab write tools elsewhere. Since T658 (SEC-T657-01) the generator denies six tools of the shipped `playwright` server on Opencode and Gemini CLI ([Server-level denial](#server-level-denial-of-six-playwright-tools)); on Cursor, and on Pi for an agent with no `mcp__` entry, `browser_run_code_unsafe`, `browser_evaluate` and `browser_file_upload` stay callable by every agent. The Copilot and Pi rows rest on vendor documentation and source, not on a live run. On GitHub Copilot/VS Code the agents' MCP grants (`gitlab`, `memory`, `sequential-thinking`, `playwright`) take effect for the first time in this release; before, the tokens were ignored. Granted tools such as `browser_snapshot`, `browser_take_screenshot`, `browser_console_messages`, `browser_network_requests` and `browser_find` can write to a workspace-relative `filename` and send page URLs and console output to the model provider: use synthetic data and test accounts only. Pages the agent opens can contain prompt-injection text, and nothing here filters it. Evidence: `docs/artifacts/fetch-replacement-evaluation-v1.md`.

## Server-level denial of six Playwright tools

Opencode, Gemini CLI and Cursor do not restrict MCP tools by an agent's tool list, so the narrowed grants above are not enforced there. For Opencode and Gemini CLI the vendors document a server-level denial, and the generator emits it (T658, SEC-T657-01) for exactly these six tools of the `playwright` server: `browser_run_code_unsafe`, `browser_evaluate`, `browser_file_upload`, `browser_drag`, `browser_drop` and `browser_network_request` (the singular; the granted `browser_network_requests` is not denied). The one list is `denyTools` on the `playwright` entry of `implementation/knowledge/mcp/servers.yaml`; the projections are generated.

| Platform | Emitted form | File |
|---|---|---|
| Opencode | top-level `permission` entries `"playwright_browser_evaluate": "deny"` and the five others (`playwright_<tool>`) | `.opencode/opencode.json` |
| Gemini CLI | `"excludeTools": ["browser_run_code_unsafe", ...]` on `mcpServers.playwright` (the tool names as the server reports them) | `.gemini/settings.json` |
| Cursor | none: no per-server denial is documented | none, so every agent can call every tool |
| Claude Code, GitHub Copilot / VS Code, Pi, Cline | none needed or none available; see the table below | none |

- **Status: documented and read from vendor source, not observed in a live run.** Sources, the exact lines read, and what is unverified: `docs/artifacts/mcp-server-denials-v1.md`.
- **Opencode: the last matching rule wins, and an agent's own rules come after the global ones.** The generated agent files grant only named Playwright tools (19 of the 25 default tools exist outside the denial list; the four agents hold between 12 and 18 of them) and never one of the six, so the denial holds for every shipped agent (a test models the order). An agent file of your own that allows one of these names, `playwright_*` or `*` is later in the order and overrides the denial. The per-agent `false` entries described below (T663) are written into every generated agent file and survive a broader allow of the global config; they do not survive an allow written later in your own agent file or another config source. Opencode's `--auto` mode still enforces an explicit `deny`.
- **Gemini CLI:** `excludeTools` takes precedence over `includeTools`. The filter runs when tools are discovered, so subagents never receive an excluded tool (read from source; the documentation does not mention subagents). `mcpServers` merges per server name, so a same-named `playwright` entry in a higher-precedence settings scope replaces the generated entry and its list. A same-named `playwright` entry in a settings source that Gemini ranks above the project file (the system settings file) replaces the generated entry and its list; project settings load only in a trusted workspace (unverified).
- **`playwright-local` is not covered.** A user-owned entry named `playwright-local` is another server name (`playwright-local_browser_evaluate` on Opencode, a different entry on Gemini CLI). It is not denied and it still holds `browser_run_code_unsafe`.
- **Install merge:** `install.sh --update` runs `scripts/merge-mcp-json.py`, with or without the provenance sidecar. For `excludeTools` it unions your list with the generated one (your elements first, nothing of yours is dropped). For Opencode it keeps your own `permission` rules (a string such as `"allow"` becomes `{"*": "allow"}`), sets the six generated keys to `deny` and puts them last, so your earlier wildcard cannot win in the same file. The six names are generator-owned: an edit that re-allows one is undone by the next update. To use one of these tools, add a server entry of your own under another name. An element the generator stops shipping later stays in your file until you remove it. On Opencode the guarantee that the denial comes last holds inside one file: Opencode merges several config sources, and a `playwright_*: allow` in another source can still follow it.
- **Still open:** on Gemini CLI and Cursor every other tool of every configured server (for example the GitLab write tools) stays callable by every agent. On Opencode the per-agent denial below closes every non-exempt server for every generated agent that does not hold it; what stays open there is the exempt read/search servers, the built-in agents and agent files of your own (below).

### Per-agent denial on Opencode (T663, SEC-T658-01, SEC-T663-01)

The generator writes `false` entries into the `tools:` map of **every** Opencode agent file (`.opencode/agents/*.md`). Opencode applies the last matching rule, so a deny written after an allow survives a broader allow before it, and a wildcard deny written before named allows leaves exactly those allows:

- `playwright_<tool>: false` for the six tools above, for every agent, last in the file (the `denyTools` list; it also stays in the server-level denial).
- `<server>_*: false` for every non-exempt server an agent holds no token of, after the agent's allows. The flag is `denyUnlessGranted`, declared on **every** entry of `servers.yaml` (the 17 servers the Opencode manifest carries): `true` for gitlab, playwright, memory, sequential-thinking, security-audit, poc-security-audit, context-retriever, filesystem, github, git and supabase; `denyUnlessGranted: false`, an explicit exemption, for brave, context7, hindsight, cwso, hf-mcp-server and toolradar (user decision of 2026-10-16, "Exempt the read/search servers": generated agents, including a primary orchestrator, keep search, documentation and memory-layer access). It is a wildcard on purpose: a list of write tools would miss the tools a pin bump adds and the mixed-access tools (`execute_graphql`, `gitlab_api_request`). For `gitlab` that is 21 of the 28 agents (for example tech-lead), which therefore also lose the GitLab read tools; the five whole-server holders (orchestrator, poc-orchestrator, devops-engineer, poc-devops-engineer, release-manager) get no GitLab deny.
- **Named-subset rule:** an agent that holds only named tools of a server gets that server's `<server>_*: false` as one of the FIRST entries of its map, and its named `<server>_<tool>: true` entries follow it. The named tools are then the only tools of that server it can call. This applies to qa-engineer and scrum-master (`gitlab`), to the four Playwright agents (`playwright`), to security-engineer and poc-security-engineer (`security-audit`, `poc-security-audit`) and to context-retriever. Here the order of the entries, not a distinct name, makes the pair work: do not reorder the file (the installer restores it on update).
- **Servers that no agent holds and that are not exempt** (`filesystem`, `github`, `git`, `supabase`) are denied in every generated agent file, including the orchestrators that can be selected as the primary agent. On Claude Code a subagent without the token cannot call them either, but the main session is not a subagent and keeps them; on Opencode use a built-in agent or an agent file of your own to reach them. The exempt servers (`brave`, `context7`, `hindsight`, `cwso`, `hf-mcp-server`, `toolradar`) get no entry at all.
- A name is never both allowed and denied in one file: the generator stops if an agent would grant a denied tool, and a test pins it for all agent files. An agent file is a map, so the same name cannot appear twice.
- **Override behaviour (SEC-T657-04):** the `true` entries an agent holds come after your global config and win, so your own global `ask` or `deny` on a tool an agent holds is silently overridden for that agent. Example: a global `ask` on `gitlab_merge_merge_request` is overridden for the five whole-server GitLab holders. No supported way through the generated files or through your project or global configuration keeps a prompt there (an `agent.<name>.permission` entry in your project config is placed before the agent's own rules and loses too); only a source loaded after the agent files can, the environment variable `OPENCODE_CONFIG_CONTENT` (observed on opencode-ai 1.19.2) and, by source reading only, the managed configuration. A tool the agent does not hold keeps your rule unless a generated deny covers it.
- **Over-match:** the wildcards also match a user-owned server whose cleaned name starts with the prefix and an underscore (`gitlab_ee` is matched by `gitlab_*`; `gitlab-ee` is not). For an agent without the server that fails closed.
- **Saved "always" approvals** do not undo a deny: the legacy runtime hides a tool whose last matching rule is a deny, and the current core tests `denied()` before it adds saved approvals (source reading; an approval saved before the deny existed is unverified).
- **Built-in agents get no per-agent deny:** Opencode's built-in agents (build, plan, general, explore, ...) and agent files of your own are not generated by this repository. Only the server-level `permission` of `.opencode/opencode.json` (the six Playwright tools) applies to them; every other tool of every configured server, the GitLab write tools included, stays callable there. That gap is a decision of the user (2026-10-16, option "No, document the gap only") and is tracked.
- **Install:** `install.sh --update` replaces `.opencode/agents/` as a tree; it does not merge agent files. An edit of a generated agent file, and an own agent file placed in that folder, do not survive an update. The MCP config file is still merged as described above.
- **Status: documented, read from vendor source and observed in the resolved rule lists of `opencode-ai@1.19.2` (`opencode debug agent`, raw output stored); a refused tool call has not been observed.** A user-owned agent file, another config source, a plugin or a managed policy that allows these names later still wins. Evidence and sources: `docs/artifacts/mcp-agent-denials-v1.md`, `docs/artifacts/mcp-agent-denials-evidence-v1.md`. Planned: moving the entries from the deprecated `tools:` map to a `permission:` block (tracked debt).

## MCP tool names per platform

Agent sources write an MCP tool as `mcp__<server>__<tool>` and a whole server as `mcp__<server>`. `sync.mjs` renders that into the form each platform documents, through the manifest key `frontmatter.agents.mcpToolNames`. A platform whose naming is unverified keeps the source form. Evidence and sources: `docs/artifacts/mcp-tool-name-mapping-v1.md`.

| Platform | Agent tool line | Narrowed Playwright grant in force |
|---|---|---|
| Claude Code | `mcp__playwright__browser_click`, `mcp__gitlab` (unchanged) | Yes |
| GitHub Copilot / VS Code | `playwright/browser_click`, `gitlab/*` | Yes. Before T657 the old tokens were ignored on this platform |
| Pi | `mcp__playwright__browser_click`, `mcp__gitlab__*`; hyphens in server names become `_` | Yes when the agent file is passed to `pi --tools` (the example subagent extension does); other extensions unverified |
| Opencode | `playwright_browser_click: true`, `gitlab_*: true`; `<server>_*: false` for every non-exempt server an agent holds no token of and the six unsafe tools as `false` (per-agent, T663) | No: the `tools` map is not an allowlist, unlisted tools keep their default. The six unsafe tools are denied server-wide and per agent, and every non-exempt server an agent holds no token of is denied for that agent (above) |
| Gemini CLI | none: the generator drops the tools line | No: subagents inherit every tool of the session. The six unsafe tools are excluded on the server entry (above) |
| Cursor | unchanged; Cursor documents no per-subagent tool list | No |
| Cline | no agent files | n/a |

**GitLab grants.** Five agents (orchestrator, devops-engineer, release-manager, poc-orchestrator, poc-devops-engineer) hold the whole `gitlab` server, which at `@zereight/mcp-gitlab@2.2.5` registers 275 tools (the raw `gitlab_api_request` tool among them is opt-in through `GITLAB_TOOLSETS=api` only), including merge, push, delete and branch/tag/release creation. scrum-master (24 tools: issues, notes, labels, milestones, read-only merge request lookups) and qa-engineer (20 tools: bug issues and notes, read-only merge request, pipeline and job lookups) hold named tools only, none of which merges, pushes, writes files, deletes, creates branches, tags or releases, triggers pipelines or sends a raw API request (T660, SEC-T657-02). This narrows the agent's MCP tool list; it is not a credential boundary: an agent with shell access (qa-engineer holds `execute`) can use `GITLAB_PERSONAL_ACCESS_TOKEN` if it is exported in the environment that starts the assistant. Use a least-privilege token. By default the server exposes only its `core` toolset until `discover_tools` activates the others (`milestones`, `labels`, `pipelines`, `issues`, `merge_requests`); `discover_tools` cannot widen the two roles' allowlist on a platform that enforces one, but it changes the visible toolset for the whole session. Both lists include `discover_tools`, which the server needs to expose the non-default toolsets (`milestones`, `labels`, `pipelines`, `issues`). This holds on Claude Code and, according to the vendor documentation (not observed in a live run), on GitHub Copilot/VS Code; on Gemini CLI and Cursor the agent tool list does not restrict MCP tools, so every agent can still call every GitLab tool there. On Opencode the generator writes per-agent `<server>_*: false` entries for every non-exempt server an agent holds no token of, so the 21 agents without a GitLab tool cannot call one, and qa-engineer and scrum-master (`gitlab_*: false` before their named allows) can call only their named GitLab tools there (per-agent, T663; documented and read from vendor source, not observed in a live tool call; `docs/artifacts/mcp-agent-denials-v1.md`).

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

Four servers in this registry use `transport: remote` (`context7`, `hindsight`, `cwso`,
`hf-mcp-server`; the URL of `hindsight` and `cwso` comes from an environment variable) — all
streamable-HTTP MCP endpoints with no local process. Every other server uses
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
| Pi | `{ "url": "…" }` | **Closed decision (T385): keep the Cursor-format assumption.** T360's web search left this inconclusive; T385 re-attempted via `context7` (a new angle) and confirmed Pi is [pi.dev](https://pi.dev), a real terminal coding-agent product (`context7` library `/websites/pi_dev`), built on the open-source `@earendil-works/pi-coding-agent` package — whose own docs state it "intentionally does not include built-in MCP... build or install those workflows as extensions or packages" (`https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/usage.md`). MCP support for Pi is therefore provided by third-party extensions rather than a single first-party spec; the `@spences10/pi-mcp` extension (part of the `my-pi` distribution, `context7` library `/spences10/my-pi`) documents `mcp.json` loaded from `~/.pi/agent/mcp.json` using the standard `mcpServers: { name: {...} }` wrapper for stdio servers, but its README provides no JSON example for a remote/HTTP server shape. Pi is documented (current main branch, `docs/mcp.md`) to have native MCP support (`pi mcp add`, `.pi/mcp.json`), but an older Pi may not, and its remote-transport shape is not confirmed by this repository; so there is no single canonical "Pi" remote-transport shape to confirm against — the actual shape depends on whichever third-party extension a given user installs, which this repo cannot target definitively. Retaining the Cursor-derived `{ "url": ... }` (no `"type"`) shape as the least-risky default; this closes the question rather than leaving it open for a third research pass. |
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
