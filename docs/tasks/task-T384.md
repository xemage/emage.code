# Task T384 — Document per-platform runtime MCP verification checklist (P2)

**ID:** T384
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Depends on:** T381
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-08)

This brief is self-contained. You do not need to read plan-033 to execute this task.

## Objective
`tests/functional/test_platform_projections.py` proves the generator is internally consistent and
deterministic (exact-shape assertions against `sync.mjs`'s own expected output) — it does NOT prove
a generated MCP config actually loads and works in the platform's real tooling. The only place that
has ever happened is a documented one-time manual spot-check for Cline (T365: this host's real
`~/.cline/data/settings/cline_mcp_settings.json` compared byte-identical to the corrected
`implementation/.cline/mcp.json`). No equivalent check, automated or documented, exists for
`vscode`/`cursor`/`gemini`/`opencode`/`pi`/`claude-code`. Close this gap by documenting an explicit,
honest, per-platform verification checklist — automated where a real published schema exists,
manual-but-documented everywhere else — so no platform is silently unaddressed.

## Inputs
- `/home/emage/Code/emage/emage.code/docs/wiki/mcp-servers.md` — the file you will extend. Read its
  full current content first (88 lines as of this brief — re-count yourself, it may have grown from
  T379's edit landing first). Its existing "Per-platform output" table (lines 48-58) and "Remote-
  server transport encoding differs per platform" section (lines 62-88, added by T364) are the
  established precedent for how this file presents per-platform, source-cited technical detail —
  follow that same voice and citation discipline (fetched-live doc URLs, not memory) for your new
  section.
- `docs/tasks/task-T365.md` — read this for the exact Cline precedent's methodology (what "manual
  verification" meant in practice for Cline: comparing a real installed settings file on the host to
  the generated output).
- Research task: for each of the 7 platforms (`vscode`/github-copilot, `cursor`, `gemini`,
  `opencode`, `pi`, `claude-code`, `cline`), determine via live web research (WebFetch/WebSearch —
  training-data memory is explicitly insufficient per this repo's established precedent from T360)
  whether that platform publishes an official, machine-readable JSON Schema for its MCP/settings
  config file that could be used for automated `jsonschema`-library validation in this repo's test
  suite (this repo already depends on `pyyaml`/`jsonschema` per `.gitlab-ci.yml`'s `unit-tests` job
  `before_script`, so the tooling is already available if a real schema exists to validate against).

## Allow-list (files you may touch)
- `docs/wiki/mcp-servers.md` — add a new section only (see Step 1); do not alter any existing
  section's content.
- IF, and only if, your research in Step 0 confirms a genuinely published, citable JSON Schema for a
  specific platform's config format: a new test file,
  `tests/functional/test_mcp_schema_validation.py`, validating that platform's generated output
  against the confirmed schema. This is conditional — do not create this file if no schema is
  confirmed; a documented manual-checklist entry is the correct, sufficient outcome for platforms
  without one.

## Deny-list (do not touch — no exceptions)
- Do NOT edit any other section of `docs/wiki/mcp-servers.md` (the "Tag system", "Core servers",
  "Extended servers", "Required environment variables", "Per-platform output", or "Remote-server
  transport encoding" sections).
- Do NOT add schema validation for a platform without a confirmed, cited, live-fetched official
  schema source — an assumed or inferred schema is not acceptable (this repeats the exact mistake
  plan-030 was created to fix: assuming one platform's config shape applies to another without
  independent per-platform verification).
- Do NOT edit `implementation/scripts/sync.mjs`, `scripts/install.sh`, or any generated MCP output
  file — this is a documentation (plus, conditionally, a new test) task, not a generator change.
- Do NOT edit `tests/functional/test_platform_projections.py` or any other existing test file.
- Do NOT create any new branch beyond the one specified in Git workflow below.

## Step 0 — Research (do this before writing anything)
For each of the 7 platforms, using live web research (not memory), determine:
1. Does the platform publish an official JSON Schema document for its MCP/settings config file
   (e.g. a `$schema` URL referenced in real user configs, or a schema file in the platform's own
   GitHub repo)?
2. If yes: cite the exact URL you fetched, and confirm it is genuinely the schema for the specific
   file this repo generates (`.vscode/mcp.json`'s `servers` block, `.cursor/mcp.json`'s
   `mcpServers` block, etc.) — not a schema for a different, unrelated config file from the same
   vendor.
3. If no, or inconclusive: record that explicitly — do not guess or infer from a sibling platform's
   schema (the same error this task exists to avoid repeating).

Record your findings in a table (this becomes the basis for Step 1's checklist) with columns:
`Platform | Published schema confirmed (Y/N) | Schema URL (if Y) | Verification method chosen`.

## Step 1 — Add the checklist section to docs/wiki/mcp-servers.md
Add a new `## Runtime verification checklist` section, placed after the existing "Remote-server
transport encoding differs per platform" section (the current last section in the file) — i.e.
append at the end of the file. Required content, one row/entry per platform, no platform omitted:

For each platform, state ONE of two verification methods, chosen per your Step 0 findings:
- **Automated (schema-backed):** only if Step 0 confirmed a real, cited schema — describe the test
  file added (if you created one) and link the cited schema source.
- **Documented manual check:** for every platform without a confirmed schema — write the literal,
  actionable steps a human (or an agent with actual access to the installed tool) would follow to
  confirm a generated config loads correctly in that platform's real tooling, mirroring the Cline
  precedent's structure (T365: compare the generated file against the platform's own real installed
  settings location, or start the tool and confirm the MCP server(s) appear as connected/available in
  its UI or CLI status output). Name the platform's real settings file location where applicable
  (research this per platform — do not guess) and what "correctly loaded" looks like from that
  platform's own UI/CLI (e.g. an MCP server list command, a status indicator, an error log location).

Every platform must have an entry — no platform may be left silently unaddressed, even if its entry
is "no automated check exists; documented manual steps are: (literal steps)."

## Step 2 — Conditional schema-validation test
If, and only if, Step 0 confirmed at least one platform has a genuinely published, citable schema:
add `tests/functional/test_mcp_schema_validation.py`, using the `jsonschema` library (already a
project test dependency per `.gitlab-ci.yml`), validating that platform's current generated output
(`implementation/.<platform>/<file>`) against the fetched/vendored schema. Cite the schema source
directly in the test file's module docstring. If you vendor a local copy of the schema (recommended,
to avoid a network dependency in CI), state exactly where you saved it and why.

If no platform has a confirmed schema, skip this step entirely and say so plainly in your task
report — this is a valid, expected outcome per the plan's own scoping ("add schema validation only
where a real published schema exists... document a manual checklist elsewhere").

## Tests to run (literal commands, run from repo root `/home/emage/Code/emage/emage.code`)

1. Markdown link check (this repo's CI runs an equivalent check — confirm any new links you added
   resolve):
   ```
   python3 -c "
   import re, os
   text = open('docs/wiki/mcp-servers.md', encoding='utf-8').read()
   for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', text):
       url = m.group(2)
       if url.startswith(('http://', 'https://', 'mailto:', '#')):
           continue
       print('local link to check manually:', url)
   "
   ```
   Any local (non-`http`) link printed must resolve to a real path relative to the file; confirm
   manually.

2. IF you added `tests/functional/test_mcp_schema_validation.py`:
   ```
   python3 -m unittest tests.functional.test_mcp_schema_validation -v
   ```
   PASS = exits 0.

3. Full verification bar:
   ```
   make verify
   python3 docs/tasks/validate-tasks.py
   python3 tests/run.py
   ```
   PASS = `make verify` drift-free (unaffected by a `docs/wiki/` edit, confirms nothing else broke);
   `validate-tasks.py` → `TASK LEDGER: PASS`; `tests/run.py` exits 0, count not reduced (increased if
   you added Step 2's test).

## Acceptance criteria (all must be true)
- [ ] Step 0's research table covers all 7 platforms, each with an explicit Y/N schema-confirmation
      finding and a cited source or an explicit "no source found" statement — no platform silently
      skipped.
- [ ] `docs/wiki/mcp-servers.md`'s new "Runtime verification checklist" section covers all 7
      platforms, each with either an automated check description (schema-backed) or literal,
      actionable manual verification steps — no platform left as "not addressed."
- [ ] No existing section of `docs/wiki/mcp-servers.md` was altered.
- [ ] Any schema-validation test added is backed by a confirmed, cited, live-fetched published
      schema — not assumed, not inferred from a sibling platform.
- [ ] If no schema was confirmed for any platform, no new test file was created, and the task report
      states this plainly.
- [ ] The full verification bar passes.

## Blocker protocol
STOP and report a blocker (do not improvise a different fix) if:
- `docs/wiki/mcp-servers.md`'s current structure has changed materially from what's described above
  (section order, line counts) → `type: dependency`, `severity: minor` — re-verify against the
  current file; append your new section at the actual end of the file regardless.
- Live research (Step 0) cannot conclusively determine whether a platform publishes a schema after a
  genuine, time-bounded attempt (state how long you spent and what you searched) → `type:
  unclear_requirements`, `severity: minor` — this is a valid "inconclusive" outcome per Step 0's own
  instructions; document it as such rather than guessing, and this is NOT a blocker requiring
  escalation — proceed to Step 1 with a "manual check, no schema found" entry for that platform.
- Any verification command fails → `type: technical`, `severity: major`, include exact output.

Max 2 retries before escalating to the orchestrator with full context (only for a genuine blocker,
not for the expected "no schema found" research outcome, which is not a blocker).

## Git workflow
1. Create branch `docs/T384-mcp-runtime-verification-checklist` from the current tip of `develop`
   (T381 should already be merged; this task has no strict functional dependency on T377-T380's
   content, but branch from current `develop` regardless).
2. Do the research (Step 0), write the checklist (Step 1), and — only if applicable — add the schema
   test (Step 2). Run all tests above; confirm all pass.
3. Commit with a Conventional Commit message, e.g.:
   ```
   docs(mcp): add per-platform runtime MCP verification checklist

   Closes the gap where only Cline (T365) had ever had a real one-time
   tool-load verification. Researched, per platform, whether an official
   published JSON Schema exists for its MCP/settings config; added a
   "Runtime verification checklist" section to docs/wiki/mcp-servers.md
   covering all 7 platforms with either an automated schema-backed check
   or literal, actionable manual verification steps. [If applicable: added
   tests/functional/test_mcp_schema_validation.py for <platform>, backed
   by <cited schema source>.]

   Refs T384
   ```
4. Push the branch, open a merge request to `develop` referencing T384, wait for CI to go green,
   then STOP — do NOT merge yourself. Report completion to the orchestrator for independent
   re-review and merge.
5. Do NOT push to `develop` or `main` directly under any circumstance.

## Constraints
- Token budget: ≤10k tokens.
- File ownership: `docs/wiki/mcp-servers.md` (new section only), plus conditionally one new test
  file.
- No unrelated refactor of any file.
