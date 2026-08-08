# Task T342 — Codify "no direct commits to protected branches, ever" in git-workflow knowledge

**ID:** T342
**Owner:** devops-engineer
**Status:** done
**Completed:** 2026-08-08
**Priority:** P1
**Depends on:** —
**Created:** 2026-08-07
**Based on:** This session's own process incidents (see Context) — the orchestrator committed
directly to local `develop` twice in the same session (once for T340's investigation ledger
update, once for T341's closeout ledger update), both times rejected by GitLab's branch
protection on push and both times recovered by moving the commit onto a new branch and opening an
MR. The user explicitly asked to close this gap at the knowledge-base level so it does not recur.

## Objective
Update the canonical git-workflow instruction (and, if warranted, the task-management skill) so
that "every change to `main`/`develop` — including single-file, docs-only, ledger-only
orchestrator edits — goes through a branch and MR, no exceptions" is an explicit, unmissable rule,
not an inference left to the reader. Propagate the fix through this repo's actual sync/install
pipeline so every platform projection (not just one file) carries the update, and land it the
correct way: via a branch and MR, not a direct commit to `develop` (deliberately dogfooding the
fix this task itself adds).

## Context
- Phase: Implementation (small, knowledge-base only — no application code)
- What happened, concretely: after closing out T340 and T341, the orchestrator committed
  `docs/tasks/*.md` ledger transitions directly on the locally-checked-out `develop` branch twice.
  `git push origin develop` was rejected both times (`GitLab: You are not allowed to push code to
  protected branches on this project`). Recovery was clean both times (`git branch <name> <sha>`,
  `git reset --hard origin/develop`, push the new branch, open an MR, merge), but the root cause —
  no explicit rule stating that *even trivial docs/ledger edits* require a branch+MR — was never
  fixed at the source.
- `implementation/knowledge/instructions/git-workflow.md` is the **canonical source** for this
  repo's git-workflow guidance (confirmed via `diff` against `.claude/rules/git-workflow.md`,
  `.cursor/rules/git-workflow.mdc`, `implementation/.claude/rules/git-workflow.md` — all identical
  in body, differing only in the platform-specific frontmatter key: `applyTo` vs `paths` vs
  `globs`). It currently covers branching strategy, worktree lifecycle, commit message format, and
  MR rules — but never states a blanket "no direct commits to `main`/`develop`" rule. The closest
  existing statement, "Agent branches merge back to `develop` via merge request after review",
  is scoped to *agent* worktree branches and doesn't cover the orchestrator's own direct edits
  (ledger updates, checkpoints) made in the primary checkout.
- `implementation/knowledge/skills/task-management/SKILL.md` § "4. Complete a Task" describes the
  ledger-edit mechanics (append to `completed-tasks.md`, delete from `active-tasks.md`, update the
  task brief header) but says nothing about how those edits reach `develop` — this is the exact
  gap that let the orchestrator assume a direct commit was fine.
- This repo has a two-tier knowledge structure: `implementation/knowledge/` is the single source
  of truth; `implementation/scripts/sync.mjs` projects it into per-platform folders. This repo's
  own root-level `.claude/`, `.github/`, `.cursor/`, etc. are themselves installed projections
  (confirmed identical in body to `implementation/knowledge/instructions/git-workflow.md` and to
  `implementation/.claude/rules/git-workflow.md`) — **figure out and use the actual, correct
  command(s) this repo uses to keep both the `implementation/`-internal platform folders and the
  repo-root platform folders in sync** (check `Makefile`, `scripts/install.sh`,
  `implementation/scripts/sync.mjs --check`, and any existing CI job that verifies zero sync drift
  — e.g. `sync-no-diff` in `.gitlab-ci.yml` — for the actual invocation pattern already relied on
  in this repo, rather than guessing at a new one).

## Inputs
- `implementation/knowledge/instructions/git-workflow.md` — file to edit (canonical source)
- `implementation/knowledge/skills/task-management/SKILL.md` § "4. Complete a Task" — likely needs
  a one-line cross-reference, not a rewrite
- `implementation/scripts/sync.mjs`, `scripts/install.sh`, `Makefile`, `.gitlab-ci.yml`'s
  `sync-no-diff` job — for the correct propagation/verification commands
