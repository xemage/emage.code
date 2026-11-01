# Artifact: security-review-t686-release-job-token-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test, mutation or pipeline run; the `grep_content` tool errored, files read directly; GitLab documentation and runner merge requests read on 2026-10-23). Recorded by the orchestrator from the reviewer's two reports (first review, delta re-review).
- **Gate**: security. **Date**: 2026-10-23.
- **Target**: T686, branch `agent/devops-engineer/T686` (from develop `f9001692`): the release job authenticates with the GitLab job token (`--token-env CI_JOB_TOKEN --token-header JOB-TOKEN`), `scripts/publish-release.py` gets a `--token-header` allowlist (`PRIVATE-TOKEN` default, `JOB-TOKEN`), `WIKI_TOKEN` is used only by `wiki-sync`, `CONTRIBUTING.md` gets the "Release token and permissions" section. Reviewed tips: `0a14dca0` (first review), fix commit `684099e1` with the clean merge `8916c935` of develop `27e27924` (delta).
- **Based on**: `docs/tasks/task-T686.md`, `docs/artifacts/security-review-t685-supply-chain-residuals-v1.md` (the WIKI_TOKEN section). The user decided on 2026-10-23 (AskUserQuestion, label verbatim): "Yes, create a task to switch (Recommended)".
- **Orchestrator checks**: the full suite on the merged tree is recorded in the task outcome. The developer's mutation log (`scratchpad/mutations-t686.txt`): round 1 41 distinct mutations (35 killed first, 2 skipped, 4 survivors strengthened and killed), round 2 27 mutations (25 killed first, n4 and n8 strengthened and killed); the reviewer judged it consistent, not reproduced.

## First review: CONDITIONAL_PASS (0 critical, 0 high, 1 medium, 4 low)

The header allowlist (three layers: argparse `choices`, `validate_token_header` in `main()`, `gitlab_request()` and `create_or_update_release()`), the single-header token placement on GET/PUT/POST, the refused redirects for 301/302/303/307/308 (tested with real local servers and a control showing the default opener would leak), the host pin and URL validation, and the CI diff (only the release job changed; `needs` and the T685 tag-tree gate intact) meet the requirement. The job token is strictly shorter-lived and narrower in endpoints than the old `api`-scope `WIKI_TOKEN`; it existed in every job already, so T686 adds no new exposure.

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T686-01 | MEDIUM | the withholding from the git/apk child processes was by name only; GitLab also exposes the job token as `CI_REGISTRY_PASSWORD` and inside `CI_REPOSITORY_URL`, so the documented and tested isolation was untrue | fixed in `684099e1`: `child_environment()` is an allowlist plus a value filter (any variable whose value contains `WIKI_TOKEN`, `CI_JOB_TOKEN`, the `--token-env` value or a deprecated `--token` value is dropped), mirrored in the release job's apk bootstrap and pinned by tests (the YAML string equals the executed bootstrap; allowlist equality; a token under a second name, inside a URL, inside an allowlisted name); the CONTRIBUTING wording is exact; CLOSED |
| SEC-T686-02 | LOW | docs: the pusher's role may exceed the old token's role; tag protection does not limit who holds a Releases-capable job token; WIKI_TOKEN minimum role; job-token settings may cause a 403 | fixed (CONTRIBUTING); CLOSED |
| SEC-T686-03 | LOW | masking of `CI_JOB_TOKEN` in job logs unverified | marked (unverified) and added to the first-tag rehearsal checklist; CLOSED |
| SEC-T686-04 | LOW | loose test pins; a fake token of the shape `glpat-...` | fixed (section-scoped needles, tightened argv-ban regex, fake token `t686-FAKE-job-token-not-a-credential`); CLOSED |
| SEC-T686-05 | LOW | argparse echoes a rejected header name (repr-escaped) | informational, no action |

## Delta re-review: PASS (0 critical, 0 high, 0 medium; 3 LOW new)

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T686-06 | LOW (availability, fail-closed; the highest-value item) | if the runner uses the credential helper (`FF_GIT_URLS_WITHOUT_TOKENS`), git needs `CI_JOB_TOKEN` in its environment: the new filter removes it, so `git fetch --tags --force` and `git fetch --unshallow --tags origin` fail and the release job never reaches the API; the docs state as fact that `.git/config` holds the clone credential (unverified; the runner version at which the helper became the default was not confirmed) | tracked debt, to be settled before the first real tag: read the "Getting source from Git repository" section of a recent job log (or `git remote -v` in a throw-away job) and note the runner version; mark the docs (unverified) until checked; if the helper is used, exempt only the two network fetches from the value filter (give them `CI_JOB_TOKEN` and the helper variables) and keep the filtered environment for `tag`, `log`, `merge-base`, `rev-list`. The manual `glab release create` fallback is documented |
| SEC-T686-07 | LOW (hardening) | `GIT_EXEC_PATH`, `GIT_ASKPASS`, `GIT_CONFIG_GLOBAL`/`SYSTEM`, `GIT_CONFIG_COUNT`/`KEY_n`/`VALUE_n` and the proxy variables are allowlisted without a stated reason (config or execution channels if job variables are attacker-influenced; no incremental risk, since the same actor could set `PYTHONPATH`); a re-encoded token inside `GIT_CONFIG_VALUE_n` would pass the substring filter | tracked debt: keep only what the runner uses and add a reason per entry |
| SEC-T686-08 | LOW (nit) | Python allows `LC_[A-Z_]+`, the bootstrap any name starting with `LC_`; the equality test covers names only | tracked debt |

## Open and unverified

The first real tag pipeline (job tokens in tag pipelines on protected tags; Releases API acceptance here; the runner's clone method; masking of `CI_JOB_TOKEN` in job logs; whether protected tags also restrict release create/update/delete); the user's GitLab settings (protected and masked `WIKI_TOKEN`, protected `v*` tags restricted to Maintainers); the poc_scan rule against older tests that still contain `glpat-FAKE-not-a-real-token`.
