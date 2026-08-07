# Task T339 — Sync `main` with `develop` for v6.6.0 (release/v6.6.0 → main)

**ID:** T339
**Owner:** orchestrator, release-manager
**Status:** done
**Completed:** 2026-08-07
**Priority:** P0
**Depends on:** T337, T338
**Created:** 2026-08-07
**Based on:** `.claude/rules/git-workflow.md`, `docs/tasks/task-T331.md` (precedent)

## Objective
Perform the standing GitFlow `release/vX.Y.Z → main` sync for v6.6.0, per the policy T331
diagnosed as historically neglected and plan-019's drift gate now enforces.

## Context
Delegated to `@release-manager`, which branched `release/v6.6.0` from `develop`'s tip and opened
MR !109. GitLab reported a genuine conflict (`detailed_merge_status: conflict`). The release-manager
subagent's own investigation (from a shallow local clone) misdiagnosed this as "unrelated
histories" / an orphan `main` commit — the orchestrator independently re-verified from a fully
unshallowed clone and found the correct root cause (see below), superseding that initial report.

## Root cause (independently verified, not guessed)
`origin/main`'s tip (`5d5fd00`, the T331/MR !103 sync commit) has two real parents (`febd85a`,
old main tip; `6b2d680`, a commit GitLab's merge API materialized during MR !103 with an identical
tree to `develop`'s real v6.5.0 tip `f75335c` but with only one parent, `febd85a` — NOT `f75335c`
itself). `f75335c` is confirmed not an ancestor of `6b2d680`
(`git merge-base --is-ancestor f75335c 6b2d680` → exit 1) despite identical trees. Consequently
`git merge-base(origin/main, origin/develop)` today resolves to the old pre-T331 divergence point
(`363aeb8`, v6.0.3-era) rather than the true v6.5.0 reconciliation point, and a 3-way merge against
that stale base re-surfaces old-style conflicts on files both branches touched independently since
v6.0.3, even though `main` and `develop` were content-identical going into this release. `main` had
zero independent commits since v6.5.0 throughout this cycle (verified before and after Phase B).

## Acceptance Criteria
- [x] `origin/main` tip confirmed unchanged (`5d5fd00`) before Phase B started
- [x] Real conflict on MR !109 confirmed via GitLab's own API (`detailed_merge_status: conflict`),
      not assumed
- [x] Exact 5 conflicting files identified via a local, non-destructive, never-pushed dry-run:
      `CONTRIBUTING.md`, `README.md`, `docs/tasks/completed-tasks.md`, `docs/wiki/README.md`,
      `docs/wiki/home.md`
- [x] Escalated per the T331 precedent rather than resolved unilaterally; user approved Option 1
      explicitly before any resolution
- [x] Resolved by taking `develop`'s side for all 5 files (matching T331's rationale — `main` had
      zero independent commits on any conflicting path); verified byte-identical to
      `origin/develop` via `git diff origin/develop` (empty) before committing
- [x] Full verification bar re-run post-resolution: 286 tests OK (skipped=17, `unittest discover`
      and `tests/run.py` agree); registry up to date; sync 0 drift (511 files);
      `verify-release-docs.py --tag v6.6.0` PASS
- [x] MR !109 became conflict-free after push (`has_conflicts: False`), MR pipeline green (5/5)
- [x] Merged via explicit API `squash=false` override (API's `squash` response field read `True`
      again — same misleading-field pattern as MR !103 — but the actual resulting commit
      `c14bf79` has 2 real parents and a tree byte-identical to `origin/develop`, confirmed via
      `git log`/`git diff`, not the API field)
- [x] `git diff origin/develop origin/main` empty (authoritative signal, not commit-SHA ancestry)
- [x] Post-merge `main` pipeline (`2740260835`) green (5/5 jobs)

## Outcome (2026-08-07)
`main` tip: `c14bf7903b8cdaa1e845a57069c7fc5888b64bd9`. `develop` tip:
`b866a778ba1870f2923b17e3cf37c2e69822cde9`. Content-identical, verified.

## Flagged follow-up (not fixed as part of this release, per user instruction)
Because `main`'s second parent from each `release/* → main` merge is a GitLab-materialized commit
without real ancestry into `develop`'s commit graph, **this same phantom-conflict pattern is
likely to recur on every future `release/* → main` merge**, regardless of actual content drift,
until some future merge lands a commit on `main` whose parent chain genuinely includes a real
`develop` commit. Recommended as a dedicated follow-up investigation, not addressed here — same
treatment T331 gave its own "add a CI drift check" recommendation (documented, not immediately
executed, then picked up as plan-019 in a later session).
