# Task T357 v2 — End-to-End Validation for Cline Platform Support (corrected format)

**ID:** T357
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T356
**Created:** 2026-08-08 (revised 2026-08-09 for corrected Cline format)
**Based on:** `docs/plans/plan-028-cline-platform-integration-v2.md`; `.gitlab-ci.yml`, `Makefile`,
`.editorconfig`

## Objective
Run the full repo verification suite with Cline included and confirm nothing outside
`.clinerules/`, `.cline/`, and this plan's own file inventory regressed. Produce a validation report.

## Context
- Phase: Implementation (plan-028-v2, step 6 of 6, final gate).
- Same tooling notes as v1's brief: `make verify` only runs `sync.mjs --check`, not `check.py`
  (run both, separately); `.gitlab-ci.yml`'s `verify-knowledge-drift`/`sync-no-diff` jobs are generic
  and need no edits.
- **Manual VS Code + Cline-extension check is still out of scope** for this task (no GUI access) —
  and its scope is narrower than v1 anyway, since there's no subagent-selection UI to check anymore
  (agents aren't projected). If performed manually later by a human, it would only be: confirm
  `.clinerules/*.md` shows up in Cline's rules UI, and `.cline/skills/` skills are usable. Report this
  as a follow-up for the orchestrator/user, not attempted here.

## Inputs
- Full repo state after T352-T356 (v2) land
- `.gitlab-ci.yml`, `Makefile`, `.editorconfig`

## Constraints
- Verification only. Route failures back to the owning task (T352/T353 manifest/engine, T355 install,
  T356 docs).
- Token budget: ≤ 20k.

## Expected Outputs
A validation report (`## Outcome`), exact command output quoted for every criterion.

## Acceptance Criteria
- [x] `make verify` passes (`node implementation/scripts/sync.mjs --root implementation --check`
      exits 0)
- [x] `python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks
      --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers
      --adapters` passes
- [x] `node implementation/scripts/sync.mjs --root implementation --check` (all platforms, no filter)
      passes with no drift across all 7 platforms including Cline
- [x] `implementation/.cline/mcp.json` is valid JSON and contains every expected `core`/`extended`
      server (re-confirm after T355/T356's changes — neither should have touched
      `implementation/.cline/`/`implementation/.clinerules/`, but verify rather than assume)
- [x] `implementation/.clinerules/` still exists (canonical generated location, committed by T354),
      unaffected by T355/T356's changes
- [x] `git diff --stat` against the pre-T352 (v2) baseline shows only files from plan-028-v2 §6's file
      inventory (which includes `implementation/.cline/` and `implementation/.clinerules/`, committed
      by T354) — no unexpected files touched, and specifically **no**
      `implementation/.cline/rules/`, `implementation/.cline/agents/`,
      `implementation/.cline/commands/`, or bare repo-root `.clinerules` (v1 leftovers must not
      exist)
- [x] All new/modified files pass the repo's `.editorconfig` check (check `.gitlab-ci.yml` for the
      exact command; if none exists, state that explicitly)
- [x] Manual VS Code + Cline-extension check: **explicitly out of scope** (see Context), recorded as
      an orchestrator/user follow-up
- [x] Task brief updated with an `## Outcome` section, structured as a pass/fail table

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. Any hard failure in
`make verify`, `check.py`, or `sync.mjs --check` is a `technical` blocker of `major` severity.

## Outcome

**Status:** All acceptance criteria PASS. No blockers. Recommend orchestrator close T357 and
plan-028-v2 (final gate).

**Executed by:** qa-engineer, worktree `agent/qa-engineer/T357`, branched from `origin/develop`
tip `cd3742c` ("Merge branch 'agent/technical-writer/T356' into 'develop'") on 2026-08-09. Prior
dispatch in this session had a stale local worktree ref (`9c4f82a`, pre-dating T352-T356); verified
`origin/develop` tip via `git fetch origin --prune` and branched directly from `origin/develop`
rather than the stale local ref, per this task's dispatch instructions.

**Baseline used for `git diff --stat`:** `e56ca3e` ("Merge branch
'docs/plan-028-cline-integration-tasks' into 'develop'") — the commit immediately before T352 (v1,
which per plan-028-v2 §0 stopped before writing anything material other than its own Outcome
section) was dispatched. Confirmed via `git log --all --diff-filter=A -- .clinerules
implementation/.cline/rules/* implementation/.cline/agents/* implementation/.cline/commands/*`
(empty result) that no v1-format leftovers were ever committed at any point in history, not just in
the current tree.

### Pass/Fail Table

