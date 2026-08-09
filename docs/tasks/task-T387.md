# Task T387 — Remove e2b/redis/figma/notion references from hand-authored docs

**ID:** T387
**Owner:** technical-writer
**Status:** pending
**Priority:** P1
**Depends on:** T386, T381
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-11)

This brief is self-contained. You do not need to read plan-033 to execute this task. You DO need
T386's commit already present on the branch you check out (see Git workflow below), and T381 must
already be merged to `develop` before this task's branch was created (T386 confirms this
prerequisite when it creates the branch — see T386's brief; if you find the branch was cut before
T381 merged, treat that as a blocker per below, do not proceed).

## Objective
Removing `e2b`/`redis`/`figma`/`notion` from `implementation/knowledge/mcp/servers.yaml` (T386) does
not auto-update hand-authored prose or manually-maintained lists/tables that name these servers by
hand. Update every such location: `implementation/PREREQUISITES.md`, `implementation/SECURITY.md`,
`docs/wiki/mcp-servers.md`, and both `AGENTS.md` files' "Extended servers (opt-in)" bullet.

## Reconciliation with T379 (read before editing either `AGENTS.md` file)
Both T387 (this task) and T379 (already merged via T381 by the time you start, per this task's
dependency) touch `AGENTS.md` (both copies), but at different, non-overlapping locations: T379 fixed
the "Tag | Emitted to" table (line 98 in both files). T387 fixes the separate "### Extended servers
(opt-in)" bullet immediately below it (line 113 in both files, unchanged by T379). They are two
different tasks with different root causes (T379: doc-drift bug fix; T387: deliberate user-requested
removal) shipping through separate validation gates (T381 vs T388) specifically so this task's branch
is cut from `develop` only after T379's fix is already merged — avoiding a same-file merge conflict.
Do NOT touch line 98's table in either file — that is T379's already-merged content; confirm it
already reads "platforms whose manifest opts in (all except `github`: `cursor`, `gemini`,
`opencode`, `pi`, `claude-code`, `cline`)" before you start (if it doesn't, T381 hasn't actually
merged — STOP, see Blocker protocol).

## Inputs (exact paths and content, verified against the current file at planning time — re-verify
against your actual branch tip before editing; see Blocker protocol)

**1. `/home/emage/Code/emage/emage.code/implementation/PREREQUISITES.md`, line 28:**
```
- platform-specific tokens for `github`, `supabase`, `e2b`, `figma`, `notion`, `redis`, `postgresql`
```

**2. `/home/emage/Code/emage/emage.code/implementation/SECURITY.md`, line 45:**
```
`extended` servers reach external infrastructure (Hugging Face, Figma, Notion, Supabase, Docker socket, Redis, Postgres). Enabling them in your platform manifest grants the AI access to those systems via MCP. Audit each server before use.
```

**3. `/home/emage/Code/emage/emage.code/docs/wiki/mcp-servers.md`:**
- Line 31 (the "Extended servers (opt-in)" list):
  ```
  `hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `e2b`, `docker`, `redis`, `postgresql`, `figma`, `notion`, `toolradar`.
  ```
- Lines 43-44 (env-var table rows — `e2b`/`redis` never had corresponding rows here, since neither
  ever declared an `env:` block in `servers.yaml`; only `figma`/`notion` have rows to remove):
  ```
  | `FIGMA_ACCESS_TOKEN` | `figma` (extended) | Personal access token |
  | `NOTION_API_KEY` | `notion` (extended) | Internal integration token |
  ```
  These two rows sit between the `SUPABASE_ACCESS_TOKEN` row (line 42, keep) and the `> **Never
  commit these...**` blockquote (line 46, keep) — read-only context confirming exactly what
  surrounds the two rows you are deleting.

**4. `/home/emage/Code/emage/emage.code/AGENTS.md` (repo root) and
`/home/emage/Code/emage/emage.code/implementation/AGENTS.md` (canonical) — both at line 113 (the
"### Extended servers (opt-in)" bullet, unchanged by T379's line-98 fix):**
```
`hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `e2b`, `docker`, `redis`, `postgresql`, `figma`, `notion`, `toolradar`. Most require additional credentials — see `servers.yaml` for the env-var contract.
```
Per the T373/T376/T379 precedent: `implementation/AGENTS.md` is hand-edited directly; root
`AGENTS.md` is NEVER hand-edited — it must be regenerated via `scripts/render_installed_agents.py`
(same mechanism T379 used). This line, like the "Tag | Emitted to" table, is plain pass-through text
in `render()` (not one of the five `_replace_one()` substitution targets), so editing
`implementation/AGENTS.md` and re-running the render is both necessary and sufficient.

## Allow-list (files/lines you may touch)
- `implementation/PREREQUISITES.md` — line 28 only.
- `implementation/SECURITY.md` — line 45 only.
- `docs/wiki/mcp-servers.md` — line 31, and lines 43-44 (delete both rows).
- `implementation/AGENTS.md` — line 113 only.
- `AGENTS.md` (repo root) — ONLY via the sanctioned render command in Step 5 below; never by hand.

