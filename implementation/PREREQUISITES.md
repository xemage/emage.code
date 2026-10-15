# Prerequisites — emage.code implementation

## Required
- **Node.js 18+** — for `scripts/sync.mjs` and for MCP servers launched via `npx`.
- **Python 3.10+** — for `check.py`, `package.py`, and registry generation.
- **Git 2.30+** — for worktree isolation, branch policies, and pack install from git URLs.

## Browser for the `playwright` server
The `playwright` MCP server (`@playwright/mcp`) does not bundle a browser and does not download one on first use. Without it the first browser tool call fails (`Chromium distribution ... is not found`). Install Chromium once:
```bash
npx playwright install chromium
```
- **Size:** about 400 MB on disk (Chromium plus ffmpeg; the headless shell is not needed). The download comes from `cdn.playwright.dev`.
- **Version:** the browser revision follows the pinned `@playwright/mcp` version (`chromium-1247` for 0.0.83). `npx playwright install chromium` installs the revision of whichever `playwright` release `npx` resolves, which can differ from the pin **(unverified)**. The command verified for the pinned version is `npx -y @playwright/mcp@0.0.83 install-browser chrome-for-testing` (it also fetches the headless shell, about 670 MB in total). Each pin bump can force a new download.
- **Why `--browser chromium`:** the default channel is Google Chrome, which needs an OS package and usually root. The entry sets `--browser chromium` so the Playwright-managed Chromium is used.
- **Sandbox:** the entry sets `--sandbox` (the default would run Chromium with `--no-sandbox`). `--sandbox` worked on the test host; it can fail in containers and on hosts that block unprivileged user namespaces **(unverified there)**. Removing it from your local config weakens the browser isolation; do so only knowingly, and `install.sh --update` restores the generated arguments.
- Browser output goes to `.playwright-mcp/` under the launch directory (git-ignored).

## Optional (extended MCP servers)
- **uv** (provides `uvx`) — launches the `git` server (`uvx mcp-server-git@<pinned version>`). Install from <https://docs.astral.sh/uv/>.
- **Docker** — runs the `github` server as a container pinned by digest (`docker run -i --rm ghcr.io/github/github-mcp-server@sha256:...`). The Docker daemon must be running and able to pull from `ghcr.io`.

Start your assistant from the project root. The `filesystem` (`.`) and `git` (`--repository .`) servers resolve the path against the launch directory; Cline's configuration is global, so use an absolute path there. The `filesystem` server can read every file in the workspace, including `.env*` files and `.git`, and the `git` server exposes write tools.

### Pin-bump policy
MCP servers launched via `npx`, `uvx` or `docker` are pinned to exact versions or digests in `implementation/knowledge/mcp/servers.yaml` (audit SEC-002); do not replace a pin with `@latest` or a range. The devops-engineer bumps the pins at every release and at least monthly; there is no automated scheduler. Each bump is a reviewed change that edits `servers.yaml` and the `APPROVED_NPX_PINS` dict in `tests/functional/test_mcp_package_pins.py` together. Before a bump, check the package with `npm audit` or OSV, and check the registry's latest version and provenance. `@zereight/mcp-gitlab` holds the GitLab token, has a single maintainer, and releases often with published advisories, so it is reviewed at every release. The flags of the `playwright` entry (hardening and `--blocked-origins`) are part of the approved form: a bump of `@playwright/mcp` re-checks them against the new version's `--help`, re-checks the browser revision, and updates the pinned flags test.

### Upgrading from v7.x
After `scripts/install.sh --update`, the `filesystem`, `git`, `github` and `supabase` entries are overwritten in place. The `playwright` entry is hardened and needs Chromium (above). The `docker`, `postgresql` and `fetch` servers (`fetch`: audit SEC-T646-01) are removed from the generated configs; the update drops them from an installed config only if its `.provenance.json` sidecar lists them. Otherwise remove them by hand or with `python3 scripts/merge-mcp-json.py --source <generated file> --dest <your file> --force-prune-keys docker,postgresql,fetch` (per file; `install.sh` does not pass this option). A server entry of your own named `docker`, `postgresql` or `fetch` is removed too if the old sidecar lists those names. A run without a sidecar writes one that does not list them, so later automatic pruning cannot remove them. Client approval for the changed servers may be requested again. Full steps: `docs/wiki/mcp-servers.md`.

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
- `GITHUB_PERSONAL_ACCESS_TOKEN` — `github` server; passed into the container by name (`-e`), never on the command line
- `SUPABASE_ACCESS_TOKEN` — `supabase` server (started with `--read-only`); read from the environment, never from argv

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
