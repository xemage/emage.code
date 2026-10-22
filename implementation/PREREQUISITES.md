# Prerequisites — emage.code implementation

## Required
- **Node.js 18+** — for `scripts/sync.mjs` and for MCP servers launched via `npx`.
- **Python 3.10+** — for `check.py`, `package.py`, and registry generation.
- **Git 2.30+** — for worktree isolation, branch policies, and pack install from git URLs. The optional `poc-security-audit` server needs **Git 2.40+** (see below).

## Browser for the `playwright` server
The `playwright` MCP server (`@playwright/mcp`) does not bundle a browser and does not download one on first use. Without it the first browser tool call fails (`Chromium distribution ... is not found`). Install the browser once, with the command pinned to the same version as the server entry:
```bash
npx -y @playwright/mcp@0.0.83 install-browser chrome-for-testing
```
- **Size:** about 670 MB on disk (Chrome for Testing, its headless shell and ffmpeg). The download comes from `cdn.playwright.dev`. The plain `playwright install chromium --no-shell` route fetches only Chromium plus ffmpeg (about 400 MB), but it needs the separate `playwright` CLI, which `npx` resolves to whatever release is current unless you pin it; it is not the lead command because it can fetch a different browser revision than the one the pinned server expects.
- **Version:** the browser revision follows the pinned `@playwright/mcp` version (`chromium-1247`, Chrome for Testing 155.0.8059.12, for 0.0.83). Each pin bump can force a new download. The browser is patched only when the pin is bumped, not by your operating system (a system Chrome would be); check the browser's security version at every pin bump.
- **What is verified about the download:** the revision, the sizes and the install time above were observed once, on one Linux host (T654). That run did not check whether Playwright verifies a checksum or signature of the downloaded archive, and this repository pins no hash of it **(unverified)**. Treat the download as trusted only to the extent that you trust `cdn.playwright.dev` and the npm package.
- **Why `--browser chromium`:** the default channel is Google Chrome, which needs an OS package and usually root. The entry sets `--browser chromium` so the Playwright-managed Chrome for Testing is used.
- **Sandbox:** the entry sets `--sandbox` (the default would run Chromium with `--no-sandbox`). `--sandbox` worked on the test host; it can fail in containers and on hosts that block unprivileged user namespaces **(unverified there)**. Removing it from your local config weakens the browser isolation; do so only knowingly, and `install.sh --update` restores the generated arguments.
- **Output directory:** browser output (page snapshots, downloads from visited pages) goes to `.playwright-mcp/` under the launch directory. It is git-ignored in this repository only; `install.sh` does not edit your project's `.gitignore`. In a project that installed emage.code, add `.playwright-mcp/` to its `.gitignore` (or point `--output-dir` at an ignored path in a user-owned entry), otherwise page content can be committed by accident.

### Local apps are blocked by the shipped entry
The shipped `playwright` entry carries a `--blocked-origins` list that denies `localhost`, `127.*`, `*.localhost`, `10.*`, `192.168.*` and `172.16` to `172.31` (plus other loopback, link-local and carrier-grade-NAT forms). Its first request to a local dev server therefore fails with `net::ERR_BLOCKED_BY_CLIENT`. **The shipped entry cannot test a local app.** This is the intended hardening, not a fault.

