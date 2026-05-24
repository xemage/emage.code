# Prerequisites — emage.code v3

## Required
- **Node.js 18+** — for `scripts/sync-v3.mjs` and for MCP servers launched via `npx`.
- **Git 2.30+** — for worktree isolation, branch policies.

## Per-platform
| Platform | Requirement |
|----------|-------------|
| GitHub Copilot | VS Code 1.90+, GitHub Copilot + Copilot Chat extensions, MCP support enabled |
| Gemini CLI | `npm install -g @google/gemini-cli` |
| Opencode | `npm install -g opencode-ai` |
| Cursor | Cursor 0.42+ (rules + commands + MCP support) |

## MCP server credentials (env vars)

Set whichever you need before launching the AI tool. See [`SECURITY.md`](SECURITY.md) for handling guidance.

### Core
- `GITLAB_PERSONAL_ACCESS_TOKEN` — read_api, write_repository, read_user
- `GITLAB_API_URL` — defaults to `https://gitlab.com/api/v4`
- `BRAVE_API_KEY`

### Extended (optional)
- `TOOLRADAR_API_KEY`
- platform-specific tokens for `github`, `supabase`, `e2b`, `figma`, `notion`, `redis`, `postgresql`

## Verifying

```bash
node --version           # ≥ 18
git --version            # ≥ 2.30
node v3/implementation/scripts/sync-v3.mjs    # emits 4 platform folders
node v3/implementation/scripts/verify-v3.mjs  # exits 0
```

```powershell
node --version           # ≥ 18
git --version            # ≥ 2.30
node scripts/sync-v3.mjs    # emits 4 platform folders
node scripts/verify-v3.mjs  # exits 0
```
