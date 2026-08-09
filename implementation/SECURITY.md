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

Servers in `knowledge/mcp/servers.yaml` reference credentials via `${env:VAR}` (or `{env:VAR}` for Opencode). The sync engine emits these placeholders verbatim — secrets are never written to generated files.

**Required env vars (core):**
- `GITLAB_PERSONAL_ACCESS_TOKEN`, `GITLAB_API_URL`
- `BRAVE_API_KEY`

**Required env vars (extended; only if you enable those servers):**
- `TOOLRADAR_API_KEY` — see warning below.

> **v1 leaked a live `TOOLRADAR_API_KEY` value (`tr_live_…`) directly in `.vscode/mcp.json`, `.opencode/opencode.json`, and `.gemini/settings.json`.** v2 replaces it with an env-var reference. **If you are migrating from v1, rotate that key immediately** with the issuing party.

Set credentials via:
- a per-user env-var (Windows: `setx`, Linux/macOS: shell rc file)
- a `.env` file consumed by your shell, **never committed**
- a secret manager (Azure Key Vault, AWS Secrets Manager, 1Password CLI, …)

---

## 3. MCP server reachability

`extended` servers reach external infrastructure (Hugging Face, Supabase, Docker socket, Postgres). Enabling them in your platform manifest grants the AI access to those systems via MCP. Audit each server before use.

`docker` and `filesystem` MCPs in particular can read/write outside your project directory. Restrict their configuration (allowed paths, allowed images) at the host level.

---

## 4. Code-execution surface

emage.code agents have `execute` tool access by default. Combined with broad terminal auto-approval, this is effectively a remote shell guided by an LLM. Treat any untrusted input that flows into agent context (web fetches, MCP responses, third-party PRs) as adversarial. The included `knowledge/instructions/security-guidelines.md` covers OWASP Top 10 considerations for generated code; review it during onboarding.

---

## 5. Reporting

Found a vulnerability? Open a private security advisory in the source repository or contact the maintainers directly. Do not file public issues for credentials or exploit paths.
