# Artifact: mcp-tool-name-mapping-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T657 (closes SEC-T655-01). **Owner**: devops-engineer. **Date**: 2026-10-15.
- Based on: security-review-t655-fetch-removal-v1.md
- **Also consumed**: `docs/artifacts/fetch-replacement-evaluation-v1.md` §5.3, `docs/artifacts/scoped-execution-primitive-v1.md` §4 platform table, the T656 report (its platform findings are re-checked below, not trusted).
- **Prior version**: none (first version). **Rollback**: revert the T657 commit; the generator keeps the source form when `mcpToolNames` is absent or `verbatim`.

## 1. What this records

Per platform: how an MCP tool and a whole MCP server are written in an agent's tool list, the source that says so, and the rendering the generator now uses. The agent sources keep one form, `mcp__<server>__<tool>` (one tool) and `mcp__<server>` (a whole server). `implementation/scripts/sync.mjs` renders it through the manifest key `frontmatter.agents.mcpToolNames` (`verbatim`, `slash`, `underscore`, `pi`). Rule applied: a platform opts in only where the documentation (or the vendor source) shows the source form is not honoured and shows the replacement form. An unverified platform keeps its rendering.

## 2. Per-platform result

| Platform (manifest) | Status | Honours the source form `mcp__server__tool` / `mcp__server`? | Documented form (tool / whole server) | Rendering now | Sources |
|---|---|---|---|---|---|
| Claude Code (`claude-code`) | **verified** | Yes | `mcp__<server>__<tool>` / `mcp__<server>` and `mcp__<server>__*` | verbatim (no change) | `https://code.claude.com/docs/en/sub-agents` (tools field: "`mcp__<server>` or `mcp__<server>__*` grants or removes every tool from the named server"); `https://code.claude.com/docs/en/permissions` (MCP section: `mcp__puppeteer`, `mcp__puppeteer__*`, `mcp__puppeteer__puppeteer_navigate`); ctx7 `/websites/code_claude` (Agent SDK: "Dynamic MCP tool names of the form `mcp__<server>__<tool>`") |
| GitHub Copilot, VS Code (`github`) | **verified** | **No.** The grammar has no `mcp__` form and unrecognised names are ignored, so every shipped `mcp__...` token granted nothing | `<server>/<tool>` / `<server>/*` | `slash`: `playwright/browser_click`, `gitlab/*` | GitHub Docs "Custom agents configuration" `https://docs.github.com/en/copilot/reference/custom-agents-configuration` ("Tool names from specific MCP servers can be prefixed with the server name followed by a `/`", `some-mcp-server/some-tool`, `some-mcp-server/*`, "All unrecognized tool names are ignored"; the table applies to "agent profiles in GitHub.com, the Copilot CLI, and supported IDEs"); VS Code custom agents page `https://code.visualstudio.com/docs/copilot/customization/custom-agents` ("To include all tools of an MCP server, use the `<server name>/*` format", "If a given tool is not available when using the custom agent, it is ignored"); VS Code source `microsoft/vscode@e941aa127412` (`src/vs/workbench/contrib/chat/browser/tools/languageModelToolsService.ts` `getToolFullReferenceName` = `${toolSet.referenceName}/${toolName}`, `getToolSetFullReferenceName` = `${referenceName}/*` for MCP; `.../mcp/common/mcpLanguageModelToolContribution.ts:82` server reference name is the label lower-cased with whitespace to `-`; `.../mcp/common/mcpServer.ts:1333` tool name with `.` replaced by `_`; no `mcp__` alias exists in the matching code). VS Code's own page documents only the `/*` form; the single-tool form is documented by GitHub for the same agent-profile format and confirmed in the VS Code source. A live VS Code run was not made **(unverified at runtime)** |
| Opencode (`opencode`) | **verified** (names); allowlist semantics **not provided** | **No.** The key `mcp__playwright` matches no tool | `<server>_<tool>` / `<server>_*` (glob) | `underscore`: `playwright_browser_click: true`, `gitlab_*: true` | ctx7 `/websites/opencode_ai`; `https://opencode.ai/docs/mcp-servers/` ("MCP server tools are registered with server name as prefix", `mymcpservername_*`); `https://opencode.ai/docs/agents/` (`tools` is deprecated; wildcards allowed in legacy `tools`; "true is equivalent to {"*": "allow"} permission"); source `anomalyco/opencode@81200db2a3a8` `packages/core/src/tool/mcp.ts:16-17` (`name(server, tool)` = `${namespace(server)}_${tool}` with `[^a-zA-Z0-9_-]` replaced by `_`) and `packages/core/src/v1/config/agent.ts:53-56` (`tools: {x: true}` becomes `permission.x = "allow"` and is merged over the defaults) |
| Gemini CLI (`gemini`) | **verified** (names); not rendered | n/a: the manifest drops the `tools` line (`"tools": "drop"`) | `mcp_<server>_<tool>` / `mcp_<server>_*` | unchanged (tools line dropped) | ctx7 `/google-gemini/gemini-cli`; `docs/core/subagents.md@06d329873703` (`tools` list supports `mcp_server_*`; "If omitted, it inherits all tools from the parent session"); `docs/tools/mcp-server.md` ("fully qualified name (FQN) using the format `mcp_{serverName}_{toolName}`") |
| Cursor (`cursor`) | **unverified, and no field exists** | n/a | Not documented for subagents. Subagent frontmatter documents `name`, `description`, `model`, `readonly`, `is_background` only; "Subagents inherit all tools from the parent, including MCP tools" | unchanged (verbatim) | `https://cursor.com/docs/subagents`; ctx7 `/websites/cursor` (the global `mcpAllowlist` in `permissions.json` uses `server:tool` and is not a per-agent grant). The generated `tools:` key (and the `.mdc` extension) is not in Cursor's documented subagent format |
| Cline (`cline`) | **verified: no agent projection** | n/a (no agent files are generated) | Cline subagents take no tool list and "don't get MCP tools" | unchanged | `https://docs.cline.bot/features/subagents`; ctx7 `/websites/cline_bot`; `cline.json` has no `agents` in `fileMap` |
| Pi (`pi`) | **verified** (name grammar); consumer of the agent file **unverified** | **No for hyphenated servers and for whole servers** | `mcp__<server>__<tool>` with every character other than letters, digits and `_` replaced by `_` (so `security-audit` becomes `security_audit`); whole server `mcp__<server>__*` | `pi`: `mcp__security_audit__run_npm_audit`, `mcp__gitlab__*` | ctx7 `/earendil-works/pi`; `earendil-works/pi@a3f265b1c6a4` `packages/coding-agent/docs/mcp.md` (line 77: "Tools are named `mcp__<server>__<tool>`, with every character other than letters, digits, and `_` replaced by `_`"; line 228: `pi --tools read,codemode,'mcp__radius__*'`) and `docs/cli.md` (line 120: `--tools` entries "are tool names or patterns where `*` matches any characters"; "Once an entry starts with `mcp__`, `--tools` filters MCP tools too"). Pi core defines no agent files; the documented consumer is the example subagent extension, whose `index.ts:305` passes the file's `tools` to `pi --tools` (`examples/extensions/subagent`). A third-party subagent extension may read the list differently **(unverified)** |

