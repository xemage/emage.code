# Task T356 v2 — Update Documentation for Cline (corrected format)

**ID:** T356
**Owner:** technical-writer
**Status:** pending
**Priority:** P1
**Depends on:** T355
**Created:** 2026-08-08 (revised 2026-08-09 for corrected Cline format)
**Based on:** `docs/plans/plan-028-cline-platform-integration-v2.md` §0, §2; `README.md`, `AGENTS.md`,
`implementation/AGENTS.md`, `docs/wiki/`

## Objective
Document Cline support with the corrected format: `README.md` row, `AGENTS.md` cross-reference note,
and `docs/wiki/cline-setup.md` — including an explicit, honest note that subagent/command projection
is not shipped this pass (no confirmed on-disk format exists for either).

## Context
- Phase: Implementation (plan-028-v2, step 5 of 6). Supersedes v1's brief.
- Do not touch `CHANGELOG.md` (CI-regenerated) or hardcode a version number — same reasoning as v1.
- `AGENTS.md` exists at both repo root and under `implementation/`; update both identically.
- **Cline auto-detecting root `AGENTS.md` is confirmed true** (found during T352 v1's blocker
  investigation — Cline auto-detects `AGENTS.md`-style files for cross-tool compatibility, same as
  `.cursorrules`/`.windsurfrules`). This needs no code, only documentation — it already works with
  the existing hand-maintained root `AGENTS.md`.

## Inputs
- `README.md` — "Supported platforms" table and the `--platform` value table
- `AGENTS.md` (root) and `implementation/AGENTS.md` — "## Knowledge Base" section
- `docs/wiki/` — structure reference

## Constraints
- Token budget: ≤ 15k.

## Expected Outputs

**1. `README.md`** — "Supported platforms" table row (note: format description differs from v1's
draft — no `agents`/`tools` mention, since that's not shipped):
```
| Cline | `.clinerules/` (root) + `.cline/skills/` + `.cline/mcp.json` | `.md` rules (`paths` frontmatter) + skills; MCP config is a staging file, not auto-applied |
```
Also add `Cline | cline` to the `--platform` value table (this may already be done by T355 — check
before adding a duplicate row).

**2. `AGENTS.md` (root) and `implementation/AGENTS.md`** — in "## Knowledge Base": add `.clinerules/`
and `.cline/` to the per-platform-folders bullet list(s), and one short sentence: Cline
auto-detects root `AGENTS.md` natively (no projection needed for that file itself, already works);
Cline users should also check `.clinerules/` for path-scoped project rules.

**3. `docs/wiki/cline-setup.md`** (new) — exactly these four sections, in this order:
- `## Install steps` — `scripts/install.sh --target <dir> --platform cline`; note this installs
  `.clinerules/` and `.cline/skills/` directly usable by Cline, plus a `.cline/mcp.json` **staging
  file** that is *not* automatically applied
- `## Plan/Act mode best practices for emage.code workflows` — how Cline's Plan/Act mode maps onto
  this repo's Plan-Approve-Execute workflow (`AGENTS.md` § Delegation Brief)
- `## MCP server setup (copying .cline/mcp.json into Cline's global config)` — explain Cline's MCP
  config is global (`~/.cline/mcp.json` for the CLI, or the IDE extension's settings panel), not
  per-project; instruct the user to **merge**, not overwrite, since they may already have other
  servers configured — show a short before/after JSON merge example
- `## Troubleshooting: rules not loading` — check that `.clinerules/` exists at the project root
  (not nested anywhere), check the Cline version supports project-level rules (a doc-site version
  note, if the docs page you read during T352/T353's investigation mentioned one — otherwise state
  "check you're on a recent Cline version" generically)

**Also include, in the "Install steps" section**: a short, explicit note that Cline subagent
(`.cline/agents/`) and slash-command projection are **not** included in this release — no confirmed
on-disk format exists for either as of this writing; only rules, skills, and MCP-staging are
supported. This is a known, intentional scope boundary, not an oversight — state it plainly rather
than omitting it.

Do not include any section referencing a vault, RAG, or `rag-retrieval` skill.

## Acceptance Criteria
- [ ] `README.md` "Supported platforms" table has the corrected Cline row (no agents/tools mention)
- [ ] `README.md`'s `--platform` value table has a `Cline | cline` row (not duplicated if T355 already
      added it)
- [ ] `AGENTS.md` (root) and `implementation/AGENTS.md` both updated: `.clinerules/` and `.cline/`
      added to the per-platform-folders bullet(s), plus the Cline/`AGENTS.md` auto-detection sentence
- [ ] `docs/wiki/cline-setup.md` created with exactly the four sections above, in that order
- [ ] The agents/commands scope-limitation note is present and explicit, not buried or omitted
- [ ] No section references a vault, RAG, or `rag-retrieval` skill
- [ ] `CHANGELOG.md` not modified; no version number hardcoded anywhere in the diff
- [ ] Task brief updated with an `## Outcome` section

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation.
