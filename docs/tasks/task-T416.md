# Task T416 — Freeze the golden-suite evaluator interface (protected paths)

**ID:** T416
**Owner:** tech-lead
**Status:** pending
**Priority:** P0
**Depends on:** T410 (done), T411 (done), T412 (done), T413 (done), T414 (done), T415 (done) — all
six now merged to `develop` via MR !201 (squash-merged `feature/T410-phase1-golden-suite-v6.12.0`
at commit `3fef6ee`; `develop` HEAD `8746eb9` as of this brief)
**Created:** 2026-08-14
**Completed:** —
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1, Layer 1 table, T416 row:
*"Freeze the evaluator interface. `tests/golden/` and `scripts/scorecard.py` become protected
paths — declared out of write scope for every agent definition."* Also §2's risk table: *"Held-out
set leaks into improvement work | Medium | Critical | T412 path guard + T463 evaluator-hash check
+ T416 write-scope exclusion. Three independent controls."* — T416 is explicitly the third of
three independent controls, not a formality; T463 (evaluator-hash check) is a later, separate
task, out of scope here.
**Also read before starting:** `docs/checkpoints/checkpoint-018-phase1-layer1-golden-suite-complete.md`
("Open questions" #2 — this brief resolves that question; do not re-derive the mechanism from
scratch, use the design below and adjust only if you find a concrete reason to deviate, documented).

## Why this matters beyond this task ("the point of no return")

Once this task closes, `tests/golden/**` and `scripts/scorecard.py` are meant to stop changing
casually. Every subsequent improvement-task agent that touches command-surface behavior
(`/new-feature`, `/code-review`, `/plan`, `/security-audit`, `/prepare-release`) must be evaluated
*against* these files, not be able to edit them to make its own work look better — that is the
entire point of having a held-out evaluation set. Getting this wrong in either direction is costly:
too loose, and the isolation work from T412-T415 (three independent held-out-leak fixes already
found and fixed this phase) was pointless; too rigid, and a genuine future bug fix in `expect.py`
or a genuine new golden case has no path forward. Design for the former risk, but leave an explicit,
documented exception path for the latter (see "Exception path" below) — don't paint the repo into
a corner.

## What "freeze" means in this repo, concretely (investigated, not left to guesswork)