## Deny-list (do not touch — no exceptions)
- Do NOT touch line 98 (the "Tag | Emitted to" table) in either `AGENTS.md` file — that is T379's
  already-merged content; leave it exactly as it is.
- Do NOT touch any other line in `PREREQUISITES.md`, `SECURITY.md`, or `docs/wiki/mcp-servers.md`
  beyond the specific lines/rows identified above.
- Do NOT edit `implementation/knowledge/mcp/servers.yaml` — that is T386's already-completed scope
  on this same branch; do not re-touch it.
- Do NOT edit `implementation/scripts/sync.mjs` or any generated `implementation/<platform>/` file
  directly.
- Do NOT edit `implementation/knowledge/skills/blocker-escalation/SKILL.md` or any of its platform
  copies — confirmed (T386's brief) to be an unrelated prose reference to "Redis-based rate
  limiting" in a worked example, not a reference to the MCP server registry. No edit to this file is
  in scope.
- Do NOT touch this repo's root self-install mirror files (`.cursor/mcp.json`,
  `.gemini/settings.json`, etc. at repo root, outside `implementation/` and outside the two
  `AGENTS.md` files) — that is T382's separate, later scope.
- Do NOT create any new branch — use the branch T386 already created (see Git workflow below).

## Step 1 — Edit PREREQUISITES.md
Change line 28 from:
```
- platform-specific tokens for `github`, `supabase`, `e2b`, `figma`, `notion`, `redis`, `postgresql`
```
to exactly:
```
- platform-specific tokens for `github`, `supabase`, `postgresql`
```

## Step 2 — Edit SECURITY.md
Change line 45 from:
```
`extended` servers reach external infrastructure (Hugging Face, Figma, Notion, Supabase, Docker socket, Redis, Postgres). Enabling them in your platform manifest grants the AI access to those systems via MCP. Audit each server before use.
```
to exactly:
```
`extended` servers reach external infrastructure (Hugging Face, Supabase, Docker socket, Postgres). Enabling them in your platform manifest grants the AI access to those systems via MCP. Audit each server before use.
```

## Step 3 — Edit docs/wiki/mcp-servers.md
Change line 31 from:
```
`hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `e2b`, `docker`, `redis`, `postgresql`, `figma`, `notion`, `toolradar`.
```
to exactly:
```
`hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`.
```
Delete lines 43-44 entirely (the `FIGMA_ACCESS_TOKEN` and `NOTION_API_KEY` table rows), leaving the
`SUPABASE_ACCESS_TOKEN` row (line 42) immediately followed by the `> **Never commit these...**`
blockquote (originally line 46) with no blank line inserted between them beyond what already existed
in the table's own row spacing.

## Step 4 — Edit implementation/AGENTS.md
Change line 113 from:
```
`hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `e2b`, `docker`, `redis`, `postgresql`, `figma`, `notion`, `toolradar`. Most require additional credentials — see `servers.yaml` for the env-var contract.
```
to exactly:
```
`hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`. Most require additional credentials — see `servers.yaml` for the env-var contract.
```

## Step 5 — Regenerate root AGENTS.md (never hand-edit)
Run from repo root `/home/emage/Code/emage/emage.code`, after Step 4's edit is saved:
```
python3 scripts/render_installed_agents.py --source implementation/AGENTS.md --dest AGENTS.md --platform all
git diff AGENTS.md
```
The diff must show ONLY the one line-113 change (same reasoning as T379's Step 2 — this is
pass-through text, so a one-line diff is expected). If it shows anything else, including any change
to line 98's table, STOP and report a blocker.

## Tests to run (literal commands, run from repo root)

1. Confirm all edits landed:
   ```
   grep -c 'tokens for `github`, `supabase`, `postgresql`' implementation/PREREQUISITES.md
   grep -c 'Hugging Face, Supabase, Docker socket, Postgres' implementation/SECURITY.md
   grep -c '`hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`\.' docs/wiki/mcp-servers.md
   grep -c 'FIGMA_ACCESS_TOKEN\|NOTION_API_KEY' docs/wiki/mcp-servers.md
   grep -c '`hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`\. Most require' implementation/AGENTS.md
   grep -c '`hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`\. Most require' AGENTS.md
   ```
   PASS = first, second, third, fifth, sixth commands each print `1`; the fourth (`FIGMA_ACCESS_TOKEN
   \|NOTION_API_KEY`) prints `0`.

2. Repo-wide grep sweep for the four names, excluding the explicitly out-of-scope historical
   records and the confirmed-unrelated `blocker-escalation` prose reference (run from repo root):
   ```
   grep -rli "e2b\|redis\|figma\|notion" . \
     --include="*.md" --include="*.yaml" --include="*.json" \
     2>/dev/null | grep -v "^\./\.git/" \
     | grep -v "docs/tasks/task-T357.md" \
     | grep -v "docs/tasks/task-T354.md" \
     | grep -v "docs/checkpoints/checkpoint-v3-008-parallel-complete.md" \
     | grep -v "docs/plans/plan-033-mcp-settings-hardening.md" \
     | grep -v "docs/tasks/task-T386.md" \
     | grep -v "docs/tasks/task-T387.md" \
     | grep -v "blocker-escalation/SKILL.md"
   ```
   PASS = empty output. (This grep intentionally excludes this brief and T386's brief themselves,
   since they legitimately quote the four names as historical/planning record; it does NOT exclude
   this repo's root self-install mirror files, e.g. `.cursor/mcp.json` — if those still contain the
   four names at this point in the plan, that is expected and correct, since T382 (root mirror
   refresh) runs AFTER this task, not before. If this grep surfaces a root mirror file, do not treat
   it as a failure of this task — note it in your report as "expected, T382 not yet run" rather than
   investigating it as a bug.)

