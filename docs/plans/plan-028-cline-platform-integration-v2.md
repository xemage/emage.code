# Plan 028 v2 — Cline platform integration (corrected format)

**Status:** approved — executing this session
**Created:** 2026-08-09
**Supersedes:** `docs/plans/plan-028-cline-platform-integration.md` (v1) — kept as historical record,
do not execute its task specs, they rest on a disproven format assumption.
**Owner:** orchestrator
**Based on:** `docs/tasks/task-T352.md` § Outcome (v1's blocker report, backend-developer delegate,
2026-08-08); independent orchestrator verification against https://docs.cline.bot/customization/cline-rules.md
and https://docs.cline.bot/mcp/configuring-mcp-servers (2026-08-08); user decision via AskUserQuestion,
2026-08-08, choosing "Redesign now, reduced scope"; `implementation/scripts/sync.mjs` (read in full
again for this revision, specifically `syncPlatform()` lines 412-511)

## 0. Why this revision exists

T352 (backend-developer, worktree `agent/backend-developer/T352`) was dispatched under v1 of this
plan and, per its brief's own Step 0 instruction, stopped before writing a manifest because live
docs materially contradicted the assumed format. The orchestrator independently re-fetched the same
two doc pages and confirmed the finding rather than taking the delegate's word alone. Confirmed
discrepancies:

| v1 assumed | Actually confirmed (docs.cline.bot, 2026-08-08/09) |
|---|---|
| Rules at `.cline/rules/*.md` | Rules at **`.clinerules/` — project root**, not nested under `.cline/` |
| Rules frontmatter: `description`/`globs`/`alwaysApply` | Only documented key is **`paths`** (glob array); no `alwaysApply` concept exists |
| MCP config at project-local `cline_mcp_settings.json` | MCP config is **global**: `~/.cline/mcp.json` (CLI) or UI-managed (IDE extension) — no project-relative file is documented |
| Skills at `.cline/skills/<name>/SKILL.md` | **Confirmed correct**, no change |
| Agents at `.cline/agents/*.md` | **No documented format found** anywhere on the doc site |
| Root `.clinerules` (singular file) as a legacy-format fallback | No such legacy single-file format is described; `.clinerules/` (the directory) is itself the current primary format |
| Cline auto-detects `AGENTS.md` for cross-tool compatibility | **Confirmed correct** by the delegate's research — this needs no projection work at all, it already works with the existing hand-maintained root `AGENTS.md` |

User chose, via `AskUserQuestion` on 2026-08-08: **redesign now with reduced scope** — ship what's
confirmed (rules, skills, MCP-as-staging-file), drop what isn't confirmed to exist (agents,
commands), and make one small, generic (not Cline-hardcoded) addition to `sync.mjs`'s engine to
support a fileMap target that resolves outside a platform's `outputDir`.

## 1. Goal

Ship Cline support for what's actually documented: project rules (`.clinerules/` at repo root) and
skills (`.cline/skills/`), plus an MCP-server **staging file** (`.cline/mcp.json`) the user copies
into Cline's real global config — not agents or commands, which have no confirmed on-disk format and
are explicitly deferred, not silently invented.

## 2. Scope

- **In scope**:
  - `implementation/platforms/cline.json` v2 manifest — `instructions` (root-relative) and `skills`
    only; no `agents`, `commands`, or `extras` block.
  - Two small, generic additions to `implementation/scripts/sync.mjs`'s `syncPlatform()`:
    1. A `rootRelative: true` flag on any `fileMap` entry, meaning: resolve that entry's `dir`
       against the repo root instead of the platform's `outputDir`, and wipe-then-regenerate that
       specific directory on real (non-`--check`) syncs — mirroring the existing whole-`outputDir`
       wipe safety net, scoped to just that directory so it can't touch anything outside it.
    2. Making the `agents` and `commands` fileMap loops **optional** — skip cleanly if a manifest
       doesn't declare that content type, instead of throwing on `undefined.dir`. This is generic
       (any future platform without agent/command support benefits), not Cline-specific code.
  - `emitMcp()` gains a `cline` format branch (same `mcpServers` shape as the existing `claude-code`
    branch — this part of v1 was never wrong, only the *filename/location* was), writing to
    `.cline/mcp.json` under the normal `outputDir` (a staging file, not `~/.cline/mcp.json` itself —
    `sync.mjs` never writes outside the repo, and this plan does not change that).
  - Generation and structural validation of `.clinerules/` + `.cline/skills/` + `.cline/mcp.json`.
  - Installer support: `scripts/install.sh --platform=cline` copies both `.cline/` and the
    root-level `.clinerules/` directory into the target project.
  - Documentation: `README.md` platform row (corrected), `AGENTS.md` cross-reference note (Cline
    auto-detects `AGENTS.md` — already true, no code needed, just document it),
    `docs/wiki/cline-setup.md` (corrected install/MCP-copy/troubleshooting content).
