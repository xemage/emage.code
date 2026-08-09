# Task T358 — Release v6.8.0: docs prep, tag, publish

**ID:** T358
**Owner:** release-manager
**Status:** pending
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
