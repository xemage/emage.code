# Prerequisites for emage.code

## Required

### AI Assistants (Choose one)

#### 1. VS Code with GitHub Copilot
- **Visual Studio Code** — Latest stable version
- **GitHub Copilot extension** — Active subscription required
- **GitHub Copilot Chat extension** — For slash commands and agent interaction

emage.code uses Copilot's agent mode with custom agents (`.github/agents/`), slash commands (`.github/prompts/`), and skills (`.github/skills/`).

#### 2. Gemini CLI
- **Gemini CLI** — `@google/gemini-cli` installed globally
- Uses custom agents (`.gemini/agents/`), commands (`.gemini/commands/`), and skills (`.gemini/skills/`).

#### 3. Opencode
- **Opencode AI** — `opencode-ai` installed globally
- Uses custom agents (`.opencode/agents/`), commands (`.opencode/commands/`), and skills (`.opencode/skills/`).

### Node.js (18+)

Required for running MCP servers via `npx`. All 7 MCP servers are launched through `npx` in `.vscode/mcp.json` or `opencode.json`.

```bash
node --version   # Must be >= 18.0.0
```

### Git

Required for the worktree isolation skill. emage.code uses Git worktrees to provide file-system isolation for parallel workstreams.

```bash
git --version    # Any modern version
```

## Required for Full Functionality

### GitLab Account + API Token

The `gitlab` MCP server requires:
- A GitLab account (gitlab.com or self-hosted)
- A personal access token with `api` scope

Set the following environment variables:
```
GITLAB_PERSONAL_ACCESS_TOKEN=<your-token>
GITLAB_API_URL=https://gitlab.com/api/v4/api/v4    # or your self-hosted URL
```

## Optional

### Brave Search API Key

For the `brave-search` MCP server (web search capability):
- Sign up at [brave.com/search/api](https://brave.com/search/api/)
- Set the environment variable:
```
BRAVE_API_KEY=<your-key>
```

### Playwright Dependencies

For the `playwright` MCP server (browser automation and testing):
- Playwright is installed automatically via `npx`
- Browser binaries may need to be installed on first run:
```bash
npx playwright install
```

## Environment Variables Summary

| Variable | Required | Purpose |
|----------|----------|---------|
| `GITLAB_PERSONAL_ACCESS_TOKEN` | Yes (for GitLab) | GitLab MCP server authentication |
| `GITLAB_API_URL` | Yes (for GitLab) | GitLab API endpoint |
| `BRAVE_API_KEY` | Optional | Brave Search MCP server |

## Verification

After installing prerequisites, verify your setup:

```bash
code --version                          # VS Code installed
code --list-extensions | grep copilot   # Copilot extensions installed
node --version                          # Node.js 18+
git --version                           # Git available
```
