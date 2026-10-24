# SECURITY — emage.code v3

This file documents security trade-offs you must review **before** copying emage.code into a project.

---

## 1. Auto-approved terminal commands (`.vscode/settings.json`)

`chat.tools.terminal.autoApprove` lets the AI execute the listed commands **without prompting the user**. emage.code v1 shipped with a broad list (git, dotnet, go, node, gemini, opencode, …) for productivity. v2 keeps the same defaults to preserve workflow parity.

**Implications:**
- Any prompt-injected agent could run, for example, `git push --force` or `dotnet build` against a malicious payload without your confirmation.
- The list does **not** include destructive commands like `rm -rf` or `git reset --hard`, but `git push`, `git commit`, and `git tag` are pre-approved — meaning published commits/tags can be created silently.

**Recommended hardening:**
1. Review `.vscode/settings.json` and remove anything you don't need.
2. Never enable auto-approval for `npm publish`, `cargo publish`, `terraform apply`, `kubectl apply`, or any deploy/destroy verb.
3. Run emage.code only inside a per-project Git worktree with branch protection on `main` / `develop`.
4. For untrusted repositories, **delete `.vscode/settings.json` entirely** and rely on per-command prompts.

---

## 2. MCP server credentials

Servers in `knowledge/mcp/servers.yaml` reference credentials via a per-platform placeholder form: `${env:VAR}` (VS Code / GitHub Copilot, Cline), `{env:VAR}` (Opencode), `${VAR}` (Pi, which documents `${VAR}` and does not expand `${env:VAR}`, T680; Gemini CLI, which documents `$VAR` and `${VAR}`, not `${env:VAR}`), and `${VAR}` (Claude Code — it expands `${VAR}` and `${VAR:-default}` from the live process environment and does **not** recognise the `${env:…}` form; see `docs/artifacts/mcp-header-url-templating-design-v2.md` §3 and §9). The sync engine emits these placeholders verbatim — secrets are never written to generated files.

**Required env vars (core):**
- `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` (a path to a mode 0600 file that holds the token; recommended) or `GITLAB_PERSONAL_ACCESS_TOKEN`, and `GITLAB_API_URL`; scope `api` limited by role, expiry at most 90 days: `PREREQUISITES.md`, "GitLab token"
- `BRAVE_API_KEY`
- `HINDSIGHT_MCP_URL`

**Required env vars (extended; only if you enable those servers):**
- `CWSO_MCP_URL`, `CWSO_BEARER_TOKEN`, `CWSO_ORIGIN` (the bearer token is sent as `Authorization: Bearer <value>`)
- `TOOLRADAR_API_KEY` — see warning below.
- `SUPABASE_ACCESS_TOKEN` (`supabase`, started with `--read-only`, read from the environment, never from argv). The Supabase token is account-wide: `--read-only` limits the server's tools, not the token. Scoping to one project and the hosted OAuth alternative: `PREREQUISITES.md`, "MCP server credentials".

The extended Python servers `security-audit` and `poc-security-audit` need no environment variable and no API key; they make local calls only.

> **v1 leaked a live `TOOLRADAR_API_KEY` value (`tr_live_…`) directly in `.vscode/mcp.json`, `.opencode/opencode.json`, and `.gemini/settings.json`.** v2 replaces it with an env-var reference. **If you are migrating from v1, rotate that key immediately** with the issuing party.

Set credentials via:
- a per-user env-var (Windows: `setx`, Linux/macOS: shell rc file)
- a `.env` file consumed by your shell, **never committed**
- a secret manager (Azure Key Vault, AWS Secrets Manager, 1Password CLI, …)

---

## 3. MCP server reachability

`extended` servers reach external infrastructure (Hugging Face, Supabase, the local file system and git repositories). Enabling them in your platform manifest grants the AI access to those systems via MCP. Audit each server before use.

The `filesystem` MCP reads every file under the directory it is launched in (`.`), including `.env*` files and `.git`; start the assistant from the project root and keep secrets out of that directory. The `git` MCP exposes write tools. Restrict their configuration at the host level.

Every `npx` and `uvx` server is pinned to an exact version, and the pins are reviewed at every release and at least monthly. See "Pin-bump policy" in `PREREQUISITES.md`; do not replace a pin with `@latest`.

---

## 4. Code-execution surface

emage.code agents have `execute` tool access by default. Combined with broad terminal auto-approval, this is effectively a remote shell guided by an LLM. Treat any untrusted input that flows into agent context (web fetches, MCP responses, third-party PRs) as adversarial. The included `knowledge/instructions/security-guidelines.md` covers OWASP Top 10 considerations for generated code; review it during onboarding.

### 4.1 Fixed-command scan tools and the client-owned allow rule

The PoC security reviewer (`poc-security-engineer`) is the exception to the `execute` default: its tool grant has no `execute`. It scans with fixed-command MCP tools instead: `scan_secrets` and `ref_containment` from the `poc-security-audit` server, and `grep_content` from the `security-audit` server. Their results never contain matched text, `stderr` or the command line.

- **A clean result is not proof of absence.** It means no match for the fixed rule set at the scanned refs. A secret in a format the rule set does not list, a short or unusual value, a dangling object or a reflog-only commit is not found, and a scan that did not complete (`complete: false`, `truncated`, an error) proves nothing. The reviewer reports such a scan as `FAIL`, never `PASS`.
- **Scope is a directory, not one repository.** The server is started with `--allowed-root .`, and `root_dir` must be a repository top level inside it; any other git repository located below that directory can be scanned too. The launch directory decides what `.` means, so start the assistant from the project root (the VS Code entry for GitHub Copilot sets `"cwd": "${workspaceFolder}"`, so open the project root as the workspace folder).
- **Submodules are not scanned.** The scan runs `git grep` without `--recurse-submodules`, so with default git configuration the content of a submodule is outside every scope (a repo-local `submodule.recurse` setting could change that; unverified); scan a submodule as a repository of its own (whether the server accepts a submodule's top level as `root_dir` was not tested). Details: [MCP Servers](../docs/wiki/mcp-servers.md#poc-security-scan-server-poc-security-audit).
- **Permissions are yours to grant.** The installer never writes `.claude/settings.json` or `.claude/settings.local.json` (`--update` and `--projections-only` leave both untouched). To pre-approve the tools in Claude Code, add `"mcp__poc-security-audit__*"` (and `"mcp__security-audit__*"` for `grep_content`) to `permissions.allow` in your own `.claude/settings.json`. Grant only what you have reviewed; the rule is a standing approval for every tool of that server. Requirements, platform availability and limits: [MCP Servers](../docs/wiki/mcp-servers.md#poc-security-scan-server-poc-security-audit).

---

## 5. Reporting

Found a vulnerability? Open a private security advisory in the source repository or contact the maintainers directly. Do not file public issues for credentials or exploit paths.