### Corrections to the T656 findings

- "Pi has no native MCP" is **wrong for current Pi**: `earendil-works/pi` main documents native MCP (`docs/mcp.md`, `pi mcp add`, `mcp.json` in the agent directory and `<project>/.pi/mcp.json`). The Pi version a user runs is not known **(unverified)**; an older Pi without MCP ignores these tokens, which is harmless.
- The other T656 facts hold: Claude Code `mcp__server__tool` (re-verified), Copilot `server/tool` and `server/*` with unrecognised names ignored (re-verified, and the single-tool form confirmed in source), Opencode `<server>_<tool>` with a glob-capable `tools` map (re-verified in docs and source), Gemini `tools: drop` (re-verified; Gemini itself supports `mcp_<server>_<tool>`), Cline no agent projection (re-verified), Cursor unverified (re-verified: no `tools` field is documented).

## 3. Effect of the narrowing, per platform

"In force" means the platform treats the list as an allowlist and the rendered names are honoured.

| Platform | Narrowed Playwright grant in force? | Why |
|---|---|---|
| Claude Code | **Yes** | `tools` is an allowlist; exact `mcp__server__tool` names are honoured |
| GitHub Copilot / VS Code | **Yes** (as of this change) | `tools` is an allowlist ("omit = all"); the rendered `playwright/<tool>` names are the documented form. Before T657 the list granted **no** MCP tool to any agent on this platform, because the old tokens are unrecognised and ignored (documented behaviour; not observed in a live run) |
| Pi | **Yes, when the agent file reaches `pi --tools`** (example subagent extension); unverified for other consumers | An entry starting with `mcp__` turns `--tools` into an MCP allowlist; the rendered names match Pi's own naming |
| Opencode | **No** | The generated `tools` map is not an allowlist: `x: true` only sets `permission.x = "allow"` over the defaults, so unlisted tools keep their default state, whatever is listed. Enforcing it would need generated deny entries (for example `playwright_*: false` ahead of the allowed names; rules are evaluated in order and the last match wins). Not implemented: it changes every agent's MCP reach and needs its own decision |
| Gemini CLI | **No** | The generator drops the `tools` line, so a Gemini subagent inherits all tools of the session, including every Playwright tool. Rendering it needs the built-in tool names (`read_file`, `grep_search`, ...) verified and mapped too, because a `tools` list restricts the agent to what it names. Not implemented |
| Cursor | **No** | Cursor documents no `tools` field; subagents inherit every tool, including MCP tools |
| Cline | n/a | No agent files; its subagents get no MCP tools |

