# Task T358 — Release v6.8.0: docs prep, tag, publish

**ID:** T358
**Owner:** release-manager
**Status:** done
**Priority:** P1
**Depends on:** —
**Created:** 2026-08-09
**Based on:** `docs/tasks/task-T337.md`, `docs/tasks/task-T347.md`, `docs/tasks/task-T350.md`
(precedent — same procedure, now three times proven), `docs/releases/v6.7.1.md`,
`docs/tasks/completed-tasks.md` entries T352-T357

## Objective
Cut release v6.8.0 from `develop`'s tip, packaging T352-T357 (the Cline platform integration: new
`implementation/platforms/cline.json` manifest, `sync.mjs` engine support, generated
`implementation/.cline/`+`implementation/.clinerules/` output, installer support, and documentation)
into a versioned, published GitLab Release. MINOR version bump (v6.7.1 → v6.8.0), per user's explicit
choice — a new capability shipped (Cline platform support), matching this repo's own convention
(minor for new capabilities, patch for fixes/infra-only).

## Context
- Phase: Release
- Follow the exact procedure T337/T347/T350 used (three-times-proven, now applying it a fourth
  time): branch `docs/release-v6.8.0` from `develop`, update release markers, write
  `docs/releases/v6.8.0.md` and `docs/checkpoints/checkpoint-release-v6.8.0.md`, run the full
  verification bar, merge to `develop` (squash), tag, watch the tag-triggered pipeline, verify the
  GitLab Release publishes.
- Land the release-docs branch via a normal MR to `develop` — per
  `.claude/rules/git-workflow.md` § "Protected Branches — No Direct Commits, Ever" (T342), no
  exceptions.
- Scope note: this task covers the `develop`-side release only (docs, tag, GitLab Release publish) —
  matching T337/T347/T350's scope exactly. The `release/v6.8.0 → main` sync is a separate follow-up
  task (T359), using the PUT-first merge procedure from `CONTRIBUTING.md` (now 2/2 successful:
  MR !126, MR !134).

## Inputs
- `docs/tasks/task-T350.md` — most recent prior procedure and evidence format to match
- `docs/releases/v6.7.1.md`, `docs/releases/_template.md` — format reference
- `docs/checkpoints/checkpoint-release-v6.7.1.md` — checkpoint format reference
- `docs/tasks/completed-tasks.md` rows for T352-T357 — full changelog source material (read
  directly, do not paraphrase from memory)
- `scripts/verify-release-docs.py` — the required docs-verification gate

## Constraints
- MINOR version: v6.8.0. Do not re-litigate the version-bump choice — already decided by the user
  this session.
- Content-accurate changelog only: read `completed-tasks.md`'s actual T352-T357 rows verbatim before
  writing highlights. This release's Highlights section should describe genuine new capability —
  Cline platform support (rules via `.clinerules/`, skills via `.cline/skills/`, MCP staging file
  via `.cline/mcp.json`) — matching this session's Feature-release precedent (contrast with v6.7.1,
  which had no Highlights since it shipped no new capability). Also note, accurately, the explicit
  scope limitation: Cline subagent/slash-command projection is not included (no confirmed on-disk
  format exists for either).
- No breaking changes in this release — do not invent one; state "None" if that's accurate (verify:
  T352-T357 only added new files/capabilities and additive engine changes gated behind manifest
  opt-in flags — `rootRelative`, optional `fileMap.agents`/`.commands` — that don't alter any
  existing platform's output, confirmed by T353/T357's own verification).
- Token budget: ≤ 60k.

## Expected Outputs
- `docs/release-v6.8.0` branch, from `develop`
- Release markers bumped to `Latest release: v6.8.0` in `README.md`, `docs/wiki/README.md`,
  `docs/wiki/home.md`
- `docs/releases/v6.8.0.md` (Install + Highlights + Breaking changes + Internal sections, per
  `docs/releases/_template.md`)
- `docs/checkpoints/checkpoint-release-v6.8.0.md`
- MR `docs/release-v6.8.0 → develop`, opened (do not self-merge — the orchestrator reviews and
  merges)
- After the orchestrator merges: tag `v6.8.0` on `develop`'s new tip, pushed to origin
- Task brief updated with an `## Outcome` section citing exact commands/output

## Acceptance Criteria
- [ ] `docs/release-v6.8.0` branched from `origin/develop`'s actual current tip (verify, don't
      assume)