- **Out of scope** (unchanged from v1, plus new items from this revision):
  - Everything v1 already excluded (RAG/vault/Obsidian, `_manifest.schema.json`, hand-editing
    `CHANGELOG.md`, hardcoding a version number, `.gitlab-ci.yml` changes).
  - **Cline subagent (`agents/*.md`) and slash-command projection** — no confirmed on-disk format
    exists; do not invent one. If Cline documents this later, it's a follow-up plan, not a gap-fill
    inside this one.
  - **Writing anything to `~/.cline/` or any path outside the repository.** `sync.mjs`'s job stops
    at generating `.cline/mcp.json` as a staging file; copying it into Cline's real global config is
    a documented manual (or install-script-assisted, staging-only) step for the user, never an
    automatic write to a path outside the project.
  - A root `.clinerules` **single-file** fallback (v1's `_extras/cline/dot-clinerules` concept) —
    dropped; `.clinerules/` the directory is the primary format, not something needing a fallback.
- **Assumptions**: the table in §0 is now the source of truth, confirmed against live docs by both
  the delegate and the orchestrator independently. If a task discovers a further discrepancy, treat
  it exactly as T352 v1 did — stop and report, don't guess.

## 3. Task graph

```mermaid
graph TD
  T352[T352 v2: Cline manifest (rules+skills+mcp only) — backend-developer] --> T353[T353 v2: sync.mjs rootRelative + optional fileMap — backend-developer]
  T353 --> T354[T354 v2: generate & validate — qa-engineer]
  T354 --> T355[T355 v2: install script (.cline/ + .clinerules/) — devops-engineer]
  T355 --> T356[T356 v2: documentation (corrected) — technical-writer]
  T356 --> T357[T357 v2: e2e validation (corrected) — qa-engineer]
```

Same task IDs as v1 (T352-T357) — these tasks were never completed under v1 (T352 blocked before
writing anything material other than its own Outcome section; T353-T357 were never dispatched), so
their briefs are revised in place rather than issued under new IDs. Each brief's own revision is
called out in its `## Outcome (v1)` / new content, not duplicated here.

## 4. Agent assignments

| Task | Agent | Priority | Estimated scope |
|------|-------|----------|-----------------|
| T352 | backend-developer | P0 | small (smaller than v1 — fewer fileMap types) |
| T353 | backend-developer | P0 | medium (two small generic engine additions) |
| T354 | qa-engineer | P0 | small |
| T355 | devops-engineer | P1 | small |
| T356 | technical-writer | P1 | small |
| T357 | qa-engineer | P0 | medium |

## 5. Artifact flow

```
T352 → implementation/platforms/cline.json (v2 shape)      (consumed by: T353, T354)
T353 → implementation/scripts/sync.mjs (modified:
        rootRelative support, optional agents/commands,
        emitMcp cline branch)                                (consumed by: T354)
T354 → .clinerules/ + .cline/ generated output, validation    (consumed by: T355, T357)
T355 → scripts/install.sh, Makefile (modified)                (consumed by: T356, T357)
T356 → README.md, AGENTS.md, docs/wiki/cline-setup.md          (consumed by: T357)
T357 → validation report, CI green
```

## 6. File inventory (new / modified)

| Path | Status | Task |
|------|--------|------|
| `implementation/platforms/cline.json` | New | T352 |
| `implementation/scripts/sync.mjs` | Modified | T353 |
| `scripts/install.sh` | Modified | T355 |
| `Makefile` | Modified | T355 |
| `README.md` | Modified | T355, T356 |
| `AGENTS.md` | Modified | T356 |
| `docs/wiki/cline-setup.md` | New | T356 |

No `_extras/cline/` content this time (dropped, see §2).

## 7. Risks & mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Even this corrected format has drifted since 2026-08-09 | Low | Medium | T352 v2 repeats the Step 0 live-docs check; a further mismatch is reported the same disciplined way, not guessed past. |
| `rootRelative`'s scoped wipe-then-regenerate accidentally targets a path outside `.clinerules/` due to a manifest typo | Low | High | T353's brief requires the resolved absolute path to be asserted as a descendant of `ROOT` and distinct from `ROOT` itself before any `fs.rm` call — never wipe `ROOT` itself. |
| Dropping agents/commands leaves Cline users without the subagent roster other platforms get | Medium | Low (scope decision, not a bug) | Explicitly documented in `docs/wiki/cline-setup.md` (T356) as a known current limitation, not silently omitted. |
| User copies `.cline/mcp.json` into `~/.cline/mcp.json` and clobbers unrelated servers they'd already configured | Medium | Medium | T356's docs explicitly say "merge, don't overwrite" and show what a merge looks like. |

## 8. Token budget

| Phase | Budget | Spent | Remaining |
|-------|--------|-------|-----------|
| Re-planning (this revision) | 15k | — | — |
| T352 (manifest, re-attempt) | 10k | — | — |
| T353 (sync.mjs engine changes) | 30k | — | — |
| T354 (validation) | 15k | — | — |
| T355-T356 (install/docs) | 25k | — | — |
| T357 (e2e validation) | 20k | — | — |
| **Total** | **115k** | — | — |

## 9. Approval

- [x] User approved redesign direction on 2026-08-08 (via `AskUserQuestion`, "Redesign now, reduced
      scope")
- [ ] Plan locked; revisions create `plan-028-cline-platform-integration-v3.md`
