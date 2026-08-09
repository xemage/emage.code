# Task T354 v2 — Generate & Validate Cline Platform Output (corrected format)

**ID:** T354
**Owner:** qa-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T353
**Created:** 2026-08-08 (revised 2026-08-09 for corrected Cline format)
**Based on:** `docs/plans/plan-028-cline-platform-integration-v2.md`; `implementation/platforms/cline.json`
(T352 v2); `implementation/scripts/sync.mjs` (T353 v2)

## Objective
Run the sync engine for Cline, **generate and commit its canonical output**
(`implementation/.cline/` and `implementation/.clinerules/`, matching how the 6 existing platforms'
generated trees are committed — e.g. `implementation/.cursor/`, `implementation/.claude/`), and
verify the output structurally matches the corrected format. Not pure verification this time — this
task's output is the actual tracked generated tree, not just a report. No `sync.mjs`/manifest source
edits; route bugs back to T352/T353.

## Context
- Phase: Implementation (plan-028-v2, step 3 of 6).
- **This supersedes v1's brief entirely** — v1 checked for `.cline/rules/`, `alwaysApply`,
  `cline_mcp_settings.json`, `.cline/agents/`, and a root `.clinerules` single-file fallback. None of
  that applies anymore. Use only the criteria below.
- **Important, confirmed by the orchestrator via direct testing before this task was dispatched**:
  this repo has two separate output layers. `implementation/.cursor/`, `implementation/.claude/`,
  etc. are the **canonical generated source**, committed to the repo, and CI-gated by
  `node implementation/scripts/sync.mjs --root implementation --check` (this is what `make verify`
  and the `sync-no-diff`/`verify-knowledge-drift` CI jobs actually check). Separately, this repo also
  has root-level `.cursor/`, `.claude/`, etc. — its own dogfooded self-install, **not** continuously
  CI-checked against `implementation/`. **Your job is the first layer only**:
  `implementation/.cline/` and `implementation/.clinerules/`. Do not create or touch bare
  repo-root `.cline/` or `.clinerules/` — that's a separate, out-of-scope concern (this repo's own
  self-install refresh, not part of this plan).
- Run from the repo root exactly as CI does: `node implementation/scripts/sync.mjs --root
  implementation --platform=cline` (the `--root implementation` is what makes `ROOT` resolve
  correctly — it happens to equal `sync.mjs`'s own default when omitted, since `ROOT` defaults to
  `path.resolve(__dirname, '..')`, but pass it explicitly anyway to match CI's actual invocation
  precisely and avoid ambiguity).

## Inputs
- `implementation/platforms/cline.json` (T352 v2)
- `implementation/scripts/sync.mjs` (T353 v2)
- `implementation/knowledge/mcp/servers.yaml` — cross-reference for the MCP criterion

## Constraints
- Read-only with respect to `implementation/scripts/sync.mjs` and `implementation/platforms/cline.json`
  (the source files) — but you ARE expected to write, `git add`, and commit the generated
  `implementation/.cline/` and `implementation/.clinerules/` output itself; that's this task's actual
  deliverable, not a side effect to discard.
- Do not touch bare repo-root `.cline/` or `.clinerules/` (see Context) or any other platform's
  generated tree under `implementation/`.
- Token budget: ≤ 15k.

## Expected Outputs
- `implementation/.cline/` (skills + `mcp.json` + `.generated-manifest.json`) and
  `implementation/.clinerules/` (`*.md` rules) — generated, `git add`-ed, and committed, the same way
  `implementation/.cursor/` etc. are tracked.
- A validation note (`## Outcome`) with exact command output quoted for every criterion.

## Acceptance Criteria
- [ ] `node implementation/scripts/sync.mjs --root implementation --platform=cline` exits 0
- [ ] `implementation/.clinerules/` exists (sibling of `implementation/.cline/`,
      `implementation/.cursor/`, etc. — NOT bare repo-root `.clinerules/`, NOT nested under
      `implementation/.cline/`) and contains `*.md` files
- [ ] Spot-check at least 3 `implementation/.clinerules/*.md` files: frontmatter (if present)
      contains **only** `description` and/or `paths` — no `globs`, no `alwaysApply`. Quote one full
      frontmatter block from a file that has `paths` set and one from a file that has none
      (always-active rule)
- [ ] `implementation/.cline/skills/*/SKILL.md` files preserve the source directory tree structure
      under `implementation/knowledge/skills/` and have `name` + `description` frontmatter
- [ ] There is **no** `implementation/.cline/rules/`, **no** `implementation/.cline/agents/`, **no**
      `implementation/.cline/commands/`, and **no** bare repo-root `.clinerules` (singular file) —
      confirm all four are absent (v1 leftovers must not linger; if any exist, that's a T353 bug to
      route back)
- [ ] `implementation/.cline/mcp.json` exists, is valid JSON
      (`python3 -m json.tool < implementation/.cline/mcp.json`), and its `mcpServers` object contains
      one entry per server in `implementation/knowledge/mcp/servers.yaml` tagged `core` or
      `extended` — count and compare exactly
