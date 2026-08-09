# Task T379 — Fix AGENTS.md extended-tag documentation drift

**ID:** T379
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T377
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-03)

**Dependency correction:** plan-033's Task Breakdown table lists T379 as `BlockedBy: —` (no
functional code dependency on T377 — this is a pure doc fix, unrelated to T377's installer code).
That is still true. However, plan-033's own "Artifact Flow" section states T379 is "gated into the
same T381 validation pass to avoid a second branch/MR cycle for a small change" — i.e. T379's commit
must land on the *same branch* as T377/T378/T380 so T381 merges all four in one MR. This brief
therefore requires checking out T377's already-created branch (see Git workflow), which in practice
means T377 must run first. `Depends on: T377` above reflects this git-workflow-sequencing
requirement, correcting the plan table's `—`, which only tracked functional/code dependencies.

This brief is self-contained. You do not need to read plan-033 to execute this task.

## Objective
`AGENTS.md`'s "MCP Servers" section contains a two-row "Tag | Emitted to" table claiming the
`extended` tag is "emitted to platforms whose manifest opts in (`gemini`, `opencode`, `cursor`)".
This is stale: every one of the 7 `implementation/platforms/*.json` manifests except `github`
declares `"mcp": {"tags": ["core", "extended"]}` — i.e. 6 platforms (`cursor`, `gemini`, `opencode`,
`pi`, `claude-code`, `cline`), not 3, actually receive extended servers. Fix the table in both
`implementation/AGENTS.md` (canonical, hand-edited directly) and the root `AGENTS.md` projection
(regenerated via the sanctioned render script, never hand-edited), plus the same stale phrase found
during investigation in `docs/wiki/mcp-servers.md`.

## Inputs (exact paths, verified against the current file — re-verify before editing; see Blocker
protocol)

**1. `/home/emage/Code/emage/emage.code/implementation/AGENTS.md`, line 98 (canonical source —
hand-edit this one directly):**
```
| `extended` | platforms whose manifest opts in (`gemini`, `opencode`, `cursor`) |
```

**2. `/home/emage/Code/emage/emage.code/AGENTS.md` (repo root — the rendered projection, currently
byte-identical to `implementation/AGENTS.md` at this exact line), line 98 — same text as above. Per
the T373/T376 precedent, this file must NEVER be hand-edited; it is regenerated via
`scripts/render_installed_agents.py --source implementation/AGENTS.md --dest AGENTS.md --platform
all` (see Step 2 below). Confirmed by reading `scripts/render_installed_agents.py`: the "Tag |
Emitted to" table (lines 95-98 of the source) is plain pass-through text — it is NOT one of the five
`_replace_one()` substitution targets (`skills_ref`/`code_ref`/`sec_ref`/`kb_ref`/`mcp_ref`), so it
flows through the render unchanged from whatever `implementation/AGENTS.md` contains at that point.
Editing `implementation/AGENTS.md` first, then re-running the render, is therefore both necessary
and sufficient to fix the root copy too.**

**3. `/home/emage/Code/emage/emage.code/docs/wiki/mcp-servers.md`, line 15 (confirmed by direct grep
during planning — this file is hand-authored, not generated, and is NOT covered by the render
script; edit it directly):**
```
| `extended` | Emitted only to platforms that opt in via their manifest (`gemini`, `opencode`, `cursor`) |
```

