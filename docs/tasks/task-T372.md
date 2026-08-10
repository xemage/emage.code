# Task T372 — Execute repo-root update install (item 2)

**ID:** T372
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** T371
**Created:** 2026-08-09
**Completed:** 2026-08-09
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
Checked out fresh `develop` post-T371/MR !159 merge (`3b8ddfc`), branched
`chore/T372-repo-root-self-install-update`. Read `scripts/install.sh --help` for the exact
invocation, ran `bash scripts/install.sh --target . --platform all --update --dry-run` first to
preview (confirmed `merge-mcp-json.py` — not plain `cp` — is invoked for both `.vscode/mcp.json` and
`.mcp.json`, proving T368's fix is live), captured `git status`/full repo listing as the before
snapshot, then ran the real `--update`.

Result:
- `.cline/` and `.clinerules/` created for the first time, byte-identical to
  `implementation/.cline/`/`implementation/.clinerules/` (`diff -r` clean).
- `.vscode/mcp.json`: only `context7` changed (gained `"type": "http"`, the generator-known refresh
  from T361/T362); `cwso` entry (url, headers, `Authorization: Bearer ${input:cwso_jwt_token}`
  placeholder) and the top-level `inputs` block are byte-for-byte unchanged — no literal secret
  anywhere, only the placeholder syntax.
- `.mcp.json`: no diff (still byte-identical to generator output, as T368's audit found).
- `.claude/`, `.cursor/`, `.github/`, `.gemini/`, `.opencode/`, `.pi/`: no diff (root trees were
  already current with `implementation/`, confirming `make verify` was accurate pre-update).
- `docs/tasks/active-tasks.md`/`completed-tasks.md`: no diff (already current from the T368-T371
  closeout).

Two collateral changes surfaced from `install_tree_into`'s `rsync --delete` / `render_installed_agents.py`
behavior, both **reverted** (`git checkout -- .claude/settings.json AGENTS.md`) as out-of-scope for
this plan, matching the T362 precedent of reverting the same class of collateral rather than silently
committing it:
1. `.claude/settings.json` — a hand-maintained, repo-root-only file with no counterpart in
   `implementation/.claude/`; `rsync --delete` wipes anything not in the source tree. Not a MCP-JSON
   issue (out of plan-031's scope), reverted.
2. `AGENTS.md` — **new finding, not previously tracked**: `scripts/render_installed_agents.py`'s
   `render()` function has a `platform == "all"` branch with hardcoded `skills_ref`/`code_ref`/
   `sec_ref`/`readme_ref`/`mcp_ref` strings that were never updated when Cline shipped in v6.8.0
   (T352-T357) — all five omit `.cline/skills/`, `.clinerules/coding-standards.md`,
   `.clinerules/security-guidelines.md`, `.cline/` from the platform-folder list, and
   `.cline/mcp.json` from the MCP-config list. Running `--platform all` (fresh or `--update`)
   silently regresses AGENTS.md's Knowledge Base section to omit Cline even though `.cline/`/
   `.clinerules/` get installed alongside it. Reverted the regression (kept this repo's existing,
   more-complete hand-verified wording) rather than accept it or silently fix the generator script,
   since it's a distinct bug outside plan-031's stated scope (JSON merge for two MCP files). Flagged
   to the user in the final report as a follow-up candidate, not silently absorbed into this task.

Full verification bar re-run after the update and after reverting collateral: `make verify` (0
drift, 550 files), `generate-registry.py --check` (up to date), `validate-tasks.py` (TASK LEDGER
PASS), `sync.mjs --check` (0 drift), `python3 tests/run.py` (299 tests, OK, skipped=17) — all green.

Committed `.cline/`, `.clinerules/`, `.vscode/mcp.json` on branch
`chore/T372-repo-root-self-install-update`, pushed, opened MR, watched CI green, merged to
`develop` via `glab mr merge --squash=false` (see MR reference below for the resulting commit SHA).
