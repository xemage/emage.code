# Task T338 — Fix main-develop-drift-gate tag-fetch rejection bug

**ID:** T338
**Owner:** devops-engineer
**Status:** done
**Completed:** 2026-08-07
**Priority:** P0
**Depends on:** — (blocking, discovered mid-release)
**Created:** 2026-08-07
**Based on:** `.gitlab-ci.yml` (`main-develop-drift-check`, `main-develop-drift-gate` jobs, added by T334)

## Objective
Fix a CI bug that blocked the v6.6.0 release's tag-triggered pipeline: both
`main-develop-drift-check` (verify stage) and `main-develop-drift-gate` (release stage) run
`git fetch origin 'refs/tags/*:refs/tags/*'` on a shallow (`GIT_DEPTH: "1"`) clone with no
`--force`. On the real runner this failed with `! [rejected] v6.0.3 -> v6.0.3 (would clobber
existing tag)` — the runner's cached git state held a stale `v6.0.3` tag object diverging from
origin's current `v6.0.3` SHA, rejecting the fetch before `scripts/check-main-develop-drift.py`
ever ran.

## Context
Discovered live, during T337's tag-push pipeline (`2740097012`, `main-develop-drift-gate: failed`)
— the plan-019 drift gate's first real production run. Independently reproduced on the
non-blocking `main-develop-drift-check` job in the same develop-push cycle, confirming it's a
fetch-mechanism defect, not real main/develop drift (both branches were genuinely in sync).
Orchestrator escalated per the "stop and report on unexpected CI failure" norm established this
session (T331 precedent); user approved the fix approach explicitly before any tag manipulation.

## Acceptance Criteria
- [x] `git fetch origin 'refs/tags/*:refs/tags/*'` → `git fetch --force origin 'refs/tags/*:refs/tags/*'`
      in both job blocks, no other changes
- [x] Branched `bugfix/main-develop-drift-tag-fetch-force` from `origin/develop`, MR !108 opened
- [x] MR pipeline green (5/5 jobs success); `main-develop-drift-check`/`main-develop-drift-gate`
      did not run on this MR (rule requires `$CI_COMMIT_BRANCH == "develop"` push, not
      `merge_request_event` — so no reproduction on the MR itself, noted honestly rather than
      claimed)
- [x] Merged (squash), merge commit `b866a778ba1870f2923b17e3cf37c2e69822cde9`
- [x] Post-merge `develop`: both fetch lines confirmed to include `--force`
      (`.gitlab-ci.yml:123`, `.gitlab-ci.yml:188`)
- [x] Fix proven effective: after T337's tag was recreated on this fixed commit, the re-run
      pipeline's `main-develop-drift-gate` job succeeded, with the tag-fetch step completing
      cleanly (`tag update` lines, no rejection) and the drift script producing a real PASS verdict

## Outcome (2026-08-07)
Fix landed cleanly on `develop` via MR !108. Confirmed effective in production on the recreated
`v6.6.0` tag's pipeline (`2740157827`) — independently verified by the orchestrator via the job's
literal trace output, not just the merge report.
