# Task T372 — Execute repo-root update install (item 2)

**ID:** T372
**Owner:** devops-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T371
**Created:** 2026-08-09
**Completed:** —
**Based on:** docs/plans/plan-031-install-mcp-json-merge-and-repo-update.md

## Objective
This repo self-hosts its own install at its root (`scripts/install.sh`'s own comment at ~line 71).
Cline was added as a supported platform in v6.8.0 (T352-T357) but the root self-install was never
refreshed to include it — `.cline/`/`.clinerules/` do not yet exist at repo root, and other
platforms' root trees are stale relative to `implementation/`. Now that T371 has merged the
merge-safe installer to `develop`, run a real `--update` install at the repo root using that fixed
installer so `.cline/`/`.clinerules/` are installed for the first time, all other platforms refresh
to latest, and — critically — the hand-maintained `cwso` entry in `.vscode/mcp.json` survives as
living proof T368's merge fix actually works outside of unit tests.

## Inputs
- `develop` post-T371 merge (must be checked out fresh, not the pre-merge worktree)
- `scripts/install.sh` usage/help text (`scripts/install.sh --help` or its `usage()` function) and
  `README.md`'s documented update-mode invocation — read the actual flags, do not guess
- Current repo-root state (`.vscode/mcp.json`'s `cwso` entry, absence of `.cline/`/`.clinerules/`)

## Expected outputs
- Repo-root filesystem changes: `.cline/`, `.clinerules/` created; `.claude/`, `.cursor/`, `.github/`,
  `.gemini/`, `.opencode/`, `.pi/` refreshed to latest generated content; `.vscode/mcp.json` and
  `.mcp.json` updated via the new merge path
- Committed via branch + MR (not left as uncommitted working-tree state on `develop`)

## Acceptance criteria
1. `git status` captured before running the install; full diff captured after — no unexpected
   destruction of existing root content (review every changed/deleted file).
2. `.cline/` and `.clinerules/` exist post-install with the expected generated content (matching
   `implementation/.cline/`/`implementation/.clinerules/`).
3. `.vscode/mcp.json` contains the `cwso` entry (headers and `${input:cwso_jwt_token}` placeholder
   intact, no literal secret ever written) AND all current generator-sourced keys, including the
   corrected `context7` `"type": "http"` field from T361/T362.
4. `.mcp.json` reflects current generator output (and preserves any legitimate hand-added content,
   per T368's audit finding).
5. Result committed through the normal branch + MR flow, CI green, merged to `develop` — no
   destructive git operations without asking first.
6. Full verification bar green again after the update.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