- This session's actual incident: two direct commits to local `develop`
  (`b0ab26b`/`f20c86b` for T340, `83f07d6` for T341's first attempt), both rejected on push with
  `GitLab: You are not allowed to push code to protected branches on this project`, both recovered
  via `git branch <name> <sha>` + `git reset --hard origin/develop` + push + MR (`!112` for the
  second case) — cite this as the concrete example in the new guidance, it's more useful than an
  abstract warning

## Constraints
- Docs/knowledge-base only. No application code, no `.gitlab-ci.yml` changes.
- Must propagate through the **real** sync pipeline this repo uses — do not hand-edit the
  generated platform folders (`implementation/.claude/`, root `.claude/`, `.cursor/`, `.github/`,
  etc.) directly; edit only the canonical source(s) and regenerate.
- After regenerating, verify **zero drift** the same way this repo's own CI does (find and reuse
  the actual check command — likely `node implementation/scripts/sync.mjs --check` and/or
  whatever the `sync-no-diff` CI job runs — don't invent a new verification method).
- **Land this via a branch and MR to `develop`, not a direct commit** — this task exists because of
  the opposite mistake; do not repeat it while fixing it. Branch name:
  `docs/342-protected-branch-commit-rule`.
- Token budget: ≤ 60k (small, contained docs change).

## Expected Outputs
- Updated `implementation/knowledge/instructions/git-workflow.md` with a new, explicit,
  hard-to-miss rule (a new section, e.g. "## Protected Branches — No Direct Commits, Ever" placed
  right after "Branching Strategy" or folded into "Merge Request Rules" — implementer's judgment
  on placement, but it must not be buried as a sub-bullet under an unrelated heading) stating:
  1. `main` and `develop` are protected; GitLab rejects **any** direct push to them regardless of
     how small, trivial, or docs/ledger-only the change is.
  2. This applies to the orchestrator's own edits (task ledger transitions, checkpoints,
     status-header updates) exactly as much as it applies to agent implementation work — there is
     no "it's just a doc update" exception.
  3. A short, concrete recovery procedure for the specific failure mode this session hit: if you
     discover you've committed directly to a local `develop`/`main` that's protected on origin
     (caught before or after an attempted push), do NOT force-push or discard the commit — create
     a new branch pointing at that commit (`git branch <name> <sha>`), reset the local protected
     branch back to match `origin` (`git reset --hard origin/<branch>`, after confirming via `git
     diff` that nothing unique would be lost), then push the new branch and open a normal MR.
- A one-line addition to `implementation/knowledge/skills/task-management/SKILL.md` § "4. Complete
  a Task" cross-referencing the new git-workflow rule at the point where the ledger edit is about
  to be committed (e.g. after step 4, before "Never do step 3 without step 2...").
