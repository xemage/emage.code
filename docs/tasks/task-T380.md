# Task T380 — Update docs describing uniform installer MCP merge behavior

**ID:** T380
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T377
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-04)

This brief is self-contained. You do not need to read plan-033 to execute this task, though you do
need T377's fix already committed on the branch you check out (see Git workflow below).

## Objective
`README.md`'s `--update` section currently describes the merge-not-overwrite behavior plan-031/T370
documented for exactly two files (`.vscode/mcp.json`, `.mcp.json`). T377 extended that same behavior
to the other five platforms' MCP/settings files. Update the doc text so it accurately describes the
now-uniform 7-platform (all platforms this repo supports) merge behavior, naming every actual file,
not just the original two.

## Inputs (exact path and content, verified against the current file — re-verify before editing; see
Blocker protocol)

`/home/emage/Code/emage/emage.code/README.md`, lines 101-110 (quoted verbatim):
```
On `--update`, the single-file MCP configs — `.vscode/mcp.json` (`github`
platform) and `.mcp.json` (`claude-code` platform) — are merged, not
overwritten: any existing top-level key the generator doesn't know about
(e.g. a hand-added MCP server entry, or a top-level `inputs` prompt block) is
preserved, while every generator-known key is refreshed to the current
generated content, recursing into nested objects (so hand-added fields inside
a known server's config are preserved too). See `scripts/merge-mcp-json.py`
for the exact algorithm. Platform directory trees (`.github/`, `.claude/`,
etc.) are still replaced wholesale on `--update` — only these two MCP config
files get this merge treatment.
```

This paragraph sits between the "Update an existing install" code block (ending line 99) and the
"Per-release install steps" paragraph (starting line 112) — read-only context, do not touch either
neighboring paragraph.

**`CONTRIBUTING.md` — checked during planning and confirmed to contain no description of the
installer's `--update` merge-vs-overwrite behavior at all** (its MCP-related content is entirely
about *adding a new platform's MCP format branch to `sync.mjs`*, an unrelated topic — see lines
119-139, read-only reference, do not touch). No edit needed there; re-confirm this yourself with the
grep in Step 2 before concluding it.

## Allow-list (files/lines you may touch)
- `README.md`, lines 101-110 only (the paragraph quoted above).

## Deny-list (do not touch — no exceptions)
- Do NOT touch any other paragraph or section of `README.md`.
- Do NOT edit `CONTRIBUTING.md` unless Step 2's re-verification finds it genuinely describes the
  old two-file-only behavior (expected: it does not) — if it does, STOP and report a blocker rather
  than silently expanding this task's scope.
- Do NOT edit `scripts/install.sh`, `scripts/merge-mcp-json.py`, or any test file — those are T377/
  T378's scope.
- Do NOT edit `AGENTS.md` (either copy) or `docs/wiki/mcp-servers.md` — those are T379's scope; this
  task is README.md only.
- Do NOT create any new branch — use the branch T377 already created (see Git workflow below).

## Step 1 — Edit README.md
Replace lines 101-110 (quoted verbatim above) with exactly:
```
On `--update`, the single-file MCP/settings configs for every platform —
`.vscode/mcp.json` (`github`), `.mcp.json` (`claude-code`), `.cursor/mcp.json`
(`cursor`), `.gemini/settings.json` (`gemini`), `.opencode/opencode.json`
(`opencode`), `.pi/mcp.json` (`pi`), and `.cline/mcp.json` (`cline`) — are
merged, not overwritten: any existing top-level key the generator doesn't
know about (e.g. a hand-added MCP server entry, or a top-level `inputs`
prompt block) is preserved, while every generator-known key is refreshed to
the current generated content, recursing into nested objects (so hand-added
fields inside a known server's config are preserved too). See
`scripts/merge-mcp-json.py` for the exact algorithm. The rest of each
platform's directory tree (`.github/`, `.cursor/`, `.claude/`, etc.) is still
replaced wholesale on `--update` — only each platform's one MCP/settings file
gets this merge treatment.
```

