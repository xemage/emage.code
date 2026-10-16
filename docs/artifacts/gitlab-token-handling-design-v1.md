# Artifact: gitlab-token-handling-design-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: solution-architect (T664). No shell, no live client run, no token used or read. The Security Engineer persona applies: nothing is graded closed without a named mechanism.
- **Date**: 2026-10-16. **Status**: PROPOSED. The user's decision is pending (section 10); this file records options and a recommendation only.
- **Based on**: `docs/tasks/task-T664.md`; `docs/plans/plan-123-post-release-follow-ups.md` (T664, T665, T666, T667, T677); `docs/artifacts/security-review-t660-gitlab-grants-v1.md` (SEC-T660-01, -03, -04, -05); `docs/releases/v8.0.0.md` (K-13, K-15, K-16, M-2, M-8 and the Gate Verdicts); `implementation/knowledge/mcp/servers.yaml` (the `gitlab` entry); `implementation/.mcp.json`, `.vscode/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`, `.cline/mcp.json`; `implementation/PREREQUISITES.md`; `docs/wiki/mcp-servers.md`; `implementation/scripts/sync.mjs` (`emitMcp`, `mapTemplatedValue`, `mapEnv`); `implementation/knowledge/agents/qa-engineer.md` and `scrum-master.md` (tool lists); `implementation/knowledge/skills/gitlab-api-push-fallback/SKILL.md`. No `requirements-vN.md` applies to this task. Vendor sources are listed in section 12.
- **Evidence labels**: **[V]** = read in vendor documentation or vendor source during this task (URL in section 12). **[U]** = not verified. **No fact in this document was observed in a live run of any client.** A [V] fact is a documentation statement, not a test result.
- **Out of scope**: Cursor. The user decided on 2026-10-16 to drop Cursor support (T661, T662). Cursor is not analysed and T665 must not extend the Cursor format.
- **Decision references**: DEC-T664-1 to DEC-T664-6 (section 10). A proposed ADR (next free number after the ADR-010 that T661 reserves) is for the orchestrator to write after the user decides; this task may write one file only.

## 1. Summary

1. **SEC-T660-01 cannot be closed by any mechanism the generator can ship.** The harness cannot put a shell-holding agent and the assistant's MCP server under different operating-system principals. Every option below leaves a same-user path to the token or to a more powerful credential of the same user (section 2, AP-3 and AP-4). What can be done is (a) make the exported or stored token weak enough that stealing it is no worse than the granted tool list, and (b) on the clients that offer a mechanism, keep the token out of the places a shell reads by default (the process environment, `/proc`, shell history).
2. **Neither role is read-only, so a "read-only token for QA and scrum" does not exist.** `qa-engineer` writes issues and notes, `scrum-master` writes issues, labels, milestones and links. A legacy PAT needs the full `api` scope for any of that (`read_api` is read-only, `write_repository` does not authenticate the API). The smallest credentials are a fine-grained PAT (GA in GitLab 19.2) or an `api`-scope project, group or bot-user token whose **role** is low.
3. **Recommendation: option D, a combination of three layers** (section 7): **R1** a least-privilege token (mandatory, documentation plus a check script, all clients); **R2** an additive token-file mode using the server's own `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` (verified in the pinned 2.2.5 source), contract-compatible with `fromEnv`; **R3** a documented, client-owned hardening posture for Claude Code (subprocess env scrub, sandbox read denies) and the native secret input of Copilot and Pi. A launcher wrapper is declined for now. Two separate tokens or server entries (option B) are deferred until T666 and T667 have fixed the role tool sets.
4. **The honest outcome** (section 7.3): after T665, SEC-T660-01 is *reduced for the environment path* on every client and *closed for AP-1 and AP-2 only on Claude Code on Linux under the documented posture, once a live test confirms it*. It stays open for AP-3 and AP-4 on every client. The user must re-accept the residual; the Security Engineer review of T665 grades it.
5. **Three side findings** matter for T665 (section 2.2): the scope text in `PREREQUISITES.md` is wrong for the tools the roles use and disagrees with the wiki; Claude Code passes an unset `${VAR}` through as literal text, which defeats any file mode that is not guarded by an empty default; and the generator emits `${env:VAR}` for Gemini CLI, Pi and Cline, a form their documentation does not show (the forms they document are `$VAR` or `${VAR}`).

## 2. Problem and threat model

### 2.1 How the token flows today

`servers.yaml` declares `GITLAB_PERSONAL_ACCESS_TOKEN: { fromEnv: GITLAB_PERSONAL_ACCESS_TOKEN, secret: true }` for the core server `gitlab` (`@zereight/mcp-gitlab@2.2.5`, stdio, started with `npx`). `emitMcp` renders a placeholder per platform (`sync.mjs`, `mapTemplatedValue`): Claude Code `${VAR}`, GitHub Copilot, Gemini CLI, Pi and Cline `${env:VAR}`, Opencode `{env:VAR}`. The client expands the placeholder from **its own process environment** and passes the value to the server in the server's `env`. The adopter documentation says to export the variable "in the environment that starts the assistant" (M-2). That environment is also the environment of every shell command the client runs for an agent: the Claude Code Bash tool, the Copilot terminal tool, the Opencode and Gemini shell tools, the Pi bash tool. The server also lives in the same session for every subagent (one stdio process per client configuration).

The `gitlab` server is `core`, so it is in all seven generated configs, including Copilot's.

### 2.2 Findings from reading the current state (inputs to T665)

