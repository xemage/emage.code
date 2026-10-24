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
| `extended` | Emitted only to platforms that opt in via their manifest (`gemini`, `opencode`, `pi`, `claude-code`, `cline`). `github` opts in to no `extended` server as a whole; it carries `security-audit` and `poc-security-audit` only, through `extraPlatforms: [github]` on those two entries (T690) |

## Core servers (always available)

| Server | Purpose | Used by |
|--------|---------|---------|
| `gitlab` | Repository, issues, MRs, pipelines | Named tools only (no agent holds the whole server): Orchestrator, PoC Orchestrator, Scrum Master, QA Engineer, DevOps, Release Manager, PoC DevOps |
| `playwright` | Browser automation, E2E testing | Named tools only: QA, Frontend, Demo Agent, PoC QA |
| `memory` | Persistent knowledge graph | Orchestrator, PoC Orchestrator (team memory) |
| `sequential-thinking` | Complex problem decomposition | Solution Architect, Orchestrator, PoC Orchestrator |
| `brave` | Technology discovery (web search) | No agent lists its tools (Technology Scout and Feasibility hold no token); available to the session |
| `context7` | Framework / API documentation lookup | No agent lists its tools (Technology Scout and Integration hold no token); available to the session |
| `hindsight` | Remote MCP endpoint; its URL is read from `HINDSIGHT_MCP_URL` | No agent lists its tools; available to the session |

