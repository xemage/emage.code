# Task T356 v2 — Update Documentation for Cline (corrected format)

**ID:** T356
**Owner:** technical-writer
**Status:** done
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

---

## Outcome

**Status:** Documentation content complete; git branch/commit/push/MR steps **blocked** — see Blocker
below.

### What was produced
- `README.md` — added the "Supported platforms" table row for Cline exactly as specified. The
  `--platform` value table already had a `Cline | cline` row (confirmed present in the up-to-date
  `develop` copy at the repo's primary checkout, added by T355) — **not** duplicated, per the
  acceptance criterion's own instruction to check first.
- `AGENTS.md` (root) — "## Knowledge Base": added `.clinerules/` and `.cline/` to both per-platform-
  folder bullets, and added the Cline/`AGENTS.md` auto-detection + `.clinerules/` sentence.
- `implementation/AGENTS.md` — same three edits, applied identically to its (differently-worded)
  "## Knowledge Base" section.
- `docs/wiki/cline-setup.md` — new file, exactly four sections in the specified order (`## Install
  steps`, `## Plan/Act mode best practices for emage.code workflows`, `## MCP server setup (copying
  .cline/mcp.json into Cline's global config)`, `## Troubleshooting: rules not loading`). The
  agents/commands scope-limitation note is in the "Install steps" section, stated plainly. No vault/
  RAG/`rag-retrieval` references anywhere. The MCP section's global-config path claim
  (`~/.cline/mcp.json` for the CLI; IDE extension via its own settings panel) was independently
  re-verified via `WebFetch` against `https://docs.cline.bot/mcp/configuring-mcp-servers` on
  2026-08-09 rather than taken on faith from this brief's draft text, and the troubleshooting
  section's version note is phrased generically ("check you're on a recent Cline version") since no
  specific minimum-version number is documented on the page checked
  (`https://docs.cline.bot/customization/cline-rules.md`, same date). `AGENTS.md` auto-detection was
  also independently re-confirmed on the same page (`"AGENTS.md at AGENTS.md, ~/.agents/AGENTS.md"`
  listed as a recognized rule source) rather than only trusting this brief's Context claim.
- `CHANGELOG.md` not touched; no version number hardcoded in any edited/created file.

### Acceptance criteria — results
- [x] `README.md` "Supported platforms" table has the corrected Cline row (no agents/tools mention)
- [x] `README.md`'s `--platform` value table has a `Cline | cline` row — already present upstream
      (added by T355); not duplicated
- [x] `AGENTS.md` (root) and `implementation/AGENTS.md` both updated: `.clinerules/` and `.cline/`
      added to the per-platform-folders bullet(s), plus the Cline/`AGENTS.md` auto-detection sentence
- [x] `docs/wiki/cline-setup.md` created with exactly the four sections above, in that order
- [x] The agents/commands scope-limitation note is present and explicit (in "Install steps"), not
      buried or omitted
- [x] No section references a vault, RAG, or `rag-retrieval` skill
- [x] `CHANGELOG.md` not modified; no version number hardcoded anywhere in the diff
- [x] Task brief updated with this `## Outcome` section

### Blocker
- **Type:** `technical`
- **Severity:** `major`
- **Description:** This session's tool set for the technical-writer role in this worktree is limited
  to `Read`, `Edit`, `Write`, `WebFetch`, `WebSearch` — there is no shell/Bash/git tool available.
  Consequently, the git-workflow portion of this task's dispatch instructions (create branch
  `agent/technical-writer/T356` from `develop`, commit with a Conventional Commits message, push, and
  open an MR to `develop` via `glab mr create`) **could not be executed**. All four content edits
  above were made directly to the files in this worktree's working directory via `Edit`/`Write`, but
  they are **uncommitted** — no `git add`/`commit`/`push`/MR has occurred.
- **Secondary finding (also worth flagging):** this worktree's checkout appears to predate the
  `develop` tip referenced by this brief. `implementation/platforms/cline.json`,
  `implementation/.cline/`, and `implementation/.clinerules/` (all landed by T352-T354 per this
  brief's Context) are **absent from this worktree** even though they are present in the repository's
  primary checkout on `develop`. The two root/`implementation/AGENTS.md` files and (aside from the
  one already-added row) `README.md` were byte-identical between this worktree and the primary
  checkout, so this did not block correct content decisions here, but whoever performs the git
  operations for this branch should confirm the worktree is rebased onto/recreated from current
  `develop` before committing, to avoid reintroducing a stale base or missing the T352-T355 files in
  the eventual diff.
- **Suggested resolution:** either (a) grant shell/git-tool access in a follow-up session so this
  branch/commit/push/MR can be completed directly, or (b) have the orchestrator (or an agent with
  shell access) create `agent/technical-writer/T356` from current `develop`, apply the four content
  edits recorded above (content is final and acceptance-criteria-verified), and open the MR.
- **Retries:** 0 (reporting immediately — this is a tooling/environment constraint, not something a
  retry of the same approach would resolve).