- All platform projections regenerated and verified zero-drift (both the `implementation/`-internal
  copies and this repo's root-level installed copies).
- Task brief updated with an `## Outcome` section, per this repo's standing pattern.

## Acceptance Criteria
- [ ] New rule present in `implementation/knowledge/instructions/git-workflow.md`, and confirmed
      identical (via `diff`) in every platform projection this repo maintains, both under
      `implementation/` and at repo root
- [ ] `task-management` skill cross-references the rule at the relevant step
- [ ] Sync/drift verification command(s) run and pass (zero diff) — cite the exact command and
      output used, matching what this repo's own CI already checks
- [ ] Full local test suite still green
- [ ] Task ledger validator (`python3 docs/tasks/validate-tasks.py`) passes
- [ ] Landed via `docs/342-protected-branch-commit-rule → develop` MR — opened, CI green, merged —
      not a direct commit to `develop`
- [ ] No application code, CI config, or files outside the stated scope touched

## Blocker Protocol
Report blockers per `AGENTS.md`: type (`technical` | `dependency` | `unclear_requirements` |
`external`) + severity (`critical` | `major` | `minor`). Max 2 retries before escalating to the
orchestrator. If the actual sync/propagation command differs from what's described above once you
inspect `Makefile`/`scripts/install.sh` directly, use what you find there — this brief's guess at
the command is secondary to the repo's actual, working mechanism.

## Outcome (2026-08-08)

### Artifacts produced
- `implementation/knowledge/instructions/git-workflow.md` — canonical source. New section
  "## Protected Branches — No Direct Commits, Ever" inserted right after "Branch Naming" /
  before "Agent Worktree Branch Naming" (not buried as a sub-bullet under an unrelated heading).
  Three numbered points (no docs/ledger exception; applies to orchestrator edits equally; this
  session's concrete precedent citing the T340/T341 rejected-push incidents) plus a
  "### Recovery procedure" subsection with the exact `git branch <sha>` /
  `git diff origin/<branch>` / `git reset --hard origin/<branch>` / `git push -u` sequence.
- `implementation/knowledge/skills/task-management/SKILL.md` — one-line cross-reference added to
  § "4. Complete a Task", after step 4 and before "Never do step 3 without step 2...", per the
  brief's placement instruction.
- All 12 platform projections of `git-workflow.md` and `task-management/SKILL.md` regenerated,
  both under `implementation/` (via `implementation/scripts/sync.mjs`) and at repo root (via
  `scripts/install.sh --target . --platform all --update`): `.claude/`, `.cursor/`, `.gemini/`,
  `.github/`, `.opencode/`, `.pi/` and their `implementation/`-internal counterparts.
- `implementation/registry/index.json` — regenerated via
  `implementation/scripts/generate-registry.py --root implementation` to pick up the new
  checksums for the two edited canonical files (was flagged as drifted by
  `tests/functional/test_validation_gate.py::test_registry_gate_passes_for_repo_artifact` before
  regeneration; see §4 below).

### Real propagation pipeline used (found by inspecting `Makefile` / `scripts/install.sh` /
`.gitlab-ci.yml` directly, per the brief's instruction to not guess)
1. Edit only `implementation/knowledge/instructions/git-workflow.md` and
   `implementation/knowledge/skills/task-management/SKILL.md` (canonical source).
2. `node implementation/scripts/sync.mjs --root implementation` (= `make sync`) — regenerates the
   `implementation/`-internal platform folders (`implementation/.claude/`, `.cursor/`, `.gemini/`,
   `.github/`, `.opencode/`, `.pi/`) from `implementation/knowledge/`.
3. `bash scripts/install.sh --target . --platform all --update` — propagates the regenerated
   `implementation/` platform trees into this repo's own root-level installed copies (`.claude/`,
   `.cursor/`, `.gemini/`, `.github/`, `.opencode/`, `.pi/`), matching the precedent in this
   repo's own history (e.g. commit `6d1fca3`, "chore: sync root .claude/ install with T301
   tool-projection fix"). Reverted two unrelated side-effect changes this step made outside this
   task's scope (`.claude/settings.json`, which isn't part of the sync source and got deleted by
   `--update`'s `rsync --delete`; `.vscode/mcp.json`, which lost a locally-added `cwso` MCP entry
   not present in the canonical `implementation/.vscode/mcp.json`) via
   `git checkout -- .claude/settings.json .vscode/mcp.json` before committing.
4. `python3 implementation/scripts/generate-registry.py --root implementation` — regenerates
   `implementation/registry/index.json`'s per-artifact checksums, which the CI-run
   `check.py --registry` gate (`tests/functional/test_validation_gate.py`) verifies are current.

### Acceptance criteria verification (exact commands + output)

**1. New rule present, confirmed identical across every platform projection:**
Wrote a verification script diffing the body (skipping the platform-specific frontmatter, lines
1–5) of every projection against the canonical source:
```
$ bash <verification script diffing tail -n +6 of each file against canonical>
=== .claude/rules/git-workflow.md ===
IDENTICAL (body)
=== .cursor/rules/git-workflow.mdc ===
IDENTICAL (body)
=== .gemini/instructions/git-workflow.md ===
IDENTICAL (body)
=== .github/instructions/git-workflow.instructions.md ===
IDENTICAL (body)
=== .opencode/instructions/git-workflow.md ===
IDENTICAL (body)
=== .pi/instructions/git-workflow.md ===
IDENTICAL (body)
=== implementation/.claude/rules/git-workflow.md ===
IDENTICAL (body)
=== implementation/.cursor/rules/git-workflow.mdc ===
IDENTICAL (body)
=== implementation/.gemini/instructions/git-workflow.md ===
IDENTICAL (body)
=== implementation/.github/instructions/git-workflow.instructions.md ===
IDENTICAL (body)
=== implementation/.opencode/instructions/git-workflow.md ===
IDENTICAL (body)
=== implementation/.pi/instructions/git-workflow.md ===
IDENTICAL (body)
```
All 12 projections identical to `implementation/knowledge/instructions/git-workflow.md`.

