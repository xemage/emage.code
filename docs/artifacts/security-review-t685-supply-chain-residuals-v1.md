# Artifact: security-review-t685-supply-chain-residuals-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test, mutation, audit or install run; the `grep_content` tool could not reach the worktree; external facts read on 2026-10-22: nodejs/Release `schedule.json`, alpinelinux.org/releases, docs.gitlab.com `api/releases` and `ci/jobs/ci_job_token`). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-23.
- **Target**: T685, branch `agent/devops-engineer/T685` (from develop `b78b8e0a`), commit `e74a42b7`: package-scoped Brave audit acceptances (`--accept GHSA:date:package@version`, a pin bump voids it, 90-day bound, `docs/artifacts/brave-audit-acceptance-v2.md`), `scripts/check-release-tag-tree.py` and its line in the blocking `main-develop-drift-gate` job, the extended commit-subject unsafe class and a three-commit real-git test, the GitHub-removal upgrade sentences, the end-of-life image examples in two knowledge files, and the checklist updates.
- **Based on**: `docs/tasks/task-T685.md`, `docs/artifacts/security-review-t676-supply-chain-v1.md`, `docs/artifacts/brave-audit-acceptance-v1.md`.
- **Orchestrator checks**: the full suite on the merged tree is recorded in the task outcome; the developer's mutation log (`scratchpad/mutations-t685.txt`: 41 killed, the first d4 mutation corrected and killed) was judged plausible by the reviewer, not re-run. The developer ran the real `audit` against npm with the five scoped accepts (ACCEPTED for the brave pin and the SDK, exit 0) and `check-release-tag-tree.py --tag v8.0.0` on the real repository (PASS).

## Verdict: CONDITIONAL_PASS (0 critical, 0 high, 0 medium, 3 LOW + 8 INFO)

SEC-T676-11, -12, -13 and -14, the release-tag tree check and the knowledge templates are closed in code and tests; the scoped acceptance and the tree gate fail closed in every traced case (no way found to accept a new advisory, a different package or a second pin silently; an unresolved tag or `origin/main` fails; a tag pointing at a tree object is refused); no Immutable Security Constraint breached; the change tightens three controls.

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T685-01 | LOW | `origin/main` is resolved by git's short-name search, so a tag named `origin/main` (fetched one line earlier) shadows it and makes the comparison trivially equal; fix: resolve `refs/remotes/origin/main` (or pass `--main-ref refs/remotes/origin/main` and require the prefix) and test a fixture with such a tag | tracked debt (register v2) |
| SEC-T685-02 | LOW | the subject unsafe class still misses default-ignorable code points (U+180B-180F, U+206A-206F, U+FFF0-FFF8, U+1BCA0-1BCA3, U+1D173-1D17A, the unassigned rest of U+E0000-E0FFF); fix: a category test (`Cc`, `Cf`, `Zl`, `Zp`, `Co`, `Cn`) plus the explicit list of the `Mn`/`Lo` members | tracked debt |
| SEC-T685-03 | LOW | the stricter tag gate is under-documented and one docstring is false: `scripts/verify-release-docs.py:15-17` still says the main duty is enforced "within its grace window"; CONTRIBUTING does not say whether pre-release tags (the CI rule admits `v1.2.3-rc.1`) must also match `main`, nor the retag procedure, nor the hotfix-during-release case (tag the main merge commit, not `origin/main^2`) | tracked debt |

INFO (not graded): the 90-day bound is relative to the run day (visible in review since the artifact and tests pin the command); an acceptance whose advisory no longer appears prints as accepted and does not fail; the tag gate, the release job and `.gitlab-ci.yml` all come from the tagged commit, so they guard against process errors, not a malicious tagger (the real controls are protected tags and a protected `WIKI_TOKEN`); the docs say an acceptance counts "only when that package is the only pinned package" while the code accepts when every at-risk pin has its own acceptance; "revoke or unset" suggests unsetting removes the credential (only revoking at GitHub does); the class strips U+200C/U+200D used legitimately in Persian and Indic subjects; a non-UTF-8 path name in a failing diff raises a traceback in `check-release-tag-tree.py` (still fail-closed); `node:24-alpine` enters maintenance on 2026-10-20 and Node 26 becomes LTS on 2026-10-28.

## The WIKI_TOKEN question (report; user decision of 2026-10-23)

Confirmed in the GitLab documentation (read 2026-10-22): the Releases API accepts the job token in the `JOB-TOKEN` header (create and update need the Developer role of the user who triggered the pipeline); the Wiki API is not on the job-token list. Today anyone who can push a release tag runs the tagged commit's script with `WIKI_TOKEN` (a long-lived, `api`-scope secret) in its environment. Recommendation: move the release job to `CI_JOB_TOKEN` (`--token-env CI_JOB_TOKEN --token-header JOB-TOKEN`, a fixed allowlist of header names; the host pin, redirect refusal and control-character checks stay), keep `WIKI_TOKEN` only for `wiki-sync` (protected and masked, minimum role), confirm protected `v*` tags are restricted to Maintainers, keep the manual `glab release create` fallback until a real tag pipeline confirms it. The user decided on 2026-10-23 (AskUserQuestion, label verbatim): "Yes, create a task to switch (Recommended)" -> T686.

## Open and unverified

The first real tag pipeline (the tree gate's `git fetch ... --depth=1` creating `origin/main` in the runner clone, the tag ref existing after the tags fetch, `needs` still gating `release`; check the `main-develop-drift-gate` output for the `release-tree: PASS` line and record it); the first run of the changed `.gitlab-ci.yml`; whether job tokens work in tag pipelines on protected tags here; the live `npm audit` JSON shape (`isDirect`, `effects`) beyond the developer's one run.
