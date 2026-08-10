# Prerequisites — emage.code implementation

## Required
- **Node.js 18+** — for `scripts/sync.mjs` and for MCP servers launched via `npx`.
- **Python 3.10+** — for `check.py`, `package.py`, and registry generation.
- **Git 2.30+** — for worktree isolation, branch policies, and pack install from git URLs.

## Per-platform
| Platform | Requirement |
|----------|-------------|
| GitHub Copilot | VS Code 1.90+, GitHub Copilot + Copilot Chat extensions, MCP support enabled |
| Gemini CLI | `npm install -g @google/gemini-cli` |
| Opencode | `npm install -g opencode-ai` |
| Cursor | Cursor 0.42+ (rules + commands + MCP support) |
| Pi | [pi.dev](https://pi.dev) terminal agent |

## MCP server credentials (env vars)

Set whichever you need before launching the AI tool. See [`SECURITY.md`](SECURITY.md) for handling guidance.

### Core
- `GITLAB_PERSONAL_ACCESS_TOKEN` — read_api, write_repository, read_user
- `GITLAB_API_URL` — defaults to `https://gitlab.com/api/v4`
- `BRAVE_API_KEY`

### Extended (optional)
- `TOOLRADAR_API_KEY`
- platform-specific tokens for `github`, `supabase`, `postgresql`

## Verifying

From the repository root:

```bash
node --version           # ≥ 18
python3 --version        # ≥ 3.10
git --version            # ≥ 2.30
make sync && make verify
```

From `implementation/scripts/`:

```bash
./sync.sh
./verify.sh
```

```powershell
.\sync.ps1
node verify.mjs --root ..
```