If you need to test a local app, add a second entry of your own, named `playwright-local`, in your MCP config file (for example `.mcp.json` for Claude Code). Do not edit the arguments of `playwright` itself: they are generator-owned and `install.sh --update` restores them.
```json
"playwright-local": {
  "command": "npx",
  "args": ["-y", "@playwright/mcp@0.0.83", "--headless", "--isolated", "--browser", "chromium", "--sandbox", "--block-service-workers", "--no-webmcp"]
}
```
- **Warning:** this entry has no origin restriction. A page it opens can redirect to, or load, any address your host reaches, including internal services and cloud metadata endpoints, and the page content is returned to the model. Use it only on a development machine, only for your own pages, and remove it when you are done.
- **Survives `install.sh --update`:** `scripts/merge-mcp-json.py` keeps keys that exist only in your file, and it prunes a name only if the old provenance sidecar lists it as generator-owned or you name it in `--force-prune-keys`. `playwright-local` is neither, so it is kept (verified by reading the script and by a test in `tests/functional/test_mcp_package_pins.py`).
- **Tool names and agents:** this server's tools are named after the server (for Claude Code `mcp__playwright-local__browser_navigate`). The generated agent tool lines list tools of the `playwright` server (for example `mcp__playwright__browser_navigate`, rendered per platform), not of `playwright-local`, so on Claude Code, GitHub Copilot/VS Code and Pi (for an agent that lists an `mcp__` tool) a subagent such as `qa-engineer` does not receive the new server's tools. On Opencode and Gemini CLI an agent's tool list does not restrict MCP tools, so any agent can call them, including `browser_run_code_unsafe`; the server-level denial below covers the `playwright` server only, so `playwright-local` is not denied there. Use it from your own session on a development machine, remove it when you are done, or add the names to a local copy of an agent file (a later `--update` overwrites that copy). The per-platform tool-name forms are recorded in `docs/artifacts/mcp-tool-name-mapping-v1.md` (recorded before Cursor was removed; its Cursor rows are historical).
- **Server-level denial of six tools (T658):** on Opencode and Gemini CLI, where an agent's tool list does not restrict MCP tools, the generated configs deny `browser_run_code_unsafe`, `browser_evaluate`, `browser_file_upload`, `browser_drag`, `browser_drop` and `browser_network_request` for the shipped `playwright` server (Opencode: top-level `permission` entries `playwright_<tool>: deny` in `.opencode/opencode.json`; Gemini CLI: `excludeTools` on the `playwright` entry of `.gemini/settings.json`). The list is `denyTools` in `implementation/knowledge/mcp/servers.yaml`. This follows the vendor documentation and source and has **not been observed in a live run**. Since T663 the Opencode generator also writes per-agent `false` entries into every agent file (per-agent): the six Playwright names for every agent, and `<server>_*: false` for every server that the agent holds no token of and that is not exempt (`denyUnlessGranted: true` on gitlab, playwright, memory, sequential-thinking, security-audit, poc-security-audit, context-retriever, filesystem, github, git and supabase), after its allows; an agent that holds only named tools of a server (all seven GitLab holders for `gitlab`: qa-engineer, scrum-master, orchestrator, poc-orchestrator, devops-engineer, release-manager and poc-devops-engineer; the Playwright agents, the security agents, context-retriever) gets that server's wildcard first, so it can call only its named tools. The read/search and memory-layer servers brave, context7, hindsight, cwso, hf-mcp-server and toolradar are exempt (`denyUnlessGranted: false`, user decision of 2026-10-16), so generated agents, including a primary orchestrator, keep them; a non-exempt server that no agent lists (filesystem, github, git, supabase) is denied in every generated agent file, as on Claude Code, where a subagent without the token cannot call it; the entries are documented and read from vendor source, not observed in a live tool call (`docs/artifacts/mcp-agent-denials-v1.md`, `docs/artifacts/mcp-agent-denials-evidence-v1.md`). On Opencode the `true` entries an agent holds come after your global config, so your own global `ask` or `deny` on a tool an agent holds is silently overridden for that agent; for example a global `ask` on `gitlab_create_merge_request` is overridden for the three agents that hold it (orchestrator, poc-orchestrator, release-manager). Since T667 no agent holds the whole `gitlab` server, so every `true` entry is a named tool and you can still override only the tools an agent holds; a tool that no agent holds, such as `gitlab_merge_merge_request`, stays denied in every generated agent file whatever your global rule says (`gitlab_*: false` comes first in each holder's map). No supported way through the generated files or through your project or global configuration keeps a prompt there (an `agent.<name>.permission` entry in your project config is also placed before the agent's own rules); only a source that Opencode loads after the agent files can, the environment variable `OPENCODE_CONFIG_CONTENT` (observed on opencode-ai 1.19.2) and, by source reading only, the managed configuration (SEC-T657-04, SEC-T663-03; `docs/artifacts/mcp-agent-denials-evidence-v1.md`). The `<server>_*` wildcards also match a user-owned server whose cleaned name starts with that prefix and an underscore (a server `gitlab_ee` is matched by `gitlab_*`, `gitlab-ee` is not); for an agent without the server that fails closed. Saved "always" approvals do not undo a deny: the legacy runtime hides a tool whose last matching rule is a deny, and the current core tests `denied()` before it adds saved approvals (source reading; an approval saved before the deny existed is unverified). Opencode's built-in agents (build, plan, general, explore, ...) and agent files of your own get no per-agent deny and no global GitLab deny; only the server-level `permission` of `.opencode/opencode.json` (the six Playwright tools) applies to them, so every other tool of every configured server, GitLab included, remains reachable through them. That gap is a decision of the user (2026-10-16, "No, document the gap only") and is tracked. A user-owned `playwright-local` entry is another server name and is not denied by either list. `install.sh --update` keeps your own `permission` and `excludeTools` entries (it unions the lists and keeps your rules) and puts the generated denial back; evidence: `docs/artifacts/mcp-server-denials-v1.md` (recorded before Cursor was removed; its Cursor rows are historical).

