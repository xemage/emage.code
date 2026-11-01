# Artifact: security-review-release-v9-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (task T709). Read-only: no shell; files read in the release worktree at `ca11bb6e`. Recorded by the orchestrator from the reviewer's report.
- **Gate**: security (release level). **Date**: 2026-11-01.
- **Target**: `release/v9.0.0` at `ca11bb6e`.
- **Based on**: `docs/tasks/task-T709.md`; `docs/plans/plan-124-release-v9.md` (both addenda of 2026-11-01); `docs/releases/v9.0.0.md`; `docs/artifacts/tracked-debt-register-v3.md`; the security reviews of T662 to T712; `docs/artifacts/brave-audit-acceptance-v3.md`; `scripts/verify-release-docs.py`, `scripts/install.sh`, `.gitlab-ci.yml`; the six generated MCP configs and `servers.yaml`. Delta since the v8.0.0 re-check `security-review-release-v8-v2.md` (T650).

## Verdict: CONDITIONAL_PASS

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 2 (SEC-T662-01, SEC-T702-09) | 1 (SEC-T662-01 closed) | 1 (SEC-T702-09, accepted by the user; remediation plan acceptance v3) |
| LOW (new) | 4 (SEC-T709-01 to -04) | 0 | 4 |

No CRITICAL or HIGH is open in any review since v8.0.0; every MEDIUM is closed or accepted by the user in recorded words; no Immutable Security Constraint is breached; no control is removed or weakened. Condition: SEC-T702-09 (owner devops-engineer; acceptance v3 with its re-audit triggers; by 2027-01-30 or the first Brave release above 2.1.4).

## SEC-T662-01 (MEDIUM): closed

Checked by hand against `security-review-t662-cursor-removal-v1.md:28` (the SEC-T703-01 condition):

| Required element | `docs/releases/v9.0.0.md` |
|---|---|
| The v8.0.0 M-9 steps | 81 to 85 |
| The `filesystem` entry | 82 |
| The keys `e2b`, `redis`, `figma`, `notion` (v5.0.0 to v6.9.0) | 83 (87, K-19 at 235) |
| `--force-prune-keys` only from the `v8.0.0` tag; edit by hand | 86 (matches `scripts/install.sh:1300` on the release branch) |
| Known Issue "a Cursor install left in a project is frozen and is not pruned" | 92, K-22 at 238 |
| SEC-T678-03 (not updated; agents not tool-restricted) | 76 (38, K-22) |

The gate checks the pointer target: `scripts/verify-release-docs.py:350-367`, called at 389; `install.sh:193` and `:1301` name the document on Cursor lines; the M-1 bold lead (72) matches the anchor; `release` needs `release-docs-gate` (`.gitlab-ci.yml:191-197, 217`).

## Brave: SEC-T702-09 (MEDIUM) accepted

Acceptance v3 is valid (the user's words verbatim, seven ids scoped to `@brave/brave-search-mcp-server@2.1.4`, expiry 2027-01-30 or the first release above 2.1.4, stdio-only condition, re-audit triggers) and not expired (npm `latest` 2.1.4 on 2026-11-01). `--transport stdio` is in `servers.yaml:150`, all six generated configs and the root `.mcp.json`, with no `BRAVE_MCP_*` variable. The user's live check UA-T712-1 (plan-124 addendum) closes SEC-T712-02. M-12 and K-28 state the conditions and the lapse rule correctly.

## The release document

No token, key or secret value; no internal host or address. Constraint 6 respected (M-5, K-24: environment mode is a plaintext secret at rest, acceptable only on an encrypted disk; the in-memory token file is the default).

## Findings

| Id | Grade | Location | Finding | Recommendation |
|---|---|---|---|---|
| SEC-T709-01 | LOW | `docs/releases/v9.0.0.md:120, 240` | M-5 and K-24 present D-11 as open ("unverified whether it was decided later"); it was ruled LOW with no user decision needed (`security-review-t697-t699-debt-checkpoint-refresh-v1.md`). | State that environment mode stays supported and that on an unencrypted disk an exported token is a plaintext secret at rest and not acceptable (Constraint 6; the TD-T697-08 ruling). |
| SEC-T709-02 | LOW | `:118` | How to lift `GITLAB_PERMISSION_MODE=modify` is given without saying that on clients whose tool lists do not restrict MCP tools (Gemini CLI, Opencode built-in agents) every agent regains the delete and teardown tools. | Add that caveat; prefer `glab` or the web UI for such operations. |
| SEC-T709-03 | LOW | `:113` | M-4 (Pi) says "export the one you use" without preferring `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` or the at-rest caveat. | Prefer the file variable; never put the token itself in a shell profile or `.env` on an unencrypted disk. |
| SEC-T709-04 | LOW | `:82` | The replacement `filesystem` launcher has two unaccepted MODERATE advisories (K-17) and runs under unrestricted Cursor agents in a frozen copy. | Say so, or advise removing the entry rather than replacing it. |

Carried unchanged: SEC-T702-08, SEC-T703-01 to -03, SEC-T701-01 to -03, SEC-T712-05 (LOW, tracked); SEC-T686-03, SEC-T686-06 (LOW, pending the first tag pipeline).

## What T711 must observe

Before the tag: the verdict sections filled (T710), or `release-docs-gate` fails on the placeholders; Brave still 2.1.4 and the date before 2027-01-30; the seven-entry gate command exits 0; `v*` tags Maintainer-only. In the pipeline: `release-docs-gate` passes (with the pointer check); `main-develop-drift-gate` passes (tag tree equals `origin/main`); SEC-T686-06: record the runner version and clone method from the `release` job log, and that the `git fetch` calls of `publish-release.py` succeed under the filtered environment (on an authentication failure: fix forward or the `glab release create` fallback; never move, delete or re-create the tag); SEC-T686-03: no job-token or `JOB-TOKEN` header value in the log, no header echo, `WIKI_TOKEN` not used by `release`; the Releases API accepts `JOB-TOKEN` (release created, body equals `docs/releases/v9.0.0.md`, `CHANGELOG.md` present); all tag jobs green; record all of it in `checkpoint-040`.

## Unverified

- The release-branch commits after develop `61098c3b` were not diffed (files read in the worktree only).
- `grep_content` searched only develop `61098c3b`: the review verdict lines, the D-11 ruling, the SEC-T686 rows.
- The reviews of T665 v2, T672, T676, T680 and T686 were not opened (register v3 relied on).
- That `--projections-only` triggers the Cursor notice (code reading); that the T703 gate passes at `ca11bb6e` (not run); T706's result; the job-token masking and the Releases API with `JOB-TOKEN`; no new advisory on sdk 1.30.0 or zod 4.3.6 after T702.