| ID | Finding | Evidence |
|---|---|---|
| F-1 | `PREREQUISITES.md` says the token needs `read_api, write_repository, read_user`. That cannot create an issue or a note: `read_api` is read-only and `write_repository` "does not support API authentication". The wiki says `api, read_repository, write_repository`, which is broader than any role needs. The two documents disagree. | `implementation/PREREQUISITES.md` (MCP server credentials); `docs/wiki/mcp-servers.md` (Required environment variables); GitLab scopes page [V] |
| F-2 | In Claude Code an unset `${VAR}` is "the unexpanded `${VAR}` text as-is" (a warning in `claude mcp list`). A non-empty literal in `GITLAB_PERSONAL_ACCESS_TOKEN` wins over a token file in the pinned server (inline before file), so a file mode needs an empty default (`${VAR:-}`), or the file is silently ignored. | Claude Code MCP page [V]; `personal-access-token.js` 2.2.5 [V] |
| F-3 | The generator emits `${env:VAR}` for Gemini CLI, Pi and Cline. Gemini documents `$VAR` and `${VAR}` and says an undefined variable "resolves to an empty string"; Pi documents `${VAR}` only; Cline's page shows no expansion at all. VS Code's MCP pages do not mention `${env:...}` (the general VS Code variable reference does, for launch and task files). If the forms are not honoured, the server is started with an empty or literal token and fails with 401 without a clear message. This is a functional defect that predates this task. It has not been observed. | Gemini MCP and configuration pages [V]; Pi `mcp.md` [V]; Cline MCP page [V]; VS Code pages [V]; behaviour [U] |
| F-4 | Every stdio MCP server the client starts inherits the exported variable by default (`filesystem`, `git`, `github`, `supabase`, `toolradar`, `brave`, `playwright`, `memory`...). A compromised package among the single-maintainer pins (K-13) receives the GitLab token. | Claude Code env-vars page (`CLAUDE_CODE_MCP_ALLOWLIST_ENV` exists because of this) [V]; behaviour of other clients [U] |
| F-5 | The `gitlab-api-push-fallback` skill uses `glab` (its own stored credential), not the MCP token. The maintainer's `glab` token and git credential helper are a second, usually more powerful credential on the same disk (AP-4). | skill text; `~/.config/glab-cli` was not read |
| F-6 | Both roles that were narrowed in T660 are **writers**. A token that cannot write issues makes them fail. | `qa-engineer.md`, `scrum-master.md` tool lines |

### 2.3 Attacker paths (a prompt-injected or misbehaving agent that holds a shell)

| ID | Path | Notes |
|---|---|---|
| AP-1 | Read the variable from the shell environment (`env`, `printenv`, `echo $VAR`) | The path SEC-T660-01 names |
| AP-2 | Read `/proc/<pid>/environ` of the client or of the MCP server (same user), `ps eww` on macOS | Persists when the token is passed to the server by environment |
| AP-3 | Read the secret at rest: the profile file that holds the `export`, a token file, a settings file, shell history, a keychain query run from the shell (`secret-tool`, `security`) | Persists for any secret that the same user can read |
| AP-4 | Read another credential of the same user: `~/.config/glab-cli`, `~/.git-credentials`, `~/.netrc`, an SSH key, `GITHUB_PERSONAL_ACCESS_TOKEN` | Outside the harness; often more powerful than the MCP token |
| AP-5 | Use a token from AP-1 to AP-4 over the network (`curl` to GitLab) | Needs a token; blocked only by network isolation (Claude Code sandbox allowlist) |
| AP-6 | Ask the MCP server itself for a tool outside the role's list | Bounded by the client's tool-list enforcement (Claude Code, Copilot, Pi when the file reaches `pi --tools`); **not bounded on Opencode and Gemini CLI** (K-15) |

Who holds a shell: not only `qa-engineer`. Every agent with `execute` can reach AP-1 to AP-5, including agents that hold no GitLab tool at all (`backend-developer`, `frontend-developer` and others). A per-role token inside one environment is therefore not possible. The token that is reachable from the shell must be weak enough for *every* shell-holding agent, or must not be reachable.

## 3. What the tools need (scope, role, fine-grained permission)

Tool families come from the 20 and 24 names in `qa-engineer.md` and `scrum-master.md` and from the sets T666 and T667 will define. GitLab facts: [V] GitLab scopes, permissions and fine-grained REST pages (section 12).

| Tool family (examples) | REST effect | Legacy scope | Minimum role (GitLab permissions page) | Fine-grained permission rows (REST page) |
|---|---|---|---|---|
| Read issues, notes, labels, milestones, issue links, members | GET | `read_api` | Guest (members: Maintainer row not confirmed) | Issue Read, Issue note Read, Label Read, Milestone Read, Issue link Read, Member Read |
| Create issue, create note, create issue link | POST | `api` | Guest | Issue Create, Issue note Create, Issue link Create |
| Update issue (labels, assignee, state), create/update label, create/edit milestone | POST, PUT | `api` | Planner (edit issues); labels and milestones rows not confirmed | Issue Update, Label Create/Update, Milestone Create/Update |
| Read merge requests, pipelines, jobs, job traces, test reports | GET | `read_api` | Guest (pipelines and jobs need project pipeline visibility) | Merge request Read, Pipeline Read, Job Read (trace is a Job Read row) |
| Create merge request, create branch, create tag | POST | `api` | Developer | Merge request Create, Branch Create, Repository tag Create |
| Push files / create commit, push to a protected branch | POST | `api` | Developer (unprotected), Maintainer (protected) | Repository (file write) Create, Commit Create |
| Create release, protect tags | POST | `api` | Maintainer ("Manage releases") | Release create row **not found** in the chunk read **[U]** |
| Merge a merge request | PUT | `api` | **Not found on the permissions page [U]**; depends on the protected-branch "allowed to merge" setting | Merge request Merge |
| Trigger, retry, cancel pipeline | POST | `api` | Developer | Pipeline Create/Update, Job Run |
| Delete anything, unprotect branch | DELETE | `api` | varies | Delete rows |

Consequences for the design:

- **No read-only token serves a writer.** The legacy scope list has no scope between `read_api` and `api` that writes issues. The legacy way to limit power is the **role**; the fine-grained way is the **permission rows**.
- **The role of the credential sets the ceiling**, not the scope. An `api` token of a Reporter-level or Planner-level identity cannot push, create branches or merge; the same scope on a Maintainer account can do all of it.
- **After T666 and T667, no agent should need merge, delete, branch/tag/release creation or pipeline trigger** (plan-123 states these exclusions for the orchestrators; the merge exclusion for `devops-engineer` and `release-manager` is open question 3 of the plan). If that holds, one shared token at **Planner or Reporter level plus MR-read and pipeline-read** covers qa-engineer, scrum-master and the orchestrators; `devops-engineer`, `release-manager` and `poc-devops-engineer` raise the ceiling to **Developer** only if they keep `create_merge_request` or `create_branch`. Any tool that needs Maintainer (`create_release`, protected-branch push) pulls the shared token up to Maintainer; **keep those out of the agent sets** so the shared token stays at Developer or below. This is an input for T666 and T667, not a decision made here.
- **Server-side branch protection is a second line outside the harness**: protected `main` and `develop` with merge restricted to Maintainers make a Developer-level token unable to merge or push there. Adopters without that protection get no such line; the docs must say so.

