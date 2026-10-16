# Artifact: security-review-t638-mcp-packages-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no execute tool; registry spot-checks via fetch). Recorded by the orchestrator from the reviewer's report.
- **Task**: T638 (plan-121 addendum 3): the application of the user-approved MCP package fixes (audit SEC-002). Reviewed commit `4b1750b`; the developer fixed M-2, M-3 and the cheap low items in one round (`6540060`), which the orchestrator verified but the reviewer did not re-read.
- **Basis**: `docs/artifacts/mcp-server-packages-v1.md`, `security-review-release-v8-v1.md`.
- **Date**: 2026-10-15.

## Verdict: CONDITIONAL_PASS

0 critical, 0 high, 3 medium, 8 low. The diff does what the user approved and the reviewer found nothing unsafe in the shipped configs: every replacement is a real vendor package or image with an immutable pin (filesystem and git published with provenance by the MCP org; supabase by Supabase with provenance; the GitHub container manifest resolves by digest); `docker run` uses only `-i --rm -e <NAME> <image@digest>` (no privileged flag, mount or host network); no token is in argv (the GitHub token is passed by name, the Supabase token comes from env); every `npx` entry has an exact pin and no `@latest` or range remains; `docker` and `postgresql` are removed; the seven platform configs and sidecars agree with `servers.yaml`.

| ID | Grade | Concern | Condition / disposition |
|---|---|---|---|
| M-1 | MEDIUM | The repository's own root self-install is not refreshed by T638, and its tracked root configs still launch `npx -y @anthropic/mcp-filesystem` (SEC-002 stays open for this checkout until the root refresh merges). | Owner: orchestrator (user-approved root refresh). The `--projections-only` refresh merges before the v8.0.0 tag; the drift baseline then goes back to empty. Do not approve the root `filesystem` entry meanwhile. |
| M-2 | MEDIUM | Exact pins stop automatic security updates and no bump or monitoring process existed (`@zereight/mcp-gitlab` holds the GitLab PAT, single maintainer, almost daily releases). | Fixed in `6540060`: a pin-bump policy in `servers.yaml`, `PREREQUISITES.md` and the wiki (bumped at every release and at least monthly by the devops-engineer; each bump edits `servers.yaml` and `APPROVED_NPX_PINS` together; `npm audit`/OSV and registry provenance checked first; the gitlab package reviewed at every release). |
| M-3 | MEDIUM | The adopter migration note must reach a shipped document: `merge-mcp-json.py` prunes removed servers only when the old sidecar lists them; a run without a sidecar overwrites the sidecar so later pruning cannot fire; `install.sh` never passes `--force-prune-keys`; pruning is by name (a user's own entry named `docker` or `postgresql` is removed). | Fixed in `6540060`: "Migrating an existing install from v7.x" in `docs/wiki/mcp-servers.md` and "Upgrading from v7.x" in `PREREQUISITES.md`, with the bootstrap limitation stated. The v8.0.0 release notes carry the same note (release task). |
| L-1 | LOW | Fresh pins (a few days old): gitlab 2.2.5 (2.2.6 already exists), the 1.0.0 reference servers, `mcp-server-git` 2026.10.10, github-mcp-server v2.0.2. | Debt; the artifact lists soaked fallbacks. |
| L-2 | LOW | Transitive dependencies float. | Debt; documented. |
| L-3 | LOW | The GitHub container runs with the default toolset (includes writes), no signature or attestation verification, an unpatched availability-only advisory (GHSA-w4q6-qw23-4rg7), and a running Docker daemon is a host-privileged prerequisite. | Debt: consider `-e GITHUB_READ_ONLY=1` and `--cap-drop ALL --security-opt no-new-privileges` (not applied: outside the approved entries). |
| L-4 | LOW | `SUPABASE_ACCESS_TOKEN` is an account-wide token; `--read-only` limits the tools, not the token's reach. | Debt: document `--project-ref` scoping and the hosted OAuth alternative. |
| L-5 | LOW | `filesystem .` and `git --repository .` depend on the launch directory (Cline's config is global); the filesystem server can read `.env*`/`.git`; the git server exposes write tools. | Fixed in `6540060` (wiki, `PREREQUISITES.md`, `cline-setup.md`). |
| L-6 | LOW | Stale prose: `implementation/AGENTS.md:117`, `implementation/SECURITY.md:49,51`, `docs/wiki/mcp-servers.md:32` and `:48` (`GITHUB_TOKEN` should be `GITHUB_PERSONAL_ACCESS_TOKEN`). | Fixed in `6540060`; `AGENTS.md` projection adds one root-drift path (47 declared in total). |
| L-7 | LOW | Test gaps: no assertion on git `--repository .` or filesystem `.`; only the claude-code projection checked. | Fixed in `6540060`: all seven projections are checked. |
| L-8 | LOW | Single-maintainer or unverified upstreams: `mcp-fetch-server` (SSRF advisory range, fix not verified), `toolradar-mcp`, `@zereight/mcp-gitlab`. | Debt. |

Not verified by the reviewer: the commit message and report, tests and mutations (none run), `npm audit`.
