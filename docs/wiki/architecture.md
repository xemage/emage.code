# Architecture

emage.code v2 is built on **six layers**, each with a clear responsibility.

## 6-layer architecture

```
┌──────────────────────────────────────────────────────────────┐
│  1. Commands              19 slash commands (user entrypoint) │
├──────────────────────────────────────────────────────────────┤
│  2. Orchestration         @orchestrator + @poc-orchestrator   │
│                           Plan → Approve → Execute lifecycle  │
├──────────────────────────────────────────────────────────────┤
│  3. Agents                28 specialists                      │
│                           backend / frontend / qa / sec / …   │
├──────────────────────────────────────────────────────────────┤
│  4. Skills                27 reusable capabilities            │
│                           code-review, validation-gates, …    │
├──────────────────────────────────────────────────────────────┤
│  5. Memory                docs/* (artifacts, ADRs, tasks) +   │
│                           MCP `memory` server (knowledge graph)│
├──────────────────────────────────────────────────────────────┤
│  6. MCP servers           gitlab, playwright, memory, brave,  │
│                           sequential-thinking, fetch, context7│
└──────────────────────────────────────────────────────────────┘
```

## Knowledge → platform projection

```
v2/implementation/knowledge/   (canonical)
        │
        ▼
   sync.mjs                    (manifest-driven generator)
        │
        ├──► .github/   (GitHub Copilot)
        ├──► .gemini/   (Gemini CLI)
        ├──► .opencode/ (Opencode)
        ├──► .pi/       (Pi)
        ├──► .claude/   (Claude Code)
        └──► .cline/ + .clinerules/ (Cline)
```

Each platform has a manifest (`v2/implementation/platforms/<name>.json`) describing:
- File extensions and naming
- Frontmatter shape (e.g. `applyTo` vs `paths`)
- MCP output format (vscode / gemini / opencode / pi / claude-code / cline)
- Which `extended` MCP servers to include

## Lifecycle states

```
pending → in_progress → blocked → in_review → done | cancelled
```

Only orchestrators transition tasks. Specialist agents report completion or blockers; they never self-promote.

## Validation gates

| Gate | When | Reviewer |
|------|------|----------|
| Architecture | After architecture phase | `@tech-lead`, `@security-engineer` |
| Implementation | After core implementation | `@tech-lead` |
| Integration | After parallel work merges | `@qa-engineer` |
| Security | Before release | `@security-engineer` |
| Release | Before deployment | `@release-manager` |

Verdicts: `PASS` / `CONDITIONAL_PASS` / `FAIL`. `FAIL` blocks progression and creates fix tasks.

## Further reading

- [`v2/plan/00-vision-v2.md`](https://gitlab.com/em-age/emage.code/-/blob/main/v2/plan/00-vision-v2.md)
- [`v2/plan/01-shared-knowledge-architecture.md`](https://gitlab.com/em-age/emage.code/-/blob/main/v2/plan/01-shared-knowledge-architecture.md)
- [`v2/plan/02-platform-adapter-spec.md`](https://gitlab.com/em-age/emage.code/-/blob/main/v2/plan/02-platform-adapter-spec.md)
- [`v2/plan/04-sync-script-design.md`](https://gitlab.com/em-age/emage.code/-/blob/main/v2/plan/04-sync-script-design.md)
