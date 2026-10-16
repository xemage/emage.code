# Artifact: mcp-server-denials-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T658 (SEC-T657-01, residual of SEC-T655-01; also SEC-T657-07 and SEC-T657-09). **Owner**: devops-engineer. **Date**: 2026-10-15.
- Based on: security-review-t657-tool-name-mapping-v1.md
- **Also consumed**: `docs/artifacts/mcp-tool-name-mapping-v1.md` (§3, §4: which platforms do not enforce an agent's tool list, and the six excluded tools), `docs/tasks/task-T658.md`. The user's decision of 2026-10-15 (AskUserQuestion, option label): "Implement Opencode deny + Gemini excludeTools first".
- **Prior version**: none (first version). **Rollback**: remove `denyTools` from the `playwright` entry of `implementation/knowledge/mcp/servers.yaml` and regenerate; the generator then emits no `permission` key and no `excludeTools`. Already merged user files keep the denial entries until they are removed by hand (the merge never deletes a user-visible entry, see §5).
- **Method**: `npx ctx7@latest library`/`docs` (Opencode: `/websites/opencode_ai`; Gemini CLI: `/google-gemini/gemini-cli`), the vendors' own pages, and the vendor repositories read at commits (shallow clones, read-only). No platform was run live, so **every row below is documented and source-verified, not observed**.

## 1. Result

Where a platform documents a server-level denial, the generator now emits it from one list: `denyTools` on the `playwright` entry of `servers.yaml`. The list holds exactly the six tools that no agent holds (mapping artifact §4): `browser_run_code_unsafe`, `browser_evaluate`, `browser_file_upload`, `browser_drag`, `browser_drop`, `browser_network_request` (the singular; the granted `browser_network_requests` is a different tool and is not denied). Nothing unverified is shipped: Cursor documents no such mechanism and gets nothing.

## 2. Per-platform result

| Platform | Status | Mechanism (as documented) | Emitted form | File | Sources |
|---|---|---|---|---|---|
| Opencode (`opencode`) | **verified** (documentation and vendor source, two source lines); not observed live | A top-level `permission` key whose name is the registered tool name `<server>_<tool>` and whose value is `"deny"`. Permission keys "are matched as wildcard patterns against the underlying tool name, so the same syntax works for built-ins, custom tools, and MCP tools", for example `"mymcp_*": "deny"` and `"mymcp_search": "ask"` | `"permission": { "playwright_browser_run_code_unsafe": "deny", "playwright_browser_evaluate": "deny", "playwright_browser_file_upload": "deny", "playwright_browser_drag": "deny", "playwright_browser_drop": "deny", "playwright_browser_network_request": "deny" }` | `implementation/.opencode/opencode.json` (the MCP config that `install.sh` merges) | `https://opencode.ai/docs/permissions` (last matching rule wins; "Agent permissions are merged with the global config, and agent rules take precedence"; "Explicit `deny` rules are still enforced" in auto mode); `https://opencode.ai/docs/agents` (the MCP note quoted left); ctx7 `/websites/opencode_ai`. Source `anomalyco/opencode@81200db2a3a8` (identical for these files at the latest release tag `v2.0.29`, `042d0832f5f3`): `packages/core/src/tool/mcp.ts:16-17,52` (permission action is `name(server, tool)`), `packages/core/src/permission.ts:88-93` (`evaluate` = `findLast`), `:158-175` (agent rules then session rules, `denied` checked first), `packages/core/src/config/normalize.ts:179-182` (top-level `permission` becomes ordered rules), `packages/core/src/config/plugin/agent.ts:84-122` (top-level rules are pushed to every agent before the agent's own rules), `packages/core/src/config/discovery.ts` and `config.ts:211-285` (`.opencode/opencode.json` is loaded). Legacy runtime `v1.19.0`: `packages/opencode/src/permission/index.ts:28-33,200`, `agent/agent.ts:138,293`, `session/tools.ts:408`, `mcp/catalog.ts:119` (same order and same tool name) |
| Gemini CLI (`gemini`) | **verified** (documentation and vendor source); not observed live | `excludeTools` (array of strings) on the `mcpServers.<name>` entry of `settings.json`: "List of tool names to exclude from this MCP server. Tools listed here will not be available to the model, even if they are exposed by the server. `excludeTools` takes precedence over `includeTools`." The filter runs while tools are discovered, before they are registered, so a subagent (whose registry is built from the parent registry) never receives an excluded tool | `"mcpServers": { "playwright": { "command": "npx", "args": [...], "excludeTools": ["browser_run_code_unsafe", "browser_evaluate", "browser_file_upload", "browser_drag", "browser_drop", "browser_network_request"] } }` | `implementation/.gemini/settings.json` | `https://geminicli.com/docs/tools/mcp-server/` (the `excludeTools` text and the precedence sentence above); ctx7 `/google-gemini/gemini-cli`. Source `google-gemini/gemini-cli@06d329873703` (v0.64.0 line): `docs/tools/mcp-server.md:179-181`, `docs/reference/configuration.md:2533-2536`, `packages/core/src/tools/mcp-client.ts:2449-2470` (`isEnabled`: `excludeTools.includes(funcDecl.name)` on the name the server reports, not the `mcp_<server>_<tool>` form; exclude wins), `:1318` (called per tool in `discoverTools`), `packages/core/src/agents/local-executor.ts:201-279` (a subagent registers tools only from `parentToolRegistry`, so an undiscovered tool cannot reach it), `packages/cli/src/config/settingsSchema.ts:161-174,3105` (`mcpServers` is `SHALLOW_MERGE`; `excludeTools` is in the server schema), `packages/core/src/tools/mcp-client-manager.ts:352-369` (excludes are unioned when an extension and a user entry meet) |
| Cursor (`cursor`) | **unverified, no mechanism found; nothing emitted** | The mapping artifact (§2) found only a global `mcpAllowlist` in `permissions.json` (server:tool form), no `excludeTools`-like key on a server entry of `mcp.json`, and no per-subagent tool list. This task did not research Cursor again | none | none | `docs/artifacts/mcp-tool-name-mapping-v1.md` §2 (Cursor row). **Cursor stays open: every agent can call every tool of every configured server** |
| Claude Code, GitHub Copilot / VS Code, Pi, Cline | not applicable | Claude Code and Copilot enforce the agent's tool list (mapping artifact §3); Pi enforces it only for agents that list an `mcp__` entry; Cline has no agent files and its subagents get no MCP tools | none | none | `docs/artifacts/mcp-tool-name-mapping-v1.md` §3 |

### 2.1 Opencode: does an explicit deny override the per-agent `x: true` allow?

**No.** The global deny does not beat a later allow for the same name. Read from source (`packages/core/src/permission.ts:88-93`, `config/plugin/agent.ts:84-122`; the legacy runtime `agent/agent.ts:138,293` does the same): the rules of an agent are the built-in defaults, then the top-level `permission` rules, then the agent's own rules, and `evaluate` returns the LAST rule that matches the tool name. So an agent-level rule (`tools: { playwright_browser_evaluate: true }`, which becomes `permission.playwright_browser_evaluate = "allow"`, or a broader `playwright_*: true`, or `"*": true`) written after the global deny wins. The docs say the same ("agent rules take precedence").

What this means here:

- The generated Opencode agent files list only the 18 distinct granted Playwright names; none of the six denied names and no wildcard that would match one. A test (`test_mcp_server_denials.py`) models the evaluation order and asserts that every one of the 28 shipped agents resolves each of the six names to `deny`, that the granted `browser_network_requests` still resolves to `allow` (an exact match: the rule for the singular `browser_network_request` does not match it), and that a built-in agent with no rules of its own is denied.
- A **per-agent `false` (deny) entry is the only form that survives a broader allow written later in the same agent**, but the generator cannot write it into agents it does not own, and it is not needed for the shipped agents: none holds a conflicting allow, and a test would fail if one did. So the global deny is the enforceable form for everything this repository ships, and it is **not** enforceable against an agent file of the user's own that re-allows these names (or `playwright_*`, or `*`) after it. That is a user's explicit override of a documented rule and stays a residual, stated in the wiki.
- SEC-T657-04 (the `x: true` entries override a user's own `ask`/`deny` for the granted tools) is unchanged and still tracked: a global `deny` of a granted tool, written by a user, is overridden by the generated agent-level allow of that agent. This task adds a denial only for the six excluded tools.
- Auto mode does not weaken it: "Explicit `deny` rules are still enforced".
- The legacy runtime also hides a tool whose last matching rule is a `deny` for `*` from the model's tool list (`permission/index.ts:204-213`); the current core refuses at call time (`permission.ts:175`). Either way the call fails.

### 2.2 Gemini CLI: key name, placement, precedence, subagents

- **Key and placement (verified)**: `excludeTools`, an array of strings, directly on `mcpServers.<name>` (documented in two pages and present in the settings schema).
- **Precedence over `includeTools` (verified)**: documented in two pages and implemented in `isEnabled` (the exclude test runs first and returns false). The generated entry has no `includeTools`.
- **Names (verified in source, not stated by the page)**: the match is against the tool name as the server reports it (`browser_evaluate`). The documentation page does not say whether the list takes the server's name or the fully qualified `mcp_<server>_<tool>` name; the source shows the server's name, and the `excludeTools` entries in the docs' own examples are server-side names (`dangerous_tool`, `file_deleter`, `gmail.send`).
- **Subagents (verified in source, not stated by any page)**: the pages do not mention subagents. In source an excluded tool is dropped in `discoverTools` before registration, a subagent builds its registry from the parent registry (`local-executor.ts:201-279`, default "all available tools" included), so it cannot receive the tool.
- **Scope merge**: `mcpServers` merges per server name (`SHALLOW_MERGE`): a same-named `playwright` entry in a higher-precedence settings scope replaces the whole generated entry, including its `excludeTools`. A user-level entry named `playwright` that wins over the project file therefore has no denial. Not tested live **(unverified)**.

## 3. What is emitted, and from where

`implementation/knowledge/mcp/servers.yaml`, entry `playwright`: `denyTools: [browser_run_code_unsafe, browser_evaluate, browser_file_upload, browser_drag, browser_drop, browser_network_request]`. This is the single source. `implementation/scripts/sync.mjs` validates it at load (each entry an exact name `[A-Za-z0-9_]+`, no wildcard, no duplicate, non-empty) and renders it for the `gemini` format (`excludeTools`) and the `opencode` format (`permission`, key from the same name cleaning as the `underscore` tool-name style) only. Other formats ignore it. Projections are generated, not hand-edited: `implementation/.opencode/opencode.json` and `implementation/.gemini/settings.json` are the only generated files that change.

## 4. The playwright-local exception

A user-owned entry named `playwright-local` is a different server name. On Opencode its tools resolve to `playwright-local_browser_evaluate` and so on, which no generated rule matches (the cleaning keeps `-`; the rule is an exact name). On Gemini CLI the generated list sits on the `playwright` entry only. So `playwright-local` is **not** denied on either platform, and it still contains `browser_run_code_unsafe`; the docs say so. Tests: `test_mcp_server_denials.py` (`test_a_user_owned_playwright_local_server_is_not_denied`, the merge tests and the documentation tests).

## 5. Install merge (`scripts/merge-mcp-json.py`, `scripts/install.sh --update`)

Before this change a leaf array or string in the destination was replaced by the generated value, and `permission` given as a string (`"allow"`, a documented shorthand for `{"*": "allow"}`) would have been replaced by the generated object. Decision and rule, identical with and without the provenance sidecar (the rule never reads it; the sidecar keeps governing server-key pruning only, and its format is unchanged):

| Case | Result |
|---|---|
| `excludeTools`, both sides lists | **Union**: the user's elements first in their order, then the generated elements the user's list lacks. A user element is never dropped |
| `excludeTools`, destination value not a list | Replaced by the generated list (fail closed) |
| `excludeTools` absent in the destination entry | Added |
| Generated element no longer shipped (a future change) | Stays in the user's file until removed by hand (fail closed); no automatic removal, because that needs a generator-owned element record in the sidecar, which was judged not worth a format change for a fail-closed leftover |
| Top-level `permission`, destination an object | The user's keys are kept in their order; each generated key is set to its generated value (`deny`) and **moved to the end**, because Opencode applies the last matching rule and a user wildcard such as `"playwright_*": "allow"` earlier in the same file must not win |
| Top-level `permission`, destination a string | Kept as `{"*": "<value>"}` first, then the generated keys |
| Top-level `permission`, destination another type | Replaced by the generated object |
| Same key, user value differs (for example the user set one of the six names to `allow`) | The generated `deny` wins: those six names are generator-owned, like the `playwright` entry's arguments. The user's other keys and entries (including `playwright-local`) are untouched |

A user who wants one of the six tools back adds a server entry of their own under another name (for example `playwright-local`), or, on Opencode, writes an allow in an agent file of their own (§2.1); editing the generated entry is undone by the next `--update`.

Tests (`tests/functional/test_mcp_server_denials.py`): the merge script run directly with and without sidecars, and `install.sh` end to end (fresh install, user edit, `--update`, with the destination sidecar present and deleted) for Opencode and Gemini; each merge is run twice and must be a fixed point, and the shipped files must be fixed points (root-install parity relies on it).

## 6. Not verified

1. **No live run** of Opencode or Gemini CLI. The effect is documented and read from source at the commits above; it was not observed. The releases people run may differ from the read commits **(unverified)**; the Opencode permission files are identical at `v2.0.29`, and the legacy runtime was read at `v1.19.0`.
2. The Gemini documentation does not state the subagent behaviour, nor whether `excludeTools` takes server-side or fully qualified names; both rest on source.
3. Gemini: precedence between a user-level and a project-level `playwright` entry (§2.2) and the effect of an untrusted workspace on project settings were not tested.
4. Cursor: no mechanism found; not re-verified in this task. Stays open.
5. Pi: an agent that lists no `mcp__` entry still reaches every MCP tool, as in the mapping artifact; no mechanism was researched here (out of scope for T658).
6. Opencode: a user-owned agent file, `OPENCODE_CONFIG_CONTENT`, managed settings, or a later `permission` in another config source that re-allows these names would win over the generated deny (last match). Managed settings would also be the strongest place for an operator to enforce it. Not tested live.
7. The six-tool list was taken from `@playwright/mcp@0.0.83`; a pin bump must re-check the tool list and update `denyTools`, the grant sets and the pins test together.

## 7. Follow-ups folded in (SEC-T657-07, SEC-T657-09)

- SEC-T657-09: `sync.mjs` validates `frontmatter.agents.mcpToolNames` once per manifest at load (an unknown, empty or non-string value stops the run even where the platform drops the tools line) and throws on a `*` that is not the whole tool part of an `mcp__server__*` token (it used to degrade silently to `_`).
- SEC-T657-07: `ArtifactTests.test_artifact_never_recommends_the_unsafe_tool` now anchors on whole-word "never", "excluded", "not" or "no" outside the tool name (with a self-check that a recommending line fails it), and `test_no_projection_names_the_unsafe_tool` has a file-count floor (28 source agents times six platforms). The part of SEC-T657-07 about pinning the non-Playwright grants (gitlab holders, no write MCP tool on read-only roles) is not done here and stays tracked.
