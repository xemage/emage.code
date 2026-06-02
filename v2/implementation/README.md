# emage.code v2

**Multi-platform AI dev-team orchestration with a single canonical knowledge base.**

emage.code is a structured multi-agent development system that brings disciplined software engineering practices to AI-assisted coding: Plan-Approve-Execute workflows, DAG-based task management, validation gates, checkpoint compression. v2 introduces a **single source of truth** for all agents, skills, commands, and instructions; the same knowledge is projected into platform-specific folders by an automated sync engine.

> Migrating from v1? See [`../plan/05-migration-from-v1.md`](../plan/05-migration-from-v1.md). v1 remains untouched at [`../../v1/`](../../v1/).

---

## Supported platforms

| Platform | Output folder | Format |
|----------|---------------|--------|
| GitHub Copilot (VS Code) | `.github/` + `.vscode/mcp.json` | `.agent.md`, `.prompt.md`, `.instructions.md` |
| Gemini CLI | `.gemini/` | `.md` (no `tools` field), `settings.json` with hooks |
| Opencode | `.opencode/` | `.md` (object `tools`), `opencode.json` |
| Cursor | `.cursor/` | `.mdc`, `applyTo` → `globs`, `mcp.json` |
| **Pi** _(new)_ | `.pi/` | `.md`, `mcp.json` |

---

## Repository layout

```
implementation/
├── knowledge/              ← single source of truth
│   ├── agents/*.md
│   ├── commands/*.md
│   ├── instructions/*.md
│   ├── skills/<name>/SKILL.md
│   ├── mcp/servers.yaml
│   └── schemas/*.schema.json
├── platforms/              ← per-platform manifests
│   ├── github.json
│   ├── gemini.json
│   ├── opencode.json
│   └── cursor.json
├── scripts/
│   ├── sync.mjs            ← Node generator (no external deps)
│   ├── verify.mjs          ← CI drift check
│   ├── sync.ps1 / sync.sh  ← thin wrappers
├── _extras/                ← non-knowledge files copied into specific platforms
├── .github/    (generated)
├── .gemini/    (generated)
├── .opencode/  (generated)
├── .cursor/    (generated)
├── .pi/        (generated)
├── .vscode/
│   ├── mcp.json            (generated)
│   └── settings.json       ← see SECURITY.md
├── docs/                   ← runtime workspace state (templates included)
├── AGENTS.md               ← workspace-level conventions
└── SECURITY.md
```

---

## Quick start (end-user)

Pick the platform you use, copy that folder to your project root, plus `AGENTS.md` and `docs/`:

### GitHub Copilot
```bash
cp -r v2/implementation/.github         <your-project>/
mkdir -p <your-project>/.vscode
cp    v2/implementation/.vscode/mcp.json <your-project>/.vscode/
cp    v2/implementation/AGENTS.md       <your-project>/
cp -r v2/implementation/docs            <your-project>/
```

```powershell
Copy-Item -Recurse v2/implementation/.github         <your-project>/
Copy-Item          v2/implementation/.vscode/mcp.json <your-project>/.vscode/
Copy-Item          v2/implementation/AGENTS.md       <your-project>/
Copy-Item -Recurse v2/implementation/docs            <your-project>/
```

### Gemini CLI
```bash
cp -r v2/implementation/.gemini  <your-project>/
cp    v2/implementation/AGENTS.md <your-project>/
cp -r v2/implementation/docs     <your-project>/
```

```powershell
Copy-Item -Recurse v2/implementation/.gemini  <your-project>/
Copy-Item          v2/implementation/AGENTS.md <your-project>/
Copy-Item -Recurse v2/implementation/docs     <your-project>/
```

### Opencode
```bash
cp -r v2/implementation/.opencode <your-project>/
cp    v2/implementation/AGENTS.md  <your-project>/
cp -r v2/implementation/docs       <your-project>/
```

```powershell
Copy-Item -Recurse v2/implementation/.opencode <your-project>/
Copy-Item          v2/implementation/AGENTS.md  <your-project>/
Copy-Item -Recurse v2/implementation/docs      <your-project>/
```

### Cursor
```bash
cp -r v2/implementation/.cursor   <your-project>/
cp    v2/implementation/AGENTS.md  <your-project>/
cp -r v2/implementation/docs       <your-project>/
```

```powershell
Copy-Item -Recurse v2/implementation/.cursor   <your-project>/
Copy-Item          v2/implementation/AGENTS.md  <your-project>/
Copy-Item -Recurse v2/implementation/docs      <your-project>/
```

### Pi
```bash
cp -r v2/implementation/.pi   <your-project>/
cp    v2/implementation/AGENTS.md  <your-project>/
cp -r v2/implementation/docs       <your-project>/
```

```powershell
Copy-Item -Recurse v2/implementation/.pi   <your-project>/
Copy-Item          v2/implementation/AGENTS.md  <your-project>/
Copy-Item -Recurse v2/implementation/docs      <your-project>/
```

Then set MCP env vars (`GITLAB_PERSONAL_ACCESS_TOKEN`, `BRAVE_API_KEY`, etc.) — see `mcp.json` for the full list.

Invoke from your AI tool:
```
/new-project "My SaaS application"
```

---

## Authoring (contributors)

1. Edit files under `knowledge/` only.
2. Run `node scripts/sync.mjs` (or `./scripts/sync.ps1` / `./scripts/sync.sh`).
3. Commit both `knowledge/` and the regenerated platform folders.
4. CI runs `node scripts/verify.mjs` — it fails if generated folders drift from `knowledge/`.

Frontmatter conventions are described in [`knowledge/README.md`](knowledge/README.md). To add a new platform, drop a `platforms/<name>.json` manifest (see existing four for shape) and re-sync — no script changes required.

---

## Architecture

emage.code v2 keeps the v1 **6-layer architecture**:

1. **Commands** — 16 slash commands, user entry points
2. **Orchestration** — Plan-Approve-Execute engine (`orchestrator`, `poc-orchestrator`)
3. **Agents** — 27 specialists
4. **Skills** — 22 reusable capabilities
5. **Memory** — `docs/` + MCP `memory` server
6. **MCP servers** — declared in [`knowledge/mcp/servers.yaml`](knowledge/mcp/servers.yaml) with `core` (always emitted) and `extended` (opted-in per platform) tags.

See [`AGENTS.md`](AGENTS.md) for the workspace contract and [`SECURITY.md`](SECURITY.md) for security trade-offs you must review before deploying.

---

## What changed vs v1

- **Single source of truth** — knowledge lives only in `knowledge/`, no triple duplication.
- **Cursor support** added (`.cursor/`).
- **MCP single registry** — `mcp/servers.yaml` replaces three divergent JSON configs.
- **Drift CI** — `verify.mjs` keeps generated folders honest.
- **`docs/` templates** populated (was empty `.gitkeep` placeholders in v1).
- **Security docs** — `SECURITY.md` documents auto-approve trade-offs and removes the leaked Toolradar API key.
- **`.gitignore`** added to keep `node_modules/` and runtime junk out of VCS.
- **Platform-detail plan docs** for Phase 2–7 backfilled under [`../plan/`](../plan/).

See [`../plan/05-migration-from-v1.md`](../plan/05-migration-from-v1.md).