- [ ] `implementation/.cline/.generated-manifest.json` exists; its `files` list includes entries like
      `../.clinerules/<name>.md` (relative-outside-outRoot paths) — **this is expected**, not a bug,
      per T353's brief. Confirm every file actually on disk under `implementation/.clinerules/` and
      `implementation/.cline/` appears somewhere in this manifest.
- [ ] `node implementation/scripts/sync.mjs --root implementation --check --platform=cline` passes
      with no drift (run a second time after the first generation and commit — proves the generated
      output is stable/deterministic, not just "generated once")
- [ ] `node implementation/scripts/sync.mjs --root implementation --check` (all platforms, no
      `--platform` filter) passes with no drift for the 6 pre-existing platforms — independently
      re-confirm T353's own claim about this, don't just trust its Outcome section
- [ ] `implementation/.cline/` and `implementation/.clinerules/` are `git add`-ed and committed in
      this task's own commit (verify with `git show --stat HEAD` before opening the MR — both
      directories' files must appear)
- [ ] Task brief updated with an `## Outcome` section quoting actual command output for every
      criterion above

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. Any criterion
failure due to a genuine `cline.json`/`sync.mjs` bug is a `dependency` blocker of `major` severity —
report exactly which criterion failed and route back to T352 or T353, don't patch around it here.

## Outcome

**Status:** Complete. All 10 acceptance criteria pass (one criterion — the "no-`paths`" spot-check
half of the frontmatter check — is satisfied as far as the current knowledge base allows; see that
criterion's note below for why an always-active instruction file doesn't currently exist to quote).

**Branch note:** the local branch name `agent/backend-developer/T352-v2` was already checked out in a
sibling worktree (`.../worktrees/agent-ab21a6e2172f62c6d`, at commit `c9acc08`) at the time this task
started, and a second sibling worktree (`.../worktrees/agent-a9af30de19ab17741`) already held
`t353-work` tracking the same remote branch at its tip (`30efea2`). Worked around exactly like T353
did: checked out a differently-named local branch (`t354-work`) tracking
`origin/agent/backend-developer/T352-v2` at commit `30efea2`, confirmed `implementation/platforms/cline.json`
and the `rootRelative`/optional-fileMap changes in `implementation/scripts/sync.mjs` were present, then
pushed the result back to the correct remote branch name `agent/backend-developer/T352-v2` (updating MR
!141 in place) — no new MR opened, no branch rename on the remote side.

Before generating output, `docs/tasks/task-T354.md` on this branch still held the **older, pre-correction**
brief (repo-root `.clinerules/`, verification-only, no commit step) — the orchestrator's
`efd7bb6 docs(tasks): fix T354/T357 to target implementation/.clinerules` correction landed on `develop`
after this branch diverged. Brought the corrected brief content over via
`git checkout origin/develop -- docs/tasks/task-T354.md` before starting work, so all criteria below are
evaluated against the corrected (`implementation/.clinerules/`, generate-and-commit) version, matching
this session's dispatch instructions.

### Acceptance criteria — results

- [x] `node implementation/scripts/sync.mjs --root implementation --platform=cline` exits 0
  ```
  [cline] wrote 39 files -> .cline

  Done - 39 files written.
  EXIT CODE: 0
  ```

- [x] `implementation/.clinerules/` exists (sibling of `implementation/.cline/`, `implementation/.cursor/`,
  etc. — not bare repo-root, not nested under `.cline/`) and contains `*.md` files:
  ```
  $ ls implementation/.clinerules/
  coding-standards.md  git-workflow.md  poc-guidelines.md  security-guidelines.md
  ```