**2. `task-management` skill cross-references the rule:** confirmed by inspection — the added
line in § "4. Complete a Task" reads "Land these edits via a branch and MR, never a direct
commit to `main`/`develop` — even though this is a ledger-only change, see `git-workflow.md` §
'Protected Branches — No Direct Commits, Ever'..." — placed at exactly the ledger-commit point
this task's brief specified.

**3. Sync/drift verification — exact commands this repo's own CI runs, reused directly:**
```
$ node implementation/scripts/sync.mjs --root implementation --check
[claude-code] checked 85 files -> .claude
[cursor] checked 85 files -> .cursor
[gemini] checked 85 files -> .gemini
[github] checked 86 files -> .github
[opencode] checked 85 files -> .opencode
[pi] checked 85 files -> .pi

OK - no drift across 511 files.
$ echo $?
0
```
This is the exact command the `sync-no-diff` CI job in `.gitlab-ci.yml` runs (job also asserts
`git diff --quiet` after running the non-`--check` form; both checked here — see §4, the `git
diff --stat` after the full sequence shows only the 27 intentionally-scoped files touched, zero
unexpected drift left uncommitted).

Also ran the registry gate's own drift check (not explicitly named in the brief's guess at the
command, but discovered via `tests/functional/test_validation_gate.py` failing pre-regeneration —
see §4):
```
$ python3 implementation/scripts/generate-registry.py --root implementation --check
registry is up to date
```

**4. Full local test suite:**
Before registry regeneration, `python3 tests/run.py -v` showed 2 failures: one from
`test_registry_gate_passes_for_repo_artifact` (registry checksums stale after editing the two
canonical files — expected, part of the propagation pipeline this task owns) and one from
`test_every_active_task_has_a_plan` (pre-existing, see below). After running
`generate-registry.py` (step 4 of the propagation sequence above):
```
$ python3 tests/run.py -v
...
Ran 293 tests in 13.834s
FAILED (failures=1, skipped=16)
```
The one remaining failure:
```
FAIL: test_every_active_task_has_a_plan (tests.performance.test_team_health.TestPlanCoverage.test_every_active_task_has_a_plan)
AssertionError: ['T342'] is not false : Active tasks not referenced by any plan in docs/plans/ ...
```
Confirmed **pre-existing and out of this task's scope** — reproduced identically on a clean
checkout of this branch's pre-existing commit (`git stash -u` to remove this task's changes, then
`python3 tests/run.py --suite performance -v`), same failure, same message, before any of this
task's changes existed. This is the exact same pattern as T341's Outcome §4 finding: it flags that
`docs/tasks/task-T342.md` (this task itself) isn't yet referenced by any file under
`docs/plans/` — filing a plan document for T342 is not among this task's Expected Outputs and is
the orchestrator's/Plan-Approve-Execute process's responsibility, consistent with how T341's
identical finding was handled (orchestrator filed `docs/plans/plan-021-...md` during closeout).

**5. Task ledger validator:**
```
$ python3 docs/tasks/validate-tasks.py
TASK LEDGER: PASS (2 active, 181 completed)
```

