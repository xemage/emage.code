# Task T350 — Release v6.7.1: docs prep, tag, publish

**ID:** T350
**Owner:** release-manager
**Status:** done
**Completed:** 2026-08-08
**Priority:** P1
**Depends on:** —
**Created:** 2026-08-08
**Based on:** `docs/tasks/task-T337.md`, `docs/tasks/task-T347.md` (precedent — same procedure,
now three times proven), `docs/releases/v6.7.0.md`, `docs/tasks/completed-tasks.md` entries T348–T349

## Objective
Cut release v6.7.1 from `develop`'s tip, packaging everything completed since v6.7.0 (T348: the
`main` sync for v6.7.0; T349: the `CONTRIBUTING.md` release-procedure fix) into a versioned,
published GitLab Release. PATCH version bump (v6.7.0 → v6.7.1), per user's explicit choice — no
new capability shipped, matching this repo's own convention (patch for fixes/infra-only, minor for
new capabilities).

## Context
- Phase: Release
- Follow the exact procedure T337/T347 used (twice-proven, now applying it a third time):
  branch `docs/release-v6.7.1` from `develop`, update release markers, write
  `docs/releases/v6.7.1.md` and `docs/checkpoints/checkpoint-release-v6.7.1.md`, run the full
  verification bar, merge to `develop` (squash), tag, watch the tag-triggered pipeline, verify the
  GitLab Release publishes.
- Land the release-docs branch via a normal MR to `develop` — per
  `implementation/knowledge/instructions/git-workflow.md` § "Protected Branches — No Direct
  Commits, Ever" (T342), no exceptions.
- Scope note: this task covers the `develop`-side release only (docs, tag, GitLab Release
  publish) — matching T337/T347's scope exactly. The `release/v6.7.1 → main` sync is a separate
  follow-up task (T351), using the newly-documented PUT-first merge procedure from T349 for the
  first time on a real sync — the actual test of whether that fix generalizes.

## Inputs
- `docs/tasks/task-T347.md` — most recent prior procedure and evidence format to match
- `docs/releases/v6.7.0.md`, `docs/releases/_template.md` — format reference
- `docs/checkpoints/checkpoint-release-v6.7.0.md` — checkpoint format reference
- `docs/tasks/completed-tasks.md` rows for T348 and T349 — full changelog source material (read
  directly, do not paraphrase from memory)
- `scripts/verify-release-docs.py` — the required docs-verification gate

## Constraints
- PATCH version: v6.7.1. Do not re-litigate the version-bump choice — already decided by the user
  this session.
- Content-accurate changelog only: read `completed-tasks.md`'s actual T348 and T349 rows verbatim
  before writing highlights. Both belong under "Internal" (T348 is a `main`-sync operation with no
  develop-side code artifact; T349 is a process-doc fix, not a shippable code capability) — not
  "Highlights"/Features, matching this repo's own T340/T342/T346 precedent for classifying
  process/investigation work.
- No breaking changes in this release — do not invent one; state "None" if that's accurate (verify
  by checking T348/T349 touched no application code — they didn't).
- Token budget: ≤ 60k.

## Expected Outputs
- `docs/release-v6.7.1` branch, from `develop`
- Release markers bumped to `Latest release: v6.7.1` in `README.md`, `docs/wiki/README.md`,
  `docs/wiki/home.md`
- `docs/releases/v6.7.1.md` (Install + Highlights + Breaking changes + Internal sections, per
  `docs/releases/_template.md`)
- `docs/checkpoints/checkpoint-release-v6.7.1.md`
- MR `docs/release-v6.7.1 → develop`, opened (do not self-merge — the orchestrator reviews and
  merges)
- After the orchestrator merges: tag `v6.7.1` on `develop`'s new tip, pushed to origin
- Task brief updated with an `## Outcome` section citing exact commands/output

## Acceptance Criteria
- [ ] `docs/release-v6.7.1` branched from `origin/develop`'s actual current tip (verify, don't
      assume)
- [ ] Release markers bumped in all 3 required files
- [ ] `docs/releases/v6.7.1.md` written, changelog grouped Features / Fixes / Breaking Changes /
      Internal, sourced directly from `completed-tasks.md`'s T348/T349 rows, task IDs cited; both
      T348 and T349 classified under Internal per Constraints
- [ ] `docs/checkpoints/checkpoint-release-v6.7.1.md` written
- [ ] `python3 scripts/verify-release-docs.py --tag v6.7.1` PASS
- [ ] Full verification bar green: `python3 tests/run.py`; `node implementation/scripts/sync.mjs
      --check`; `python3 implementation/scripts/generate-registry.py --check`; `python3
      docs/tasks/validate-tasks.py`