## 4. The four Playwright grant sets

The agent bodies name no Playwright tool, so the sets follow the roles (assumption, reviewable). `@playwright/mcp@0.0.83` registers 25 tools by default (live `tools/list` on 2026-10-15 and README at tag `v0.0.83`, commit `f183dad4a529`). **Excluded from every set**: `browser_run_code_unsafe` (runs code in the server process, RCE-equivalent, not removable by any 0.0.83 flag), `browser_evaluate` (arbitrary page script), `browser_file_upload` (hands host file paths to a page), `browser_drag`, `browser_drop`, `browser_network_request` (full headers and bodies of one request).

| Agent | Tools (all `mcp__playwright__<tool>`) |
|---|---|
| qa-engineer | browser_navigate, browser_navigate_back, browser_snapshot, browser_find, browser_take_screenshot, browser_click, browser_type, browser_fill_form, browser_select_option, browser_press_key, browser_hover, browser_handle_dialog, browser_wait_for, browser_console_messages, browser_network_requests, browser_resize, browser_tabs, browser_close |
| frontend-developer | browser_navigate, browser_navigate_back, browser_snapshot, browser_find, browser_take_screenshot, browser_click, browser_type, browser_fill_form, browser_select_option, browser_press_key, browser_hover, browser_wait_for, browser_console_messages, browser_network_requests, browser_emulate_media, browser_resize, browser_tabs, browser_close |
| poc-qa-engineer | browser_navigate, browser_snapshot, browser_find, browser_take_screenshot, browser_click, browser_type, browser_fill_form, browser_select_option, browser_press_key, browser_handle_dialog, browser_wait_for, browser_console_messages, browser_close |
| demo-agent | browser_navigate, browser_navigate_back, browser_snapshot, browser_take_screenshot, browser_click, browser_hover, browser_type, browser_fill_form, browser_press_key, browser_wait_for, browser_resize, browser_close |

What the narrowing does not fix: a granted `browser_navigate` still follows redirects to internal addresses (the `--blocked-origins` list does not cover them), and `browser_click`/`browser_type` act on pages that can carry prompt-injection text. Egress filtering through `--proxy-server` stays the closure (evaluation §5.3, SEC-T655-07).

## 5. Changes to existing shipped lines

The whole-server and per-tool tokens that existed before T657 change only on a platform whose documentation shows the old form is not honoured:

- **GitHub Copilot / VS Code** (documentation and source above): every `mcp__...` token in the 14 agent files that carry one is rewritten (`mcp__gitlab` to `gitlab/*`, `mcp__memory` to `memory/*`, `mcp__sequential-thinking` to `sequential-thinking/*`, `mcp__security-audit__<tool>` to `security-audit/<tool>`, `mcp__poc-security-audit__<tool>` to `poc-security-audit/<tool>`, `mcp__context-retriever__retrieve` to `context-retriever/retrieve`).
- **Opencode**: `mcp__gitlab: true` to `gitlab_*: true` (and `memory_*`, `sequential-thinking_*`), `mcp__security-audit__<tool>: true` to `security-audit_<tool>: true`, `mcp__poc-security-audit__<tool>` to `poc-security-audit_<tool>`, `mcp__context-retriever__retrieve` to `context-retriever_retrieve`.
- **Pi**: whole servers gain `__*` (`mcp__gitlab` to `mcp__gitlab__*`, `mcp__memory__*`, `mcp__sequential_thinking__*`); hyphens in server names become `_` (`mcp__security_audit__<tool>`, `mcp__poc_security_audit__<tool>`, `mcp__context_retriever__retrieve`).
- **Claude Code, Cursor, Gemini, Cline**: unchanged (Claude Code honours the old form; the others are unverified or have no tools line).

The full before/after list is in the T657 report; the generated files are the diff of `implementation/.github/agents`, `.opencode/agents` and `.pi/agents`.

## 6. Limits

L-1 no live run of VS Code, Opencode, Pi, Gemini or Cursor was made; Copilot, Opencode and Pi rest on vendor documentation plus vendor source at the commits named above. L-2 the Pi agent file consumer is extension-specific. L-3 Pi's built-in tokens in the generated lists (`search`, `edit`, `execute`, `web`) are not Pi tool names (pre-existing, not changed). L-4 Opencode's built-in tokens in the generated map (`read`, `search`, `execute`, `web`) are not Opencode tool names either (pre-existing). L-5 the grant sets are inferred from the roles. L-6 server names with an underscore pair, a dot or whitespace are mapped by the documented rules but none is shipped.