The `fetch` server was removed in v8.0.0 (audit SEC-T646-01). Agents read web pages with the platform `web` tool; no agent is granted a fetch tool any more, and no agent was given Playwright in its place. See [Migrating an existing install](#migrating-an-existing-install-from-v7x).

## Extended servers (opt-in)

`cwso`, `hf-mcp-server`, `context-retriever`, `security-audit`, `poc-security-audit`, `filesystem`, `git`, `supabase`, `toolradar`.

The `docker` and `postgresql` servers were removed in v8.0.0 (audit SEC-002); see [Migrating an existing install](#migrating-an-existing-install-from-v7x). The `github` server (the GitHub MCP container) was removed in v9.0.0 (user decision 2026-10-22): `install.sh --update` prunes the generated entry through the provenance sidecar; if you used it, copy the entry from your old config under your own server name (for example `github-mine`) before updating.

Most require additional credentials — see [`servers.yaml`](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/knowledge/mcp/servers.yaml) for the full env-var contract. The two Python servers `security-audit` and `poc-security-audit` need no credentials; `poc-security-audit` is described [below](#poc-security-scan-server-poc-security-audit).

## Required environment variables

| Variable | Server | Notes |
|----------|--------|-------|
| `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` | `gitlab` | Recommended (T665). A **path** to a mode 0600 file that holds the token; not a secret. See [GitLab token](#gitlab-token) |
| `GITLAB_PERSONAL_ACCESS_TOKEN` | `gitlab` | The token itself (environment mode, still supported). Scope `api`, limited by role, expiry at most 90 days: see [GitLab token](#gitlab-token). A non-empty value wins over the file |
| `GITLAB_API_URL` | `gitlab` | Not a secret |
| `BRAVE_API_KEY` | `brave` | Free tier: 2000 queries/month |
| `HINDSIGHT_MCP_URL` | `hindsight` | URL of the remote endpoint |
| `CWSO_MCP_URL` | `cwso` (extended) | URL of the remote endpoint |
| `CWSO_BEARER_TOKEN` | `cwso` (extended) | Sent as `Authorization: Bearer <value>` |
| `CWSO_ORIGIN` | `cwso` (extended) | Sent as the `Origin` header |
| `TOOLRADAR_API_KEY` | `toolradar` (extended) | API key |
| `SUPABASE_ACCESS_TOKEN` | `supabase` (extended) | Supabase personal access token, recorded as account-wide by the T638 security review (L-4). Read from the environment, never from argv. The server starts with `--read-only`, which limits the tools, not the token. Project scoping and the hosted OAuth alternative: [Package pins](#package-pins-and-runtime-requirements-of-the-extended-servers) |

The placeholder form differs per platform (verification status: [Placeholder forms](#placeholder-forms)). Claude Code's `.mcp.json` references these as `${VAR}`, and as `${VAR:-}` for the two GitLab token variables (an optional empty default, T665); Gemini CLI uses `${VAR}`; Pi uses `${VAR}` and leaves the two optional GitLab token variables out of the entry (T680); GitHub Copilot / VS Code and Cline use `${env:VAR}`; Opencode uses `{env:VAR}`. Claude Code reports an unset variable in `claude mcp list` and uses the literal `${VAR}` text. Export the variables for the servers you use in the environment that starts your assistant.

> **Never commit these.** Use environment variables or a secret vault. See [`SECURITY.md`](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/SECURITY.md) for the full rules.

## GitLab token

The `gitlab` server needs one credential. The scope and role table, the token types in order of preference, the file-mode steps, the per-client posture with its verified and unverified labels, the stated residual, the migration from v8.0.0 and the three live checks that you must run are in **one place**: [`implementation/PREREQUISITES.md`, "GitLab token"](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/PREREQUISITES.md#gitlab-token). This page does not repeat the table, so the two cannot disagree. Design and evidence: `docs/artifacts/gitlab-token-handling-design-v1.md` (SEC-T660-01, decisions of 2026-10-16).

In short:

- **Scope `api`, limited by role.** The roles that write issues and notes (`qa-engineer`, `scrum-master`) cannot work with `read_api`, and `write_repository` does not authenticate against the REST API; do not add scopes. Limit the power with the **role**: Planner or Reporter where enough, Developer at most, never Maintainer or Owner; expiry at most 90 days. Use a dedicated credential, never your own `glab` or git token.
- **One token, and a Developer-level one if you use the merge-request roles.** `orchestrator`, `poc-orchestrator` and `release-manager` hold `create_merge_request`, which needs Developer. A Developer-level `api` token can push to unprotected branches, create tags and start pipelines that run code on your runners, whatever the agents' tool lists say; a token per role is not offered (decision of 2026-10-22). If you want a lower-privilege token, the **Reporter profile** (a Planner or Reporter token; those three roles are meant to hand merge requests to the top-level session, and `create_merge_request` is expected to fail with an authorization error; unverified, not run, and the agent files are unchanged for this profile) is a supported mode; that token is not read-only (it still reads the project and writes issues and notes), and the role holds per project, so use a project or group access token or a dedicated user. The exposure wording, what keeps working and the unverified points: [`implementation/PREREQUISITES.md`, "Reporter profile"](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/PREREQUISITES.md#reporter-profile).
- **File mode** (`GITLAB_PERSONAL_ACCESS_TOKEN_FILE`) keeps the token out of the process environment; the exported variable stays supported. Remove the old export when you adopt it, because a non-empty variable wins over the file.
- **The fine-grained personal access token is not recommended first yet.** It is unverified until the user has run the live check; today the order is project or group access token, then the `api` token of a dedicated low-role user.
- **Server-side limit.** The generated entry sets `GITLAB_PERMISSION_MODE=modify`: the server refuses every delete and teardown tool on every client (the teardown list is from the README on main, not matched to 2.2.5, unverified), including your own session. It does not stop a shell that holds the token from calling the API. The server reads four more operator controls that the entry does not set (`GITLAB_DENIED_TOOLS_REGEX`, `GITLAB_ALLOWED_PROJECT_IDS`, `GITLAB_TOOLS`, `GITLAB_TOOLSETS`); what each does, its limits and the unverified points are in [`implementation/PREREQUISITES.md`, "Server-side limits"](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/PREREQUISITES.md#server-side-limits).
- **The residual stays open** and was re-accepted by the user on 2026-10-16: an agent that runs as your OS user can read the token file or the `glab` credentials. Mitigated, not closed.
- **`scripts/check-gitlab-token.py`** (standard library only, read-only, never prints the token) checks scope, expiry and owner of the token that the server uses.

### Placeholder forms

What each client does with the placeholder the generator writes, as read on 2026-10-16 (documentation and vendor source on the vendors' main branches, not matched to installed releases; **none observed in a live run**):

| Client | Generated | Documented form | Finding | Status |
|--------|-----------|-----------------|---------|--------|
| Claude Code | `${VAR}`, `${VAR:-}` for the GitLab token variables | `${VAR}` and `${VAR:-default}` | An unset `${VAR}` stays as literal text, hence the empty default | documented; the empty default is unverified |
| Gemini CLI | `${VAR}` since T665 | `$VAR`, `${VAR}`, `${VAR:-DEFAULT}` | `${env:VAR}` (the earlier form) is not documented; the resolver looks it up as a variable named `env:VAR` and the server started with an empty value. **Fixed** | documented; source read, not run |
| GitHub Copilot / VS Code | `${env:VAR}` | `${env:NAME}` through the variables reference that the MCP page points to | Unchanged. An unset variable's behaviour is not stated | documented (indirect); unset unverified |
| Opencode | `{env:VAR}` | `{env:VAR}` | Unchanged; unset is an empty string | documented |
| Pi | `${VAR}` since T680; optional `env` variables left out; `hindsight` and `cwso` not generated | `${VAR}` | **Observed** (T680) on four releases (0.99.0, 1.0.0, 1.3.0, 1.4.0); `${env:VAR}` (the earlier form) stayed literal text and an unset or empty variable fails the server. **Fixed**: `${VAR}` plus the new `optional: true` key in `servers.yaml`. See the verified-forms table below | observed (`pi mcp list`); project-level `.pi/mcp.json` not tested; in-session path and other releases unverified |
| Cline | `${env:VAR}` | not shown on the vendor page | The VS Code extension expands `${env:VAR}` (source) and leaves an unset one as literal text; the CLI/SDK loader was not shown to expand | source read; CLI unverified |

#### Pi: verified forms

Run on 2026-10-22 (T680) with `@earendil-works/pi-coding-agent` 1.4.0, and the same checks on 0.99.0, 1.0.0 and 1.3.0 (four releases, not a range), in a scratch directory outside the repository: `pi mcp list --json` with `PI_CODING_AGENT_DIR` pointing at a scratch `mcp.json` and a fake stdio MCP server that wrote the environment it received to a file (a fake HTTP listener for the `url` and header cases). Pi ran under `env -i` with only `PATH`, a scratch `HOME`, the agent directory and the test variables, so no ambient secret reached a recorded file; no real credential was used, and the runs needed no network beyond the package installation (Pi's own start-up calls were not checked). The recorded output files and the scratch merge files were deleted afterwards; the command lines of the experiment (`run.sh`, the fake server and the test configs) are in the T680 session scratchpad at `/tmp/claude-1000/-home-emage-Code-emage-emage-code/00f8372f-6371-46d2-9fa7-bac00c806f40/scratchpad/pi-run` (outside the repository, no values in them). **Observed** means seen in that output; Pi's behaviour for a project-level `.pi/mcp.json` (trust prompt), inside an interactive session (same `createDefaultTransport` code, read, not run) and on other releases is **unverified**. The first Pi that this repository targets is the built-in MCP support (`docs/mcp.md` of the package); `pi-mcp-adapter` 5.4.0 is a third-party extension that this repository does not target specifically (its source has special handling for a Pi with its own MCP config, read, not run); only its `interpolateEnvVars` function was executed, alone, so its column is a function result, not a run of the extension.

| Form in `env` / `headers` | Pi 0.99.0, 1.0.0, 1.3.0, 1.4.0 (`pi mcp list`) | `pi-mcp-adapter` 5.4.0 (function only) |
|---------------------------|------------------------------------|----------------------------------------|
| `${VAR}` | expanded (observed) | expanded |
| `$VAR` | expanded (observed) | **not** expanded |
| `${env:VAR}` | literal text, the server starts with the text `${env:VAR}` (observed) | becomes `$` followed by the value |
| `${VAR:-}` | literal text (observed) | literal text |
| `Bearer ${VAR}` (text around it) | expanded (observed, headers; env) | expanded |
| `VAR` unset or set but empty | the server is **not started**: `Failed to resolve MCP server "x" env "VAR" from environment variable: VAR`; `pi mcp list` exits 1 (observed, `env` and `headers`) | replaced by an empty string |
| `url` containing any placeholder | never expanded; a templated `url` is rejected as `url must be an http or https URL`, the other servers still connect (observed) | not run |
| entry for a variable omitted | the server starts, and a stdio server still receives the variable when it is set in Pi's environment (observed) | not run |

What the generator does with this: it renders `${VAR}` for every server on Pi, and omits an `env` variable marked `optional: true` (the two GitLab token variables; `optional` is refused on `headers` and `url`, because Pi does not pass a header through from its environment), so the file-mode and the environment-mode token both work with the same generated entry and neither has to be exported empty. Everything else is required: an unset `BRAVE_API_KEY`, `GITLAB_API_URL`, `GITHUB_PERSONAL_ACCESS_TOKEN`, `SUPABASE_ACCESS_TOKEN` or `TOOLRADAR_API_KEY` stops that one server on Pi (fail closed, with a named variable in `pi mcp list`) instead of passing a literal `${env:...}` text as the credential, as the earlier form did. `hindsight` and `cwso` use a templated `url`, which Pi 1.x does not expand: Pi rejects such an entry (observed: `pi mcp list` exits 1 although the other servers connect, on 1.4.0), so `servers.yaml` marks both `skipFormats: [pi]` and they are not generated for Pi. `install.sh --update` prunes the entries an older release generated and prints "pruned the retired generator server". To use either on Pi, add an entry of your own with a literal URL under a name of your choice.

## Playwright server (`playwright`)

The `playwright` entry (`@playwright/mcp@0.0.83`) is a `core` server for browser automation and E2E testing. It is launched with `--headless --isolated --browser chromium --sandbox --block-service-workers --no-webmcp` and a `--blocked-origins` list that names loopback, link-local, private and carrier-grade-NAT address ranges, `localhost` forms, IPv6 loopback and mapped forms, and user-information URLs. The list is one argument made of semicolon-separated glob patterns (`*` is a wildcard and `{a,b}` is brace alternation, so `172.{16,...,31}.*` covers 172.16 to 172.31). Do not split it, quote it again or expand it. In the T654 and T655 tests the entry was started by a driver that spawned the server directly, without a shell, on Linux; clients that route `args` through a shell, and Windows, are unverified, and a shell would treat the `;` and `*` in this value specially.

It needs a browser that is not installed by `npx`: see [`implementation/PREREQUISITES.md`](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/PREREQUISITES.md). Output files (snapshots, downloads from visited pages) are written to `.playwright-mcp/` in the launch directory. This repository's `.gitignore` excludes it, but `install.sh` does not edit the `.gitignore` of a project that installs emage.code: add `.playwright-mcp/` to that project's `.gitignore`, or point `--output-dir` at an ignored path in a user-owned entry, so page content is not committed by accident.

**Local apps are blocked.** The same list denies `localhost`, `127.*`, `*.localhost`, `10.*`, `192.168.*` and `172.16` to `172.31`, which are the addresses of a local dev server. With the shipped entry the first request to a local app fails with `net::ERR_BLOCKED_BY_CLIENT`, so **the shipped `playwright` entry cannot be used for E2E testing of a local app**. Do not edit its arguments: they are generator-owned and `install.sh --update` restores them. To test a local app, add a second, user-owned entry named `playwright-local` that has the same arguments without `--blocked-origins` (the JSON is in `implementation/PREREQUISITES.md`, section "Local apps are blocked by the shipped entry"). It has no origin restriction at all, so a page it opens can reach every address your host reaches, including internal services and cloud metadata endpoints; use it only on a development machine, for your own pages, and remove it afterwards. `scripts/merge-mcp-json.py` keeps keys that exist only in your file and prunes a name only if the old provenance sidecar lists it as generator-owned or you pass it to `--force-prune-keys`, so `playwright-local` survives `install.sh --update` (a test pins this). The generated agent tool lines name the `playwright` server's tools, not `playwright-local`'s, so on Claude Code, GitHub Copilot/VS Code and Pi (for an agent that lists an `mcp__` tool) subagents do not receive the second server's tools; on Opencode and Gemini CLI an agent's tool list does not restrict MCP tools, so any agent can call them. The server-level denial of six tools ([below](#server-level-denial-of-six-playwright-tools)) covers the `playwright` server only: `playwright-local` is another server name and is not denied, on any platform. The entry has no origin restriction and includes `browser_run_code_unsafe`: use it from your own session on a development machine, and remove it when you are done.

**Limits. This is not a security boundary.** The origin flags block a direct navigation or sub-request to a listed origin. They do not cover redirects (an allowed page that answers `302` to a blocked address still reaches it, and the page content is returned to the model), WebSockets, a DNS name that resolves to an internal address, or the `browser_run_code_unsafe` tool, which runs code on the host. The flags only narrow what the entry reaches; the Playwright `--help` text says the same. Four agents (`qa-engineer`, `frontend-developer`, `poc-qa-engineer`, `demo-agent`) hold named Playwright tools only (T657, SEC-T655-01): none holds the whole server or `browser_run_code_unsafe`, `browser_evaluate` or `browser_file_upload`. Where that narrowing is in force depends on the platform; see [MCP tool names per platform](#mcp-tool-names-per-platform). On the platforms where it is not in force (Opencode, Gemini CLI, and Pi for agents that list no `mcp__` tool) an agent's tool list does not restrict MCP tools: every agent, not only these four, can call every tool of every configured MCP server that is not denied server-wide or, on Opencode since T663, per agent ([Per-agent denial](#per-agent-denial-on-opencode-t663-sec-t658-01): the six tools for every agent and `<server>_*` for every non-exempt server an agent holds no token of), including the GitLab write tools elsewhere. Since T658 (SEC-T657-01) the generator denies six tools of the shipped `playwright` server on Opencode and Gemini CLI ([Server-level denial](#server-level-denial-of-six-playwright-tools)); on Pi for an agent with no `mcp__` entry, `browser_run_code_unsafe`, `browser_evaluate` and `browser_file_upload` stay callable by every agent. The Copilot and Pi rows rest on vendor documentation and source, not on a live run. On GitHub Copilot/VS Code the agents' MCP grants (`gitlab`, `memory`, `sequential-thinking`, `playwright`) take effect for the first time in this release; before, the tokens were ignored. Granted tools such as `browser_snapshot`, `browser_take_screenshot`, `browser_console_messages`, `browser_network_requests` and `browser_find` can write to a workspace-relative `filename` and send page URLs and console output to the model provider: use synthetic data and test accounts only. Pages the agent opens can contain prompt-injection text, and nothing here filters it. Evidence: `docs/artifacts/fetch-replacement-evaluation-v1.md`.

## Server-level denial of six Playwright tools

Opencode and Gemini CLI do not restrict MCP tools by an agent's tool list, so the narrowed grants above are not enforced there. For Opencode and Gemini CLI the vendors document a server-level denial, and the generator emits it (T658, SEC-T657-01) for exactly these six tools of the `playwright` server: `browser_run_code_unsafe`, `browser_evaluate`, `browser_file_upload`, `browser_drag`, `browser_drop` and `browser_network_request` (the singular; the granted `browser_network_requests` is not denied). The one list is `denyTools` on the `playwright` entry of `implementation/knowledge/mcp/servers.yaml`; the projections are generated.

| Platform | Emitted form | File |
|---|---|---|
| Opencode | top-level `permission` entries `"playwright_browser_evaluate": "deny"` and the five others (`playwright_<tool>`) | `.opencode/opencode.json` |
| Gemini CLI | `"excludeTools": ["browser_run_code_unsafe", ...]` on `mcpServers.playwright` (the tool names as the server reports them) | `.gemini/settings.json` |
| Claude Code, GitHub Copilot / VS Code, Pi, Cline | none needed or none available; see the table below | none |

- **Status: documented and read from vendor source, not observed in a live run.** Sources, the exact lines read, and what is unverified: `docs/artifacts/mcp-server-denials-v1.md` (recorded before Cursor was removed; its Cursor rows are historical).
- **Opencode: the last matching rule wins, and an agent's own rules come after the global ones.** The generated agent files grant only named Playwright tools (19 of the 25 default tools exist outside the denial list; the four agents hold between 12 and 18 of them) and never one of the six, so the denial holds for every shipped agent (a test models the order). An agent file of your own that allows one of these names, `playwright_*` or `*` is later in the order and overrides the denial. The per-agent `false` entries described below (T663) are written into every generated agent file and survive a broader allow of the global config; they do not survive an allow written later in your own agent file or another config source. Opencode's `--auto` mode still enforces an explicit `deny`.
- **Gemini CLI:** `excludeTools` takes precedence over `includeTools`. The filter runs when tools are discovered, so subagents never receive an excluded tool (read from source; the documentation does not mention subagents). `mcpServers` merges per server name, so a same-named `playwright` entry in a higher-precedence settings scope replaces the generated entry and its list. A same-named `playwright` entry in a settings source that Gemini ranks above the project file (the system settings file) replaces the generated entry and its list; project settings load only in a trusted workspace (unverified).
- **`playwright-local` is not covered.** A user-owned entry named `playwright-local` is another server name (`playwright-local_browser_evaluate` on Opencode, a different entry on Gemini CLI). It is not denied and it still holds `browser_run_code_unsafe`.
- **Install merge:** `install.sh` runs `scripts/merge-mcp-json.py` whenever the config already exists, in every mode (`--update`, `--projections-only` and, since T672, a plain install, which used to overwrite it), with or without the provenance sidecar. A rule of yours that the generated `deny` replaces is named on stderr (names only, never values). For `excludeTools` it unions your list with the generated one (your elements first, nothing of yours is dropped). For Opencode it keeps your own `permission` rules (a string such as `"allow"` becomes `{"*": "allow"}`), sets the six generated keys to `deny` and puts them last, so your earlier wildcard cannot win in the same file. The six names are generator-owned: an edit that re-allows one is undone by the next update. To use one of these tools, add a server entry of your own under another name. An element the generator stops shipping later stays in your file until you remove it. On Opencode the guarantee that the denial comes last holds inside one file: Opencode merges several config sources, and a `playwright_*: allow` in another source can still follow it.
- **Still open:** on Gemini CLI every other tool of every configured server (for example the GitLab write tools) stays callable by every agent. On Opencode the per-agent denial below closes every non-exempt server for every generated agent that does not hold it; what stays open there is the exempt read/search servers, the built-in agents and agent files of your own (below).

### Per-agent denial on Opencode (T663, SEC-T658-01, SEC-T663-01)

The generator writes `false` entries into the `tools:` map of **every** Opencode agent file (`.opencode/agents/*.md`). Opencode applies the last matching rule, so a deny written after an allow survives a broader allow before it, and a wildcard deny written before named allows leaves exactly those allows:

- `playwright_<tool>: false` for the six tools above, for every agent, last in the file (the `denyTools` list; it also stays in the server-level denial).
- `<server>_*: false` for every non-exempt server an agent holds no token of, after the agent's allows. The flag is `denyUnlessGranted`, declared on **every** entry of `servers.yaml` (the 16 servers the Opencode manifest carries): `true` for gitlab, playwright, memory, sequential-thinking, security-audit, poc-security-audit, context-retriever, filesystem, git and supabase; `denyUnlessGranted: false`, an explicit exemption, for brave, context7, hindsight, cwso, hf-mcp-server and toolradar (user decision of 2026-10-16, "Exempt the read/search servers": generated agents, including a primary orchestrator, keep search, documentation and memory-layer access). It is a wildcard on purpose: a list of write tools would miss the tools a pin bump adds and the mixed-access tools (`execute_graphql`, `gitlab_api_request`). For `gitlab` that is 21 of the 28 agents (for example tech-lead), which therefore also lose the GitLab read tools; the seven GitLab holders (qa-engineer, scrum-master, orchestrator, poc-orchestrator, devops-engineer, release-manager, poc-devops-engineer) get `gitlab_*: false` first and their named allows after it.
- **Named-subset rule:** an agent that holds only named tools of a server gets that server's `<server>_*: false` as one of the FIRST entries of its map, and its named `<server>_<tool>: true` entries follow it. The named tools are then the only tools of that server it can call. This applies to all seven GitLab holders (qa-engineer, scrum-master, orchestrator, poc-orchestrator, devops-engineer, release-manager and poc-devops-engineer; `gitlab`), to the four Playwright agents (`playwright`), to security-engineer and poc-security-engineer (`security-audit`, `poc-security-audit`) and to context-retriever. Here the order of the entries, not a distinct name, makes the pair work: do not reorder the file (the installer restores it on update).
- **Servers that no agent holds and that are not exempt** (`filesystem`, `git`, `supabase`) are denied in every generated agent file, including the orchestrators that can be selected as the primary agent. On Claude Code a subagent without the token cannot call them either, but the main session is not a subagent and keeps them; on Opencode use a built-in agent or an agent file of your own to reach them. The exempt servers (`brave`, `context7`, `hindsight`, `cwso`, `hf-mcp-server`, `toolradar`) get no entry at all.
- A name is never both allowed and denied in one file: the generator stops if an agent would grant a denied tool, and a test pins it for all agent files. An agent file is a map, so the same name cannot appear twice.
- **Override behaviour (SEC-T657-04):** the `true` entries an agent holds come after your global config and win, so your own global `ask` or `deny` on a tool an agent holds is silently overridden for that agent. Example: a global `ask` on `gitlab_create_merge_request` is overridden for the three agents that hold it (orchestrator, poc-orchestrator, release-manager). Since T667 no agent holds the whole `gitlab` server, so every `true` entry is a named tool and you can still override only the tools an agent holds; a tool that no agent holds, such as `gitlab_merge_merge_request`, stays denied in every generated agent file whatever your global rule says (`gitlab_*: false` comes first in each holder's map). No supported way through the generated files or through your project or global configuration keeps a prompt there (an `agent.<name>.permission` entry in your project config is placed before the agent's own rules and loses too); only a source loaded after the agent files can, the environment variable `OPENCODE_CONFIG_CONTENT` (observed on opencode-ai 1.19.2) and, by source reading only, the managed configuration. A tool the agent does not hold keeps your rule unless a generated deny covers it.
- **Over-match:** the wildcards also match a user-owned server whose cleaned name starts with the prefix and an underscore (`gitlab_ee` is matched by `gitlab_*`; `gitlab-ee` is not). For an agent without the server that fails closed.
- **Saved "always" approvals** do not undo a deny: the legacy runtime hides a tool whose last matching rule is a deny, and the current core tests `denied()` before it adds saved approvals (source reading; an approval saved before the deny existed is unverified).
- **Built-in agents get no per-agent deny:** Opencode's built-in agents (build, plan, general, explore, ...) and agent files of your own are not generated by this repository. Only the server-level `permission` of `.opencode/opencode.json` (the six Playwright tools) applies to them; every other tool of every configured server, the GitLab write tools included, stays callable there. That gap is a decision of the user (2026-10-16, option "No, document the gap only") and is tracked.
- **Install:** `install.sh --update` replaces `.opencode/agents/` as a tree; it does not merge agent files. An edit of a generated agent file, and an own agent file placed in that folder, do not survive an update. The MCP config file is still merged as described above.
- **Status: documented, read from vendor source and observed in the resolved rule lists of `opencode-ai@1.19.2` (`opencode debug agent`, raw output stored); a refused tool call has not been observed.** A user-owned agent file, another config source, a managed policy (or a plugin: unverified) that allows these names later still wins. Evidence and sources: `docs/artifacts/mcp-agent-denials-v1.md`, `docs/artifacts/mcp-agent-denials-evidence-v1.md`. Planned: moving the entries from the deprecated `tools:` map to a `permission:` block (tracked debt).

## MCP tool names per platform

Agent sources write an MCP tool as `mcp__<server>__<tool>` and a whole server as `mcp__<server>`. `sync.mjs` renders that into the form each platform documents, through the manifest key `frontmatter.agents.mcpToolNames`. A platform whose naming is unverified keeps the source form. Evidence and sources: `docs/artifacts/mcp-tool-name-mapping-v1.md` (recorded before Cursor was removed; its Cursor rows are historical).

| Platform | Agent tool line | Narrowed Playwright grant in force |
|---|---|---|
| Claude Code | `mcp__playwright__browser_click`, `mcp__gitlab__get_pipeline` (unchanged) | Yes |
| GitHub Copilot / VS Code | `playwright/browser_click`, `gitlab/get_pipeline` | Yes. Before T657 the old tokens were ignored on this platform |
| Pi | `mcp__playwright__browser_click`, `mcp__gitlab__get_pipeline`; hyphens in server names become `_` | Yes when the agent file is passed to `pi --tools` (the example subagent extension does); other extensions unverified |
| Opencode | `playwright_browser_click: true`, `gitlab_get_pipeline: true` (after `gitlab_*: false`); `<server>_*: false` for every non-exempt server an agent holds no token of and the six unsafe tools as `false` (per-agent, T663) | No: the `tools` map is not an allowlist, unlisted tools keep their default. The six unsafe tools are denied server-wide and per agent, and every non-exempt server an agent holds no token of is denied for that agent (above) |
| Gemini CLI | none: the generator drops the tools line | No: subagents inherit every tool of the session. The six unsafe tools are excluded on the server entry (above) |
| Cline | no agent files | n/a |

**GitLab grants.** No agent holds the whole `gitlab` server any more (T667). At `@zereight/mcp-gitlab@2.2.5` the server registers 275 tools (the raw `gitlab_api_request` tool among them is opt-in through `GITLAB_TOOLSETS=api` only), including merge, push, delete and branch/tag/release creation; seven agents hold named tools only. scrum-master (24 tools: issues, notes, labels, milestones, read-only merge request lookups), qa-engineer (19 tools: bug issues and notes, read-only merge request, pipeline, job and test report lookups), orchestrator (16 tools: read-only issue, merge request, pipeline and branch lookups, and `create_merge_request`), poc-orchestrator (8 tools: merge request lookups, `create_merge_request`, pipeline lookups), devops-engineer (11 tools: read-only pipeline, job, merge request and test report summary lookups and the two CI lint tools `validate_ci_lint` and `validate_project_ci_lint`, which validate YAML and change nothing), release-manager (17 tools: read-only merge request, approval state, pipeline, issue, branch, tag and release lookups, and `create_merge_request`) and poc-devops-engineer (6 tools: pipeline lookups and the two CI lint tools) hold none that merges, approves, pushes, writes files, deletes, creates branches, tags or releases, triggers, retries or cancels pipelines, reads CI variables, environments or deployments, or sends a raw API request; no agent of these seven holds a tool that reads raw job output (T688, SEC-T660-02): a shell can still run `glab ci trace`, and on Gemini CLI the tool list does not restrict MCP tools (T660 for qa-engineer and scrum-master, T666 for the two orchestrators, T667 for the other three; SEC-T657-02, SEC-T660-04). By policy the top-level session merges after its own verification and creates the tag and the release with the user's approval; release-manager opens the release merge requests and reads the result. This is a tool-list narrowing and a policy, not an enforcement. Six of the seven roles hold `execute`, and the setup instructions export `GITLAB_PERSONAL_ACCESS_TOKEN` into the environment that starts the assistant, so a shell in those roles can merge, tag, release or push with that token. Use a least-privilege token and, preferably, the token file (T665, SEC-T660-01: mitigated, not closed; see [GitLab token](#gitlab-token)). The pinned server reads further operator controls that the generated entry does not set and that you can add to the `env` of your own `gitlab` entry (a key you add there is kept by `install.sh --update`; Opencode names that map `environment`): `GITLAB_DENIED_TOOLS_REGEX` (a deny-list by pattern; the server's README gives no syntax or matching rules), `GITLAB_ALLOWED_PROJECT_IDS` (a project allow-list that the README says is "checked only for `/projects/:id` paths"; that endpoints such as `/search`, `/users` and `/groups/:id` are therefore not constrained is from the README on main, not matched to 2.2.5, unverified; whether it constrains the named tools of these roles is unverified), and `GITLAB_TOOLS` and `GITLAB_TOOLSETS` (which tools the server registers; an explicit `GITLAB_TOOLS` list replaces the default `core` toolset and does not merge with it). `GITLAB_PERMISSION_MODE` takes `readonly`, `modify` or `full` (per the README; unverified, see PREREQUISITES). None of them stops a shell that holds the token from calling the API; details and the unverified points: [`implementation/PREREQUISITES.md`, "Server-side limits"](https://gitlab.com/em-age/emage.code/-/blob/main/implementation/PREREQUISITES.md#server-side-limits). `create_merge_request` can target any project and branch the token reaches and can start merge request pipelines; the CI lint tools with `dry_run` resolve `include:` entries server-side. The user's own main session and Opencode's built-in agents are not agents of this set and are unaffected. By default the server exposes only its `core` toolset until `discover_tools` activates the others (`milestones`, `labels`, `pipelines`, `issues`, `merge_requests`, `ci`, `tags`, `releases`); `discover_tools` cannot widen the seven roles' allowlist on a platform that enforces one, but it changes the visible toolset for the whole session. All seven lists include `discover_tools`, which the server needs to expose the non-default toolsets (`milestones`, `labels`, `pipelines`, `issues`, `ci`, `tags`, `releases`). This holds on Claude Code and, according to the vendor documentation (not observed in a live run), on GitHub Copilot/VS Code, and on Pi for an agent whose file is passed to `pi --tools` with an `mcp__` entry (vendor documentation and source; other consumers of the agent files are unverified; not observed in a live run); on Gemini CLI the agent tool list does not restrict MCP tools, so every agent can still call every GitLab tool there. On Opencode the generator writes per-agent `<server>_*: false` entries for every non-exempt server an agent holds no token of, so the 21 agents without a GitLab tool cannot call one, and the seven named holders (`gitlab_*: false` before their named allows) can call only their named GitLab tools there (per-agent, T663; documented and read from vendor source, not observed in a live tool call; `docs/artifacts/mcp-agent-denials-v1.md`).

## Corrections to the cited artifacts

Three statements in the immutable artifacts that this page cites were corrected by later reviews (T674, TD-T671-ART in `docs/artifacts/tracked-debt-register-v1.md`). The artifacts stay as recorded; where they differ from this table, this table governs. A `-v2` of the artifacts was not written because only statements changed, not the decisions or the evidence.

| Artifact and place | Statement as recorded | Corrected statement | Basis |
|--------------------|-----------------------|---------------------|-------|
| `docs/artifacts/mcp-server-denials-v1.md` §2.1 (second bullet) | The generated Opencode agent files list "only the 18 distinct granted Playwright names" | **19.** The four agents together hold 19 distinct Playwright tools, which is every one of the 25 default tools of `@playwright/mcp@0.0.83` outside the six-tool denial list (each agent holds between 12 and 18). The [Server-level denial](#server-level-denial-of-six-playwright-tools) section above states 19, and `tests/functional/test_mcp_grant_pins.py` pins that sentence to the grant sets | SEC-T658-07(a); counted from `EXPECTED_PLAYWRIGHT_GRANTS` in `tests/functional/test_mcp_package_pins.py` |
| `docs/artifacts/mcp-server-denials-v1.md` §2.2 (Scope merge) and §6 item 3 | "A user-level entry named `playwright` that wins over the project file therefore has no denial" | **A user-level entry does not win over the project file.** Gemini CLI's documented order (lowest to highest) is defaults, system defaults, user settings, project settings, system override settings, environment variables, command line, so project settings override user settings and only the system override settings file ranks above the project file. A same-named `playwright` entry in the system override settings therefore replaces the generated entry and its `excludeTools`; project settings load only in a trusted workspace (unverified) | SEC-T658-03; vendor page `https://geminicli.com/docs/reference/configuration/`, read on 2026-10-22 through a web-fetch summary, not run; the [Server-level denial](#server-level-denial-of-six-playwright-tools) section above already states it |
| `docs/artifacts/mcp-tool-name-mapping-v1.md` §4 ("What the narrowing does not fix") | Lists redirects through a granted `browser_navigate` and prompt-injection text on a page | **Also not fixed:** granted tools such as `browser_snapshot`, `browser_take_screenshot`, `browser_console_messages`, `browser_network_requests` and `browser_find` can write to a workspace-relative `filename` and send page URLs and console output to the model provider; use synthetic data and test accounts only (the limits paragraph of the [Playwright server](#playwright-server-playwright) section) | SEC-T657-05, SEC-T657-06 |

## Package pins and runtime requirements of the extended servers

Every `npx` and `uvx` entry in `servers.yaml` is pinned to an exact version (audit SEC-002); `@latest` and ranges are not used.

| Server | Launcher | Needs |
|--------|----------|-------|
| `filesystem` | `npx -y @modelcontextprotocol/server-filesystem@1.0.0 .` | Node.js |
| `git` | `uvx mcp-server-git@2026.10.10 --repository .` | `uv` on `PATH` |
| `supabase` | `npx -y @supabase/mcp-server-supabase@0.13.0 --read-only` | Node.js |

**Pin maintenance.** The devops-engineer bumps the pins at every release and at least monthly; there is no automated scheduler. Each bump is a reviewed change that edits `servers.yaml` and the `APPROVED_NPX_PINS` dict in `tests/functional/test_mcp_package_pins.py` together. Before a bump, check the package with `npm audit` or OSV, and check the registry's latest version and its provenance. `@zereight/mcp-gitlab` holds the GitLab token, has a single maintainer, and releases often with published advisories, so it is reviewed at every release.

The full checklist for a bump and for a release (provenance, audit script, advisory read, browser version, hash locks, container provenance, live denial checks) is `docs/wiki/mcp-pin-bump-checklist.md` (page `mcp-pin-bump-checklist`).

**Supabase token scope (T638 review, L-4).** `SUPABASE_ACCESS_TOKEN` is a Supabase personal access token, recorded by the T638 security review as account-wide. The `--read-only` flag that the generated entry sets limits what the server's tools do; it does not narrow the token, so anything that can read the environment of the server process holds the full token. Two ways to narrow the exposure, both in your own client config because the generated entry sets neither: (1) scope the server to one project with `--project-ref=<ref>`. The flag is named by that review and is **unverified** against the pinned `@supabase/mcp-server-supabase@0.13.0`: the vendor pages read on 2026-10-22 document only the hosted server's `project_ref` and `read_only` URL parameters, not stdio flags. (2) Use the hosted Supabase server at `https://mcp.supabase.com/mcp`, which signs you in with OAuth in the browser, so no personal access token is needed (vendor page read on 2026-10-22). This repository generates and tests no entry for the hosted server; add one of your own under another name. Vendor advice for any token: scope it to the project the server connects to, grant only the permissions your enabled tools need, and connect to a production project only when the task requires it.

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

**Submodules are not scanned (SEC-013).** The server runs `git grep` without `--recurse-submodules` (the `worktree` and `index` scopes pass only `--untracked --no-exclude-standard` or `--cached`; read in `poc_scan.py`, not run), and with default git configuration git does not descend into a submodule (a repo-local `submodule.recurse` setting could change that; unverified), so the content of a submodule is outside every scope, including a `complete: true` result. A secret that lives only in a submodule is not found; scan the submodule as a repository of its own. Whether the server accepts a submodule's top level as `root_dir` (its `.git` is a file; see limit L-6 in the module docstring) was not tested **(unverified)**. The launch-directory dependency of `--allowed-root .` is stated in [Requirements](#requirements).

### Requirements

| Requirement | Detail |
|-------------|--------|
| Python package `mcp` | Pinned `mcp==2.2.0` in `implementation/runtime/security/requirements-mcp-server.txt`, the same pin as the memory server. That release declares Python 3.10 or newer on PyPI; the repository itself states no minimum. Without it the client shows a generic "Connection closed" error. |
| `git` 2.40 or newer on `PATH` | The scanner reads attributes from git's empty tree with `--attr-source`; an older git exits non-zero and every call fails closed as `git_failed`. |
| A regex library with `RE_DUP_MAX` of at least 1024 | Used by `git grep -E` and `git log -G`. glibc has 32767. Where it is lower (some musl and BSD builds), every scope except `tracked_names` ends `regex_unsupported` with `complete: false`. |
| Launch from the project root | The configs start the server with `--allowed-root .` and an `implementation.…` module path, both relative to its launch directory. The server accepts only repositories inside that directory. In VS Code the entry sets `"cwd": "${workspaceFolder}"`, so the launch directory is the workspace folder; open the project root as the workspace folder. |
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

The entry is generated into `.mcp.json` (Claude Code), `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`, `.cline/mcp.json` and, since T690, GitHub Copilot's `.vscode/mcp.json`. The `github` platform does not carry the `extended` servers as a group: `servers.yaml` lists `extraPlatforms: [github]` on `security-audit` and `poc-security-audit` and on no other entry, so `cwso`, `hf-mcp-server`, `context-retriever`, `filesystem`, `git`, `supabase` and `toolradar` stay out of `.vscode/mcp.json`. `sync.mjs` refuses a platform name in `extraPlatforms` that no manifest declares, before it writes a file.

The VS Code entries differ from the others in one key. Each carries `"cwd": "${workspaceFolder}"` (`cwd: workspace` in `servers.yaml`), so the server starts in the workspace folder and `-m implementation.runtime.security...` and `--allowed-root .` resolve against it. VS Code documents `cwd` ("Working directory for the server command. Defaults to the workspace folder when run in a workspace.") and `${workspaceFolder}` as a predefined variable of the server configuration (<https://code.visualstudio.com/docs/copilot/reference/mcp-configuration>, read 2026-10-24); a live VS Code run was **not** made **(unverified)**. The same page says workspace MCP servers inherit Workspace Trust, and it separates trusting a server to start from approving individual tool calls, so VS Code can ask for either before the scan runs; the prompts were not observed **(unverified)**. Whether the `python3` that VS Code launches can import `mcp` depends on your machine **(unverified)**. VS Code starts the server from its own process environment, not from a terminal virtual environment: start VS Code from a shell where the virtual environment of [Requirements](#requirements) is active (for example `source .venv-mcp/bin/activate && code .`), or make `python3` on the `PATH` of the VS Code process able to import `mcp`.

The Copilot agent files list the tools in Copilot's form, `security-audit/<tool>` and `poc-security-audit/<tool>` (`frontmatter.agents.mcpToolNames: slash`; see `docs/artifacts/mcp-tool-name-mapping-v1.md`): `security-engineer` holds the four `security-audit` tools and `poc-security-engineer` holds `security-audit/grep_content`, `poc-security-audit/scan_secrets` and `poc-security-audit/ref_containment`, as on the other platforms, and no other Copilot agent lists either server. The server's own denials and its allowed root are unchanged. The config holds no secret and no placeholder, because neither server reads an environment variable. The `FAIL` rule above is unchanged: a scan that did not complete is `FAIL` on Copilot as everywhere else.

## Per-platform output

| Platform | Output file |
|----------|-------------|
| GitHub Copilot | `.vscode/mcp.json` |
| Gemini CLI | `.gemini/settings.json` |
| Opencode | `.opencode/opencode.json` |
| Pi | `.pi/mcp.json` |
| Claude Code | `.mcp.json` (repo root) |
| Cline | `.cline/mcp.json` (staging file — see [Cline Setup](cline-setup)) |

All platform configs are regenerated by `node implementation/scripts/sync.mjs --root implementation`.

## Provenance-aware merge on `--update`

Every platform's generated MCP/settings file is accompanied by a `<mcpfile>.provenance.json`
sidecar recording the exact set of server keys the generator owned at that generation. On every
merge of an existing config (`scripts/install.sh --update`, `--projections-only`, or a plain install
over an existing file since T672), this sidecar lets the merge (`scripts/merge-mcp-json.py`)
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
takes effect for keys retired after a sidecar exists. Since T672 the merge says so: when there is
no sidecar, it prints a note naming the servers of yours that the generated config lacks and that
it therefore kept (see [Files and notes the installer produces](quick-start#files-and-notes-the-installer-produces)).

**One-time bootstrap bridge:** `scripts/merge-mcp-json.py --force-prune-keys <name1,name2,...>`
prunes exactly the named dest-only keys, with no dependency on sidecar history — used only once,
explicitly, by `docs/tasks/task-T382.md` to close the already-decided `e2b`/`redis`/`figma`/
`notion` removal gap for already-installed roots. It is not invoked automatically by `--update`
anywhere in this codebase, and is not a general-purpose "prune whatever" convention — every
invocation names an explicit, already-reviewed list.

## Migrating an existing install from v7.x

v8.0.0 corrects and pins the MCP server entries (audit SEC-002). Four extended entries named npm packages that do not exist (the `@anthropic/mcp-filesystem` name belonged to an unrelated npm account, so a third party could have published under it); every `npx` server is now pinned to an exact version; `docker` and `postgresql` are removed. After upgrading:

1. Run `scripts/install.sh --update` in your project.
2. The `filesystem`, `git` and `supabase` entries are overwritten in place: `command` and `args` are replaced and the new `env` entry is added. A key you added yourself inside one of those entries (for example an extra `env` variable) is kept; delete it if you no longer want it. Your own server entries with other names are kept.
3. `docker` and `postgresql` are removed automatically only if the installed file's `<file>.provenance.json` sidecar lists them as generator-owned. If the install has no sidecar (v6.9.0 or earlier), or the sidecar no longer lists them, remove both server objects from every installed MCP config by hand, or run once per file and once per name: `python3 scripts/merge-mcp-json.py --source <generated file> --dest <your file> --force-prune-keys docker`, then the same with `postgresql`. Use one name per call: the script refuses, and writes nothing, if any named key is missing from the destination or still present in the source, so the combined `--force-prune-keys docker,postgresql` fails as soon as one of the two is already gone. `install.sh` does not pass this option, so this is a direct call. The files are `.mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.cline/mcp.json`, `.pi/mcp.json` and `.vscode/mcp.json`. Cline's real configuration is global (see [Cline Setup](cline-setup)): remove the two entries from it directly.
4. If you had your own server entry named `docker` or `postgresql` and the old sidecar lists those names, the update removes it as well, because only the name is compared. Re-add it under another name.
5. Set `SUPABASE_ACCESS_TOKEN` (`supabase`) in the environment that starts your assistant and install `uv` if you use `git`. An unset variable stops only that server.
6. The `fetch` server is removed the same way as `docker` and `postgresql` (step 3): automatically when the installed file's `<file>.provenance.json` sidecar lists it, otherwise delete the `fetch` object by hand or run the step 3 command with `--force-prune-keys fetch` (a separate call, not combined with the other names). The `playwright` entry is overwritten with the hardened arguments and needs Chrome for Testing, installed with the pinned command in `implementation/PREREQUISITES.md`; that file also explains how to test a local app (`playwright-local`).
7. Your client may ask you to approve the changed servers again (Claude Code asks before using a project-scoped server from `.mcp.json`). Approve the new entries after checking them.
8. **v9.0.0: the `github` server is removed** (the GitHub MCP container, user decision 2026-10-22). It is pruned automatically when the sidecar lists it, otherwise delete the `github` object by hand or run the step 3 command with `--force-prune-keys github`. If you used it, copy the entry from your old config under your own server name (for example `github-mine`) before updating: `install.sh --update` removes only the generator-owned name `github`. A GitHub server that you keep under your own name is outside every generated denial on Opencode and Gemini CLI (those denials name the generated servers only), so give it a fine-grained, read-only token. If you no longer use a GitHub server, revoke or unset `GITHUB_PERSONAL_ACCESS_TOKEN`. The harness ships no GitHub tooling any more; your own session keeps whatever you configured yourself.

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
| Pi | `{ "url": "…" }` | **Closed decision (T385): keep the `{ "url": ... }` shape with no `type` field.** T360's web search left this inconclusive; T385 re-attempted via `context7` (a new angle) and confirmed Pi is [pi.dev](https://pi.dev), a real terminal coding-agent product (`context7` library `/websites/pi_dev`), built on the open-source `@earendil-works/pi-coding-agent` package — whose own docs state it "intentionally does not include built-in MCP... build or install those workflows as extensions or packages" (`https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/usage.md`). MCP support for Pi is therefore provided by third-party extensions rather than a single first-party spec; the `@spences10/pi-mcp` extension (part of the `my-pi` distribution, `context7` library `/spences10/my-pi`) documents `mcp.json` loaded from `~/.pi/agent/mcp.json` using the standard `mcpServers: { name: {...} }` wrapper for stdio servers, but its README provides no JSON example for a remote/HTTP server shape. Pi is documented (current main branch, `docs/mcp.md`) to have native MCP support (`pi mcp add`, `.pi/mcp.json`), but an older Pi may not, and its remote-transport shape is not confirmed by this repository; so there is no single canonical "Pi" remote-transport shape to confirm against — the actual shape depends on whichever third-party extension a given user installs, which this repo cannot target definitively. Retaining the `{ "url": ... }` (no `"type"`) shape, which Pi inherited from the format of another platform and now emits under its own `pi` format value, as the least-risky default; this closes the question rather than leaving it open for a third research pass. |
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
discipline to all 6 platforms: **automated (schema-backed)** where live research
(2026-08-10) confirmed the platform publishes a genuine, citable JSON Schema for the
exact config file this repo generates, **documented manual check** everywhere else — no
platform is left silently unaddressed.

| Platform | Verification method | Basis |
|----------|---------------------|-------|
| GitHub Copilot (VS Code) | Documented manual check | No officially published, standalone-fetchable JSON Schema found for `.vscode/mcp.json` — see below. |
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
