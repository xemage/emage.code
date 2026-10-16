# Artifact: security-review-release-v8-v2.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, no test run; the `security-audit` tools could not reach the release tree, `poc-security-audit` was not callable; the reviewer read files at the branch tip, not the commit diff). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security, release-level re-check (T650). **Date**: 2026-10-15.
- **Target**: `release/v8.0.0` at `57d0107d437110d12a2d3cf46cf19597bed913e1`. Later commits on the branch (the T645 amendment, T660 and the verdict commit) are outside this review; the T660 diff gets its own review and the orchestrator re-runs the scans named in the T652 checklist on the final tree.
- **Based on**: `docs/tasks/task-T650.md`, `docs/artifacts/security-review-release-v8-v1.md` (T633) and every later review (T635, T636, T638, T640, T646, T655, T657, T658), `docs/artifacts/release-rehearsal-t647-v1.md`, `fetch-ssrf-test-t653-v1.md`, `fetch-replacement-evaluation-v1.md`, `docs/releases/v8.0.0.md`.

## Verdict: CONDITIONAL_PASS

0 critical, 0 high. Three MEDIUM open at the review: SEC-T658-01 and SEC-T657-02 (carried) and SEC-T650-01 (new); 4 new LOW. No Immutable Security Constraint is breached; no required control is omitted or weakened in the delta; no secret was found in any file read. `validation-gates` § Verdict Rules requires a MEDIUM security finding to be fixed before the release ships (the next-release-cycle rule does not apply); the Release gate therefore cannot issue a shipping verdict while one stands unless the user records an explicit risk acceptance.

## Answers

