# Task T301 — Map abstract tool categories to real Claude Code tool identifiers

**ID:** T301
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T300
**Created:** 2026-07-31
**Completed:** 2026-07-31
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Fix the confirmed defect where `implementation/platforms/claude-code.json` + `sync.mjs` copy the
abstract emage.code tool categories (`read, search, edit, execute, agent, web, todo, mcp__gitlab, ...`)
verbatim into generated `.claude/agents/*.md` frontmatter instead of translating them to real Claude
Code tool identifiers — silently leaving every generated Claude Code subagent with almost no usable
tools. Confirmed live: an Orchestrator subagent invoked on this platform could call only
`mcp__memory` and `mcp__sequential-thinking` — no `Read`, `Bash`, `Edit`, `Write`, or `Agent`.

## Inputs
- `implementation/platforms/claude-code.json`
- `implementation/scripts/sync.mjs` (the `cfg.tools === 'string'` branch, near line 257-259)
- `implementation/knowledge/agents/*.md` (source of the abstract `tools:` arrays)

## Expected outputs
- `implementation/platforms/claude-code.json` with a new `toolMap` object under
  `frontmatter.agents`.
- `implementation/scripts/sync.mjs` updated to apply `toolMap` translation before joining tool
  names into the Claude Code frontmatter string.
- Regenerated `implementation/.claude/**` (via `make sync`).

## Acceptance criteria
1. `implementation/platforms/claude-code.json` gains:
   ```json
   "toolMap": {
     "read": "Read", "search": "Read", "edit": "Edit, Write", "execute": "Bash",
     "agent": "Agent", "web": "WebFetch, WebSearch", "todo": "TodoWrite"
   }
   ```
   under `frontmatter.agents`. `mcp__*` entries are passed through unchanged.
2. `node --check implementation/scripts/sync.mjs` exits 0 (syntax valid).
3. `make sync` runs, then `grep "^tools:" implementation/.claude/agents/orchestrator.md` shows a
   line containing `Read`, `Bash`, `Edit`, `Write`, `Agent`, `WebFetch`, `WebSearch`, `TodoWrite`,
   `mcp__gitlab`, `mcp__memory`, `mcp__sequential-thinking` — and does NOT contain the bare tokens
   `read,`, `search,`, `execute,`, or `todo,`.
4. `make verify` exits 0 (no regression in any other platform's projection).
5. Per R8, paste all four command outputs verbatim into Execution notes before claiming done.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

**Run 2026-07-31.**

Implemented:
- `implementation/platforms/claude-code.json`: added `toolMap` under `frontmatter.agents`
  (`read`→`Read`, `search`→`Read`, `edit`→`Edit, Write`, `execute`→`Bash`, `agent`→`Agent`,
  `web`→`WebFetch, WebSearch`, `todo`→`TodoWrite`).
- `implementation/scripts/sync.mjs`, `applyAgentFrontmatter()`, `cfg.tools === 'string'` branch:
  now expands each abstract tool name through `cfg.toolMap` (splitting comma-joined mapped
  values into separate array entries) and deduplicates the result (`read`/`search` both map to
  `Read`, so without dedup the output contained `Read, Read`).

`node --check implementation/scripts/sync.mjs`:
```
SYNTAX_OK
```

`make sync` (excerpt) + `grep "^tools:" implementation/.claude/agents/orchestrator.md`:
```
[claude-code] wrote 84 files -> .claude
...
Done - 505 files written.

tools: Read, Edit, Write, Bash, Agent, WebFetch, WebSearch, TodoWrite, mcp__gitlab, mcp__memory, mcp__sequential-thinking
```
Contains all required real tool names; no bare `read,`/`search,`/`execute,`/`todo,` tokens present.

`make verify`:
```
node implementation/scripts/sync.mjs --root implementation --check
[claude-code] checked 84 files -> .claude
[cursor] checked 84 files -> .cursor
[gemini] checked 84 files -> .gemini
[github] checked 85 files -> .github
[opencode] checked 84 files -> .opencode
[pi] checked 84 files -> .pi

OK - no drift across 505 files.
```

**Regression found and fixed (not part of the original plan text, discovered during
verification):** `python3 tests/run.py -v` initially came back `FAILED (failures=27, skipped=13)`
— every failure was `test_claude_code_agents_use_tools_string` in
`tests/functional/test_platform_projections.py`. Root cause: that test (added under T294) asserted
the projected tools string is a **verbatim echo** of the source abstract tool array — i.e. it
encoded the bug this task fixes as the "correct" behavior. Updated the test to assert the
`toolMap`-translated, deduplicated result instead, and added an explicit check that no abstract
category name (`read`/`search`/`edit`/`execute`/`todo`) leaks into the projected string. After the
fix: `python3 tests/run.py -v` → `Ran 266 tests in 11.115s` / `OK (skipped=13)`. Re-ran `make sync`
+ `make verify` after the test edit — still clean (505 files, no drift). Re-ran the T300 baseline
suite — still `55 passed in 0.21s`, unchanged.

Confirmed a real subagent tools line too (not just orchestrator):
```
implementation/.claude/agents/backend-developer.md:tools: Read, Edit, Write, Bash, WebFetch, WebSearch, mcp__fetch
implementation/.claude/agents/qa-engineer.md:tools: Read, Edit, Write, Bash, WebFetch, WebSearch, mcp__playwright, mcp__gitlab
```
Confirmed Cursor's array-format projection is untouched (toolMap is claude-code-only):
```
tools: [read, search, edit, execute, agent, web, todo, mcp__gitlab, mcp__memory, mcp__sequential-thinking]
```

All acceptance criteria met. Not yet committed — commit happens as part of this task's completion
per Conventional Commits (`fix(sync): ...`) before moving to T307.
