# Task T347 — Release v6.7.0: docs prep, tag, publish

**ID:** T347
**Owner:** release-manager
**Status:** in_progress
**Priority:** P1
**Depends on:** —
**Created:** 2026-08-08
**Based on:** `docs/tasks/task-T337.md` (v6.6.0 precedent — same procedure, twice-proven),
`docs/releases/v6.6.0.md`, `docs/tasks/completed-tasks.md` entries T340–T346

## Objective
Cut release v6.7.0 from `develop`'s tip, packaging everything completed since v6.6.0 (T340–T346:
the merge-API phantom-ancestry investigation and its remediation, the protected-branch commit
rule, and the T316 Pattern A cleanup wave) into a versioned, published GitLab Release. MINOR
version bump (v6.6.0 → v6.7.0), per user's explicit choice — this repo's own convention (minor for
new capabilities, patch for fixes-only) applies here because T341 shipped a genuine new capability
(`scripts/verify-main-sync-merge.py`), not just fixes.

## Context
- Phase: Release
- Follow the exact procedure T337 used for v6.6.0 (twice-proven this session): branch
  `docs/release-v6.7.0` from `develop`, update release markers, write
  `docs/releases/v6.7.0.md` and `docs/checkpoints/checkpoint-release-v6.7.0.md`, run the full
  verification bar, merge to `develop` (squash), tag, watch the tag-triggered pipeline, verify the
  GitLab Release publishes.
- Land the release-docs branch via a normal MR to `develop` — per
  `implementation/knowledge/instructions/git-workflow.md` § "Protected Branches — No Direct
  Commits, Ever" (T342), no exceptions for release-prep docs either.
- Scope note: this task covers the `develop`-side release only (docs, tag, GitLab Release
  publish) — matching T337's scope exactly. The separate `release/vX.Y.Z → main` sync (T331/T339's
  pattern) is explicitly NOT part of this task; if warranted, it will be scheduled as its own
  follow-up task after this one, the same way T339 followed T337/T338.

## Inputs
- `docs/tasks/task-T337.md` — exact prior procedure and evidence format to match
- `docs/releases/v6.6.0.md`, `docs/releases/_template.md` — format reference
- `docs/checkpoints/checkpoint-release-v6.6.0.md` — checkpoint format reference
- `docs/tasks/completed-tasks.md` rows for T340–T346 — full changelog source material (read
  directly, do not paraphrase from memory)
- `CONTRIBUTING.md` § Releasing — the documented release steps, including the (T341-added)
  "Post-merge squash verification" subsection, which does not apply here (that's for
  `release/* → main`, not this `develop`-only step) but should be recognizable to you as prior
  context
- `scripts/verify-release-docs.py` — the required docs-verification gate

## Constraints
- MINOR version: v6.7.0. Do not re-litigate the version-bump choice — it was already decided by
  the user this session.
- Content-accurate changelog only: read `completed-tasks.md`'s actual T340–T346 rows verbatim
  before writing highlights — do not invent or embellish beyond what those rows document. In
  particular, T340 is an investigation with no code artifact and T346 is a verification gate with
  no code artifact — both belong under "Internal", not "Highlights"/features.
- **Breaking changes section is not optional here — do not skip it.** T344's
  `ConcurrentMergeOrchestrator.__init__` signature change (`(self, client)` →
  `(self, worker_client, orchestrator_client)`) is a real breaking API change to a class in
  `implementation/runtime/cwso/concurrent_merge.py`, even though a full-repo `grep` (done during
  T344/T346) found no caller outside this repo's own tests. State this plainly: what changed, why
  (the live server's permission model requires it), and that no external caller is known to be
  affected as of this release.
- Token budget: ≤ 60k.

## Expected Outputs
- `docs/release-v6.7.0` branch, from `develop`
- Release markers bumped to `Latest release: v6.7.0` in `README.md`, `docs/wiki/README.md`,
  `docs/wiki/home.md`
- `docs/releases/v6.7.0.md` (Install + Highlights + Breaking changes + Internal sections, per
  `docs/releases/_template.md`)
- `docs/checkpoints/checkpoint-release-v6.7.0.md`
- MR `docs/release-v6.7.0 → develop`, opened (do not self-merge — the orchestrator reviews and
  merges, per this session's established pattern)
- After the orchestrator merges: tag `v6.7.0` on `develop`'s new tip, pushed to origin
- Task brief updated with an `## Outcome` section citing exact commands/output, matching T337's
  evidentiary style

## Acceptance Criteria
- [ ] `docs/release-v6.7.0` branched from `origin/develop`'s actual current tip (verify, don't
      assume — this session has repeatedly hit stale-worktree-base issues)
- [ ] Release markers bumped in all 3 required files
- [ ] `docs/releases/v6.7.0.md` written, changelog grouped Features / Fixes / Breaking Changes /
      Internal, sourced directly from `completed-tasks.md`'s T340–T346 rows, task IDs cited
- [ ] Breaking changes section explicitly covers T344's constructor signature change (see
      Constraints — do not omit)
- [ ] `docs/checkpoints/checkpoint-release-v6.7.0.md` written
- [ ] `python3 scripts/verify-release-docs.py --tag v6.7.0` PASS
- [ ] Full verification bar green: `python3 tests/run.py` (or `unittest discover`, whichever this
      repo's docs specify — check `docs/tasks/task-T337.md` for the exact command it used) green;
      `node implementation/scripts/sync.mjs --check` 0 drift; `python3
      implementation/scripts/generate-registry.py --check` up to date; `python3
      docs/tasks/validate-tasks.py` PASS
- [ ] MR opened, not self-merged
- [ ] (Post-merge, may require a second pass once the orchestrator merges) Tag `v6.7.0` created and
      pushed; tag-triggered pipeline watched to completion; GitLab Release publish confirmed via
      `glab api` (not assumed from pipeline success alone — check the actual Release object exists)

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalating. If the tag-push
pipeline fails on something unrelated to this task's own docs (e.g. a CI infrastructure issue, as
happened with T338's tag-fetch bug during v6.6.0's own release), report it plainly rather than
guessing at a fix outside this task's scope — the orchestrator will decide whether to fix inline or
file a follow-up task.