**6. Landed via branch + MR, not a direct commit:**
```
$ git push origin docs/342-protected-branch-commit-rule
   590ae51..28e7d6f  docs/342-protected-branch-commit-rule -> docs/342-protected-branch-commit-rule

$ glab mr create --source-branch docs/342-protected-branch-commit-rule --target-branch develop ...
https://gitlab.com/em-age/emage.code/-/merge_requests/113

$ glab api projects/:id/merge_requests/113
"state": "opened", "web_url": "https://gitlab.com/em-age/emage.code/-/merge_requests/113",
"source_branch": "docs/342-protected-branch-commit-rule", "target_branch": "develop"
```
MR **not** merged (per `.claude/rules/git-workflow.md`'s "require at least 1 approval") —
awaiting review per this task's delegation, which explicitly reserved merge/closeout for the
orchestrator's independent verification.

**7. No files outside stated scope touched:**
```
$ git diff --stat 590ae51..28e7d6f
 27 files changed, 627 insertions(+), 3 deletions(-)
```
All 27 files are: the 2 canonical knowledge files, their 24 platform projections (12 files ×
2 locations: `implementation/`-internal + repo root), and `implementation/registry/index.json`.
No application code, `.gitlab-ci.yml`, or `docs/tasks/active-tasks.md` /
`docs/tasks/completed-tasks.md` touched. (Two unrelated files —
`.claude/settings.json`, `.vscode/mcp.json` — were transiently modified by
`scripts/install.sh --update`'s `rsync --delete` behavior as a known side effect of that
mechanism, unrelated to this task's content; reverted via `git checkout --` before committing,
per §"Real propagation pipeline used" step 3 above, and confirmed absent from the final commit.)

### Acceptance criteria
- [x] New rule present in `implementation/knowledge/instructions/git-workflow.md`, confirmed
      identical (via diff) in every platform projection, both under `implementation/` and at repo
      root
- [x] `task-management` skill cross-references the rule at the relevant step
- [x] Sync/drift verification commands run and pass (zero diff) — `sync.mjs --check` and
      `generate-registry.py --check`, matching this repo's own CI
- [x] Full local test suite green modulo one pre-existing, out-of-scope failure (see §4) — same
      disposition as T341's Outcome, not a regression introduced by this task
- [x] Task ledger validator (`python3 docs/tasks/validate-tasks.py`) passes
- [x] Landed via `docs/342-protected-branch-commit-rule → develop` MR — opened
      (`https://gitlab.com/em-age/emage.code/-/merge_requests/113`), not a direct commit to
      `develop`. CI status and merge left to the orchestrator per delegation (not self-merged).
- [x] No application code, CI config, or files outside the stated scope touched (see §"No files
      outside stated scope touched" above for the two transient, reverted exceptions)

### Concerns / follow-up for the orchestrator
1. This task's own `active-tasks.md` row (`T342`) is not yet referenced in any `docs/plans/*.md`
   file, same pattern T341 hit — `test_every_active_task_has_a_plan` will keep failing until a
   plan doc references it or the orchestrator confirms this is acceptable for this task's scope
   (per T341 precedent, resolved by filing `docs/plans/plan-021-...md`; a similar plan reference
   for T342 would resolve it here).
2. Per delegation: `active-tasks.md`, `completed-tasks.md`, and this file's `**Status:**` header
   intentionally left as `in_progress` — for the orchestrator to transition after independently
   reviewing MR !113 and this Outcome section's evidence, and after confirming CI is green on the
   MR pipeline.
3. MR CI pipeline status was not polled to completion as part of this task (acceptance criterion
   stops at "MR opened") — the orchestrator should confirm the MR pipeline (including
   `sync-no-diff`) is green before merging, consistent with how MR !111 (T341) was handled.

### Orchestrator closeout (2026-08-08)
- Independently reviewed the actual diff (not just the agent's summary): confirmed the new
  "Protected Branches — No Direct Commits, Ever" section in
  `implementation/knowledge/instructions/git-workflow.md` states the rule unambiguously (no
  docs/ledger exception, applies to orchestrator edits, cites the concrete T340/T341 incident,
  includes a working recovery procedure), and confirmed the one-line `task-management` skill
  cross-reference lands at the correct point (right before the ledger commit step).
- Independently confirmed all 12 platform projections (6 under `implementation/`, 6 at repo root)
  are body-identical to the canonical source via direct `diff`, and confirmed
  `.vscode/mcp.json`/`.claude/settings.json` were NOT touched in the final commit (the agent's
  reported transient `install.sh --update` side-effect was correctly reverted before committing).
- Resolved concern #1: filed `docs/plans/plan-022-protected-branch-commit-rule.md` on the same MR
  branch, which fixed the `unit-tests` job (`test_every_active_task_has_a_plan`).
- Resolved concern #3: polled MR !113's pipeline to completion after the plan-022 fix — green
  (`mergeable`), re-ran the full local suite and ledger validator one more time on the final branch
  state (293 tests OK, `TASK LEDGER: PASS`) before merging.
- MR !113 merged (squash, source branch removed):
  `merge_commit_sha: b5686bf4c29919912f15ca3a71d18967e189c189`, target `develop`, `main` untouched.
- Landed this closeout itself via `docs/342-ledger-closeout → develop` (not a direct commit to
  `develop`) — dogfooding the rule this task just added, same pattern used for T340/T341's
  closeouts after the mistake was first caught.
- Worktree and branch cleaned up: `.claude/worktrees/agent-ae571659fd355bf7b` removed, remote
  `docs/342-protected-branch-commit-rule` deleted (local copy never existed outside the worktree).
