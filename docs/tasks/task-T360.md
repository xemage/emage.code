# Task T360 — Audit remote MCP transport formats per platform (P030-01)

**ID:** T360
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-09
**Completed:** 2026-08-09
**Based on:** docs/plans/plan-030-mcp-remote-transport-alignment.md

## Objective
Build a documentation-backed evidence table of every emage.code platform projection that emits
hosted/remote MCP servers (`context7`, `hf-mcp-server`, per
`implementation/knowledge/mcp/servers.yaml`), and determine — per platform, from that platform's
own current official docs, not by analogy to another platform — whether its remote transport
encoding in `implementation/scripts/sync.mjs` is current or stale. Cline is already confirmed stale
(a real runtime failure was observed). Do not assume any other platform shares that same defect;
prove or disprove each one independently.

## Context
- Phase: Implementation (audit sub-phase)
- Plan: `docs/plans/plan-030-mcp-remote-transport-alignment.md` — read the full plan, including the
  "Plan Review Corrections (2026-08-09)" section at the top, before starting. That section already
  contains preliminary orchestrator research (with source URLs) as a starting point — you must
  independently verify every claim in it against the cited primary sources (and any others you find
  more authoritative) before relying on it. Do not just copy it forward without checking.
- `emitMcp()` in `implementation/scripts/sync.mjs` (currently lines 293-378) has one branch per
  platform `format`: `vscode`/`cursor` (shared, lines 298-309), `gemini` (311-339), `opencode`
  (341-351), `claude-code` (353-363), `cline` (365-375). Confirm these line numbers against the
  actual current file — they may have moved again since this brief was written.

## Inputs
- `implementation/scripts/sync.mjs` (the `emitMcp` function and all format branches)
- `implementation/knowledge/mcp/servers.yaml` (confirms only `context7` and `hf-mcp-server` carry
  `transport: remote`)
- `implementation/platforms/*.json` (which manifest maps to which `format`/`outputFile`: `github.json`
  → `vscode` → `.vscode/mcp.json`; `cursor.json` → `cursor` → `.cursor/mcp.json`; `pi.json` → also
  `cursor` format → `.pi/mcp.json`; `gemini.json` → `gemini` → `.gemini/settings.json`;
  `opencode.json` → `opencode` → `.opencode/opencode.json`; `claude-code.json` → `claude-code` →
  `../.mcp.json`; `cline.json` → `cline` → `.cline/mcp.json`)
- Official docs per platform, fetched live (WebFetch/WebSearch/context7 MCP tool) — do not rely on
  training-data memory, this is exactly what caused the drift being fixed:
  - Claude Code: `code.claude.com/docs/en/mcp`
  - Cline: `docs.cline.bot/mcp/mcp-overview`
  - VS Code / GitHub Copilot: `code.visualstudio.com/docs/agents/reference/mcp-configuration`
  - Cursor: `cursor.com/docs/mcp`
  - Gemini CLI: `raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/tools/mcp-server.md`
    (prefer the raw GitHub source over SEO mirror sites — several third-party "geminicli.com" /
    mintlify-style mirrors returned inconsistent or contradictory answers during preliminary
    research; treat those as unreliable and confirm against the primary repo docs)
  - Opencode: `opencode.ai/docs/mcp-servers/`
  - Pi: attempt to identify the specific "Pi" product this repo's `pi.json` platform manifest
    targets (check `docs/tasks/task-T046.md`, `docs/decisions/`, `docs/wiki/quick-start.md` for any
    identifying detail beyond the generic name) and its MCP config docs, if a confirmable official
    source exists. If — and only if — no confirmable, unambiguous official source can be found,
    that absence must be stated explicitly in the table (not silently treated as "same as Cursor").

## Expected Outputs
- `docs/tasks/task-T360.md` (this file) updated with an `## Execution notes` section containing the
  full audit table:

  | Platform | Emitted file(s) | Current repo encoding | Doc-confirmed expected encoding | Change needed (Y/N) | Source URL |
  |---|---|---|---|---|---|

  covering every platform listed in Inputs above, plus a one-line verdict summary at the end
  ("Confirmed stale: ...", "Confirmed current, no change: ...", "Inconclusive: ...").
- No code changes in this task — audit only, read-only.

## Acceptance Criteria
1. Every platform format branch in `emitMcp()` that can emit a remote server is covered in the
   table (vscode, cursor, gemini, opencode, claude-code, cline) plus Pi's inherited verdict.
2. Cline is explicitly marked confirmed stale, with the exact correct replacement value cited from
   its official docs (not assumed).
3. No platform is marked "change needed: Y" without a cited, fetched-live doc source backing the
   correct value.
