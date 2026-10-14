# T637 — Verify the MCP server packages the configs launch, and propose corrected and pinned entries (audit SEC-002)

**ID:** T637
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Addendum 2: T637)
- `docs/artifacts/security-review-release-v8-v1.md` (SEC-002) and the orchestrator's finding that the four names pre-date v7.0.1
- `implementation/knowledge/mcp/servers.yaml` (the source of truth), `implementation/.mcp.json` and the other generated platform configs, `scripts/` and `implementation/scripts/sync.mjs` (the generator)
- The user's decisions of 2026-10-14 on the T633 audit (AskUserQuestion, verbatim option labels): SEC-001 "Yes, fix before the release (Recommended)"; SEC-002 "Fix before the release (Recommended)"; SEC-003 "I'll check; both are set (grade drops to LOW)".

## 1. What and why

Research only; change no file except your artifact. For every server in `servers.yaml` that launches a package with `npx` or `uvx` (and the four known-bad entries: `@anthropic/mcp-filesystem`, `@github/mcp-github`, `@modelcontextprotocol/mcp-git`, `@supabase/mcp`), establish from the npm registry / package index (WebFetch/WebSearch) whether the package exists, who owns the scope and whether it is the vendor's own, the latest published version and publish date, the repository link, download or maintenance signals, and any advisories you can find; for the four nonexistent names, find the vendor's documented real launcher or package (candidates to check: `@modelcontextprotocol/server-filesystem`, the git server, GitHub's official MCP server, `@supabase/mcp-server-supabase`) and say if the entry should instead be removed. Propose the exact corrected `servers.yaml` entries with an exact pinned version for every npx entry (and whether `-y` should stay), flag entries whose upstream is a single maintainer, and state the impact on each platform projection. Do NOT edit `servers.yaml` or run the generators: the proposal comes back to the user for approval of the names and pins before a later task applies it.

## 2. Output

`docs/artifacts/mcp-server-packages-v1.md`: a per-server evidence table, the corrected and pinned entries as exact YAML, the risks, and a list of what you could not verify.

## 3. Constraints

- You have WebFetch/WebSearch and a shell. Write only your artifact. Do not commit, push or merge. Do not edit `servers.yaml`, generated configs, ledgers or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere. No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.

## 4. Acceptance criteria

1. Every npx/uvx entry has evidence (existence, owner, version, date, source) or a stated gap.
2. Exact replacement entries are given for the four known-bad names, or an explicit remove recommendation with the reason.
3. No file other than the artifact is modified.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
