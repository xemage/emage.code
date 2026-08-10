# Task T386 — Remove e2b/redis/figma/notion from servers.yaml; regenerate implementation/ trees

**ID:** T386
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Depends on:** T381
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-10)

**Dependency correction:** plan-033's Task Breakdown table lists T386 as `BlockedBy: —` (no
*functional* code dependency on T377-T381's merge-safety work — this task only edits
`servers.yaml` and regenerates `implementation/`, neither of which T377-T381 touch). That remains
true in isolation. However, plan-033's own Risks table and T388's brief both require that the
`chore/T386-...` branch (which carries both this task's and T387's commits) be "branched from
`develop` after T381 has already merged (not in parallel)" — specifically to prevent T387's
`AGENTS.md` "Extended servers" bullet edit from being cut from a stale pre-T379 `develop`, which
would conflict with T379's already-merged "Tag | Emitted to" table fix on the same file. Since T386
and T387 share one branch, T386 (which creates that branch) must not create it until T381 has
merged, even though T386's own diff never touches `AGENTS.md`. `Depends on: T381` above encodes this
git-workflow sequencing requirement, correcting the plan table's `—`. If you are asked to start this
task before T381 has merged, STOP and report a blocker (see below) rather than branching early.

This brief is self-contained. You do not need to read plan-033 to execute this task.

## Objective
Per the user's explicit request (not a discovered defect — a deliberate removal), delete the four
`extended`-tagged server entries `e2b`, `redis`, `figma`, `notion` from
`implementation/knowledge/mcp/servers.yaml` (clean YAML removal, not commenting-out), then
regenerate every `implementation/` canonical platform tree so the removal cascades through the
generator path (`node implementation/scripts/sync.mjs --root implementation`). This task only
touches the canonical `implementation/` source of truth and its generated trees — hand-authored docs
naming these servers are T387's scope, and this repo's own root self-install mirror is T382's scope
(after both T386/T387 land via T388).

## Inputs (exact path and content, verified against the current file — re-verify before editing; see
Blocker protocol)

`/home/emage/Code/emage/emage.code/implementation/knowledge/mcp/servers.yaml` — the four blocks to
remove, quoted verbatim with their exact current line numbers:

**`e2b` — lines 92-96:**
```yaml
  e2b:
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "e2b-mcp"]
```

**`redis` — lines 104-108:**
```yaml
  redis:
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "redis-mcp"]
```

**`figma` — lines 116-120:**
```yaml
  figma:
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "@figma/mcp"]
```

**`notion` — lines 122-126:**
```yaml
  notion:
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "@notion/mcp"]
```