4. No platform is marked "change needed: N" purely by assumption — each has either a cited doc
   confirming current correctness, or an explicit "inconclusive" note if no authoritative source
   was found (Pi is the anticipated case for this).
5. The table distinguishes "missing required field entirely" from "wrong field value" from "wrong
   field name" as distinct staleness categories, since different platforms may exhibit different
   failure modes.

## Blocker Protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

**Executed by:** backend-developer, 2026-08-09. Read-only audit — no code or generated-artifact
changes made in this task.

### Method
For each platform, the current `emitMcp()` branch in `implementation/scripts/sync.mjs` (confirmed
against the current file, not the plan's original line numbers — see below) was compared against
that platform's own official documentation, fetched live via WebFetch and the `fetch` MCP tools
(both a summarized fetch and a raw markdown/text fetch were used per platform, to cross-check
against model-summarization error). No claim below relies on training-data memory.

`emitMcp()` line numbers confirmed against current file (matches the plan's "Plan Review
Corrections" section exactly): `vscode`/`cursor` shared branch starts line 298 (`url` assignment
line 302), `gemini` branch starts line 311 (`url` assignment line 314), `opencode` branch starts
line 341 (`type`/`url` assignment line 344), `claude-code` branch starts line 353 (`type`
assignment line 356), `cline` branch starts line 365 (`type` assignment line 368).

Platform manifest → format → output file mapping confirmed against
`implementation/platforms/*.json`: `github.json` → `vscode` → `.vscode/mcp.json`; `cursor.json` →
`cursor` → `.cursor/mcp.json`; `pi.json` → `cursor` (same branch, verbatim) → `.pi/mcp.json`;
`gemini.json` → `gemini` → `.gemini/settings.json`; `opencode.json` → `opencode` →
`.opencode/opencode.json`; `claude-code.json` → `claude-code` → `../.mcp.json`; `cline.json` →
`cline` → `.cline/mcp.json`.

### Audit table

| Platform | Emitted file(s) | Current repo encoding | Doc-confirmed expected encoding | Staleness category | Change needed (Y/N) | Source URL |
|---|---|---|---|---|---|---|
| VS Code / GitHub Copilot (`vscode` format, `github.json`) | `.vscode/mcp.json` | `{ "url": s.url }` — no `"type"` field | `{ "type": "http", "url": s.url }` — `"type"` is a **required** field for HTTP/SSE servers (`"http"` or `"sse"`); doc's own minimal example uses server name `context7` with exactly this shape | Missing required field entirely (`"type"` absent) | **Y** | https://code.visualstudio.com/docs/agents/reference/mcp-configuration (fetched live, both WebFetch summary and raw `fetch_readable`; "HTTP and Server-Sent Events (SSE) servers" section, `type` marked Required, example `{"servers":{"context7":{"type":"http","url":"https://mcp.context7.com/mcp"}}}`) |
| Cursor (`cursor` format, `cursor.json`) | `.cursor/mcp.json` | `{ "url": s.url }` — no `"type"` field | `{ "url": s.url, "headers"?: {...} }` — no `"type"` field is used or documented for remote servers | N/A — current encoding matches doc | **N** | https://cursor.com/docs/mcp (fetched live via WebFetch and raw `fetch_markdown`; "Using `mcp.json`" → "Remote Server" example: `{"mcpServers":{"server-name":{"url":"http://localhost:3000/mcp","headers":{"API_KEY":"value"}}}}`, no `type` key present; STDIO-only table lists `type` as required, remote table does not) |
| Gemini CLI (`gemini` format, `gemini.json`) | `.gemini/settings.json` | `{ "url": s.url }` | `{ "httpUrl": s.url }` — `"url"` is reserved for the legacy SSE transport (`"url"` (string): SSE endpoint URL); `"httpUrl"` (string) is the field for the streamable-HTTP transport. One of `command` / `url` / `httpUrl` is required; using `"url"` silently selects the deprecated SSE transport instead of streamable HTTP | Wrong field name (`"url"` used where `"httpUrl"` is required for HTTP transport) | **Y** | https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/tools/mcp-server.md (fetched live via raw `fetch_txt` against the primary GitHub repo doc, per the brief's explicit instruction to prefer this over third-party "geminicli.com"/mintlify mirrors, which were not used) |
| Opencode (`opencode` format, `opencode.json`) | `.opencode/opencode.json` | `{ "type": "remote", "url": s.url }` | `{ "type": "remote", "url": s.url }` — both fields Required per the "Remote" section's options table | N/A — current encoding matches doc | **N** | https://opencode.ai/docs/mcp-servers/ (fetched live via raw `fetch_markdown`; "Remote" section example `{"mcp":{"my-remote-mcp":{"type":"remote","url":"https://my-mcp-server.com", ...}}}`, options table marks `type` and `url` both Required) |
| Claude Code (`claude-code` format, `claude-code.json`) | `../.mcp.json` | `{ "type": "http", "url": s.url }` | `{ "type": "http", "url": s.url }` — every current project-scope `.mcp.json` example in the reference doc uses `"type": "http"`; doc explicitly warns that a `url` with no `type` is a configuration error (server skipped, not silently misconfigured) | N/A — current encoding matches doc | **N** | https://code.claude.com/docs/en/mcp (fetched live via WebFetch; confirmed at multiple points in the doc, e.g. project-scope example `{"mcpServers":{"shared-server":{"type":"http","url":"https://example.com/mcp"}}}` and plugin/env-interpolation examples, all using `"type":"http"`) |
| Cline (`cline` format, `cline.json`) | `.cline/mcp.json` | `{ "type": "http", "url": s.url }` | `{ "type": "streamableHttp", "url": s.url }` — doc states omitting `"type"` (or, by extension, supplying an unrecognized value) falls back to the legacy `sse` transport; the two named, currently-supported values are `"streamableHttp"` (recommended) and `"sse"` (legacy). `"http"` is not a documented accepted value at all | Wrong field value (`"http"` is not a recognized Cline transport identifier; confirmed-broken at runtime per the task brief's background) | **Y** (already confirmed stale prior to this audit; re-confirmed independently here via two separate live fetches of the same source) | https://docs.cline.bot/mcp/mcp-overview (fetched live via WebFetch and raw `fetch_readable`, cross-checked; both fetches independently returned `"type": "streamableHttp"` as the recommended remote value and explicitly named `"http"` as not a recognized option) |
| Pi (`cursor` format reused verbatim, `pi.json`) | `.pi/mcp.json` | `{ "url": s.url }` (byte-identical generator branch to Cursor — `pi.json`'s `mcp.format` is literally `"cursor"`, confirmed in `implementation/platforms/pi.json`) | **Inconclusive — no distinct authoritative official "Pi" MCP doc source located.** Checked `docs/tasks/task-T046.md` (only says "Pi platform" with no identifying product detail beyond the generic name; artifacts listed are internal repo paths, not an external product reference), `docs/decisions/` (grepped all ADRs for "pi" as a whole word — zero matches, so ADR-001 does not concern this platform despite an earlier substring false-positive), and `docs/wiki/quick-start.md` (lists `Pi` → `pi` format id and `.pi/` output dir alongside Gemini/Opencode/Claude Code for instruction-file format, but gives no vendor URL or distinguishing detail). A live web search for an official "Pi" coding-agent/CLI product with its own MCP config docs returned only unrelated third-party/community projects (`oh-my-pi`, `pi-mcp-adapter`, `pi-mcp-server`, LobeHub listings) — none is a first-party vendor doc for a product this repo's `pi.json` manifest can be confirmed to target. Per the task brief, this absence is stated explicitly and the verdict is **not** silently treated as "same as Cursor," even though the generator code happens to produce byte-identical output to the (confirmed-correct) Cursor branch. | N/A — no category assignable without a confirmed doc | **Inconclusive** (not Y, not N — see note) | No authoritative source found. Searched: `docs/tasks/task-T046.md`, `docs/decisions/*.md` (grep, no word-boundary match), `docs/wiki/quick-start.md`, live web search for an official "Pi" MCP/config doc. |

### Verdict summary
- **Confirmed stale (change needed):** `vscode` (missing required `"type"` field) and `gemini`
  (wrong field name, `"url"` instead of `"httpUrl"`) — newly identified by this audit, not
  previously named in the plan's original (uncorrected) text. `cline` (wrong field value, `"http"`
  instead of `"streamableHttp"`) — already flagged stale prior to this task from the real runtime
  failure, independently re-confirmed here against the primary doc.
- **Confirmed current, no change:** `cursor` and `opencode` — both audited independently against
  their own primary docs and found already correct.
- **Confirmed current, no change (by transitive doc coverage):** `claude-code` — corrects the
  plan's original (pre-correction) claim that it shared Cline's staleness; the current audit found
  `"type": "http"` is Claude Code's own documented, correct value, unrelated to Cline's requirement.
- **Inconclusive:** `pi` — no distinct authoritative official "Pi" MCP doc source could be located;
  flagged explicitly rather than assumed identical to Cursor, even though `pi.json` reuses the
  `cursor` format branch verbatim in the generator today.