**4. Checked and confirmed NOT stale (no edit needed, but you must independently re-confirm with the
grep commands below before concluding this) — `README.md` and `CONTRIBUTING.md`: neither file
contains the phrase "gemini, opencode, cursor" or any "opt(s) in" wording describing extended-tag
emission. Both files reference the platform folder list (`.github/`, `.gemini/`, `.opencode/`,
`.cursor/`, `.pi/`, `.claude/`) in unrelated contexts (a "never edit by hand" table and a "generated
folders" sentence) that have nothing to do with the `core`/`extended` tag system — do not touch
either file.**

**Source of truth for the corrected list — `implementation/platforms/*.json`'s `mcp.tags` field,
confirmed by direct read of all 7 manifests:**
| Manifest | `mcp.tags` |
|---|---|
| `github.json` | `["core"]` |
| `cursor.json` | `["core", "extended"]` |
| `gemini.json` | `["core", "extended"]` |
| `opencode.json` | `["core", "extended"]` |
| `pi.json` | `["core", "extended"]` |
| `claude-code.json` | `["core", "extended"]` |
| `cline.json` | `["core", "extended"]` |

6 of 7 platforms (all except `github`) receive extended servers.

## Allow-list (files/lines you may touch)
- `implementation/AGENTS.md` — line 98 only (the "Tag | Emitted to" table's `extended` row).
- `AGENTS.md` (repo root) — ONLY via the sanctioned render command in Step 2 below; never by hand.
- `docs/wiki/mcp-servers.md` — line 15 only (the equivalent table row).

## Deny-list (do not touch — no exceptions)
- Do NOT hand-edit root `AGENTS.md` directly — regenerate it via
  `scripts/render_installed_agents.py` only (Step 2).
- Do NOT edit any other line in `implementation/AGENTS.md`, root `AGENTS.md`, or
  `docs/wiki/mcp-servers.md` beyond the one row/line identified above. In particular, do NOT touch
  the "### Extended servers (opt-in)" bullet immediately below the table in either `AGENTS.md`
  file, or the equivalent "## Extended servers (opt-in)" section in `docs/wiki/mcp-servers.md` —
  those list the four servers this session is separately removing (`e2b`, `redis`, `figma`,
  `notion`) and are T387's scope, not yours. Touching them here would create a merge conflict with
  T387's branch, which is explicitly sequenced to branch from `develop` only after this task's
  branch (via T381) has already merged — see T387's brief for the reconciliation note.
- Do NOT edit `README.md` or `CONTRIBUTING.md` — confirmed not stale (see Inputs #4); if your own
  re-verification finds them stale after all, STOP and report a blocker rather than silently
  expanding scope.
- Do NOT edit `scripts/render_installed_agents.py` or `PLATFORM_MAP` — read-only reference, used
  only to run the render command.
- Do NOT edit `implementation/platforms/*.json` — these are the read-only source of truth you are
  reading from, not editing.
- Do NOT create any new branch — use the branch T377 already created (see Git workflow below).

## Step 1 — Edit the canonical source
In `implementation/AGENTS.md`, change line 98 from:
```
| `extended` | platforms whose manifest opts in (`gemini`, `opencode`, `cursor`) |
```
to exactly:
```
| `extended` | platforms whose manifest opts in (all except `github`: `cursor`, `gemini`, `opencode`, `pi`, `claude-code`, `cline`) |
```

## Step 2 — Regenerate the root projection (never hand-edit)
Run from repo root `/home/emage/Code/emage/emage.code`, after Step 1's edit is saved:
```
python3 scripts/render_installed_agents.py --source implementation/AGENTS.md --dest AGENTS.md --platform all
git diff AGENTS.md
```
Review the resulting `git diff AGENTS.md` line by line. Because your Step 1 edit is the only change
to the source file, and because the "Tag | Emitted to" table passes through the render unmodified,
the diff must show ONLY the single table-row line changing (byte-for-byte the same edit you made in
Step 1). If the diff shows anything else — any other line changing, added, or removed — STOP and
report a blocker (see below) rather than committing an unexpected diff. (This differs from T376's
situation, where a real content gap required substituted-ref changes across five sections; here, the
row is static pass-through text, so a one-line diff is the expected, correct outcome.)

## Step 3 — Edit the wiki doc
In `docs/wiki/mcp-servers.md`, change line 15 from:
```
| `extended` | Emitted only to platforms that opt in via their manifest (`gemini`, `opencode`, `cursor`) |
```
to exactly:
```
| `extended` | Emitted only to platforms that opt in via their manifest (all except `github`: `cursor`, `gemini`, `opencode`, `pi`, `claude-code`, `cline`) |
```

## Step 4 — Re-confirm README.md/CONTRIBUTING.md are not stale
```
grep -n "gemini.*opencode.*cursor\|opts\? in" README.md CONTRIBUTING.md
```
Expected: zero matches related to extended-tag emission (any match found must be inspected —
CONTRIBUTING.md/README.md may legitimately mention `.gemini/`, `.opencode/`, `.cursor/` in unrelated
platform-folder-list contexts; only a match describing which platforms receive `extended` servers is
in scope). If you find a genuinely stale match, STOP and report a blocker rather than silently
editing it (it would exceed this task's allow-list).

## Tests to run (literal commands, run from repo root)

1. Confirm all three edits landed exactly once each:
   ```
   grep -c 'all except `github`: `cursor`, `gemini`, `opencode`, `pi`, `claude-code`, `cline`' implementation/AGENTS.md
   grep -c 'all except `github`: `cursor`, `gemini`, `opencode`, `pi`, `claude-code`, `cline`' AGENTS.md
   grep -c 'all except `github`: `cursor`, `gemini`, `opencode`, `pi`, `claude-code`, `cline`' docs/wiki/mcp-servers.md
   ```
   PASS = every command prints `1`.

2. Confirm the stale phrase is fully gone from all three files:
   ```
   grep -c '(`gemini`, `opencode`, `cursor`)' implementation/AGENTS.md AGENTS.md docs/wiki/mcp-servers.md
   ```
   PASS = every count is `0`.

3. Full verification bar:
   ```
   make verify
   python3 implementation/scripts/generate-registry.py --root implementation --check
   python3 docs/tasks/validate-tasks.py
   python3 tests/run.py
   ```
   PASS = `make verify` → drift-free (this does NOT check `docs/wiki/` or root `AGENTS.md`'s
   projection consistency — it only checks `implementation/` generated trees against
   `implementation/knowledge/`, so your `docs/wiki/mcp-servers.md` edit is outside its scope;
   `generate-registry.py --check` → registry up to date; `validate-tasks.py` → starts with `TASK
   LEDGER: PASS`; `tests/run.py` → exits 0, same or greater count than your own recorded baseline.

## Acceptance criteria (all must be true)
- [ ] `git diff` (final, on your branch, this task's own commit) touches exactly three files:
      `implementation/AGENTS.md`, `AGENTS.md`, `docs/wiki/mcp-servers.md`.
- [ ] Each of the three files' edit is exactly the one line/row change specified above — no other
      content changed in any of the three files.
- [ ] Root `AGENTS.md` was produced by the Step 2 render command, never hand-edited — confirmed by
      the fact that `git diff AGENTS.md` after Step 2 shows only the one expected line.
- [ ] Test 1 and Test 2 above both pass exactly as specified.
- [ ] README.md and CONTRIBUTING.md were checked (Step 4) and confirmed to need no change, or a
      blocker was raised if they did.
- [ ] The full verification bar (test 3) passes.
- [ ] The "### Extended servers (opt-in)" / "## Extended servers (opt-in)" sections (the four
      servers being removed by T386/T387) were NOT touched by this task.

## Blocker protocol
STOP and report a blocker (do not improvise a different fix) if:
- The branch T377 created (`bugfix/T377-install-mcp-merge-all-platforms`) does not exist → `type:
  dependency`, `severity: major` — this task has no functional need for T377's code, but per the
  git-workflow sequencing note above, cannot stack its commit without the branch existing; ask the
  orchestrator to sequence T377 first.
- The actual current line 98 content in `implementation/AGENTS.md` or root `AGENTS.md` doesn't match
  the verbatim text quoted above, or line 15 of `docs/wiki/mcp-servers.md` doesn't match → `type:
  dependency`, `severity: major` — re-verify against the current file before proceeding; the line
  may have shifted.
- Any `implementation/platforms/*.json` manifest's `mcp.tags` field doesn't match the table above
  (a platform's tags changed since this brief was written) → `type: dependency`, `severity: major`
  — recompute the corrected platform list from the actual current manifests, do not use the table
  in this brief if it's stale.
- Step 2's `git diff AGENTS.md` shows anything beyond the single expected line → `type: technical`,
  `severity: major` — do not commit an unexpected diff; report the exact unexpected lines.
- Step 4 finds a genuinely stale match in README.md/CONTRIBUTING.md → `type: unclear_requirements`,
  `severity: minor` — this brief's allow-list doesn't cover those files; report the finding for the
  orchestrator to scope a follow-up rather than silently expanding this task.
- Any verification command fails → `type: technical`, `severity: major`, include exact output.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Check out the EXISTING branch `bugfix/T377-install-mcp-merge-all-platforms` (created by T377 —
   do NOT create a new branch, do NOT branch from `develop`).
2. Confirm T377's commit is present.
3. Make the three edits (Steps 1-3); run Step 4's check and all tests above; confirm all pass.
4. Commit with a Conventional Commit message, e.g.:
   ```
   docs(agents): fix stale extended-tag emission list in MCP Servers table

   AGENTS.md's "Tag | Emitted to" table claimed extended servers are only
   emitted to gemini/opencode/cursor. Direct read of every
   implementation/platforms/*.json manifest shows 6 of 7 platforms (all
   except github) declare mcp.tags: [core, extended]. Corrected the table
   in implementation/AGENTS.md (hand-edited canonical source), regenerated
   root AGENTS.md via render_installed_agents.py (never hand-edited, per
   the T373/T376 precedent), and fixed the same stale phrase found in
   docs/wiki/mcp-servers.md. README.md/CONTRIBUTING.md checked, not stale.

   Refs T379
   ```
5. Do NOT push. Do NOT open a merge request. Do NOT merge to `develop` or `main`. Stop after the
   local commit (stacked on top of T377's/T378's commits, same branch) and report completion
   (commit SHA, full test output) back to the orchestrator. T380 will stack a further commit on this
   same branch; T381 will push it and open the MR.

## Constraints
- Token budget: ≤8k tokens.
- File ownership: `implementation/AGENTS.md` line 98, root `AGENTS.md` (via render only),
  `docs/wiki/mcp-servers.md` line 15 — nothing else.
- No unrelated refactor of any file.
