# 03 — Cursor integration

## Cursor conventions in 2026

| Concept | Cursor location | Format |
|---------|----------------|--------|
| Always-on / glob-scoped rules | `.cursor/rules/*.mdc` | YAML frontmatter (`description`, `globs`) + Markdown body |
| Slash commands | `.cursor/commands/*.mdc` | YAML frontmatter + Markdown body |
| Sub-agents | `.cursor/agents/*.mdc` | YAML frontmatter (`name`, `description`, `tools`) + Markdown body |
| Workspace conventions | `AGENTS.md` (workspace root) | Markdown |
| MCP servers | `.cursor/mcp.json` | `{ "mcpServers": { ... } }` (same shape as Cursor's standard) |

## Mapping emage.code → Cursor

| Knowledge type | Cursor target |
|----------------|---------------|
| `knowledge/agents/<n>.md` | `.cursor/agents/<n>.mdc` |
| `knowledge/commands/<n>.md` | `.cursor/commands/<n>.mdc` |
| `knowledge/instructions/<n>.md` | `.cursor/rules/<n>.mdc` (`applyTo` → `globs`) |
| `knowledge/skills/<s>/SKILL.md` | `.cursor/skills/<s>/SKILL.md` |
| `knowledge/mcp/servers.yaml` (`core` + `extended`) | `.cursor/mcp.json` |
| `AGENTS.md` (workspace) | `AGENTS.md` (copied at project root) |

## Frontmatter transform

Cursor's rule files want:

```yaml
---
description: "..."
globs: "**/*.{ts,js}"      # was applyTo in knowledge/
---
```

The Cursor manifest declares `renameKeys: { applyTo: globs }` and `keepKeys: [description, globs]`. Agents and commands keep `tools` as an array (Cursor format). No additional fields are required.

## Skills in Cursor

Cursor has no native "skill" concept. emage.code skills are markdown files that agents read explicitly via the file-read tool. v2 emits skills under `.cursor/skills/<name>/SKILL.md` and the orchestrator/agents reference them by relative path the same as in other platforms. This is intentionally low-tech and works regardless of Cursor's evolving feature set.

## Limitations / known gaps

- **Cursor `.cursor/agents/` reach:** Cursor's agent feature has been evolving. If a given Cursor build doesn't honor `.cursor/agents/`, the orchestrator definition is still readable via the rules system because `AGENTS.md` references it. Test on the user's specific Cursor version during onboarding.
- **MCP server limits:** Some Cursor versions cap the number of MCP servers. The `extended` tag opts the user into 19 servers; reduce by editing `cursor.json`'s `mcp.tags` to `["core"]` if the user hits a cap.
- **Slash commands UX:** Cursor renders commands by filename. `/new-project`, `/new-feature`, `/code-review` etc. all map cleanly; longer command names should be tested.

## Verification recipe

```bash
# In a fresh empty project root
cp -r <repo>/emage.code/v2/implementation/.cursor   .
cp    <repo>/emage.code/v2/implementation/AGENTS.md .
cp -r <repo>/emage.code/v2/implementation/docs      .
export GITLAB_PERSONAL_ACCESS_TOKEN="..."
cursor .
# In Cursor's AI panel:
#   /new-feature "add login form"
# Expect: orchestrator proposes a plan and waits for approval.
```

```powershell
# In a fresh empty project root
Copy-Item -Recurse <repo>/emage.code/v2/implementation/.cursor   .
Copy-Item          <repo>/emage.code/v2/implementation/AGENTS.md .
Copy-Item -Recurse <repo>/emage.code/v2/implementation/docs      .
$env:GITLAB_PERSONAL_ACCESS_TOKEN = "..."
cursor .
# In Cursor's AI panel:
#   /new-feature "add login form"
# Expect: orchestrator proposes a plan and waits for approval.
```
