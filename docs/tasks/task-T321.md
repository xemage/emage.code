# Task T321 — Write the registry-publishing hand-off into `../CWSO`

**ID:** T321
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Depends on:** T317
**Created:** 2026-08-02
**Completed:** 2026-08-03
**Based on:** docs/plans/plan-017-deployment-docs-and-registry-hardening.md

## Objective
Hand off the CWSO Container Registry publishing gap to CWSO's own team, following the exact
convention plan-016's T310 established (which CWSO's team successfully picked up and shipped —
see `../CWSO` commit `f7400f3` and the T169/T170 history). Write real, actionable documents
directly into `../CWSO` using CWSO's own conventions. Do NOT modify `../CWSO/.gitlab-ci.yml`
yourself. Do NOT touch `../CWSO/docs/tasks/active-tasks.md`.

## Inputs
- `../CWSO/.gitlab-ci.yml` (confirm exact current job names/structure — they may have changed
  since this plan was written)
- `../CWSO/docs/plans/_template.md`, `../CWSO/docs/tasks/_template.md`
- `../CWSO/docs/tasks/active-tasks.md`, `../CWSO/docs/tasks/completed-tasks.md` (to find the next
  free CWSO task IDs — do not assume; CWSO was at T176 when this plan was written, confirm the
  real current value)

## Expected outputs
- `../CWSO/docs/artifacts/emagecode-integration-registry-gap-v1.md`
- `../CWSO/docs/plans/plan-registry-publishing-completion.md`
- `../CWSO/docs/tasks/task-T<NNN>.md` × 2 (CWSO's own next free IDs)

## Acceptance criteria
1. Confirmed CWSO's next free task ID via
   `grep -n "^| T" ../CWSO/docs/tasks/active-tasks.md ../CWSO/docs/tasks/completed-tasks.md | tail -5`
   before writing anything.
2. Issue summary states precisely: no `build:rollout` job exists; `deploy:registry` only pushes
   `orchestrator`/`git-shadow` (confirm current `needs:` list yourself); only `:latest` is
   published, no semver tags; the project is public with registry access enabled (not an
   auth/access problem).
3. Fix plan (CWSO's own template) includes a literal suggested CI YAML snippet for the missing
   `build:rollout` job (mirroring `build:merge-engine`'s structure), the missing `deploy:registry`
   entries, and a semver-on-tag push. Stated explicitly as a suggestion for CWSO's own team to
   adapt, not a mandate.
4. Two CWSO task briefs written using CWSO's own next free IDs and its own `_template.md`.
5. `../CWSO/docs/tasks/active-tasks.md` is NOT modified — verify via `git -C ../CWSO diff --stat
   docs/tasks/active-tasks.md` showing no changes.
6. `git -C ../CWSO status --porcelain` shows exactly the 3 new untracked files, nothing else
   changed.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed: 2026-08-03

CWSO next free task IDs confirmed: T178, T179 (T177 was last in ../CWSO/docs/tasks/).
Active-tasks.md was empty (no pending rows).

### Files created in `../CWSO`:

```
-rw-r--r-- 1 emage emage 3272 Aug  3 docs/artifacts/emagecode-integration-registry-gap-v1.md
-rw-r--r-- 1 emage emage 4651 Aug  3 docs/plans/plan-registry-publishing-completion.md
-rw-r--r-- 1 emage emage 1737 Aug  3 docs/tasks/task-T178.md
-rw-r--r-- 1 emage emage 1836 Aug  3 docs/tasks/task-T179.md
```

Note: plan called for 3 files (artifact + plan + 2 task briefs = 4). Added T179 as the second
task brief as specified (one for build:rollout, one for deploy:registry expansion + semver).

### `git -C ../CWSO status --porcelain`
```
?? docs/artifacts/emagecode-integration-registry-gap-v1.md
?? docs/plans/plan-registry-publishing-completion.md
?? docs/tasks/task-T178.md
?? docs/tasks/task-T179.md
```
Only 4 new untracked files; no existing CWSO files were modified.

**Result: PASS**