There is **no existing repo mechanism** for declaring per-agent, per-path write-scope exclusions.
Confirmed by direct investigation before writing this brief:
- `implementation/scripts/sync.mjs` (598 lines) generates every platform's agent projection
  (`.claude/agents/*.md`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.github/`, `.cline/`) from
  the 27 source files in `implementation/knowledge/agents/*.md`. It handles frontmatter/MCP-tag
  projection only — **no shared-include or common-body mechanism** exists for injecting the same
  paragraph into all 27 agent bodies. A protected-paths declaration must be added to each of the 27
  source files' body text individually (never hand-edit the generated platform folders — sync.mjs
  regenerates them from source).
- The closest existing precedent for a "declared, guard-enforced constraint across many files" is
  the repo-wide static-guard pattern used three times already this phase:
  `tests/functional/test_link_integrity.py`, `test_check_version_consistency.py`,
  `test_golden_held_out_isolation.py`. T416 should follow this same pattern, not invent a new one.
- Actual git-level write enforcement (blocking a real edit to `tests/golden/expect.py` at commit
  time) is **out of scope for this task** — there is no mechanism in this environment to
  distinguish "which agent role authored this diff" at the git level, and building one is a much
  larger undertaking than this task's "small" scope. T416 is a **declarative + auditable** control
  (agent instructions say don't touch it, a static guard proves the instruction is present and
  consistent everywhere, same trust model as this repo's other conventions — e.g. `git-workflow.md`'s
  branch-protection rules, which are also enforced by written policy + review discipline, not a
  bot). Do not attempt to build commit-time enforcement; if you find a cheap way to do it, flag it
  as a `type: unclear_requirements, severity: minor` observation and proceed with the declarative
  design regardless.

## Objective

1. **Author a canonical protected-paths declaration**, e.g. `docs/artifacts/protected-paths-v1.md`
   (your call on exact filename/location, following this repo's `<type>-v<N>.md` artifact
   convention). Must state, precisely:
   - Protected paths: `tests/golden/**`, `scripts/scorecard.py`.
   - What "protected" means: no agent definition may edit these paths as part of normal
     improvement-task work, full stop.
   - **Explicit standing exception, not a loophole:** the orchestrator retains read access for
     audit/verification purposes (already exercised repeatedly this phase — T412's adversarial
     probes, T413/T414/T415's grep verification, this session's own narrative-leak audit — freezing
     write-scope must not imply freezing read/audit access, which is a different and still-needed
     capability).
   - **Documented exception path for genuine future maintenance** (e.g. a real bug found in an
     `expect.py`, or a legitimately new golden case): must go through an explicit, user- or
     orchestrator-authorized task (a normal `T<NNN>` task brief naming this exception by task ID),
     never a silent edit by an agent executing unrelated improvement work. Name this requirement
     explicitly in the doc so a future orchestrator has a concrete process to point to rather than
     having to invent one under time pressure.
   - Cite the risk-table line this closes (see "Based on" above) and name T412's guard and the
     (not-yet-built) T463 evaluator-hash check as the other two legs of the three-control design,
     so a future reader understands this is one leg of three, not the whole story.
2. **Add a short, consistent pointer to that doc in all 27 agent source files**
   (`implementation/knowledge/agents/*.md`) — not full prose duplicated 27 times, one line/short
   paragraph per file (e.g. under a "Constraints" heading, adding one if a file has none) stating
   the two protected paths are out of write scope and pointing to the canonical doc for the full
   policy. Then run `implementation/scripts/sync.mjs` to regenerate every platform projection from
   the updated sources — **do not hand-edit any `.claude/agents/`, `.cursor/agents/`, etc. file
   directly.** Verify the sync is clean (re-run and confirm no diff on a second run, mirroring
   this repo's own `sync-no-diff` CI job).
3. **Build a new repo-wide static guard**, `tests/functional/test_protected_paths_declared.py`
   (or your chosen name, following the `test_<subject>.py` convention), mirroring the established
   pattern (`test_link_integrity.py`/`test_check_version_consistency.py`/
   `test_golden_held_out_isolation.py` — read at least one before writing this) with real-tree +
   synthetic-fixture coverage:
   - Confirms every one of the 27 `implementation/knowledge/agents/*.md` files contains the
     protected-paths pointer (fails loudly, listing which files are missing it, if any agent is
     added later without it — this is the guard's actual future value, not just a one-time check).
   - Confirms `tests/golden/` and `scripts/scorecard.py` actually exist on disk (a sanity check
     that the thing being declared "frozen" is real, not a stale/aspirational reference).
   - Does **not** attempt commit-time or diff-time enforcement (see "out of scope" above).

## Held-out isolation — still applies, read-only this time

You will be reading `tests/golden/held-out/**` content as part of confirming these paths exist and
verifying the guard's real-tree test. Per T412's isolation discipline: read-only, and if you write
any example/fixture content into your new guard test, do not reference real held-out case IDs or
fixture content — use synthetic fixtures (mirror `test_golden_held_out_isolation.py`'s own
`TestFindViolationsSyntheticFixtures` pattern, which never touches real held-out data).

## Inputs

- `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1 (T416 row + risk table)
- `docs/checkpoints/checkpoint-018-phase1-layer1-golden-suite-complete.md`
- `implementation/scripts/sync.mjs`, `implementation/knowledge/agents/*.md` (27 files)
- `tests/functional/test_link_integrity.py`, `test_check_version_consistency.py`,
  `test_golden_held_out_isolation.py` (pattern precedent — read at least one fully)
- `.claude/rules/git-workflow.md`'s "Protected Branches" section (closest existing precedent in
  this repo for a declarative-plus-review-discipline protection scheme, not code-enforced)

## Expected outputs

- `docs/artifacts/protected-paths-v1.md` (or equivalent — your call on filename)
- Updated `implementation/knowledge/agents/*.md` (all 27) with the protected-paths pointer
- Regenerated platform projections via `implementation/scripts/sync.mjs` (do not hand-edit)
- `tests/functional/test_protected_paths_declared.py` (new static guard)

## Acceptance criteria

1. Canonical protected-paths doc exists, states both protected paths, the orchestrator read
   exception, and the documented future-exception process (task-brief-authorized only).
2. All 27 agent source files under `implementation/knowledge/agents/` contain the pointer —
   verified by direct `grep -L` (list any missing, expect zero).
3. `implementation/scripts/sync.mjs` re-run produces no further diff (projections match source).
4. New guard test passes against the real tree; deliberately break it once (remove the pointer
   from one agent file in a temp/throwaway change) to prove it actually catches the omission, then
   restore — mirrors T412's own "prove it live with a probe" precedent, don't just assert the
   guard works.
5. `python3 tests/run.py` exits 0 (full suite, no regression).
6. `git status` clean; `tests/golden/**` and `scripts/scorecard.py` themselves are untouched by
   this task (you are declaring them protected, not modifying their content).

## Blocker protocol

- If you find a cheaper/better mechanism than the declarative-doc-plus-guard design above ->
  `type: unclear_requirements`, `severity: minor` — document the alternative and your reasoning,
  but do not silently deviate from the brief's design without flagging it first.
- If `sync.mjs` behaves unexpectedly when 27 files change at once (e.g. a bug only surfaces at
  scale) -> `type: technical`, `severity: major` — this blocks acceptance criterion 3, escalate
  rather than working around it.

## Git workflow

1. Create worktree: `git worktree add ../worktrees/t416-freeze -b feature/T416-protected-paths-v6.12.0 develop`
   (fresh branch from current `develop`, which now includes the full golden suite per MR !201 —
   do not reuse the old `feature/T410-...` branch, it was already squash-merged and deleted).
2. Do the work, verify the full acceptance bar above.
3. Commit with a Conventional Commit message (`feat(agents): freeze golden-suite evaluator paths
   ... Refs T416`).
4. Do not push, do not open an MR. Report worktree path, branch name, commit SHA, and explicit
   confirmation of each of the 6 acceptance criteria back to the orchestrator.

## Constraints

- Token budget: ~30k tokens ("small" scope per the plan, though touching 27 files — most of the
  per-file edits should be short and mechanical once the pointer text is settled).
- File ownership: `docs/artifacts/protected-paths-v1.md`, `implementation/knowledge/agents/*.md`
  (27 files, body text only — do not touch frontmatter `tools:`/`name:`/`description:` fields,
  out of scope), `tests/functional/test_protected_paths_declared.py`, and whatever
  `implementation/scripts/sync.mjs` regenerates under the platform projection folders (`.claude/`,
  `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.github/`, `.cline/` agent directories — regenerated
  output only, never hand-edited). Do not touch `tests/golden/**`, `scripts/scorecard.py`,
  `docs/benchmarks/**` (these are the paths being frozen, not files this task modifies).
