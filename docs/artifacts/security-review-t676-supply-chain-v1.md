# Artifact: security-review-t676-supply-chain-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test, mutation, audit or install run; the `grep_content` tool could not reach the worktree; registry digests and advisories read through fetch tools on 2026-10-22). Recorded by the orchestrator from the reviewer's two reports (first review, delta re-review).
- **Gate**: security. **Date**: 2026-10-22.
- **Target**: T676 (supply-chain and verification checklist items, tracked debt), branch `agent/devops-engineer/T676` (from develop `1d9dd68d`): hash-locked CI Python (`ci/requirements-*.in/.txt`, `--require-hashes`, `--only-binary=:all:`), supported base images pinned by digest, `scripts/audit-mcp-pins.py` and `docs/wiki/mcp-pin-bump-checklist.md`, 13 added blocked-origins entries, the commit-subject sanitiser of `scripts/publish-release.py`, and (after the user's decision of 2026-10-22) the removal of the `github` MCP server. Reviewed tips: `a6e20bd3` (first review), `965bd5c5` with the later clean merge `783daf92` (delta).
- **Based on**: `docs/tasks/task-T676.md`, `docs/artifacts/tracked-debt-register-v1.md` (T676 rows), `security-review-t675-ci-release-hardening-v1.md`, `security-review-t638-mcp-packages-v1.md`.
- **User decisions of 2026-10-22** (AskUserQuestion, labels verbatim): the Brave audit risk "Accept with conditions (Recommended)"; the GitHub MCP server "Remove GitHub MCP server" (free-text answer; it replaced the read-only hardening the developer had added).
- **Orchestrator checks**: full suite on the merged tree recorded in the task outcome; the developer's mutation logs `scratchpad/mutation-log.txt` (24, all killed) and `mutation-log-2.txt` (43, all killed; srv-1 re-run) were judged plausible by the reviewer, not re-run; the orchestrator's secret scan over every commit of the branch (`git log -p origin/develop..HEAD`, patterns: bearer values, `glpat-`, `ghp_`, `ctx7sk-`, `sk-`, `authorization:` with a value) found no credential-shaped string.

## First review: CONDITIONAL_PASS (0 critical, 0 high, 2 medium, 8 low)

No Immutable Security Constraint breached; the change reduces supply-chain exposure (hash-locked installs, end-of-life images replaced, runtime `apk add` removed from the `WIKI_TOKEN` job, wider blocked-origins list).

| Id | Grade | Finding | Disposition (delta review) |
|---|---|---|---|
| SEC-T676-01 | MEDIUM | the checklist's "isolated" `opencode debug config` command expanded `$HOME` in the calling shell, so it loaded and printed the real global config (how a bearer value reached a session transcript) | fixed (`t=$(mktemp -d); env -i ... HOME="$t" ... > "$t/config.json"`, only `playwright_*` keys read; the warning phrase and a negative regex pinned by a test); CLOSED. The credential printed in that session must be treated as exposed: rotation is a user action, to be confirmed |
| SEC-T676-02 | MEDIUM | `npm audit`: 2 high findings from `@brave/brave-search-mcp-server@2.1.4` via `@modelcontextprotocol/sdk@1.30.0` (GHSA-6qxp-vccf-f47h, -22jm-h49p-29qw, -6prh-2h8m-c8cw, -46jr-4wx8-v453, -rvq5-wwqv-78pq; vulnerable below 1.32) | accepted by the user with conditions (`docs/artifacts/brave-audit-acceptance-v1.md`, expiry the first brave release above 2.1.4 or 2026-11-21): stdio launch; the 2.1.4 tarball was read (no `taskStore`, bearer, client transport or `client/auth` outside tests); a test pins the brave entry to a plain stdio launch (no `--transport/--host/--port`, no `BRAVE_MCP_*`); `audit-mcp-pins.py --accept GHSA-x:YYYY-MM-DD` (date mandatory, expired fails, accepted printed not hidden); CLOSED under the acceptance |
| SEC-T676-03 | LOW | `audit` could print "no known vulnerabilities" for an unexpected valid JSON object | fixed (requires `vulnerabilities` and `metadata`; unknown severity counts as critical); CLOSED |
| SEC-T676-04 | LOW | the npm subprocess read `~/.npmrc`; the registry fetch followed redirects; printed titles unfiltered | fixed (two distinct empty config files, `--registry`, no-redirect opener, control/bidi stripping); CLOSED |
| SEC-T676-05 | LOW | a lone CR still forged a changelog entry; invisible tag characters survived | fixed (bytes and `%x00` framing, extended unsafe class, real-git test); CLOSED, residual SEC-T676-12 |
| SEC-T676-06 | LOW | blocked-origins list: no matcher test; apex names not blocked | fixed (apex entries, 39 entries, ported matcher test, skipped when the vendor bundle is absent); CLOSED; Teredo and trailing-dot forms documented as residual |
| SEC-T676-07 | LOW | the GitHub server read-only by default: restore advice incomplete | CLOSED by removal (user decision) |
| SEC-T676-08 | LOW | hash-locked installs could still build from source; very new versions locked | fixed (`--only-binary=:all:`, quoted YAML lines, `--exclude-newer` header); CLOSED, INFO SEC-T676-14 |
| SEC-T676-09 | LOW | `python:3.12-alpine` digest stale; EOL table static | fixed (re-resolved digest `sha256:92abd2ba...` on all 8 jobs, `ci_images_reviewed_on` guard: 120 days); CLOSED |
| SEC-T676-10 | LOW | checklist test gaps, secret regex | fixed; CLOSED |

## Delta re-review: CONDITIONAL_PASS: 0 critical, 0 high, 0 medium, 3 LOW + 1 INFO new

The GitHub removal is complete in everything read; `--update` prunes the `github` entry only when the old sidecar lists it and keeps a renamed user entry (tested); removing the server weakens no control.

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T676-11 | LOW | `--accept` is global by advisory id (a future pin pulling the same SDK would be accepted, printed as ACCEPTED, exit 0) and its date is not bounded by the script | tracked: T685 (scope to a package, bound the date to 60-90 days) |
| SEC-T676-12 | LOW | the NUL framing is not tested across several commits; U+034F and Khmer inherent vowels not in the unsafe class | tracked: T685 |
| SEC-T676-13 | LOW | a user-owned GitHub server has no generated denial; the notes do not tell adopters to revoke or unset their GitHub PAT | tracked: T685 (two sentences in the upgrade note) |
| SEC-T676-14 | INFO | the lock `--exclude-newer` equals the generation day: reproducibility, not a cooldown | optional at the next lock regeneration |

## Open and unverified

- The brave acceptance is live until 2026-11-21 or the first brave release above 2.1.4: after that the audit must pass without `--accept` or the artifact must be renewed with the user.
- The first real GitLab pipeline run of the changed `.gitlab-ci.yml` (the commands were run in the pinned images); Gemini CLI and Opencode enforcement during a real tool call (SEC-T658-02 and K-20 stay open as debt, honestly labelled "not run (unverified)").
- The reviewer could not compare against a short prefix of the leaked credential (unknown to the reviewer); the orchestrator's scan found no credential-shaped string in the branch commits.
- Register rows not closed by T676 (to T685): TL-T649-13 / QA-T648-03 (the ancestor check of the release tag against `origin/main`; `check-main-develop-drift.py` documents that SHA ancestry gives false results for GitLab API merges, so a tree comparison is proposed); the `WIKI_TOKEN` reuse question (the developer evaluated `CI_JOB_TOKEN` for the release job: the Releases API is supported by job tokens, the Wiki API is not; no change made); the knowledge templates that still show `node:20-alpine` and `alpine:3.19` as examples.