## Optional (extended MCP servers)
- **uv** (provides `uvx`) — launches the `git` server (`uvx mcp-server-git@<pinned version>`). Install from <https://docs.astral.sh/uv/>.
- **Docker** — runs the `github` server as a container pinned by digest (`docker run -i --rm ghcr.io/github/github-mcp-server@sha256:...`). The Docker daemon must be running and able to pull from `ghcr.io`.

- **`poc-security-audit` server (PoC security scan; optional)** — needs Python `mcp==2.2.0` (`pip install -r implementation/runtime/security/requirements-mcp-server.txt`, in a virtual environment that the `python3` your assistant launches can use; the installer prints the command) and **Git 2.40 or newer** on `PATH`: an older git makes every call fail closed as `git_failed`. Its config is generated for every platform except GitHub Copilot (Claude Code also needs an allow rule in your own `.claude/settings.json`). Setup steps: the "Optional: the PoC security scan server" section of `README.md`.

Start your assistant from the project root. The `filesystem` (`.`) and `git` (`--repository .`) servers resolve the path against the launch directory; Cline's configuration is global, so use an absolute path there. The `filesystem` server can read every file in the workspace, including `.env*` files and `.git`, and the `git` server exposes write tools.

### Pin-bump policy
MCP servers launched via `npx`, `uvx` or `docker` are pinned to exact versions or digests in `implementation/knowledge/mcp/servers.yaml` (audit SEC-002); do not replace a pin with `@latest` or a range. The devops-engineer bumps the pins at every release and at least monthly; there is no automated scheduler. Each bump is a reviewed change that edits `servers.yaml` and the `APPROVED_NPX_PINS` dict in `tests/functional/test_mcp_package_pins.py` together. Before a bump, check the package with `npm audit` or OSV, and check the registry's latest version and provenance. `@zereight/mcp-gitlab` holds the GitLab token, has a single maintainer, and releases often with published advisories, so it is reviewed at every release. The flags of the `playwright` entry (hardening and `--blocked-origins`) are part of the approved form: a bump of `@playwright/mcp` re-checks them against the new version's `--help`, re-checks the browser revision, and updates the pinned flags test.

### Upgrading from v7.x
After `scripts/install.sh --update`, the `filesystem`, `git`, `github` and `supabase` entries are overwritten in place. The `playwright` entry is hardened and needs Chrome for Testing (above). The `docker`, `postgresql` and `fetch` servers (`fetch`: audit SEC-T646-01) are removed from the generated configs; the update drops them from an installed config only if its `.provenance.json` sidecar lists them. Otherwise remove them by hand or with `python3 scripts/merge-mcp-json.py --source <generated file> --dest <your file> --force-prune-keys <name>`, run once per name and per file (`install.sh` does not pass this option). Use the per-name form: the combined `--force-prune-keys docker,postgresql,fetch` refuses and writes nothing if any one of the names is already gone from that file, which is the usual case after a partial clean-up. The `fetch` name alone is `--force-prune-keys fetch`. A server entry of your own named `docker`, `postgresql` or `fetch` is removed too if the old sidecar lists those names. A run without a sidecar writes one that does not list them, so later automatic pruning cannot remove them. Client approval for the changed servers may be requested again. Full steps: `docs/wiki/mcp-servers.md`.

## Per-platform
| Platform | Requirement |
|----------|-------------|
| GitHub Copilot | VS Code 1.90+, GitHub Copilot + Copilot Chat extensions, MCP support enabled |
| Gemini CLI | `npm install -g @google/gemini-cli` |
| Opencode | `npm install -g opencode-ai` |
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
git --version            # ≥ 2.30 (≥ 2.40 for the poc-security-audit server)
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