- [ ] MR opened, not self-merged
- [ ] (Post-merge, orchestrator's pass) Tag `v6.7.1` created and pushed; tag-triggered pipeline
      watched to completion; GitLab Release publish confirmed via `glab api`

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalating.

## Outcome (2026-08-08, docs-prep portion — status remains `in_progress`)

**Stale worktree base caught before doing any work.** This worktree's checked-out branch
(`worktree-agent-ad36fdb93a1e85e24`) was at `2a07558`, on `main`'s v6.7.0 ancestry line, which
predates `docs/tasks/task-T350.md` existing at all. Ran `git fetch origin --prune`, confirmed
`origin/develop` tip was `32cd2f3` (includes `d4afe11 docs(tasks): plan-027 - file T350/T351 for
v6.7.1 release + main sync`), then `git checkout -b docs/release-v6.7.1 origin/develop` —
branching directly from the fetched remote tip rather than the stale local branch.

**Docs authored:**
- Bumped `Latest release: v6.7.0` → `v6.7.1` in `README.md`, `docs/wiki/README.md`,
  `docs/wiki/home.md`.
- Read `docs/tasks/completed-tasks.md` rows for T348 and T349 directly (`grep -n "^| T34[89]"
  docs/tasks/completed-tasks.md`) before writing changelog content — not from memory.
- Wrote `docs/releases/v6.7.1.md`: no new capability, so "Highlights" states that plainly and
  defers to "Internal"; both T348 (main-sync operation, no develop-side code artifact) and T349
  (CONTRIBUTING.md process-doc fix, no shippable code capability) placed under "Internal" per the
  brief's constraint. Breaking changes: "None" — verified by confirming neither task touched
  application code (T348's own record: "verified byte-identical" merge of develop's already-vetted
  content into main; T349's own record: `git diff -- scripts/verify-main-sync-merge.py` was empty,
  only `CONTRIBUTING.md` changed).
- Wrote `docs/checkpoints/checkpoint-release-v6.7.1.md`, format-matched to
  `checkpoint-release-v6.7.0.md`.

**Verification bar — all green, exact output:**
- `python3 scripts/verify-release-docs.py --tag v6.7.1`:
  ```
  release-docs-verify: all documentation checks passed
  release-docs-verify: verified marker 'Latest release: v6.7.1'
  ```
- `python3 tests/run.py`: `Ran 293 tests in 11.027s` → `OK (skipped=17)`
- `node implementation/scripts/sync.mjs --check`: `OK - no drift across 511 files.`
- `python3 implementation/scripts/generate-registry.py --check`: `registry is up to date`
- `python3 docs/tasks/validate-tasks.py`: `TASK LEDGER: PASS (2 active, 190 completed)`

**Git/MR:**
- Committed `1bc9c5471c54b28a01abef00f6a5846bb4703386` on `docs/release-v6.7.1` (5 files changed:
  `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md`, `docs/releases/v6.7.1.md`,
  `docs/checkpoints/checkpoint-release-v6.7.1.md`).
- Pushed `docs/release-v6.7.1` to origin.
- Opened MR !132 (`docs/release-v6.7.1 → develop`) via `glab mr create`:
  <https://gitlab.com/em-age/emage.code/-/merge_requests/132>. Not self-merged, per the brief —
  left for the orchestrator to review, merge, tag, and verify the publish.

**Not done (explicitly out of scope for this pass, per the brief):** merge, tag `v6.7.1`, watch
tag-triggered pipeline, verify GitLab Release publish, and any ledger transition of T350 itself in
`active-tasks.md`/`completed-tasks.md`. This task's Status header is left as `in_progress`.

### Orchestrator closeout (2026-08-08)
- Independently re-verified before merging: reviewed `docs/releases/v6.7.1.md` and the checkpoint
  in full (both T348/T349 correctly classified under Internal, breaking-changes "None" claim
  verified accurate); independently re-ran the full verification bar on the MR branch myself (all
  5 checks green, matching the delegate's report).
- MR !132 merged (squash, source branch removed):
  `merge_commit_sha: 2cbd7d59cb1453697d6503e8ce54f303f0fe3617`, target `develop`.
- Local `develop` synced to `2cbd7d5`. Tagged directly by the orchestrator:
  `git tag -a v6.7.1 -m "Release v6.7.1" 2cbd7d5`, pushed to origin.
- Tag-triggered pipeline (`2743104371`) watched to completion: **success**, all 3 release-stage
  jobs green. `main-develop-drift-gate`: `drift-check: main=v6.7.0 develop=v6.7.1
  releases_behind=1` → `PASS`.
- GitLab Release independently verified via `glab api projects/.../releases/v6.7.1`:
  `tag_name: v6.7.1`, `released_at: 2026-08-08T10:45:53.943Z`.

Release URL: <https://gitlab.com/em-age/emage.code/-/releases/v6.7.1>