## 4. GitLab credential types today

| Type | Scope control | Role control | Tier / availability | Expiry | Source |
|---|---|---|---|---|---|
| Legacy personal access token | scopes `api`, `read_api`, ... | the owner's role | all tiers | default 365 days; maximum 365 days by default, 400 days only behind a disabled flag; administrators can change the maximum (17.6 and later); no-expiry only if an administrator turns the requirement off | [V] |
| Project or group access token | same scopes | a role chosen at creation; a bot user is created; cannot reach other projects | **GitLab.com: Premium or Ultimate**; self-managed: any licence; creation can be restricted by the top-level group | as above | [V] project page; group page [U] |
| Fine-grained personal access token | per-resource permission rows (create, read, update, delete) on a Group and project, User or Global boundary; reach: personal projects, all your projects and groups, or "only the projects and groups you select" (blog) | the owner's role still applies (two checks: token permission and owner right) | **GA in GitLab 19.2**, beta since 18.10; Free, Premium, Ultimate; `GET /personal_access_tokens/self` returns `granular_scopes` since 19.5 | as above | [V] |
| Service account | not researched | not researched | not researched | | **[U]** |
| OAuth (the pinned server supports it) | `api` or `read_api` | the user's role | not evaluated | | server README [V]; not evaluated here |

Not established: whether the pinned server's 44 tool calls all succeed with a fine-grained token (the server may use GraphQL or endpoints with partial fine-grained coverage; the blog says GraphQL coverage is partial) **[U]**; whether the server sends the token in a header a fine-grained token accepts **[U]**; whether individual projects can be selected in the creation form (blog says yes, docs page does not describe the options) **[U]**; the exact role list of a project access token **[U]**.

## 5. Client facts

All rows are documentation or source statements [V] unless marked [U]. None was run. "Token reaches the shell" means: if the adopter follows the shipped instruction and exports the variable, the client's own shell tool inherits it.

| Client | How the generated config references the token | Native way to supply a secret without exporting it | Token reaches the agent's shell today | Sources |
|---|---|---|---|---|
| **Claude Code** | `${VAR}` and `${VAR:-default}` are expanded in `command`, `args`, `env`, `url`, `headers` from Claude Code's own environment [V]. Unset without a default gives literal text and a warning [V]. | No `envFile`: the MCP page does not mention it [V] (the last 22,928 characters of the page were not read [U]). `headersHelper` is for HTTP and SSE servers only, not stdio [V]. The settings `env` block copies values into Claude Code's own environment "as written" [V], so it is not a mitigation and also writes the secret into a settings file. | Yes. `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` "strips credentials from the environments of the subprocesses Claude Code starts, such as Bash commands, hooks, and stdio MCP servers", recognising a credential by variable name (`...TOKEN` qualifies) or value shape; the Claude Code process keeps the credentials; on Linux the scrub also runs Bash in an isolated PID namespace so subprocesses cannot read host process environments through `/proc` [V]. Whether the **explicitly configured** MCP `env` entry survives the scrub is not stated **[U]**. `CLAUDE_CODE_MCP_ALLOWLIST_ENV=1` starts stdio servers with "only a safe baseline environment plus the server's configured `env`" (the baseline is not defined **[U]**; it may affect `npx`, `uvx`, `docker`). The Bash sandbox (macOS, Linux, WSL2) enforces `sandbox.filesystem.denyRead` and a network allowlist for shell commands; "Claude's file tools, MCP servers, and hooks run outside it", so file tools need `Read` deny rules [V]. The unsandboxed retry can be turned off (`allowUnsandboxedCommands: false`) [V]. | code.claude.com mcp, env-vars, sandboxing, settings |
| **GitHub Copilot / VS Code** | `${env:VAR}` is emitted. VS Code's MCP pages do not mention `${env:...}` [V]; it is documented in the general variable reference for launch and task files [V]. For `mcp.json` **[U]**. | `inputs` entry `{ "type": "promptString", "id": ..., "password": true }` referenced as `${input:id}` in `env` or `headers`; VS Code "prompts you for the value when the server starts for the first time" and "securely stored for subsequent use" (storage detail **[U]**). `envFile` for stdio servers in workspace and profile `mcp.json` (not for the workspace-root `.mcp.json`) [V]. `sandboxEnabled` for local stdio servers on macOS and Linux [V]. For Copilot harness sessions, configurations "that require interactive input, such as `${input:...}`" are not forwarded [V]. | Yes if exported before VS Code starts (the integrated terminal and the agent terminal inherit). With `${input:...}` there is no export. | code.visualstudio.com mcp-configuration, mcp-servers |
| **Opencode** | `{env:VAR}`; an unset variable becomes an empty string [V]. | `{file:path}` substitutes the file's contents, relative to the config file or absolute (`/`, `~`) [V]. The MCP page shows `{env:}` only in remote examples; use in a local server's `environment` is **[U]**. Opencode has no secret store. | Yes. | opencode.ai config and mcp-servers pages |
| **Gemini CLI** | Generated `${env:VAR}`. Documented forms: `$VAR_NAME`, `${VAR_NAME}`, `${VAR_NAME:-DEFAULT_VALUE}`, `%VAR_NAME%` (Windows) [V]. `${env:VAR}` is not documented (F-3). Whether Gemini resolves it **[U]**. | No `envFile` for servers [V]. The CLI redacts variables named `*TOKEN*`, `*SECRET*`, `*PASSWORD*`, `*KEY*`, `*AUTH*`, `*CREDENTIAL*` from the **inherited** environment of an MCP server; variables declared in the server's `env` are not redacted [V]. `security.environmentVariableRedaction` exists (default `false`); which processes it covers (shell tool) **[U]**. The product page says Gemini CLI "was replaced by Antigravity CLI on June 18, 2026" (viability of this platform is outside this task) [V]. | Yes (shell tool inherits unless redaction is on **[U]**). | geminicli.com mcp-server, reference/configuration, cli/enterprise |
| **Pi** | Generated `${env:VAR}`. Pi's `mcp.md` shows `${VAR}` only [V]; the generated form **[U]**. Pi's MCP support is native on the main branch; older versions may lack it (existing wiki note). | `env` values can be `!command`, "which must make up the whole value": the token can come from `!secret-tool lookup ...` without any export [V]. User-level credentials belong in `~/.pi/agent/mcp.json`; the project file `.pi/mcp.json` is read only after trust [V]. Inheritance of the parent environment is not stated **[U]**. | Yes. | github.com/earendil-works/pi `docs/mcp.md` (via fetch summary) |
| **Cline** | Generated `${env:VAR}`. Cline's page shows only literal values and does not say whether expansion works [V]. | The real file is global (`~/.cline/data/settings/cline_mcp_settings.json`, override `CLINE_MCP_SETTINGS_PATH`; the IDE has its own path) [V]. The page advises "Store secrets in environment variables" [V]. No agent files exist, so there is no per-role tool list. | Yes. | docs.cline.bot mcp page |
| **Pinned server** `@zereight/mcp-gitlab@2.2.5` | n/a | `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` exists in the README and in `config.js`/`personal-access-token.js` of 2.2.5. Precedence: `--token`, then a **non-empty** `GITLAB_PERSONAL_ACCESS_TOKEN`, then the file; the file is read once at module load with `readFileSync`, trimmed; an empty file throws; **no mode, owner or symlink check**; a warning is printed when a file path is set and an inline token wins [V]. There is no token-script, keychain or `GITLAB_TOKEN` source [V]. Behaviour with an **empty string** in `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` **[U]**. Operator controls: `GITLAB_PERMISSION_MODE` (`readonly`, `modify`, `full`; `modify` blocks every delete tool and teardown tools such as `cancel_pipeline`, `stop_environment`, `unprotect_branch`), `GITLAB_TOOLS`, `GITLAB_TOOLSETS`, `GITLAB_DENIED_TOOLS_REGEX`, `GITLAB_ALLOWED_PROJECT_IDS` (checked only for `/projects/:id` paths of `gitlab_api_request`) [V]. | | mcp-gitlab README and unpkg 2.2.5 |