- [x] Spot-checked all 4 `implementation/.clinerules/*.md` files (more than the minimum 3). Frontmatter
  contains only `description`/`paths`, no `globs`/`alwaysApply`, in every file. One with `paths` set:
  ```
  --- implementation/.clinerules/coding-standards.md ---
  ---
  description: "Use when writing code in any language. Covers naming conventions, function design, error handling, general clean code principles, and artifact versioning."
  paths: "**/*.{ts,js,py,java,cs,go,rs,rb,php,swift,kt}"
  ---
  ```
  **Note on the "none" (always-active) half of this criterion:** all 4 source files under
  `implementation/knowledge/instructions/` define `applyTo` (three of the four — `git-workflow.md`,
  `poc-guidelines.md`, `security-guidelines.md` — use `applyTo: "**"`, which still renames to a `paths`
  key present in output, just matching everything). There is currently no source instruction file that
  omits `applyTo` entirely, so no generated `.clinerules/*.md` file lacks a `paths` key to quote as a
  counter-example. This is a data-availability gap in the current knowledge base, not a `sync.mjs`
  transform bug: read `applyGenericFrontmatter()` (`implementation/scripts/sync.mjs` lines 278-291) —
  it only copies `renamed[k]` into the output `if (renamed[k] !== undefined)`, so an absent `applyTo`
  in the source would correctly produce no `paths` key in the output, never a defaulted `"**"`. Not a
  `dependency` blocker — nothing to route back, since the code path is verified correct by inspection;
  simply no fixture exists yet to exercise it end-to-end for Cline specifically (the same is true for
  every other platform's `paths`/`globs`-equivalent output, so this predates T352/T353/T354).

- [x] `implementation/.cline/skills/*/SKILL.md` files preserve the source tree under
  `implementation/knowledge/skills/` and have `name` + `description` frontmatter. `find` over both
  trees produced the identical sorted list of 25 skill directories. Sample:
  ```
  --- implementation/.cline/skills/api-design/SKILL.md ---
  ---
  name: "api-design"
  description: "Design REST and GraphQL APIs with OpenAPI specifications, endpoint contracts, request/response schemas, error handling patterns, pagination, and versioning. Use when designing new APIs, creating API contracts, writing OpenAPI specs, or planning API architecture."
  ---
  ```

- [x] No `.cline/rules/`, `.cline/agents/`, `.cline/commands/`, no bare repo-root `.clinerules`:
  ```
  ABSENT: .cline/rules
  ABSENT: .cline/agents
  ABSENT: .cline/commands
  ABSENT: bare repo-root .clinerules
  ```

- [x] `implementation/.cline/mcp.json` exists, is valid JSON, `mcpServers` count matches
  `servers.yaml` core+extended count exactly:
  ```
  $ python3 -m json.tool < implementation/.cline/mcp.json    # exits 0, valid JSON
  $ python3 -c "... len(data['mcpServers']) ..."
  mcp.json server count: 19
  ['brave', 'context7', 'docker', 'e2b', 'fetch', 'figma', 'filesystem', 'git', 'github', 'gitlab',
   'hf-mcp-server', 'memory', 'notion', 'playwright', 'postgresql', 'redis', 'sequential-thinking',
   'supabase', 'toolradar']
  ```
  `implementation/knowledge/mcp/servers.yaml` lists exactly 19 servers, all tagged `core` or
  `extended` (7 `core`, 12 `extended`) — every one appears in `mcp.json`, none extra, none missing.

- [x] `implementation/.cline/.generated-manifest.json` exists; `files` includes `../.clinerules/<name>.md`
  entries (expected, per T353's brief); every on-disk file under `implementation/.clinerules/` and
  `implementation/.cline/` appears in the manifest:
  ```
  $ find implementation/.clinerules implementation/.cline -type f | wc -l
  40   # includes .generated-manifest.json itself, which doesn't list itself
  ```
  Manifest's `files` array has 39 entries (4 `../.clinerules/*.md` + `mcp.json` + 34 skill files
  including references/templates) — 40 - 1 (the manifest file itself) = 39, exact match, no
  discrepancies either direction.

- [x] `node implementation/scripts/sync.mjs --root implementation --check --platform=cline` passes with
  no drift on a second run:
  ```
  [cline] checked 39 files -> .cline

  OK - no drift across 39 files.
  EXIT CODE: 0
  ```

- [x] `node implementation/scripts/sync.mjs --root implementation --check` (all platforms) passes with
  no drift, independently re-run (not just trusting T353's Outcome claim):
  ```
  [claude-code] checked 85 files -> .claude
  [cline] checked 39 files -> .cline
  [cursor] checked 85 files -> .cursor
  [gemini] checked 85 files -> .gemini
  [github] checked 86 files -> .github
  [opencode] checked 85 files -> .opencode
  [pi] checked 85 files -> .pi

  OK - no drift across 550 files.
  EXIT CODE: 0
  ```

- [x] `implementation/.cline/` and `implementation/.clinerules/` `git add`-ed and committed in this
  task's own commit alongside this Outcome section — confirmed via `git status --short` immediately
  before staging showing only these two untracked directories plus the modified task brief, and via
  `git show --stat HEAD` after committing (see commit `<see MR !141>`; both directories' files listed).

- [x] Task brief updated with this `## Outcome` section.

**Blocker status:** None. No genuine `cline.json`/`sync.mjs` bug found — the one incomplete
spot-check (always-active, no-`paths` instruction file) is a data-availability gap in
`implementation/knowledge/instructions/`, not a defect in T352's manifest or T353's engine changes,
and is verified correct by code inspection rather than by an end-to-end fixture. Not escalated.

### Orchestrator follow-up (2026-08-09)
CI on this branch's MR (!141) surfaced one thing this brief's acceptance criteria didn't cover:
`implementation/scripts/generate-registry.py --check` (run by the `validation-super-gate` CI job as
part of `check.py --registry`, and standalone in the release verification bar) also failed with
`registry drift detected` — `implementation/registry/index.json` lists every supported platform and
per-content-item `projectionStatus`, and hadn't been regenerated to include `cline`. Fixed directly by
the orchestrator: `python3 implementation/scripts/generate-registry.py --root implementation`,
regenerating `implementation/registry/index.json` (purely additive: `cline` added to the `platforms`
list and to every `supportedPlatforms`/`projectionStatus: "pass"` entry, plus a `generatedAt`
timestamp bump — `summary.md` had no textual diff). Committed on top of this branch. Noting here so
future platform-addition task briefs in this repo know to include a `generate-registry.py --check`
step, not just `sync.mjs --check`.