Surrounding context you must NOT touch (read-only reference — confirms exactly what stays, in
order): `docker` (lines 98-102, immediately before `redis`), `postgresql` (lines 110-114,
immediately after `redis`, immediately before `figma`), `toolradar` (lines 128-136, immediately
after `notion`, the last entry in the file). After your edit, the `servers:` map's remaining order
must be: `gitlab`, `playwright`, `fetch`, `memory`, `sequential-thinking`, `brave`, `context7`
(unchanged `core` block), then `hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `docker`,
`postgresql`, `toolradar` (the `extended` block, with `e2b`/`redis`/`figma`/`notion` removed, all
other entries in their original relative order).

**Confirmed during planning — `implementation/scripts/sync.mjs` has zero hardcoded references to any
of the four server names (verified: `grep -in "e2b\|redis\|figma\|notion"
implementation/scripts/sync.mjs` returns no matches).** The generator is purely data-driven off
`servers.yaml` — there is no special-case code branch to also remove for any of these four servers.
Re-run this grep yourself before editing, to confirm it's still true.

## Allow-list (files/lines you may touch)
- `implementation/knowledge/mcp/servers.yaml` — ONLY the four blocks quoted above (delete them
  entirely, including each block's blank-line separator from its neighbor, so no double-blank-line
  or dangling comment is left behind).
- Every file under `implementation/.github/`, `implementation/.cursor/`, `implementation/.gemini/`,
  `implementation/.opencode/`, `implementation/.pi/`, `implementation/.claude/`,
  `implementation/.cline/`, `implementation/.vscode/`, `implementation/.mcp.json` — but ONLY as a
  side effect of running the sanctioned regeneration command in Step 2 below. Never hand-edit any
  generated file directly.

## Deny-list (do not touch — no exceptions)
- Do NOT remove, reorder, or modify any other entry in `servers.yaml` (`gitlab`, `playwright`,
  `fetch`, `memory`, `sequential-thinking`, `brave`, `context7`, `hf-mcp-server`, `filesystem`,
  `github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`) — 15 entries must remain, exactly
  as they are today, in their current relative order.
- Do NOT edit the file's header comment (lines 1-14) describing the tag system — it makes no
  per-server reference that needs updating.
- Do NOT edit `implementation/scripts/sync.mjs` — confirmed to need no change (see Inputs above).
- Do NOT edit any hand-authored doc (`implementation/PREREQUISITES.md`, `implementation/
  SECURITY.md`, `docs/wiki/mcp-servers.md`, either `AGENTS.md`) — that is T387's separate scope,
  sequenced after this task specifically so its `AGENTS.md` edit doesn't race T379's.
- Do NOT touch this repo's root self-install mirror (`.cursor/mcp.json`, `.gemini/settings.json`,
  etc. at repo root, outside `implementation/`) — that is T382's scope, after both this task and
  T387 land via T388.
- Do NOT edit `implementation/knowledge/skills/blocker-escalation/SKILL.md` or any of its platform
  copies — confirmed during planning to contain only an unrelated prose reference ("Redis-based
  distributed rate limiting") in a worked example, not a reference to the MCP server registry. No
  edit to this file is in scope for T386 or T387.
- Do NOT run `node implementation/scripts/sync.mjs` without `--root implementation` — running it
  with no `--root` flag or a wrong root will target the wrong tree.
- Do NOT push to `develop` or `main`. Do NOT open a merge request. Do NOT merge anything. Stop after
  a local commit on your feature branch (see Git workflow below) — T387 will stack a further commit
  on the same branch; T388 performs the push/MR/merge.

## Step 1 — Edit servers.yaml
Delete the four blocks quoted above (`e2b`, `redis`, `figma`, `notion`) from
`implementation/knowledge/mcp/servers.yaml`, each including its trailing blank line, so the file
reads cleanly with no double-blank gaps and no orphaned comments.

## Step 2 — Regenerate
Run from repo root `/home/emage/Code/emage/emage.code`:
```
node implementation/scripts/sync.mjs --root implementation
```
This WRITES files (no `--check` flag) — this is intentional and correct for this step; you are
regenerating the canonical `implementation/` trees from the edited registry. Confirm with `git
status`/`git diff --stat` that only files under `implementation/` changed (plus your `servers.yaml`
edit itself).

## Tests to run (literal commands, run from repo root, after Step 2)

1. Confirm the four entries are gone, no commented-out remnants:
   ```
   grep -c "^  e2b:\|^  redis:\|^  figma:\|^  notion:" implementation/knowledge/mcp/servers.yaml
   ```
   PASS = prints `0`.

2. Confirm the 15 remaining entries are all still present and unmodified (spot-check via key
   presence — full content diff is covered by test 4 below):
   ```
   grep -c "^  gitlab:\|^  playwright:\|^  fetch:\|^  memory:\|^  sequential-thinking:\|^  brave:\|^  context7:\|^  hf-mcp-server:\|^  filesystem:\|^  github:\|^  git:\|^  supabase:\|^  docker:\|^  postgresql:\|^  toolradar:" implementation/knowledge/mcp/servers.yaml
   ```
   PASS = prints `15`.

3. Drift check — the regenerated trees must exactly match what the generator produces from the
   edited registry (this is the identical check `.gitlab-ci.yml`'s `sync-no-diff` job runs):
   ```
   node implementation/scripts/sync.mjs --root implementation
   git diff --quiet -- implementation/ && echo "PASS: no post-regen drift"
   ```
   PASS = prints `PASS: no post-regen drift` (running the generator a second time produces zero
   additional diff — proves your Step 2 run already captured everything).

4. Registry check:
   ```
   python3 implementation/scripts/generate-registry.py --root implementation --check
   ```
   PASS = registry up to date, exit 0.

5. Zero-hit grep across every regenerated `implementation/` platform tree:
   ```
   grep -rli "e2b\|redis\|figma\|notion" implementation/.github implementation/.cursor implementation/.gemini implementation/.opencode implementation/.pi implementation/.claude implementation/.cline implementation/.vscode implementation/.mcp.json 2>/dev/null
   ```
   PASS = empty output (zero files), with one documented exception you must verify separately, not
   assume: each platform's `implementation/.<platform>/skills/blocker-escalation/SKILL.md` contains
   the unrelated `redis` prose reference. Run the grep exactly as shown; if it returns ONLY
   `blocker-escalation/SKILL.md` paths (one per platform, `redis` only, never `e2b`/`figma`/
   `notion`), that is the expected, already-investigated, out-of-scope match — treat it as PASS. Any
   other file appearing, or `e2b`/`figma`/`notion` appearing anywhere, is a FAIL.

6. Full verification bar:
   ```
   make verify
   python3 docs/tasks/validate-tasks.py
   python3 tests/run.py
   ```
   PASS = `make verify` drift-free, `validate-tasks.py` → `TASK LEDGER: PASS`, `tests/run.py` exits
   0 (count not reduced from your own recorded baseline).

## Acceptance criteria (all must be true)
- [ ] `e2b`, `redis`, `figma`, `notion` entries fully removed from `servers.yaml` (test 1), no
      commented-out remnants.
- [ ] All 15 other entries in `servers.yaml` unmodified (test 2), same relative order.
- [ ] `node implementation/scripts/sync.mjs --root implementation` run and its full output committed;
      re-running it produces zero additional diff (test 3).
- [ ] `generate-registry.py --check` passes (test 4).
- [ ] Zero-hit grep across regenerated `implementation/` trees, modulo the one documented
      `blocker-escalation`/`redis` exception (test 5).
- [ ] Full verification bar (test 6) passes.
- [ ] `git diff` (this task's commit) touches `implementation/knowledge/mcp/servers.yaml` plus only
      files under `implementation/` produced by the regeneration — no hand-authored doc, no
      repo-root file outside `implementation/`.

## Blocker protocol
STOP and report a blocker (do not improvise a different fix) if:
- T381 has not yet merged to `develop` when you are asked to start this task → `type: dependency`,
  `severity: minor` — per the sequencing correction above, branching before T381 merges risks a
  stale-base conflict for T387's later `AGENTS.md` edit; ask the orchestrator to confirm T381 has
  merged before you create this task's branch.
- The actual current content of `servers.yaml`'s four target blocks doesn't match the verbatim YAML
  quoted above (different line numbers, different `args`/`command` values) → `type: dependency`,
  `severity: major` — re-verify against the current file before editing; content may have shifted.
- `implementation/scripts/sync.mjs` is found to contain a hardcoded reference to any of the four
  server names after all (contradicting the Inputs section's confirmed-clean finding) → `type:
  unclear_requirements`, `severity: major` — this brief's premise assumed a pure data-driven
  generator; if that's wrong, report the exact reference found before deciding whether it's also in
  scope to remove.
- Test 3's drift check is non-empty (the committed regenerated trees don't match a fresh
  regeneration) → `type: technical`, `severity: major` — do not commit a tree that doesn't match
  what the generator actually produces.
- Test 5 finds any hit beyond the documented `blocker-escalation`/`redis` exception → `type:
  technical`, `severity: major` — investigate before committing; the removal did not fully cascade.
- Any verification command fails → `type: technical`, `severity: major`, include exact output.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Confirm T381 has already merged to `develop` (`git log origin/develop --oneline | grep -i
   "T377\|T378\|T379\|T380"` returns at least one commit) — if not, STOP per Blocker protocol above.
2. Create branch `chore/T386-remove-e2b-redis-figma-notion-mcp-servers` from the current tip of
   `develop` (post-T381 merge).
3. Make the change (Steps 1-2); run all tests above; confirm all pass.
4. Commit with a Conventional Commit message, e.g.:
   ```
   chore(mcp): remove e2b/redis/figma/notion from server registry

   User-requested removal (not a discovered defect) of four extended-tagged
   MCP server entries from implementation/knowledge/mcp/servers.yaml.
   Regenerated every implementation/ canonical platform tree via
   `node implementation/scripts/sync.mjs --root implementation` so the
   removal cascades through the generator path. No hardcoded per-server
   references existed in sync.mjs to also update. Hand-authored docs
   (PREREQUISITES.md, SECURITY.md, docs/wiki/mcp-servers.md, both
   AGENTS.md files) are a separate follow-up commit (T387) on this same
   branch.

   Refs T386
   ```
5. Do NOT push. Do NOT open a merge request. Do NOT merge to `develop` or `main`. Stop after the
   local commit and report completion (branch name, commit SHA, full test output) back to the
   orchestrator. T387 will check out this same branch and stack its own commit on top; T388 will
   push it and open the MR.

## Constraints
- Token budget: ≤10k tokens.
- File ownership: `implementation/knowledge/mcp/servers.yaml` plus generated output under
  `implementation/`, produced only via the sanctioned regeneration command.
- No unrelated refactor of `servers.yaml` or the generator.