- [ ] Release markers bumped in all 3 required files
- [ ] `docs/releases/v6.8.0.md` written, changelog grouped Features / Fixes / Breaking Changes /
      Internal, sourced directly from `completed-tasks.md`'s T352-T357 rows, task IDs cited; Cline
      platform support classified under Highlights/Features (genuine new capability, unlike
      v6.7.1's Internal-only precedent); the agents/commands scope limitation stated plainly
- [ ] `docs/checkpoints/checkpoint-release-v6.8.0.md` written
- [ ] `python3 scripts/verify-release-docs.py --tag v6.8.0` PASS
- [ ] Full verification bar green: `python3 tests/run.py`; `node implementation/scripts/sync.mjs
      --root implementation --check`; `python3 implementation/scripts/generate-registry.py --root
      implementation --check`; `python3 docs/tasks/validate-tasks.py`
- [ ] MR opened, not self-merged
- [ ] (Post-merge, orchestrator's pass) Tag `v6.8.0` created and pushed; tag-triggered pipeline
      watched to completion; GitLab Release publish confirmed via `glab api`

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalating.

## Outcome (2026-08-09, docs-prep portion — status remains `pending`, this pass done by release-manager)

**Stale worktree base caught before doing any work.** This worktree's checked-out branch
(`worktree-agent-aeddbe8677f519ae0`) was at `9c4f82a`, on `main`'s v6.7.1 ancestry line, which
predates `docs/tasks/task-T358.md` existing at all. Ran `git fetch origin`, confirmed
`origin/develop` tip was `4669639` (includes `b013ba3 docs(tasks): file T358/T359 for v6.8.0
release + main sync`), then `git checkout -b docs/release-v6.8.0 origin/develop` — branching
directly from the fetched remote tip rather than the stale local branch. Confirmed via
`git merge-base --is-ancestor HEAD origin/develop` returning `no` on the original stale HEAD before
switching.

**Docs authored:**
- Bumped `Latest release: v6.7.1` → `v6.8.0` marker in `README.md`, `docs/wiki/README.md`,
  `docs/wiki/home.md`.
- Read `docs/tasks/completed-tasks.md` rows for T352–T357 directly (`grep -n "^| T35[2-7]"
  docs/tasks/completed-tasks.md`) before writing changelog content — not from memory.
- Wrote `docs/releases/v6.8.0.md`: Cline platform support (T352–T357, plan-028-v2) classified
  under Highlights/Features — a genuine new capability, unlike v6.7.1's Internal-only precedent —
  covering the `cline.json` manifest, `.clinerules/`/`.cline/skills/`/`.cline/mcp.json` output,
  installer support, and documentation. The agents/commands scope limitation (no confirmed on-disk
  Cline subagent/slash-command format) stated plainly, matching `docs/wiki/cline-setup.md`'s own
  wording. Breaking changes: "None" — verified by confirming T352–T357 only added new
  files/capabilities and additive, opt-in-gated `sync.mjs` engine changes (`rootRelative`, optional
  `fileMap.agents`/`.commands`) that leave every other platform's output unchanged, per T353's and
  T357's own `sync.mjs --check` (0 drift) verification.
- Wrote `docs/checkpoints/checkpoint-release-v6.8.0.md`, format-matched to
  `checkpoint-release-v6.7.1.md`.

**Verification bar — all green, exact output:**
- `python3 scripts/verify-release-docs.py --tag v6.8.0`:
  ```
  release-docs-verify: all documentation checks passed
  release-docs-verify: verified marker 'Latest release: v6.8.0'
  ```
- `python3 tests/run.py`: `Ran 293 tests in 13.508s` → `OK (skipped=17)`
- `node implementation/scripts/sync.mjs --root implementation --check`:
  `OK - no drift across 550 files.` (7 platforms checked, incl. `cline`: 39 files)
- `python3 implementation/scripts/generate-registry.py --root implementation --check`:
  `registry is up to date`
- `python3 docs/tasks/validate-tasks.py`: `TASK LEDGER: PASS (2 active, 198 completed)`

**Git/MR:**
- Committed `df759ec` on `docs/release-v6.8.0` (5 files changed: `README.md`,
  `docs/wiki/README.md`, `docs/wiki/home.md`, `docs/releases/v6.8.0.md`,
  `docs/checkpoints/checkpoint-release-v6.8.0.md`).
- Pushed `docs/release-v6.8.0` to origin.
- Opened MR !150 (`docs/release-v6.8.0 → develop`) via `glab mr create`:
  <https://gitlab.com/em-age/emage.code/-/merge_requests/150>. Not self-merged, per the brief —
  left for the orchestrator to review, merge, tag, and verify the publish.

**Not done (explicitly out of scope for this pass, per the brief):** merge, tag `v6.8.0`, watch
tag-triggered pipeline, verify GitLab Release publish, and any ledger transition of T358 itself in
`active-tasks.md`/`completed-tasks.md`. This task's Status header is left as `pending` — the
orchestrator owns the ledger transition to `in_progress`/`done`.

### Orchestrator closeout (2026-08-09)
- Independently re-verified before merging: reviewed `docs/releases/v6.8.0.md` and the checkpoint
  in full (Cline platform support correctly classified under Highlights, scope limitation stated
  plainly, Breaking changes "None" claim verified accurate); independently re-ran the full
  verification bar on the MR branch myself (`verify-release-docs.py`, `tests/run.py`, `sync.mjs
  --check`, `generate-registry.py --check`, `validate-tasks.py` — all 5 green, matching the
  delegate's report).
- MR !150 merged (squash, source branch removed): `merge_commit_sha: a2fb072...`, target `develop`.
- Local `develop` synced to `a2fb072`. Tagged directly by the orchestrator:
  `git tag -a v6.8.0 -m "Release v6.8.0" a2fb072`, pushed to origin.
- Tag-triggered pipeline (`2745022108`) watched to completion: **success**, all 3 release-stage jobs
  green (`release`, `main-develop-drift-gate`, `release-docs-gate`).
- GitLab Release independently verified via `glab api projects/.../releases/v6.8.0`:
  `tag_name: v6.8.0`, `released_at: 2026-08-09T08:32:33.879Z`.

Release URL: <https://gitlab.com/em-age/emage.code/-/releases/v6.8.0>
