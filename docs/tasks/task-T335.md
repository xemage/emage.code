# Task T335 — Document the drift gate in `CONTRIBUTING.md`

**ID:** T335
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T332
**Created:** 2026-08-07
**Completed:** 2026-08-07
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

**Executed by:** technical-writer, 2026-08-07.

**Environment note:** No shell/Bash tool was available in this agent session (only
Read/Edit/Write/WebFetch/WebSearch). The acceptance-criteria commands below could not be
literally invoked as subprocess calls. Instead, the full, exact content of `CONTRIBUTING.md`
was read verbatim via the Read tool (both before and after the edit) and the grep/diff
semantics were computed by hand against that exact byte-for-byte content. This is noted as a
deviation from "run every one for real" — flagging it explicitly per instructions rather than
fabricating literal shell output. The orchestrator may want to re-run these as real shell
commands to double check; the computed results below are derived from the actual file content,
not assumed.

**Edit performed:** exact verbatim `### Drift detection` subsection (as specified in the task
brief, char-for-char) inserted into `CONTRIBUTING.md` § Releasing, between the paragraph "Do not
use ad-hoc inline `--notes`, as that can drift from `docs/releases/vX.Y.Z.md`." (line 162) and
the `### Hotfixes` subsection (originally line 164, now line 190 after insertion). No other line
in the file was changed, reworded, or reflowed.

1. `grep -c "### Drift detection" CONTRIBUTING.md` → computed result: **1**
   (single occurrence, at line 164 post-edit).

2. `grep -c "check-main-develop-drift.py" CONTRIBUTING.md` → computed result: **1**
   (single occurrence, at line 167 post-edit, satisfies "1 or more").

3. `grep -c "main-develop-drift-gate" CONTRIBUTING.md` → computed result: **1**
   (single occurrence, at line 173 post-edit, satisfies "1 or more").

4. `grep -n "### Drift detection\|### Hotfixes" CONTRIBUTING.md` → computed result:
   ```
   164:### Drift detection
   190:### Hotfixes
   ```
   164 < 190 — Drift detection precedes Hotfixes. PASS.

5. `git diff CONTRIBUTING.md` — could not be run as a literal `git diff` subprocess (no Bash
   tool). Verified equivalently by diffing the full pre-edit and post-edit file content
   (captured via Read tool before and after the Edit call): lines 1-162 are byte-identical
   before and after; a new contiguous block of 26 lines (`### Drift detection` through the
   blank line before `### Hotfixes`) was inserted after line 162; all content from the
   original line 164 (`### Hotfixes`) onward is byte-identical to the post-edit content from
   line 190 onward, just shifted down by 26 lines. No deletions, no reflow, no whitespace
   changes to any pre-existing line. Faithful diff summary:
   ```
   @@ CONTRIBUTING.md @@
    Do not use ad-hoc inline `--notes`, as that can drift from `docs/releases/vX.Y.Z.md`.
   +
   +### Drift detection
   +
   +`main` and `develop` are checked for content drift on every release and on every push to
   +`develop`, using `scripts/check-main-develop-drift.py`. The check compares the
   +`Latest release: vX.Y.Z` marker in `README.md` on each branch and counts how many tagged
   +releases separate them.
   +
   +- **Grace window:** `main` may lag `develop` by up to 1 release — the normal transient state
   +  between a release being tagged and its `release/vX.Y.Z → main` sync MR landing.
   +- **Blocking gate (`main-develop-drift-gate`, `release` stage):** runs on every tag push. If
   +  `main` is already more than 1 release behind at the moment a new release is tagged, this job
   +  fails and blocks the `release` job (CHANGELOG + GitLab Release publish) until the outstanding
   +  `release/vX.Y.Z → main` MR is merged.
   +- **Informational check (`main-develop-drift-check`, `verify` stage):** runs on every push to
   +  `develop`, non-blocking (`allow_failure: true`), for earlier visibility between releases.
   +
   +**If the gate fails:** the job output lists exactly which release tags are missing from `main`.
   +Resolve it the normal way — branch `release/vX.Y.Z` from `develop` for the oldest missing
   +release, open an MR to `main` per the "Cutting a release" steps above, get it merged, then retry
   +the tag push (or re-run the pipeline once `main` is caught up).
   +
   +See `docs/tasks/task-T331.md` for the incident this gate was built to prevent, and
   +`docs/plans/plan-019-main-develop-drift-detection.md` for the full design rationale (why content
   +comparison instead of `git merge-base --is-ancestor`, why a 1-release grace window, why a
   +blocking release-time gate instead of a scheduled pipeline).
   +
    ### Hotfixes
   ```
   Only an addition — no deletions, no unrelated reflow. PASS.

6. Markdown-link check: the inserted text contains two file references —
   `` `docs/tasks/task-T331.md` `` and `` `docs/plans/plan-019-main-develop-drift-detection.md` ``
   — both rendered as inline code spans (single backticks), plain text, **not** markdown link
   syntax (`[text](url)`). No `[` `]` `(` `)` link construct was introduced anywhere in the
   inserted block. Confirmed by visual inspection of the exact inserted text above: zero new
   markdown links, so nothing to validate against the `markdown-links` CI job. PASS.

**Scope confirmation:** only `CONTRIBUTING.md` was modified (the new subsection insert) and this
task brief (`docs/tasks/task-T335.md`, this Execution notes section). No files under `scripts/`,
`tests/`, or `.gitlab-ci.yml` were read for editing purposes or touched. No commit or push was
performed — left for the orchestrator per task constraints.

**Result: all 6 acceptance criteria PASS** (criteria 1-4 and 6 by direct/computed grep-equivalent
inspection of the exact file content; criterion 5 by full before/after content diff, since no
Bash/`git` tool was available in this session to run the literal commands).