1. **SEC-002 (`@anthropic/mcp-filesystem`) is gone** from `servers.yaml` and from all 14 generated MCP configs (root and `implementation/`, seven platforms); every `npx`, `uvx` and `docker` entry is pinned to an exact version or digest; the root drift baseline is empty after refresh 19. Caveat: the primary checkout (stale develop `bfd4ba7`) still has the old entry; that is not the release branch.
2. **SEC-001 is still fixed**: `refuse_unsafe_path`, `guard_managed_paths`, `platform_managed_paths` and `same_tree` in `install.sh`; `merge-mcp-json.py` refuses a symlinked destination or sidecar; `TestInstallRefusesSymlinkedManagedPaths` has 13 cases under rsync and cp with canaries (not run by the reviewer; the T636 review and the orchestrator's canary re-run stand).
3. **The M-9 note was accurate but incomplete (SEC-T650-01)**: `@anthropic/mcp-filesystem` is E404 on npm, the npm `anthropic` org lists only four unrelated 2022 packages, and the package is in the tagged `servers.yaml` at v5.0.0, v6.0.0 and v7.0.1 (about four months of exposure); v5.0.0 to v6.9.0 also shipped `e2b-mcp` (unscoped, E404, claimable by anyone), `redis-mcp` (an unrelated third-party package exists), `@figma/mcp` (E404, Figma org) and `@notion/mcp` (E404, owner unverified), none of which an install without a usable sidecar ever pruned. Fixed in the T645 amendment (666f36f), which also verified the tag range.
4. **Known issues text compliant**: K-15 carries the T658 required wording and the unchanged T657 remainder, K-16 carries SEC-T657-02, K-13 carries the SEC-T646-02 correction. One inaccuracy in the safe direction (SEC-T650-02): "no such mechanism on Cursor" omitted the Cursor CLI deny list; fixed in the T645 amendment.
5. **Status of every MEDIUM-or-higher finding at the release**: SEC-001, SEC-002 (graded HIGH by T637), T638 M-1/M-2/M-3, SEC-T646-01, SEC-T655-02, SEC-T655-03, SEC-T657-03 closed; SEC-003 LOW on the user's statement (D-4 unverified); T635, T636, T640 have no MEDIUM; SEC-T655-01 is superseded by SEC-T657-01 and SEC-T657-02; open: SEC-T658-01 (re-scoped SEC-T657-01), SEC-T657-02, SEC-T650-01.

## Findings

| ID | Grade | OWASP | Location | Finding | Disposition |
|---|---|---|---|---|---|
| SEC-T650-01 | SECURITY:MEDIUM | A08, A06 | `docs/releases/v8.0.0.md` M-9, K-19 | M-9 and K-19 named only the four v7.x nonexistent launchers (see answer 3) | Condition 1: fixed by the T645 amendment before T651 (owner release-manager) |
| SEC-T650-02 | LOW | A05 (accuracy) | K-15 | "On Cursor there is no such mechanism" is inaccurate for the Cursor CLI (`.cursor/cli.json` `permissions.deny`, `Mcp(server:tool)`, one doc page, untested, not per agent) | Fixed by the T645 amendment; optional research and emission as part of the SEC-T658-01 plan |
| SEC-T650-03 | LOW now, MEDIUM or HIGH if D-4 is false | A02, A05, A07 | `.gitlab-ci.yml` `release` job; SEC-003 | The LOW grade of SEC-003 rests on the user's statement that `WIKI_TOKEN` is Protected and Masked and `v*` tags are protected; nobody has verified it. If the variable is not Protected any pipeline that can read variables gets it (masking is evadable by encoding); release creation on a Maintainer-only tag needs a Maintainer-level `api` token, so SEC-003 returns to MEDIUM at least, HIGH if the token is an `api`-scope Maintainer or Owner token, and blocks the release. If the variable is Protected but `v*` is not protected, the release job fails closed without a token (functional failure) but any Developer could create `v*` tags: restrict "Allowed to create" to Maintainers | Condition 4: the user confirms D-4 before T652; the release manager records the answer in Gate Verdicts |
| SEC-T650-04 | LOW | A08, A06 | `.gitlab-ci.yml` `release`, `release-docs-gate`, `main-develop-drift-gate` | Floating images (`python:3.12-alpine`, `alpine:3.20`) and unpinned `apk add` run in the job that holds the token | Tracked debt: pin by digest at the next release |
| SEC-T650-05 | LOW (process) | A09 | `security-audit` grep tool | The tool accepts only a `root_dir` inside the primary checkout (stale develop), so it could not scan the release worktree; `poc-security-audit` `scan_secrets` and `ref_containment` were not callable; a `**/*` glob returned a line from the user's untracked, ignored local `.env` in the primary checkout (a CWSO bearer token; the value is not reproduced in any record; its own `exp` claim appears past, not verified) | Tracked: fix the tool root restriction; the orchestrator runs the scans before the tag; the user may check that the token is expired or rotated |

## Release job path

Tag jobs: `release-docs-gate` (alpine:3.20, `verify-release-docs.py`), `main-develop-drift-gate`, `release` (`publish-release.py --token "${WIKI_TOKEN}"`, needs the other two); all match the tag regex. The token travels in argv (SEC-T619-05, SEC-003) and in a `PRIVATE-TOKEN` header; `urllib` redirects would re-send it (SEC-T635-02); `validate_api_target` is a prefix check (SEC-T635-01); no error path prints the token; the script runs from the tagged commit, so whoever can create the tag runs code with the token. The upstream GitLab source limits a release description to 1,000,000 characters (the document is about 54 KB); rendering on gitlab.com was not verified (K-12). The repository and release are public; the release text publishes the remaining weaknesses on purpose.

## Secret and held-out scan

`grep_content` returned matches only from the primary checkout (stale develop): no private-key header, AWS, GitHub, Slack, API-key or JWT pattern in tracked files except fake test values (`tests/functional/test_mcp_secret_guard.py`), a `glpat-xxxx` placeholder in a test and a checkpoint, and the ignored local `.env` line noted above. The reviewer read the release document, `.gitlab-ci.yml`, `publish-release.py`, `merge-mcp-json.py`, `check-version-consistency.py`, `servers.yaml`, the 14 MCP configs, the drift baseline, `.gitignore` and parts of `install.sh` and its tests. The release document gives counts only for the held-out set (K-2). This is not a clean result from the fixed-rule scanners; `.env*` tracking on the release branch is not confirmed. T642's `tests/golden/` exclusion is correct (`startswith` on the relative POSIX path) and adds no exposure; the T658 merge rules match the T658 review.

## Conditions for the Release gate (T651)

1. SEC-T650-01 fixed in the release document (done, 666f36f).
2. SEC-T657-02: fixed (named GitLab tools for qa-engineer and scrum-master, T660) or recorded as a user-accepted risk. The user chose to fix it on 2026-10-15 ("Fix now: named tools for qa-engineer and scrum-master (Recommended)").
3. SEC-T658-01: the parts that cannot be fixed (Cursor IDE, Gemini per-agent scoping, Pi without `mcp__` entries) recorded as a user-accepted risk in the Gate Verdicts. The user accepted them on 2026-10-15 ("Accept the unfixable remainder; fix the rest after v8.0.0 (Recommended)"); the fixable parts (Opencode per-agent denies, a Cursor CLI deny list) are a tracked follow-up after v8.0.0.
4. The user confirms D-4 before T652; any "no" returns SEC-003 to MEDIUM or HIGH and blocks the release.
5. SEC-T650-02 folded into the same document edit as condition 1 (done).
6. The orchestrator runs `scan_secrets`, `ref_containment` and `git ls-files '.env*'` on `release/v8.0.0`, plus the held-out isolation test, before the tag.
7. SEC-T650-03 to -05 tracked as debt.

## Limits

No tests, no `sync.mjs --check`, no `verify-release-docs.py`, no `npm audit` or `pip-audit` were run by the reviewer; the other sidecars, the other platforms' agent projections (qa-engineer and scrum-master sampled on Claude Code and Copilot), `docs/wiki/*`, `PREREQUISITES.md`, `sync.mjs` and the T647 tooling beyond its artifact were not read; the T636, T638, T640, T646, T655, T657 and T658 reviews were relied on for what was not re-read; no platform was run live; the GitLab settings behind D-4, the pinned `@zereight/mcp-gitlab@2.2.5` README (the reviewer read `main`) and `@anthropic` account ownership beyond the registry evidence were not checked; nothing under `tests/golden/held-out/` was opened and no `.env*` file was opened deliberately.
