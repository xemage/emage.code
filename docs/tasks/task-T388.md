# Task T388 — Validation gate and merge server removal to develop

**ID:** T388
**Owner:** tech-lead, orchestrator
**Status:** done
**Priority:** P1
**Depends on:** T386, T387
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-12)

This brief is self-contained. It has two roles: `tech-lead` performs a read-only review and issues a
VERDICT; the orchestrator then runs the verification bar and performs the actual git mechanics
(push, open MR, merge). `tech-lead` must never edit code during this review (per
`.claude/rules/security-guidelines.md`'s "Read-Only Agents" classification) and must never push,
open an MR, or merge — those are the orchestrator's steps below.

## Objective
Independently verify T386 (registry removal + `implementation/` regeneration) and T387 (hand-authored
doc updates) on branch `chore/T386-remove-e2b-redis-figma-notion-mcp-servers`, and if verification
passes, land the branch on `develop` via the standard branch + MR flow per
`.claude/rules/git-workflow.md`. This is a **separate** Implementation Gate from T381 — kept distinct
because T377-T380 (T381's scope) and T386-T387 (this gate's scope) have different Conventional
Commit types (`fix` for the merge-safety bug vs `chore`/`docs` for the deliberate removal) and
different root causes (discovered defect vs explicit user request). T381 must already be merged to
`develop` before this branch was created (T386 confirmed this when it created the branch) — verify
this is actually true before proceeding (Step 1 of the verification bar).

## Inputs
- Branch `chore/T386-remove-e2b-redis-figma-notion-mcp-servers` (created by T386, extended by T387)
  — check out its current tip, do not use a stale local copy.
- `git diff develop...chore/T386-remove-e2b-redis-figma-notion-mcp-servers` — the full diff to
  review. Expected scope: `implementation/knowledge/mcp/servers.yaml` (T386), the regenerated
  `implementation/<platform>/` files affected by removing four `extended`-tagged servers (T386 —
  every `implementation/` platform tree that emits `extended` servers, i.e. all except
  `implementation/.github/` and `implementation/.vscode/`, per T379's already-corrected finding that
  6 of 7 platforms opt into `extended`), `implementation/PREREQUISITES.md`,
  `implementation/SECURITY.md`, `docs/wiki/mcp-servers.md`, `implementation/AGENTS.md`, and root
  `AGENTS.md` (all T387). Any file outside this set appearing in the diff is out-of-scope collateral
  and must be flagged, not silently accepted.

## Allow-list (what this task may do)
- Read-only review of the diff (tech-lead).
- Running the verification commands listed below (no file edits produced by running them).
- Git operations only: checkout, push the existing branch, open a merge request, merge after CI is
  green (orchestrator). No source file edits by either role in this task.

## Deny-list (do not do — no exceptions)
- Do NOT edit `servers.yaml`, any regenerated `implementation/` file, any of the four hand-authored
  docs, or either `AGENTS.md` in this task. If verification fails, the fix belongs in a new fix task
  routed back to T386's or T387's owner — not hand-patched here.
- Do NOT push directly to `develop` or `main`.
- Do NOT merge if any verification command fails, or if CI is not green.
- Do NOT force-push, do NOT skip CI, do NOT use `--no-verify`.
- Do NOT merge based solely on T386's/T387's own completion reports — the diff and verification
  commands below must be independently re-run and re-reviewed in this task, not assumed from prior
  reports.
- Do NOT run the repo-root self-install refresh (`scripts/install.sh --update --platform all`) in
  this task — that is T382's separate scope, which runs after both this gate AND T381 have merged.

## Verification bar (literal commands, run from repo root `/home/emage/Code/emage/emage.code`, after
checking out `chore/T386-remove-e2b-redis-figma-notion-mcp-servers`)

1. Confirm T381 actually merged before this branch was cut (required precondition per T386's
   sequencing correction):
   ```
   git merge-base --is-ancestor origin/develop chore/T386-remove-e2b-redis-figma-notion-mcp-servers 2>&1; echo "exit=$?"
   git log develop --oneline | grep -i "T377\|T378\|T379\|T380" | head -3
   ```
   The branch's merge-base with `develop` should already include T377-T380's commits (from T381's
   merge). If T381's commits are absent from this branch's history, that's a sequencing violation —
   `type: dependency`, `severity: major` (see Blocker protocol), do not proceed to merge.

2. ```
   make verify
   ```
   PASS = drift-free output (current file count), exit 0. This is the most important check for this
   specific gate — it directly validates that T386's `sync.mjs` regeneration output matches what the
   generator produces from the edited `servers.yaml`, i.e. that the removal is complete and
   self-consistent across all `implementation/` platform trees.

3. ```
   python3 implementation/scripts/generate-registry.py --root implementation --check
   ```
   PASS = registry up to date, exit 0.

4. ```
   python3 docs/tasks/validate-tasks.py
   ```
   PASS = output starts with `TASK LEDGER: PASS`, exit 0.

5. ```
   python3 tests/run.py
   ```
   PASS = exits 0.