## Step 2 — Re-verify CONTRIBUTING.md is not stale
```
grep -n "single-file MCP\|merged, not\|overwritten\|merge-mcp-json" CONTRIBUTING.md
```
Expected: zero matches (or only matches unrelated to describing `--update`'s merge-vs-overwrite
behavior — inspect any hit before concluding it's unrelated). If a genuinely stale description is
found, STOP and report a blocker rather than editing it yourself (outside this task's allow-list).

## Tests to run (literal commands, run from repo root `/home/emage/Code/emage/emage.code`)

1. Confirm all seven file names now appear in the updated paragraph:
   ```
   grep -c '`.vscode/mcp.json`' README.md
   grep -c '`.mcp.json`' README.md
   grep -c '`.cursor/mcp.json`' README.md
   grep -c '`.gemini/settings.json`' README.md
   grep -c '`.opencode/opencode.json`' README.md
   grep -c '`.pi/mcp.json`' README.md
   grep -c '`.cline/mcp.json`' README.md
   ```
   PASS = every command prints at least `1` (some file names may legitimately also appear elsewhere
   in `README.md`, e.g. the platform-output table near the top of the file — a count ≥1 is the
   correct bar, not necessarily exactly `1`).

2. Markdown link check (this repo's CI runs an equivalent check as the `markdown-links` job; your
   edit adds no new links, but confirm you haven't broken existing ones in the paragraph, e.g. the
   `scripts/merge-mcp-json.py` reference must still resolve as a valid repo-relative path):
   ```
   test -f scripts/merge-mcp-json.py && echo "PASS: referenced path exists"
   ```

3. Full verification bar:
   ```
   make verify
   python3 implementation/scripts/generate-registry.py --root implementation --check
   python3 docs/tasks/validate-tasks.py
   python3 tests/run.py
   ```
   PASS = all four pass per the same conditions documented in prior briefs (`make verify` → 0 drift;
   `generate-registry.py --check` → up to date; `validate-tasks.py` → `TASK LEDGER: PASS`;
   `tests/run.py` → exits 0, count not reduced from your own recorded baseline). None of these
   commands inspect `README.md` prose directly, but they must still pass since your edit sits on the
   same branch as T377/T378's code changes.

## Acceptance criteria (all must be true)
- [ ] `git diff` (this task's own commit) touches exactly one file: `README.md`.
- [ ] The diff replaces exactly the paragraph at (originally) lines 101-110 with the target text
      above — no other line in `README.md` changed.
- [ ] All seven platform MCP/settings file names are named explicitly in the updated paragraph (not
      a vague "all platforms" with no file list).
- [ ] `CONTRIBUTING.md` was checked (Step 2) and confirmed to need no change, or a blocker was raised
      if it did.
- [ ] Test 1 passes for all seven `grep -c` checks.
- [ ] The full verification bar (test 3) passes.

## Blocker protocol
STOP and report a blocker (do not improvise a different fix) if:
- The branch T377 created (`bugfix/T377-install-mcp-merge-all-platforms`) does not exist → `type:
  dependency`, `severity: major`.
- The actual current `README.md` content at lines 101-110 doesn't match the verbatim text quoted
  above → `type: dependency`, `severity: major` — re-verify against the current file; the paragraph
  may have shifted or been reworded since this brief was written.
- Step 2 finds a genuinely stale description in `CONTRIBUTING.md` → `type: unclear_requirements`,
  `severity: minor` — report the finding; do not edit it yourself.
- Any verification command fails → `type: technical`, `severity: major`, include exact output.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Check out the EXISTING branch `bugfix/T377-install-mcp-merge-all-platforms` (created by T377 —
   do NOT create a new branch, do NOT branch from `develop`).
2. Confirm T377's (and, if already landed, T378's/T379's) commits are present.
3. Make the edit (Step 1); run Step 2's check and all tests above; confirm all pass.
4. Commit with a Conventional Commit message, e.g.:
   ```
   docs(readme): describe uniform 7-platform MCP merge-on-update behavior

   README.md's --update section only described the plan-031/T370-era
   two-file merge scope (.vscode/mcp.json, .mcp.json). T377 extended the
   same merge-not-overwrite behavior to the other five platforms'
   MCP/settings files. Named every file explicitly so the doc reflects
   current, not historical, scope. CONTRIBUTING.md checked, not stale.

   Refs T380
   ```
5. Do NOT push. Do NOT open a merge request. Do NOT merge to `develop` or `main`. Stop after the
   local commit (stacked on top of prior commits on this branch) and report completion (commit SHA,
   full test output) back to the orchestrator. T381 will push this branch and open the MR.

## Constraints
- Token budget: ≤8k tokens.
- File ownership: `README.md`, lines 101-110 only.
- No unrelated refactor of this file.