## 6. Options

### Option A: least-privilege token only

- **What**: documentation and a check. The token is a dedicated credential for the harness (never the maintainer's own `glab` token): a fine-grained PAT, else a role-limited project or group access token, else an `api` PAT of a dedicated low-role user; expiry 30 to 90 days; project selection; a check script that reads `GET /personal_access_tokens/self` and `GET /user` and warns on over-broad scope, long expiry or a high role. Fix F-1.
- **Mechanism**: capping the *power* of the credential, not hiding it. Branch protection on the GitLab side is a second cap.
- **Gain against SEC-T660-01**: removes the premise "the shell can merge and push" for any shell-holding agent on any client, including Opencode and Gemini CLI where the tool list is not enforced (K-15). The damage of AP-1 to AP-5 becomes the token's power, which for a Planner or Reporter-level identity equals the issue and note writes the roles already hold.
- **Remains open**: AP-1 to AP-5 stay possible; only their impact is capped. The cap must cover the union of what all seven roles need; if T666 or T667 keeps `create_merge_request` or branch creation, the ceiling is Developer. AP-4 (a stronger `glab` token) is untouched.
- **Adopter cost**: create one token, possibly a second GitLab identity; on GitLab.com a project access token needs Premium or Ultimate, a fine-grained PAT does not (GitLab 19.2 or later on self-managed). Rotation duty.
- **T665 work**: documentation, the check script (optional, DEC-T664-5), tests for the documentation claims. No generator change.
- **`fromEnv` compatibility**: complete (no change).
- **Migration**: create the new token, change the exported value, revoke the old one. `--update` changes nothing.

### Option B: separate tokens or server entries per use

- **What**: a second server entry (for example `gitlab-issues`) with an issue-writer token for `qa-engineer` and `scrum-master`, and the existing `gitlab` entry with a stronger token for the roles that need it.
- **Mechanism**: the stdio server and its environment are per client configuration, shared by every subagent. Per-role credentials are only possible by giving the roles different **server names**, so the agents' tool lines (`mcp__gitlab-issues__create_issue`), the per-platform tool-name mapping, the pins and `GitLabGrantSetTests` all change.
- **Gain**: nothing on its own. If both tokens are exported, a `qa-engineer` shell sees both (AP-1). B only has value when the stronger token is also unreachable from the shell, which is option C for that token. On Opencode and Gemini CLI any agent can call both servers' tools anyway.
- **Adopter cost**: two tokens, two approvals of project-scoped servers, a larger config; the user's own sessions must pick the right server.
- **T665 work**: large and in conflict with T666 and T667, which edit the same tool lists and the same grant-set tests.
- **`fromEnv` compatibility**: a second `fromEnv` variable; additive.
- **Migration**: new server key in every config; agent files change; the old key must be pruned by hand or by provenance.
- **Verdict**: deferred. Revisit after T666 and T667 if the union of the role sets still needs more than the Planner or Reporter ceiling for most roles.

### Option C: keep the token out of the agents' shell environment

#### C1: native token file (`GITLAB_PERSONAL_ACCESS_TOKEN_FILE`)

- **Mechanism**: the generated entry passes a *path* in `env`; the server reads the file once at startup. The secret is in no process environment: closes AP-1 and AP-2 for the token, and removes it from shell history and from env dumps in logs.
- **Remains open**: AP-3 (the file is readable by the same user; the server does no mode check), AP-4. Adds a gotcha: inline beats file (F-2). A file inside the project directory is readable by the extended `filesystem` server; the file must live outside any project.
- **Adopter cost**: create a 0600 file outside the project; export or set the path (not a secret); remove the old export.
- **T665 work**: small: one more `env` entry, an optional `default` field in the `fromEnv` spec (rendered as `${VAR:-}` on Claude Code only), documentation, tests.
- **`fromEnv` compatibility**: additive. An optional `default` key; existing specs render unchanged.
- **Migration**: automatic for the config (`--update` rewrites the `gitlab` entry; generated values win); the adopter opts in. A stale `GITLAB_PERSONAL_ACCESS_TOKEN` export would still win over the file and only produces the server's warning.

#### C2: client-native mechanisms

- **Claude Code**: `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`; on Linux it also isolates the PID namespace (closes AP-2 for Bash). Together with C1 and `sandbox.filesystem.denyRead` for the token file (and `~/.config/glab-cli`, `~/.git-credentials`) plus `Read(...)` deny rules for the file tools, and `allowUnsandboxedCommands: false`, this closes AP-1 to AP-4 for the Bash tool on Claude Code. Network isolation (`sandbox.network.allowedDomains`) closes AP-5 where GitLab is not allowed. The MCP server and the file tools run outside the sandbox, so the server still gets the token. These are client settings that the installer never writes; they would be documentation only. Unverified: the effect of the scrub on the configured MCP `env` entry; macOS behaviour of `ps eww` (the PID namespace is documented for Linux only).
- **Copilot / VS Code**: `inputs` with `password: true`. Closes AP-1 for the Copilot agent's terminal when the adopter does not also export the variable. Stored value location **[U]**. Not usable together with the `${env:...}` placeholder in the same entry, so it needs a generator mode or a manual edit that `--update` reverts (generated values win).
- **Pi**: `!command` values (for example a keychain lookup) never export a secret. The same-user shell can run the same command (AP-3). Pi's agent restrictions are weak (K-15).
- **Opencode**: `{file:...}` is a file mode of the same strength as C1 (AP-3 open); Opencode offers no scrub or sandbox in the facts researched **[U]**.
- **Gemini CLI**: no secret input; redaction applies to the *inherited* environment of servers, not to the agent's shell (**[U]**); `$VAR` forms only.
- **Cline**: the global settings file; no mechanism.
- **Adopter cost**: per client, one-time; Claude Code settings are the adopter's own.
- **Generator work**: none for Claude Code and Pi (documentation); a generator mode for Copilot `inputs` is larger and is **not** recommended in T665.

#### C3: launcher wrapper

- **What**: a small POSIX script installed with the project that reads the token from a file or a keychain command and `exec`s `npx -y @zereight/mcp-gitlab@2.2.5` with the token set only in the server's environment. The client config then starts the script (`command`), not `npx`, and the client's own environment never holds the token.
- **Gain over C1**: a keychain source (no token at rest in a plain file) and one rendering for every client. On macOS the Keychain asks the user before an unknown process reads an item (platform behaviour **[U]**); on Linux a libsecret item is readable by any same-user process once the keyring is unlocked (**[U]**), so the shell can run the same lookup (AP-3).
- **Cost**: a new executable that handles a credential and needs its own review, tests and Security Engineer review; POSIX only (Windows is not verified anywhere in the repository); it changes the pinned launcher form that `test_mcp_package_pins.py` asserts (`npx -y @zereight/mcp-gitlab@2.2.5`) and the K-13 pin review; the server's `PATH`, `HOME` and `npm` cache handling must be preserved; every adopter inherits the script's bugs. The server's own `_FILE` source already provides the file case without an executable.
- **Verdict**: declined for T665. Offer it again only if the user wants keychain sources on all clients.

### Option D: combination (recommended)

R1 (A) + R2 (C1) + R3 (C2: Claude Code posture, Pi `!command`, Copilot `inputs` as documentation) + the optional server-side controls of DEC-T664-3. B and C3 are deferred and declined respectively. See section 7.

### Comparison

| Option | AP-1 env | AP-2 /proc | AP-3 at rest | AP-4 other creds | AP-5 network use | AP-6 tool bypass | Impact of a stolen token | Adopter cost | T665 size |
|---|---|---|---|---|---|---|---|---|---|
| A least privilege | open | open | open | open | open | unchanged | **capped to token power** | token + role/identity | S (docs, check script) |
| B split | open (both tokens exported) | open | open | open | open | unchanged | capped only for the weak token | high | L, conflicts with T666/T667 |
| C1 token file | **closed** | **closed** (env) | open | open | open | unchanged | unchanged | medium | S/M |
| C2 Claude Code posture (scrub + sandbox + file) | **closed** (Bash) | **closed on Linux**, macOS [U] | **closed for sandboxed Bash and denied Read**; open for unsandboxed paths | closed only for the denied paths | closed where GitLab is not on the allowlist | unchanged | unchanged | medium, client settings | docs only |
| C2 Copilot `inputs`, Pi `!command` | closed (token never exported) | partly [U] | open (same-user lookup) | open | open | unchanged | unchanged | medium | docs only |
| C3 launcher | closed | closed (child env only) | open (file) or partly (macOS keychain) | open | open | unchanged | unchanged | high | M/L, new reviewed executable |
| **D = A + C1 + C2 docs** | closed on Claude Code/Linux under the posture | same | closed for sandboxed Bash only | open elsewhere | as C2 | unchanged | **capped** | medium | M |

"Closed" means a documented mechanism exists; every Claude Code cell depends on a live test that has not been run.

## 7. Recommendation

### 7.1 Option D, composed of

- **R1. Least-privilege token (mandatory, all clients).**
  - The docs name the token a dedicated harness credential; never the `glab` or git token of the maintainer.
  - Preference order: (1) fine-grained PAT limited to the project(s), with exactly the permission rows of section 3 for the shipped role sets (Free tier, GitLab 19.2 or later; conditional on a live compatibility test, section 8.4); (2) a project or group access token with role Planner or Reporter and scope `api` (Premium or Ultimate on GitLab.com), Developer only if the final role sets create branches or merge requests; (3) an `api`-scope legacy PAT of a dedicated user whose role in the project is Planner, Reporter or Developer. Never Maintainer or Owner; never a token with `read_user`, `write_repository` or `admin` scopes for this purpose.
  - Expiry at most 90 days, rotation noted in the pin-bump checklist.
  - Correct F-1 in `PREREQUISITES.md` and the wiki (one scope table from section 3).
  - Branch protection advice for adopters: protected `main` and `develop`, merge restricted to Maintainers.
- **R2. Token file mode, additive and opt-in.** `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` is added to the `gitlab` entry as a non-secret `fromEnv`; both gitlab variables get `default: ""` rendered as `${VAR:-}` for Claude Code (F-2); the other formats render as today. The documented default for new installs leads with the file mode; the environment mode remains supported (DEC-T664-2).
- **R3. Client posture, documented and client-owned.**
  - Claude Code: `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`, the Bash sandbox with `denyRead` for the token file and for `~/.config/glab-cli` and `~/.git-credentials`, `Read(...)` deny rules for the same paths, `allowUnsandboxedCommands: false`, and optionally `CLAUDE_CODE_MCP_ALLOWLIST_ENV=1` to keep the token from the sibling MCP servers (F-4). Each statement is labelled with what is unverified until the live test (8.4) has run.
  - Copilot / VS Code: the `inputs` form as a manual alternative, with the `--update` caveat, no generator mode.
  - Pi: the `!command` form.
  - Opencode, Gemini CLI, Cline: file mode (Opencode `{file:}` where verified) or nothing; state plainly that there is no mechanism and that R1 is the only control there.
- **R4 (decision DEC-T664-3, optional).** Server-side limits in the shipped entry: `GITLAB_PERMISSION_MODE=modify` and/or a `GITLAB_DENIED_TOOLS_REGEX`. These are enforced by the server on every client, including Opencode and Gemini CLI where tool lists are not (K-15, SEC-T660-04). They do **not** stop AP-5 (a shell calling the API with a token). They also bind the user's own session in that client.

### 7.2 Why not the others

- **B** costs a rewrite of the grant lists that T666 and T667 are about to redo, and gives nothing unless the stronger token is also unreachable.
- **C3** adds a credential-handling executable for a gain that the server's own `_FILE` mode already mostly provides.
- **A alone** is necessary but leaves AP-1 and AP-2 open everywhere; **C alone** leaves a stolen token as powerful as the maintainer made it.

### 7.3 What this does and does not close (grades need the Security Engineer review)

| Statement | Mechanism | Status |
|---|---|---|
| A stolen token is no more powerful than the granted tool surface | R1 (role/permission ceiling) | Documented control; the ceiling depends on the T666/T667 sets; **not closed**, because tokens of arbitrary power still work and the check script only warns |
| The token is not in the shell environment or `/proc` on Claude Code (Linux) | R2 + scrub (PID namespace) | Mechanism documented by the vendor; **unconfirmed until a live test**; macOS and every other client **not closed** |
| The token file and the `glab` credential are not readable by an agent's shell | Claude Code sandbox `denyRead` + `Read` deny rules | Mechanism documented by the vendor; unconfirmed until a live test; **not available** on Opencode, Gemini CLI, Pi, Cline and Copilot |
| Another credential of the same user (AP-4) | none in the harness | **Open on every client**; the only closures are an isolated user, container or VM with only the scoped credential, outside this task |
| Tool-list bypass on Opencode and Gemini CLI (AP-6) | R4 server-side controls, T663 for Opencode | Partial; T663 and R4 only |

Proposed disposition of SEC-T660-01 after T665 (for the Security Engineer to grade): the environment-path component is mitigated by R1 to R3 where a mechanism exists; the residual (AP-3, AP-4, and every client without a mechanism) is documented and requires the user's explicit acceptance (DEC-T664-1). It is not "closed".

## 8. Scope of T665 under the recommendation

### 8.1 In scope (devops-engineer; technical-writer for the two documents)

1. **`implementation/knowledge/mcp/servers.yaml`**: add `GITLAB_PERSONAL_ACCESS_TOKEN_FILE: { fromEnv: GITLAB_PERSONAL_ACCESS_TOKEN_FILE }` (not `secret`: it holds a path) and `default: ""` on both gitlab credential entries. Comments only; the pin policy and the `APPROVED_NPX_PINS` entry for `@zereight/mcp-gitlab@2.2.5` do not change.
2. **`implementation/scripts/sync.mjs`** (`mapTemplatedValue`): an optional `default` key; for the `claude-code` format render `${VAR:-default}` (documented syntax); every other format renders as today. The empty-default case on Claude Code is unverified (section 5) and must be checked against Claude Code behaviour or documented as unverified before it is relied on. Regenerate all projections; declare root drift in `tests/_baselines/root-install-drift.json`; do not refresh the root install.
3. **Placeholder-form check (F-3)**: read the vendor source or documentation for Gemini CLI, Pi, Cline and VS Code and record which placeholder forms each honours. If a platform does not honour `${env:VAR}`, change its `template` string in `emitMcp` to the documented form and say so in the release notes. This is a functional fix, separate from the security change, and may be split into its own task at the orchestrator's choice. Do not touch the Cursor format (removed by T662).
4. **Merge behaviour**: confirm with `scripts/merge-mcp-json.py` and a test that `--update` rewrites the gitlab `env` (generated wins), keeps user-added keys, and neither drops nor duplicates the new variable; confirm the stale-key case (a user who sets a literal token inline in the file is told by documentation, not by code).
5. **Documentation** (`implementation/PREREQUISITES.md`, `docs/wiki/mcp-servers.md`, K-16 wording only if it is edited anyway): one scope/role/permission table (section 3), the credential-type order (section 7.1 R1), the token-file steps (`umask 077`, outside any project, not in the `filesystem` server's root, path variable), the per-client posture (section 5 facts with their [V]/[U] labels), the AP-3 and AP-4 residual stated in plain words, the operator controls of SEC-T660-03 (this overlaps T674; coordinate so the text appears once), the migration steps (section 9).
6. **Check script (if DEC-T664-5 says yes)**: `scripts/check-gitlab-token.py`, standard library only; reads the token from the file or the environment variable named by the user, never prints it, never logs argv; HTTPS only with a host allowlist from `GITLAB_API_URL`; calls `GET /personal_access_tokens/self` and `GET /user`; reports scopes (or `granular_scopes`), days to expiry, whether the owner is a bot; exit codes for "too broad", "expires after 90 days", "unreachable". Tests use a local fake HTTP server and a synthetic string that is not shaped like a GitLab token.
7. **Tests**: platform-projection tests for the new variable and default in all six formats; a test that no generated config contains a token-shaped literal; the pins test for the unchanged launcher; documentation assertions anchored to the paragraph they protect (SEC-T658-06 style) for the scope table and the residual wording; the check script tests; merge tests.

### 8.2 Out of scope

Option B (second server entry), the launcher script (C3), a Copilot `inputs` generator mode, any write to client settings (`.claude/settings*.json`, `.vscode/mcp.json` of the user), the named tool sets (T666, T667), the Opencode per-agent denies (T663), the Cursor format, a live run with a real token by an agent.

### 8.3 Order and dependencies

- Start after the user decides (DEC-T664-1 to -5).
- **Same-file conflicts**: `emitMcp`/`mapTemplatedValue` are edited by T662 (Cursor removal) and refactored by T677; `servers.yaml` and the grant tests by T666 and T667. Recommended order: T662, then T665, with T677 explicitly dependent on T665 as well as T672 and T675 (the plan names only the last two). T665 must not wait for T666 and T667 to ship, but the permission table in the documentation must be re-checked against their final tool sets before the release (a one-line gate in the T667 acceptance).
- Gates: all gates listed in `task-T664.md` section 3 for `implementation/`, `scripts/` and `tests/`; the Security Engineer review is mandatory (a new credential-handling script and a changed credential path).

### 8.4 Live verification that no agent can do (needs the user, DEC-T664-4)

An agent cannot hold or use a token, so these checks need the user or an authorised human-run step with a throwaway token on a scratch project:

1. The pinned server with a **fine-grained PAT** carrying only the section 3 rows: run the 20 `qa-engineer` and 24 `scrum-master` tools (a table of pass/fail per tool).
2. Claude Code with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`: the gitlab server still authenticates (explicit `env` survives the scrub); a Bash command cannot read the variable, `/proc/<pid>/environ` or the token file under `denyRead`.
3. `${GITLAB_PERSONAL_ACCESS_TOKEN:-}` with an empty value and a set `GITLAB_PERSONAL_ACCESS_TOKEN_FILE`: the file is used; and the reverse (the variable set, no file).
4. Whether Gemini CLI, Pi, Cline and VS Code expand `${env:VAR}` (F-3).
5. Whether a Developer-level token can merge into a protected `develop`/`main` when "allowed to merge" is Maintainers only.

## 9. Migration of existing v8.0.0 installs

1. `install.sh --update` rewrites the `gitlab` entry: the new `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` entry appears; on Claude Code the placeholder gains `:-`. The variable the adopter already exports keeps working in the same way. Claude Code prompts again to approve the changed project-scoped server (M-2).
2. Nothing breaks if the adopter does nothing. The documented risk (K-16) stays as it is.
3. To adopt the recommendation: create the scoped token (R1); write it to a 0600 file outside any project; export the **path** (or set it in the client's own settings); **remove the old export from the shell profile**, because an inline value beats the file and the server only warns; run the check script and `claude mcp list` (or the client's equivalent); **revoke the old broad token**, because it has sat in a profile file and in process environments.
4. Existing installs and the repository root keep the old rendering until the next `--update` or `--projections-only` refresh, as in D-1 of the T660 review.
5. Rollback to v8.0.0 files restores the old entry; the token file is simply not used.

## 10. Decisions the user must make

Each decision lists options, my recommendation and the consequence. All are PENDING.

- **DEC-T664-1. Residual risk after T665.** Options: (a) accept that SEC-T660-01 is mitigated, not closed, and that AP-3 and AP-4 stay open on every client and AP-1/AP-2 on every client except Claude Code under the posture; (b) require more (a launcher with a keychain, an isolated user or a container recipe, a separate MCP process under another OS user), at a cost the harness cannot carry in this sprint. **Recommendation: (a)**, with the Security Engineer grading the residual in the T665 review. Consequence of (b): a new task and probably a MAJOR change in how the MCP server is started.
- **DEC-T664-2. Default mode.** Options: (a) env mode stays the documented default; file mode is documented as a hardening option; (b) file mode is the documented default and env mode is the fallback; (c) file mode only (breaking). **Recommendation: (b)** for new installs with env mode still supported, no breaking change. (c) is only reasonable if the next release is already a MAJOR for the Cursor removal and you want a clean break.
- **DEC-T664-3. Server-side limits in the shipped entry.** Options: (a) none (T660 status quo); (b) ship `GITLAB_PERMISSION_MODE=modify` (blocks all delete and teardown tools server-side for every client and for your own session); (c) also a `GITLAB_DENIED_TOOLS_REGEX` for merge, push and release tools once T666 and T667 are done. **Recommendation: (b) now, (c) after T667, provided you do not use MCP delete/cancel tools in your own session** (please state whether you do; your own sessions merge through `glab`/the API according to the project rules). This is the only enforced control on Opencode and Gemini CLI. It does not address AP-5.
- **DEC-T664-4. Live verification.** The five checks in 8.4 need a throwaway token on a scratch project, run by you or in a session you authorise; agents cannot do it. Options: (a) you run them before the T665 merge; (b) T665 ships the documentation with every unverified statement labelled as such and the checks are tracked debt. **Recommendation: (a)** for checks 1 to 3 (they decide whether the fine-grained PAT and the scrub can be recommended at all), (b) for the rest.
- **DEC-T664-5. Check script.** Options: (a) in T665; (b) documentation only. **Recommendation: (a).** It turns "use a least-privilege token" from advice into a check; it is small, stdlib only, and needs the Security Engineer review anyway.
- **DEC-T664-6. Token type order in the docs.** Whether the project may lead with the fine-grained PAT (needs GitLab 19.2 or later; Free tier) or must lead with the project access token (stable, Premium/Ultimate on GitLab.com). **Recommendation: lead with the fine-grained PAT only if check 1 of 8.4 passes; otherwise lead with a Reporter/Developer project or group token and list the fine-grained PAT as "pending verification".**

Decisions I have made and ask you to ratify by approving this artifact: B is deferred; C3 is declined; no Copilot `inputs` generator mode; Cursor is not handled.

## 11. Not verified

- No live run of any client or the pinned server; every [V] fact is documentation or source text read through a fetch tool, whose summarisation can be wrong. Package source for 2.2.5 was read from unpkg (`config.js`, `personal-access-token.js`); the integrity hash was not compared to the pin.
- Claude Code: the effect of `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` on explicitly configured MCP `env` entries; the empty default `${VAR:-}`; the "safe baseline" of `CLAUDE_CODE_MCP_ALLOWLIST_ENV`; whether the settings `env` block reaches subagents differently from the main session (both are the same process by the text read, not tested); the last 22,928 characters of the MCP page; macOS behaviour of `ps eww`; whether SCRUB can be set from a settings `env` block (the page says to set it in the environment that starts the client). The user's local settings were not read.
- Copilot: `${env:VAR}` in `mcp.json`; where `inputs` values are stored; the Copilot agent terminal's environment inheritance.
- Opencode: `{file:}` and `{env:}` inside a local server's `environment`; environment inheritance of local MCP servers; Opencode's own sandbox or read-deny options.
- Gemini CLI: `${env:VAR}` resolution (the source file path tried returned 404, so the resolver code was not read); the scope of `security.environmentVariableRedaction`; the Antigravity CLI notice and its consequence for this platform.
- Pi and Cline: `${env:VAR}`; inheritance of the parent environment; Pi was read from a repository documentation file through a fetch summary, not from a release.
- GitLab: the role list of project and group access tokens; the merge permission role; labels and milestones minimum roles; fine-grained project selection UI; fine-grained coverage of GraphQL endpoints the server may use; the release-create permission row; service accounts; GitLab.com's current version (GA is documented for 19.2).
- The contents of `~/.config/glab-cli`, any `.env*` file and the user's local settings were not opened; the existence and privilege of the maintainer's `glab` token is an assumption from F-5.

## 12. Sources

- GitLab: personal access tokens https://docs.gitlab.com/user/profile/personal_access_tokens/ ; scopes https://docs.gitlab.com/security/tokens/access_token_scopes/ ; project access tokens https://docs.gitlab.com/user/project/settings/project_access_tokens/ ; roles and permissions https://docs.gitlab.com/user/permissions/ ; fine-grained tokens https://docs.gitlab.com/auth/tokens/fine_grained_access_tokens/ ; fine-grained REST permissions https://docs.gitlab.com/auth/tokens/fine_grained_access_tokens_rest/ ; blog https://about.gitlab.com/blog/fine-grained-pats/ ; personal access token API (`self`) https://docs.gitlab.com/api/personal_access_tokens/
- Pinned server: https://github.com/zereight/gitlab-mcp ; https://unpkg.com/@zereight/mcp-gitlab@2.2.5/README.md ; https://unpkg.com/@zereight/mcp-gitlab@2.2.5/build/config.js ; https://unpkg.com/@zereight/mcp-gitlab@2.2.5/build/personal-access-token.js
- Claude Code: https://code.claude.com/docs/en/mcp ; https://code.claude.com/docs/en/env-vars ; https://code.claude.com/docs/en/sandboxing ; https://code.claude.com/docs/en/settings ; https://code.claude.com/docs/en/permissions (fetched; the permissions page was not read in the part that covers Read-deny versus Bash)
- VS Code / Copilot: https://code.visualstudio.com/docs/copilot/reference/mcp-configuration ; https://code.visualstudio.com/docs/copilot/customization/mcp-servers ; https://code.visualstudio.com/docs/reference/variables-reference
- Opencode: https://opencode.ai/docs/mcp-servers/ ; https://opencode.ai/docs/config/
- Gemini CLI: https://geminicli.com/docs/tools/mcp-server/ ; https://geminicli.com/docs/reference/configuration/ ; https://geminicli.com/docs/cli/enterprise/
- Pi: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/mcp.md
- Cline: https://docs.cline.bot/mcp/configuring-mcp-servers

## 13. Handoff context package (T665)

- **task_id**: T665 (devops-engineer; technical-writer for `PREREQUISITES.md` and the wiki page; Security Engineer review).
- **definition**: implement the user's decision on this artifact (default: section 8.1 under DEC-T664-1 (a), -2 (b), -3 (b), -5 (a)).
- **constraints**: no token is created, read, printed or used by any agent; no `.env*`, `~/.config/glab-cli`, user `.claude/settings*.json` or `.vscode/mcp.json`; never open `tests/golden/held-out/`; no write to `tests/golden/**`; do not refresh the root install, declare drift; keep the pinned launcher form of `@zereight/mcp-gitlab@2.2.5` and the Cursor format untouched; every unverified statement stays labelled in the docs; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`; no push, no merge, no tag.
- **depends_on**: the user's decision on DEC-T664-1 to -6; T662 (Cursor removal) before merging T665 because of `emitMcp`; T666 and T667 for the final permission table (a re-check, not a start condition). T677 should depend on T665.
- **input_artifacts**: `gitlab-token-handling-design-v1.md` (this file), `security-review-t660-gitlab-grants-v1.md`, `docs/releases/v8.0.0.md` (K-16, M-2, M-8), `implementation/knowledge/mcp/servers.yaml`, `implementation/scripts/sync.mjs`, `scripts/merge-mcp-json.py`, `tests/functional/test_mcp_package_pins.py`, `tests/functional/test_platform_projections.py`.
- **expected_outputs**: the changes of 8.1 with tests; regenerated projections and registry; the root-drift declaration; an updated `PREREQUISITES.md` and wiki page; a Security Engineer review artifact.
- **blocker_policy**: report with type and severity (`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`). A blocker of type `external` (a live check of 8.4 not yet run) is `minor` for the code and `major` for any documentation claim that depends on it; ship the claim labelled unverified rather than stating it as fact.
