# Task T349 — Fix release/main-sync merge procedure docs in CONTRIBUTING.md

**ID:** T349
**Owner:** devops-engineer
**Status:** in_progress
**Priority:** P1
**Depends on:** —
**Created:** 2026-08-08
**Based on:** `docs/tasks/task-T348.md` § Outcome (the discovery), `docs/plans/plan-026-release-merge-procedure-fix.md`
(design decision — already made, this task is implementation)

## Objective
`CONTRIBUTING.md` § Releasing has two problems T348 (the v6.7.0 `main` sync) found by hitting them
for real: (1) the documented recovery procedure tells the operator to `git push` directly to
`main`, which cannot work because `main` is push-protected (`push_access_levels: ['No one']`,
confirmed via API, same as `develop`); (2) the standard merge step only ever passed
`squash: false` in the `/merge` call's own body, which failed to prevent squashing on every one of
the 3 times it was tried this session (MR !103, !109, !125) — but a different sequence
(`PUT`-updating the MR resource's own `squash` attribute to `false` *before* calling `/merge`)
worked the one time it was tried (MR !126). Fix both.

## Context
- Phase: Implementation (docs-only correction + procedure strengthening)
- Design already decided in `docs/plans/plan-026-release-merge-procedure-fix.md` § 2 — implement
  it, don't re-derive it: adopt the PUT-first sequence as the new standard step now, on the one
  confirmed data point, because it's a strict superset of the current step (adds a call, changes
  nothing else) with a plausible mechanistic explanation, and `scripts/verify-main-sync-merge.py`
  remains unchanged as the safety net regardless.
- Full evidence trail for both findings: `docs/tasks/task-T348.md` § Outcome, Steps 5–7. Read it in
  full before editing — cite the exact MR numbers and API responses it documents, don't
  paraphrase from memory.
- `CONTRIBUTING.md`'s current relevant sections (line numbers as of this task's filing — verify
  they still match before editing, this repo's own content moves):
  - § "Cutting a release" (~line 130) — step 5 area ("Open MR `release/vX.Y.Z → main`") is where
    the PUT-first sequence becomes the new documented standard.
  - § "Post-merge squash verification" (~line 190) — the "Recovery procedure" subsection currently
    documents the broken direct-push sequence; fix it to the branch+MR sequence T348 actually used
    (see `docs/tasks/task-T348.md` § Outcome Step 6 for the exact commands that worked).

## Inputs
- `docs/tasks/task-T348.md` § Outcome — the full evidence trail (API responses, exact commands,
  independent git-plumbing verification) for both findings
- `CONTRIBUTING.md` — file to edit
- `docs/tasks/task-T340.md`, `docs/tasks/task-T341.md` — prior context (why the verification tool
  exists, what was previously unresolved about the root cause)

## Constraints
- Docs-only. Do not touch `scripts/verify-main-sync-merge.py` — it stays exactly as-is, a
  post-merge safety net, not a merge-performing tool (per plan-026 § 3, explicitly out of scope).
- Do not touch GitLab project settings.
- Do not build new scripts/automation for the merge sequence — document it as `glab api` commands
  the orchestrator runs directly, matching how this exact operation has actually been performed
  every time this session.
- State the PUT-first finding's confidence level honestly: 1 confirmed success (MR !126) against 3
  prior failures of the old sequence (MR !103, !109, !125) — don't overclaim certainty, but do
  adopt it as standard per the plan's reasoning (superset change, low downside, plausible
  mechanism).
- Token budget: ≤ 40k (small, contained docs fix).
- Land via a branch + MR to `develop` (branch: `docs/349-fix-release-merge-procedure`) — no direct
  commit to `develop`.

## Expected Outputs
- `CONTRIBUTING.md` § "Cutting a release": the MR-merge step updated to document the PUT-first
  sequence as the standard procedure for `release/vX.Y.Z → main` merges specifically (not a
  blanket change to how all MRs are merged in this repo — `feature/*`/`bugfix/* → develop` merges
  keep their existing squash-and-merge convention unchanged). Exact sequence to document:
  1. `glab api -X PUT projects/:id/merge_requests/:iid -f squash=false` (confirm response shows
     `squash: false`)
  2. `glab api -X PUT projects/:id/merge_requests/:iid/merge -f should_remove_source_branch=true`
     (no `squash` param needed in this call — the MR resource itself now carries the correct
     value)
  3. `python3 scripts/verify-main-sync-merge.py <mr_iid>` (unchanged — still run immediately after,
     as the safety net; document that a FAIL here still means the recovery procedure below is
     needed)
- `CONTRIBUTING.md` § "Post-merge squash verification" → "Recovery procedure" subsection: replaced
  with the actual working branch+MR sequence (mirror `docs/tasks/task-T348.md` § Outcome Step 6's
  exact commands — branch from `origin/main`, `git merge --no-ff <true-source-tip> -s ours`,
  verify empty diff and correct ancestry before pushing, push, open MR, merge using the same
  PUT-first sequence from the point above).
- Task brief updated with an `## Outcome` section citing exact commands/output.

## Acceptance Criteria
- [ ] "Cutting a release" documents the PUT-first sequence as the standard `release/*→main` merge
      step, with the confidence caveat (1 confirmed success vs 3 prior failures) stated honestly
- [ ] "Recovery procedure" no longer tells the operator to `git push` directly to `main` — replaced
      with the actual branch+MR sequence that worked in T348
- [ ] `scripts/verify-main-sync-merge.py` unchanged (git diff confirms zero changes to this file)
- [ ] Both edits cite/cross-reference `docs/tasks/task-T348.md` for the evidence, matching this
      repo's existing citation style (see the current "Drift detection" § for the pattern)
- [ ] Full local test suite green
- [ ] Landed via `docs/349-fix-release-merge-procedure → develop` MR — opened, not self-merged

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalating. If
`CONTRIBUTING.md`'s section line numbers have moved since this brief was written, that's not a
blocker — just locate the sections by heading text instead.
