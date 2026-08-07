# Task T335 — Document the drift gate in `CONTRIBUTING.md`

**ID:** T335
**Owner:** technical-writer
**Status:** pending
**Priority:** P1
**Depends on:** T332
**Created:** 2026-08-07
**Completed:** —
**Based on:** `docs/plans/plan-019-main-develop-drift-detection.md` §3, `CONTRIBUTING.md` § Releasing (current)

## Objective

Add a new subsection to `CONTRIBUTING.md` § Releasing documenting the drift-detection mechanism
(T332/T334): what it checks, the 1-release grace window, and the exact remediation steps when it
FAILs. This is documentation only — it does not change the documented release flow itself
(tag placement, `release/vX.Y.Z → main` steps 1-7 stay as currently written). This directly
addresses the fact that `main`/`develop` sync being "documented but not enforced" was T331's root
cause — the new subsection makes clear that step 5/6 is now machine-checked, not just documented
convention.

## Inputs

- `CONTRIBUTING.md` § Releasing (current file — read the full section before editing)
- `scripts/check-main-develop-drift.py` (T332 — for exact behavior description)
- `docs/plans/plan-019-main-develop-drift-detection.md` §3 (rationale to summarize, not
  copy-paste verbatim)

## Expected outputs

- `CONTRIBUTING.md`, modified in place (one new subsection added)

## Exact edit

In `CONTRIBUTING.md`, immediately after the existing subsection that ends with the
`glab release create ...` code block and the paragraph "Do not use ad-hoc inline `--notes`, as
that can drift from `docs/releases/vX.Y.Z.md`." — and immediately **before** the `### Hotfixes`
subsection — insert a new subsection:

```markdown
### Drift detection

`main` and `develop` are checked for content drift on every release and on every push to
`develop`, using `scripts/check-main-develop-drift.py`. The check compares the
`Latest release: vX.Y.Z` marker in `README.md` on each branch and counts how many tagged
releases separate them.

- **Grace window:** `main` may lag `develop` by up to 1 release — the normal transient state
  between a release being tagged and its `release/vX.Y.Z → main` sync MR landing.
- **Blocking gate (`main-develop-drift-gate`, `release` stage):** runs on every tag push. If
  `main` is already more than 1 release behind at the moment a new release is tagged, this job
  fails and blocks the `release` job (CHANGELOG + GitLab Release publish) until the outstanding
  `release/vX.Y.Z → main` MR is merged.
- **Informational check (`main-develop-drift-check`, `verify` stage):** runs on every push to
  `develop`, non-blocking (`allow_failure: true`), for earlier visibility between releases.

**If the gate fails:** the job output lists exactly which release tags are missing from `main`.
Resolve it the normal way — branch `release/vX.Y.Z` from `develop` for the oldest missing
release, open an MR to `main` per the "Cutting a release" steps above, get it merged, then retry
the tag push (or re-run the pipeline once `main` is caught up).

See `docs/tasks/task-T331.md` for the incident this gate was built to prevent, and
`docs/plans/plan-019-main-develop-drift-detection.md` for the full design rationale (why content
comparison instead of `git merge-base --is-ancestor`, why a 1-release grace window, why a
blocking release-time gate instead of a scheduled pipeline).
```

## Acceptance criteria

1. `grep -c "### Drift detection" CONTRIBUTING.md` → 1
2. `grep -c "check-main-develop-drift.py" CONTRIBUTING.md` → 1 or more
3. `grep -c "main-develop-drift-gate" CONTRIBUTING.md` → 1 or more
4. New subsection appears after the `glab release create` guidance and before `### Hotfixes`
   (confirm via `grep -n "### Drift detection\|### Hotfixes" CONTRIBUTING.md` — Drift detection
   line number must be less than Hotfixes line number).
5. No other content in `CONTRIBUTING.md` changed (confirm via `git diff CONTRIBUTING.md` showing
   only an addition, no deletions/reflow of unrelated lines).
6. Markdown link check still passes for this file (no new broken links introduced):
   run the same check as the `markdown-links` CI job, or at minimum manually confirm any new
   markdown links in the added text resolve (`docs/tasks/task-T331.md` and
   `docs/plans/plan-019-main-develop-drift-detection.md` both exist as plain-text references, not
   markdown links, in the exact text above — no link syntax to validate).

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<not yet picked up>