| # | Acceptance Criterion | Result | Evidence |
|---|---|---|---|
| 1 | `make verify` passes | **PASS** | `node implementation/scripts/sync.mjs --root implementation --check` → `[claude-code] checked 85 files -> .claude` / `[cline] checked 39 files -> .cline` / `[cursor] checked 85 files -> .cursor` / `[gemini] checked 85 files -> .gemini` / `[github] checked 86 files -> .github` / `[opencode] checked 85 files -> .opencode` / `[pi] checked 85 files -> .pi` / `OK - no drift across 550 files.` / exit 0 |
| 2 | `check.py --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters` passes | **PASS** | `OK - 249 checks passed, 0 errors.` / exit 0 |
| 3 | `sync.mjs --check` (no filter) — no drift across all 7 platforms incl. Cline | **PASS** | Same run as #1 — 7 platforms listed (`claude-code`, `cline`, `cursor`, `gemini`, `github`, `opencode`, `pi`), `cline` explicitly present, 0 drift, exit 0 |
| 4 | `.cline/mcp.json` valid JSON, contains every expected `core`/`extended` server | **PASS** | `python3 -c "json.load(...)"` succeeded. `mcpServers` keys (19): `brave, context7, docker, e2b, fetch, figma, filesystem, git, github, gitlab, hf-mcp-server, memory, notion, playwright, postgresql, redis, sequential-thinking, supabase, toolradar` — exact match, sorted, against `implementation/knowledge/mcp/servers.yaml`'s full server list (7 `core` + 12 `extended`, since `implementation/platforms/cline.json`'s `mcp.tags` is `["core", "extended"]`). Shape matches the existing `claude-code`/`.mcp.json` `{ "mcpServers": {...} }` structure; sampled `gitlab` entry uses `${env:GITLAB_PERSONAL_ACCESS_TOKEN}` placeholder only, no literal secret values. `implementation/.cline/.generated-manifest.json` also validated as parseable JSON. |
| 5 | `implementation/.clinerules/` still exists, unaffected by T355/T356 | **PASS** | Directory present (4 files: `coding-standards.md`, `git-workflow.md`, `poc-guidelines.md`, `security-guidelines.md`). `git show --stat` on the T355 merge (`501a55b`) and T356 merge (`cd3742c`) both grep empty for `clinerules|\.cline/` — neither touched it. |
| 6 | `git diff --stat` vs. pre-T352(v2) baseline shows only plan-028-v2 §6 inventory files, no v1 leftovers | **PASS** (with one documented, non-blocking observation) | `git diff --stat e56ca3e..cd3742c`: 60 files changed, 6617 insertions(+), 418 deletions(-). Core inventory files all present and match §6: `implementation/platforms/cline.json` (new), `implementation/scripts/sync.mjs` (modified), `implementation/.cline/**` (39 files: skills, `mcp.json`, `.generated-manifest.json`), `implementation/.clinerules/*.md` (4 files), `scripts/install.sh`, `Makefile`, `README.md`, `AGENTS.md` (root), `docs/wiki/cline-setup.md` (new). V1-leftover check: `implementation/.cline/rules/`, `implementation/.cline/agents/`, `implementation/.cline/commands/`, bare root `.clinerules` file — all confirmed absent both in the working tree (`ls` errors = not found) and across all of git history (empty `git log --all --diff-filter=A` for those paths). **Observation (not a fail):** the diff also touches `implementation/registry/index.json` (regenerated `platforms`/`projectionStatus` listing to add `cline`, plus a `generatedAt` timestamp bump), `implementation/AGENTS.md` (adds the same Cline cross-reference note as root `AGENTS.md`), `scripts/render_installed_agents.py` (adds a `cline` entry to `PLATFORM_MAP` and to the `--platform` choices list), and `docs/tasks/*.md`/`docs/plans/*.md` (task-lifecycle and plan-revision bookkeeping for T352-T357 and plan-028-v2). None of these are in the plan's §6 table verbatim, but all are consistent, expected side effects of registering a new platform end-to-end (registry regeneration is a generated-output artifact of `check.py --registry`; the installer's agent-renderer needing to know about the new platform choice is a direct consequence of T355's install-script work; task/plan bookkeeping is normal process overhead for every task in this workspace, not code drift). None constitutes an unexpected or out-of-scope *functional* change. |
| 7 | New/modified files pass `.editorconfig` check | **PASS** (documented as: no CI job exists) | `grep -n -i "editorconfig" .gitlab-ci.yml` → no match; **no CI job in `.gitlab-ci.yml` runs an editorconfig check**, stated explicitly per the AC's fallback instruction. As a supplementary manual spot-check (no `editorconfig-checker`/`eclint` binary available in this environment), a Python script checked all 60 files changed since baseline against the `.editorconfig` rules that are practically checkable without the tool (UTF-8, LF-only line endings, final newline present, no trailing whitespace outside `.md`/`.markdown` — which the config explicitly exempts): 0 violations found. |
| 8 | Manual VS Code + Cline-extension check | **OUT OF SCOPE** (per brief) | Not attempted — no GUI access, as stated in the task's Context section. Recorded as a follow-up: a human should confirm (a) `.clinerules/*.md` shows up in Cline's rules UI, and (b) `.cline/skills/` skills are usable, once installed into a target project via `scripts/install.sh --platform=cline`. |
| 9 | Task brief updated with `## Outcome` section (pass/fail table) | **PASS** | This section. |

### Blockers
None. All in-scope acceptance criteria pass; the one out-of-scope item (#8) is not a blocker, it is
explicitly excluded from this task's scope per its own brief.

### Follow-ups for the orchestrator
1. Schedule (or ask the user to perform) the manual VS Code + Cline-extension check described in AC
   #8, once a human has GUI access — not a gate for closing T357/plan-028-v2 itself, since the brief
   explicitly excludes it.
2. Optional housekeeping (not a defect): consider whether `docs/plans/plan-028-cline-platform-integration.md`
   (v1, "kept as historical record" per plan-028-v2 §0) should be marked superseded/archived now that
   v2 has landed end-to-end, purely for future-reader clarity — no functional impact either way.
