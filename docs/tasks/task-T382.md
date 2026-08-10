# Task T382 — Execute repo-root update install (prove merge-safety + removal live)

**ID:** T382
**Owner:** devops-engineer
**Status:** blocked
**Priority:** P0
**Depends on:** T381, T388, T393
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-06)

This brief is self-contained. You do not need to read plan-033 to execute this task. You DO need
both T381 and T388 already merged to `develop` before you start — this task is blocked by both (see
Blocker protocol).

## Objective
Use the now-fixed `develop` installer (T377-T381's merge-safety fix, merged) together with the
now-updated server registry (T386-T388's `e2b`/`redis`/`figma`/`notion` removal, merged) to update
this repository's own root self-install, proving both changes live in one combined run — mirrors the
plan-031/T372 precedent, extended to also cover the removal. This is the actual filesystem mutation
of this repo's own root `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.cline/`, `.mcp.json`,
`.vscode/mcp.json` — not a test in a temp directory.

## Inputs
- `develop`, checked out fresh at its current tip — **must** already contain both T381's merged MR
  (installer merge-safety) and T388's merged MR (server removal). Verify both are present before
  proceeding (see Step 0).
- `scripts/install.sh`'s usage/help text (`scripts/install.sh --help`) — read it, don't guess flags.
- The current root self-install state, for a before/after diff:
  `/home/emage/Code/emage/emage.code/.vscode/mcp.json` (contains a hand-added `cwso` server block —
  `url: http://127.0.0.1:8080/mcp`, `headers.Authorization: Bearer ${input:cwso_jwt_token}` — and a
  top-level `inputs` array; both are placeholder-only, no literal secret; core-only file, so it does
  NOT currently contain `e2b`/`redis`/`figma`/`notion`, meaning the removal is not expected to touch
  this specific file's server list, only its `context7` shape if that ever drifts), plus
  `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`,
  `.cline/mcp.json`, `.mcp.json` (all `extended`-tagged files — these DO currently contain
  `e2b`/`redis`/`figma`/`notion` entries per the repo-wide grep run during this plan's investigation,
  and are expected to lose them in this run).

## Allow-list (what this task may touch)
- Repo-root platform output files only, via the sanctioned `scripts/install.sh --update` command
  (Step 2 below) — `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.cline/`, `.clinerules/`,
  `.github/`, `.claude/`, `.vscode/mcp.json`, `.mcp.json`, root `AGENTS.md`, root `CLAUDE.md`, and
  `docs/` (per `install_docs()`'s merge-preserve behavior). All changes must come from running the
  installer — never hand-edit any of these files directly.

## Deny-list (do not touch — no exceptions)
- Do NOT hand-edit any generated/installed file directly (same rule as every prior repo-root
  install task in this repo's history — T362, T372, T376). The installer is the only sanctioned
  mutator.
- Do NOT run `node implementation/scripts/sync.mjs` (without `--check`) in this task — that
  regenerates `implementation/`'s own trees, a different, already-completed step from T386. This
  task only runs `scripts/install.sh --update`, which copies FROM `implementation/` INTO the repo
  root.
- Do NOT proceed if either T381 or T388 has not actually merged to `develop` yet (see Blocker
  protocol) — this task's "no unexpected destruction" and "no e2b/redis/figma/notion" proof points
  are only meaningful once both are live.
- Do NOT revert or "clean up" any diff you don't understand without investigating first — per AC #2
  below, only two classes of change are expected; anything else must be investigated, not silently
  discarded or silently accepted.
- Do NOT push to `develop` or `main` directly. Do NOT merge yourself. Stop after opening the MR and
  confirming CI is green (see Git workflow below) — report completion to the orchestrator, who
  performs the final independent re-review and merge (same pattern as every prior repo-root install
  task: T362, T372, T376 were all independently re-reviewed by the orchestrator before merging, not
  merged on the delegate's own report).

## Step 0 — Confirm both prerequisite merges are actually present
```
git fetch origin
git log origin/develop --oneline | grep -i "T377\|T378\|T379\|T380" | head -5
git log origin/develop --oneline | grep -i "T386\|T387" | head -5
```
Both searches must return at least one commit. If either returns nothing, STOP — see Blocker
protocol. Do not proceed on the assumption that "the orchestrator said both are merged" without this
direct confirmation.

## Step 1 — Dry-run first (always, regardless of expected outcome)
```
git checkout develop && git pull origin develop
scripts/install.sh --target . --update --platform all --dry-run
```
Confirm the dry-run output shows `merge-mcp-json.py`, not a plain `cp`, being invoked for
`.vscode/mcp.json`, `.mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`,
`.opencode/opencode.json`, `.pi/mcp.json`, and `.cline/mcp.json` (all seven should now show the
merge path, not just the original two — this is itself a live confirmation that T377's fix reached
`develop`). Capture this output.

## Step 2 — Execute for real
```
git status --short   # confirm clean tree before starting
scripts/install.sh --target . --update --platform all
git status --short
git diff --stat
```
Capture the full `git status`/`git diff --stat` output — you will need it for Step 3.

## Step 2b — Apply the one-time bootstrap bridge (T393-added; e2b/redis/figma/notion)
Per plan-034/T389-T393 (its `feature/T389-mcp-merge-provenance-tracking` branch merged via T393
before this task starts — confirmed in Step 0/T393's own gate), the general provenance-diffing
mechanism cannot retroactively prune `e2b`/`redis`/`figma`/`notion` on this run, because this repo's
root had zero provenance history before that fix shipped — this is the general mechanism's own
documented bootstrap-safe default (see `docs/decisions/ADR-002-mcp-merge-provenance-tracking.md`),
not a bug. Closing this specific, already-reviewed gap requires the one-time, explicitly-named bridge
flag T390 added to `scripts/merge-mcp-json.py`. Confirm its exact current name/usage before running —
```
python3 scripts/merge-mcp-json.py --help
```
— in case it differs from `--force-prune-keys` as named when this brief was written (T390's brief
explicitly allowed it to deviate from that name if ADR-002 required it); use whichever flag the
actually-merged script exposes, but always pass exactly the four names below, no more, no fewer:

Run it once per `extended`-tagged root mirror file (the six files confirmed above to currently
contain these four entries — `.vscode/mcp.json` is `core`-only and never had them, skip it):
```
for f in .cursor/mcp.json .gemini/settings.json .opencode/opencode.json .pi/mcp.json .cline/mcp.json .mcp.json; do
  python3 scripts/merge-mcp-json.py --source "implementation/$f" --dest "$f" --force-prune-keys e2b,redis,figma,notion
done
```
This must run AFTER Step 2's normal `--update` pass (so the ordinary merge/refresh has already
happened) and BEFORE Step 3's diff classification (so Step 3's "Class (b)" expectation — the four
names gone — is evaluated against the final, post-bridge state). If any invocation errors (non-zero
exit), STOP — per T390's design, the bridge flag errors rather than silently no-oping when a named key
isn't actually present as a dest-only key in that specific file; investigate before proceeding
(a non-zero exit on one file, e.g. because that file already lost the key via some other path, is not
necessarily a problem — confirm the key is actually already absent before treating it as a blocker —
but do not silently retry with a different name list either way).

## Step 3 — Classify the diff
Per plan-033's investigation, exactly two classes of change are expected in this run. Every changed
file's diff must be attributable to one of these two classes; anything else is a FAIL requiring
investigation before you proceed to commit:

**Class (a) — merge-safety fix, no destructive loss (T377-T381):**
- `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`,
  `.cline/mcp.json` — any generator-known key (e.g. `context7`) refreshed to current generated
  content; any hand-added key at this repo's root (if one exists) preserved, not deleted.
- `.vscode/mcp.json` — the hand-added `cwso` server block and the `inputs` array must survive
  completely unchanged (byte-for-byte) — this is the single most important non-destruction check in
  this task, since it is real hand-authored content unique to this repo, with real precedent (T362
  had to revert a destructive run before the merge fix existed; T372 first proved the fix preserves
  it). If `cwso` or `inputs` is missing or altered after this run, that is an immediate FAIL — STOP,
  do not commit, report a blocker.
- `.mcp.json` — same non-destruction expectation, though this file currently has no known hand-added
  content (confirm before assuming there's nothing to check).

**Class (b) — server removal (T386-T388):**
- `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`,
  `.cline/mcp.json`, `.mcp.json` — the `e2b`, `redis`, `figma`, `notion` server entries no longer
  present. `.vscode/mcp.json` is core-only and never had these four entries, so it is not expected to
  show a Class (b) diff.

**Any diff outside classes (a)/(b)** — e.g. an unrelated file like `.claude/settings.json` changing,
`AGENTS.md` changing unexpectedly, a brand-new top-level file/directory appearing, or any file
outside the platform-output allow-list changing — is a FAIL. Do not commit it. Investigate (likely
candidate: an unrelated hand-maintained file being swept up by a full-tree `rsync --delete`, the same
class of collateral T362 and T372 both had to revert) and either explain-and-accept with orchestrator
sign-off or revert the specific unexpected file with `git checkout -- <file>` before committing the
rest.

## Step 4 — Zero-hit grep for the removed servers (repo-wide, not just root platform files)
```
grep -rli "e2b\|redis\|figma\|notion" --include="*.json" . | grep -v "^\./\.git/"
```
Expected: this returns ONLY files already excluded from T387's scrub as historical records
(`docs/tasks/task-T357.md`, `docs/tasks/task-T354.md`,
`docs/checkpoints/checkpoint-v3-008-parallel-complete.md`, this plan file itself — none of which are
`.json`, so this specific `--include="*.json"` grep should in practice return **zero** matches
entirely once this task completes) plus, if present, `implementation/knowledge/skills/
blocker-escalation/SKILL.md` and its platform copies (a prose "Redis-based rate limiting" example,
confirmed unrelated to the MCP registry — but that file is `.md`, not `.json`, so it will not appear
in this specific `--include="*.json"` grep either). If this grep returns any `.json` hit, that is a
FAIL — the removal did not fully propagate to this repo's root mirror; investigate before committing.

## Tests to run (literal commands, run from repo root, after Step 2 and before committing)
```
make verify
python3 implementation/scripts/generate-registry.py --root implementation --check
python3 docs/tasks/validate-tasks.py
python3 tests/run.py
node implementation/scripts/sync.mjs --root implementation --check
```
PASS = all five commands exit 0, matching the same PASS conditions documented in T381's brief (`make
verify`/`sync.mjs --check` → drift-free; `generate-registry.py --check` → up to date;
`validate-tasks.py` → `TASK LEDGER: PASS`; `tests/run.py` → exits 0, count not reduced). None of
these five commands are expected to be affected by a root self-install refresh (they all validate
`implementation/`-tree state and the task ledger, not the root mirror) — running them here is a
regression guard, confirming this task's changes didn't accidentally disturb anything they check.

## Acceptance criteria (all must be true)
- [ ] Step 0 confirms both T381's and T388's merges are present on `develop` before proceeding.
- [ ] `git status`/`git diff --stat` captured before and after Step 2.
- [ ] Every changed file's diff is attributable to Class (a) or Class (b) per Step 3 — no unexplained
      diff committed.
- [ ] `.vscode/mcp.json`'s hand-added `cwso` block and `inputs` array survive byte-for-byte unchanged.
- [ ] Step 4's repo-wide `.json`-scoped grep for `e2b|redis|figma|notion` returns zero hits.
- [ ] The full verification bar (5 commands above) passes after the update.
- [ ] Result committed through the normal branch + MR flow (see Git workflow below) — never a direct
      commit to `develop`.
- [ ] Any collateral/unrelated diff found was either reverted or explicitly flagged to the
      orchestrator with reasoning — never silently committed.

## Blocker protocol
STOP and report a blocker (do not improvise a workaround) if:
- Step 0 cannot confirm either T381's or T388's merge is present on `origin/develop` → `type:
  dependency`, `severity: critical` — do not proceed; this task's entire premise depends on both.
- Step 3 finds a diff outside the two expected classes that you cannot confidently explain →
  `type: technical`, `severity: major` — do not silently commit or silently discard it; report the
  exact file and diff for orchestrator disposition, the same pattern T362 and T372 both used
  successfully for this exact class of problem.
- `.vscode/mcp.json`'s `cwso` block or `inputs` array is missing or altered after Step 2 → `type:
  technical`, `severity: critical` — this means T377's merge-safety fix did not actually reach
  `develop` correctly, or regressed; do not proceed to commit under any circumstance.
- Step 4's grep finds a `.json` hit for any of the four removed server names → `type: technical`,
  `severity: major` — the removal (T386-T388) did not fully propagate; do not commit until resolved.
- Any verification command fails → `type: technical`, `severity: major`, include exact output.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Create branch `chore/T382-repo-root-update-install` from the current tip of `develop` (post both
   T381 and T388 merges — confirmed by Step 0).
2. Run Steps 1-4 and the verification bar; confirm all pass.
3. Commit with a Conventional Commit message, e.g.:
   ```
   chore(install): refresh repo-root self-install (merge-safety + server removal)

   Ran `scripts/install.sh --target . --update --platform all` against the
   now-fixed develop (T377-T381 installer merge-safety extended to
   cursor/gemini/opencode/pi/cline; T386-T388 removed e2b/redis/figma/notion
   from the MCP server registry). Confirmed no destructive loss of the
   hand-added cwso MCP block or inputs array in .vscode/mcp.json, and zero
   remaining e2b/redis/figma/notion references in any repo-root MCP/settings
   JSON file. Full verification bar green after.

   Refs T382
   ```
4. Push the branch, open a merge request to `develop` referencing T382 (and T377-T381/T386-T388 as
   the work it proves live), wait for CI to go green, then STOP — do NOT merge yourself. Report
   completion to the orchestrator for independent re-review and merge (same pattern as T362, T372,
   T376 — the orchestrator always independently re-verifies a repo-root self-install change before
   merging, never on the delegate's own report alone).
5. Do NOT push to `develop` or `main` directly under any circumstance.

## Constraints
- Token budget: ≤20k tokens.
- File ownership: repo-root platform output files only, and only via `scripts/install.sh`.
- This task does not cut a new release/version tag.