6. The grep sweep from T387's acceptance criteria, independently re-run (not trusted from T387's own
   report):
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
     | grep -v "docs/tasks/task-T388.md" \
     | grep -v "blocker-escalation/SKILL.md"
   ```
   PASS = empty output, EXCEPT for this repo's root self-install mirror files (`.cursor/mcp.json`,
   `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`, `.cline/mcp.json`,
   `.mcp.json`, all at repo root, outside `implementation/`) — those are explicitly out of scope
   for T386/T387 and are refreshed later by T382; their continued appearance in this grep at this
   point in the plan is expected, not a failure. Confirm any hit is exactly one of those six root
   mirror files before treating this as PASS; any other unexplained hit is a FAIL.

7. Full diff review (tech-lead, read-only):
   ```
   git diff develop...chore/T386-remove-e2b-redis-figma-notion-mcp-servers --stat
   git diff develop...chore/T386-remove-e2b-redis-figma-notion-mcp-servers -- implementation/knowledge/mcp/servers.yaml implementation/PREREQUISITES.md implementation/SECURITY.md docs/wiki/mcp-servers.md implementation/AGENTS.md AGENTS.md
   ```
   Confirm: `servers.yaml`'s diff removes exactly the four documented blocks, no other entry
   touched; the regenerated `implementation/` platform files' diffs are consistent with removing
   four servers (no unrelated content changed — spot-check via `--stat` that changed line counts are
   plausible for a 4-server removal, not a wholesale rewrite); the four hand-authored docs' diffs are
   each scoped to exactly the lines documented in T387's brief; both `AGENTS.md` files' diffs touch
   ONLY line 113 (the "Extended servers" bullet) — line 98 (T379's table, already merged via T381)
   must be unchanged in this diff.

## Acceptance criteria (all must be true)
- [ ] Step 1 confirms T381's commits are already present in this branch's history via `develop`.
- [ ] All verification commands (2-6) pass per their stated PASS conditions.
- [ ] `tech-lead` issues an explicit VERDICT: `PASS`, `CONDITIONAL_PASS`, or `FAIL`, referencing the
      specific diff and command output reviewed.
- [ ] On `PASS`/`CONDITIONAL_PASS`: orchestrator independently re-reviews the full diff (not just
      trusting T386's/T387's/tech-lead's reports), including confirming the grep sweep from step 6
      is clean modulo the documented root-mirror exception, pushes the branch, opens an MR from
      `chore/T386-remove-e2b-redis-figma-notion-mcp-servers` to `develop` referencing T386 and T387
      in the title or description, waits for CI to go green, then merges (per `git-workflow.md`'s
      convention — squash for a single logical change, or standard merge if the two commits should
      be preserved distinctly; default to squash-and-merge unless the orchestrator has reason to
      preserve the two-commit history).
- [ ] On `FAIL`: merge is blocked. A fix task is created and routed to T386's or T387's owner; this
      gate is re-run after the fix lands on the same branch.
- [ ] Branch name is exactly `chore/T386-remove-e2b-redis-figma-notion-mcp-servers` (already created
      by T386 — do not rename it).
- [ ] Post-merge `develop` tip re-passes verification commands 2-5 (re-run fresh).

## Blocker protocol
STOP and report a blocker if:
- The branch doesn't exist, or T386's/T387's commits aren't both present on it → `type: dependency`,
  `severity: critical`.
- Step 1 finds T381's commits are NOT present in this branch's ancestry → `type: dependency`,
  `severity: major` — the branch was cut before T381 merged, in violation of the required
  sequencing; do not merge; the branch needs to be rebased onto post-T381 `develop` (or recreated)
  before this gate can pass — escalate to the orchestrator for a decision rather than attempting the
  rebase yourself in this read-only-review task.
- Any verification command (2-6) fails → `type: technical`, `severity: major` (or `critical` if
  `python3 tests/run.py` fails), do not merge, create a fix task instead.
- The diff includes files outside the expected set (see Inputs) → `type: technical`, `severity:
  major` — scope creep must be resolved before merge.
- Step 6's grep surfaces an unexplained hit (not a root self-install mirror file, not an already
  excluded historical record) → `type: technical`, `severity: major` — the removal is incomplete;
  do not merge.
- CI does not go green after pushing/opening the MR → `type: technical`, `severity: major`, do not
  merge, investigate the specific failing job before retrying.

Max 2 retries before escalating to the user with full context (what was tried, exact failure).

## Git workflow
1. Check out `chore/T386-remove-e2b-redis-figma-notion-mcp-servers` at its current tip.
2. Run the verification bar (all 7 checks above); tech-lead reviews the diff and issues VERDICT.
3. On `PASS`/`CONDITIONAL_PASS`: `git push -u origin
   chore/T386-remove-e2b-redis-figma-notion-mcp-servers`.
4. Open a merge request targeting `develop`, title referencing T386 and T387 (e.g. "chore(mcp):
   remove e2b/redis/figma/notion server entries (T386, T387)").
5. Wait for CI to report green on the MR. Do not merge before CI completes.
6. Merge (squash-and-merge by default, per `git-workflow.md`'s convention for `chore/*` branches).
7. Delete the merged branch (normal cleanup per the Worktree Lifecycle in `git-workflow.md`).
8. Confirm post-merge `develop` tip re-passes verification commands 2-5 (re-run them on fresh
   `develop`, not just trust the pre-merge branch state).

## Constraints
- Token budget: ≤8k tokens.
- No source file edits in this task.
- Never commit directly to `develop` or `main` — only merge via the reviewed MR.