3. Full verification bar:
   ```
   make verify
   python3 implementation/scripts/generate-registry.py --root implementation --check
   python3 docs/tasks/validate-tasks.py
   python3 tests/run.py
   node implementation/scripts/sync.mjs --root implementation --check
   ```
   PASS = all five exit 0 per the same conditions documented in prior briefs.

## Acceptance criteria (all must be true)
- [ ] All four server names removed from every hand-authored location listed above; no dangling
      comma, stray "and", or broken list punctuation left behind (visually inspect each edited line).
- [ ] `implementation/PREREQUISITES.md` line 28's token list retains its remaining entries
      (`github`, `supabase`, `postgresql`) unchanged aside from the four removals.
- [ ] `docs/wiki/mcp-servers.md`'s env-var table loses exactly the `FIGMA_ACCESS_TOKEN` and
      `NOTION_API_KEY` rows; no other row touched.
- [ ] Root `AGENTS.md` was produced by the Step 5 render command, never hand-edited.
- [ ] Test 1's six checks all pass exactly as specified.
- [ ] Test 2's repo-wide sweep (scoped to non-mirror files) is empty.
- [ ] The full verification bar (test 3) passes.
- [ ] `implementation/knowledge/skills/blocker-escalation/SKILL.md` (any copy) was NOT edited.
- [ ] Line 98 of both `AGENTS.md` files (T379's table fix) is unchanged by this task's diff.

## Blocker protocol
STOP and report a blocker (do not improvise a different fix) if:
- The branch T386 created (`chore/T386-remove-e2b-redis-figma-notion-mcp-servers`) does not exist,
  or does not contain T386's commit → `type: dependency`, `severity: critical`.
- Line 98 of `implementation/AGENTS.md`/root `AGENTS.md` does NOT already read T379's corrected text
  ("platforms whose manifest opts in (all except `github`: ...)") → `type: dependency`, `severity:
  major` — this means T381 has not actually merged to `develop` yet even though this branch exists;
  editing `AGENTS.md` now risks the exact conflict this task's sequencing was designed to avoid; do
  not proceed, ask the orchestrator to confirm T381's merge status first.
- The actual current content at any of the quoted line numbers doesn't match what's shown above →
  `type: dependency`, `severity: major` — re-verify against the current file before editing.
- Step 5's `git diff AGENTS.md` shows anything beyond the single expected line-113 change → `type:
  technical`, `severity: major` — do not commit an unexpected diff.
- Test 2's grep surfaces a hit in a file that is NOT a root self-install mirror file and NOT already
  excluded → `type: technical`, `severity: major` — investigate before committing.
- Any verification command fails → `type: technical`, `severity: major`, include exact output.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Check out the EXISTING branch `chore/T386-remove-e2b-redis-figma-notion-mcp-servers` (created by
   T386 — do NOT create a new branch, do NOT branch from `develop`).
2. Confirm T386's commit is present, and confirm (per the Blocker protocol above) that
   `AGENTS.md`/`implementation/AGENTS.md` already carry T379's merged fix.
3. Make the five edits (Steps 1-5); run all tests above; confirm all pass.
4. Commit with a Conventional Commit message, e.g.:
   ```
   docs(mcp): remove e2b/redis/figma/notion references from hand-authored docs

   T386 removed these four extended-tagged servers from
   implementation/knowledge/mcp/servers.yaml and regenerated
   implementation/'s generated trees. This commit updates the
   hand-authored (non-generated) prose that named them by hand:
   implementation/PREREQUISITES.md's credential token list,
   implementation/SECURITY.md's infrastructure-reach paragraph,
   docs/wiki/mcp-servers.md's extended-server list and env-var table
   (FIGMA_ACCESS_TOKEN, NOTION_API_KEY rows removed), and both AGENTS.md
   files' "Extended servers (opt-in)" bullet (root AGENTS.md regenerated
   via render_installed_agents.py, never hand-edited). Sequenced after
   T381 specifically so this AGENTS.md edit lands on top of T379's
   already-merged "Tag | Emitted to" table fix without conflict.

   Refs T387
   ```
5. Do NOT push. Do NOT open a merge request. Do NOT merge to `develop` or `main`. Stop after the
   local commit (stacked on top of T386's commit, same branch) and report completion (commit SHA,
   full test output) back to the orchestrator. T388 will push this branch and open the MR.

## Constraints
- Token budget: ≤8k tokens.
- File ownership: the five files/lines named above only.
- No unrelated refactor of any file.
